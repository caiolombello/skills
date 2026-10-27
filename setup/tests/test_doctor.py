"""Exercise the read-only diagnostic CLI against isolated repositories/homes."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

SETUP = Path(__file__).resolve().parents[1]


def snapshot(root):
    result = {}
    for path in [root, *sorted(root.rglob("*"))]:
        stat = path.lstat()
        content = os.readlink(path) if path.is_symlink() else (
            path.read_bytes() if path.is_file() else None)
        result[str(path.relative_to(root))] = (stat.st_mode, stat.st_mtime_ns, content)
    return result


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="doctor with spaces ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.home = self.root / "home"
        self.home.mkdir()
        self.skill = self.repo / "demo-skill"
        self.skill.mkdir(parents=True)
        self.metadata = "---\nname: demo-skill\ndescription: Use for a synthetic demonstration.\n---\n"
        (self.skill / "SKILL.md").write_text(self.metadata + "\n# Demonstration\n")

    def run_cli(self, *args, code=0):
        before = snapshot(self.root)
        result = subprocess.run([
            sys.executable, str(SETUP / "doctor.py"), "--repo", str(self.repo),
            "--home", str(self.home), "--format", "json", *args,
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root), before, "diagnosis changed fixture files")
        return json.loads(result.stdout)

    def test_clean_source_is_read_only(self):
        report = self.run_cli()
        self.assertEqual(report["skills"], ["demo-skill"])
        self.assertEqual(report["findings"], [])
        self.assertFalse(report["runtime_verified"])

    def test_invalid_metadata_and_missing_manifest_entry_fail(self):
        (self.skill / "SKILL.md").write_text("---\nname: wrong\ndescription: [list]\n---\n")
        profiles = self.repo / "install-manifests"
        profiles.mkdir()
        (profiles / "review.txt").write_text("missing-skill\n")
        report = self.run_cli(code=1)
        self.assertEqual({f["code"] for f in report["findings"]}, {"metadata", "manifest", "empty-source"})

    def test_yaml_errors_are_reported_without_running_tags(self):
        (self.skill / "SKILL.md").write_text("---\nname: [broken\n---\n")
        self.assertEqual(self.run_cli(code=1)["findings"][0]["code"], "metadata")

    def test_local_links_checked_but_examples_and_web_links_ignored(self):
        (self.skill / "SKILL.md").write_text(self.metadata + """
[missing](references/missing.md)
[web](https://example.com/missing)
```markdown
[example](references/example.md)
```
""")
        report = self.run_cli()
        self.assertEqual([f["code"] for f in report["findings"]], ["reference"])
        self.assertIn("missing.md", report["findings"][0]["message"])
        self.run_cli("--strict", code=1)

    def test_source_link_is_not_followed(self):
        (self.skill / "SKILL.md").unlink()
        secret = self.root / "private"
        secret.write_text("must not parse")
        (self.skill / "SKILL.md").symlink_to(secret)
        report = self.run_cli(code=1)
        self.assertEqual(report["findings"][0]["code"], "source-link")
        self.assertNotIn("must not parse", json.dumps(report))

    def test_installed_links_and_duplicate_alias(self):
        target = self.home / ".agents/skills/demo-skill"
        target.parent.mkdir(parents=True)
        target.symlink_to(self.skill)
        (target.parent / "duplicate-name").symlink_to(self.skill)
        (target.parent / "broken-name").symlink_to(self.root / "absent")
        report = self.run_cli("--installed", "--provider", "codex", code=1)
        self.assertEqual({f["code"] for f in report["findings"]}, {"duplicate", "broken-link"})
        self.assertIn("source-link", {s["status"] for s in report["installed"]})

    def test_copies_distinguish_local_edits_from_outdated_source(self):
        target = self.home / ".agents/skills/demo-skill"
        target.parent.mkdir(parents=True)
        shutil.copytree(self.skill, target)
        sys.path.insert(0, str(SETUP))
        try:
            from install import fingerprint
            owned = fingerprint(target)
        finally:
            sys.path.pop(0)
        state = self.home / ".local/state/caiolombello-skills"
        state.mkdir(parents=True)
        (state / "installed.json").write_text(json.dumps({str(target): {"fingerprint": owned}}))
        (self.skill / "SKILL.md").write_text(self.metadata + "\nNew source\n")
        report = self.run_cli("--installed", "--provider", "codex")
        self.assertEqual(report["installed"][0]["status"], "outdated-copy")
        (target / "SKILL.md").write_text("private local edits")
        report = self.run_cli("--installed", "--provider", "codex")
        self.assertEqual(report["installed"][0]["status"], "locally-edited-copy")
        self.assertNotIn("private local edits", json.dumps(report))

    def test_external_root_alias_is_not_scanned(self):
        outside = self.root / "external"
        outside.mkdir()
        (outside / "do-not-read").write_text("private")
        (self.home / ".agents").mkdir()
        (self.home / ".agents/skills").symlink_to(outside)
        report = self.run_cli("--installed", "--provider", "codex")
        self.assertEqual(report["findings"][0]["code"], "external-root")
        self.assertEqual(report["installed"], [])

    def test_manifest_directory_link_is_not_followed(self):
        outside = self.root / "private-profiles"
        outside.mkdir()
        (outside / "private.txt").write_text("sensitive-value\n")
        (self.repo / "install-manifests").symlink_to(outside)
        report = self.run_cli(code=1)
        self.assertEqual(report["findings"][0]["code"], "manifest")
        self.assertNotIn("sensitive-value", json.dumps(report))

    def test_invalid_evaluation_and_missing_artifact_are_reported(self):
        folder = self.skill / "evals"
        folder.mkdir()
        path = folder / "scenarios.json"
        path.write_text("{broken")
        self.assertEqual(self.run_cli(code=1)["findings"][0]["code"], "evaluation")
        path.write_text(json.dumps({"version": 1, "cases": [{
            "id": "missing-fixture", "prompt": "Review this synthetic file.",
            "expectations": ["Use the fixture"], "artifacts": ["fixtures/missing.py"],
        }]}))
        report = self.run_cli(code=1)
        self.assertEqual(report["findings"][0]["code"], "evaluation")
        self.assertIn("artifact", report["findings"][0]["message"])

    def test_nonstring_yaml_key_is_a_finding_not_a_crash(self):
        (self.skill / "SKILL.md").write_text(self.metadata.replace("\n---\n", "\n7: extra\n---\n"))
        self.assertEqual(self.run_cli(code=1)["findings"][0]["code"], "metadata")


if __name__ == "__main__":
    unittest.main()
