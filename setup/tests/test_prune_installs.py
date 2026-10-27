"""Pruning selects current and legacy roots without touching the real home."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("bash") and shutil.which("readlink"), "shell tools unavailable")
class PruneInstallTests(unittest.TestCase):
    def test_default_scan_covers_both_opencode_roots_and_preserves_foreign_data(self):
        with tempfile.TemporaryDirectory(prefix="prune fixtures ") as folder:
            base = Path(folder)
            repo = base / "source"
            scripts = repo / "install-manifests"
            scripts.mkdir(parents=True)
            script = scripts / "prune-stale-installs.sh"
            shutil.copy2(ROOT / "install-manifests/prune-stale-installs.sh", script)
            (scripts / "codex-keep.txt").write_text("kept-skill\n")
            for name in ("kept-skill", "stale-skill"):
                skill = repo / name
                skill.mkdir()
                (skill / "SKILL.md").write_text("fixture\n")
            selected_home = base / "selected home"
            foreign = base / "foreign skill"
            foreign.mkdir()
            for suffix in ("skills", "skill"):
                target = selected_home / ".config/opencode" / suffix
                target.mkdir(parents=True)
                (target / "kept-skill").symlink_to(repo / "kept-skill")
                (target / "stale-skill").symlink_to(repo / "stale-skill")
                (target / "foreign-skill").symlink_to(foreign)
                (target / "real-skill").mkdir()
                (target / "real-skill/private.txt").write_text("preserve")
            command = ["bash", str(script), "--home", str(selected_home)]
            preview = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            for suffix in ("skills", "skill"):
                target = selected_home / ".config/opencode" / suffix
                self.assertTrue((target / "stale-skill").is_symlink())
                self.assertIn(str(target), preview.stdout)
            applied = subprocess.run(command + ["--apply"], text=True, capture_output=True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            for suffix in ("skills", "skill"):
                target = selected_home / ".config/opencode" / suffix
                self.assertFalse((target / "stale-skill").is_symlink())
                self.assertTrue((target / "kept-skill").is_symlink())
                self.assertEqual((target / "foreign-skill").resolve(), foreign)
                self.assertEqual((target / "real-skill/private.txt").read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
