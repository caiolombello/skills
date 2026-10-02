"""Filesystem behavior checks; no providers, credentials, network or packages."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "install.py"
spec = importlib.util.spec_from_file_location("installer", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skills with spaces ")
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo with spaces"
        (self.repo / "setup").mkdir(parents=True)
        shutil.copyfile(SCRIPT, self.repo / "setup/install.py")
        self.home = self.root / "isolated home"
        self.source = self.repo / "demo-skill"
        (self.source / "references").mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Synthetic test\n---\n")
        (self.source / "references/test.md").write_text("original reference\n")
        self.target = self.home / ".agents/skills/demo-skill"

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *extra, success=True, default=True):
        args = [sys.executable, str(self.repo / "setup/install.py"), "--home", str(self.home)]
        if default:
            args.extend(["--provider", "codex", "--skill", "demo-skill"])
        result = subprocess.run(args + list(extra), capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def transaction(self):
        return json.loads((self.home / ".local/state/caiolombello-skills/installed.json").read_text())[str(self.target)]["transaction"]

    def test_dry_run_writes_nothing(self):
        self.run_cli()
        self.assertFalse(self.home.exists())

    def test_apply_idempotent_update_and_rollback(self):
        self.run_cli("--apply")
        first = self.transaction()
        self.run_cli("--apply")
        self.assertEqual(first, self.transaction())
        (self.source / "references/test.md").write_text("updated reference\n")
        self.run_cli("--apply")
        second = self.transaction()
        self.assertNotEqual(first, second)
        self.run_cli("--rollback", second, default=False)
        self.assertEqual((self.target / "references/test.md").read_text(), "updated reference\n")
        self.run_cli("--rollback", second, "--apply", default=False)
        self.assertEqual((self.target / "references/test.md").read_text(), "original reference\n")
        self.assertEqual(self.transaction(), first)
        self.run_cli("--rollback", first, "--apply", default=False)
        self.assertFalse(self.target.exists())

    def test_foreign_directory_is_preserved(self):
        self.target.mkdir(parents=True)
        (self.target / "mine").write_text("do not replace")
        self.run_cli("--apply", success=False)
        self.assertEqual((self.target / "mine").read_text(), "do not replace")

    def test_local_edit_blocks_update_and_rollback(self):
        self.run_cli("--apply")
        tx = self.transaction()
        (self.target / "SKILL.md").write_text("user edit")
        self.run_cli("--apply", success=False)
        self.run_cli("--rollback", tx, "--apply", success=False, default=False)
        self.assertEqual((self.target / "SKILL.md").read_text(), "user edit")

    def test_owned_live_symlink_is_left_alone(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.source, target_is_directory=True)
        self.run_cli("--apply")
        self.assertTrue(self.target.is_symlink())
        self.assertFalse((self.home / ".local/state/caiolombello-skills/installed.json").exists())

    def test_broken_foreign_symlink_is_preserved(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.root / "missing")
        self.run_cli("--apply", success=False)
        self.assertTrue(self.target.is_symlink())

    def test_alias_root_deduplicates_providers(self):
        (self.home / ".agents/skills").mkdir(parents=True)
        (self.home / ".claude").mkdir()
        (self.home / ".claude/skills").symlink_to(self.home / ".agents/skills", target_is_directory=True)
        self.run_cli("--provider", "claude", "--apply")
        entries = json.loads((self.home / ".local/state/caiolombello-skills/installed.json").read_text())
        self.assertEqual(len(entries), 1)

    def test_escaping_alias_and_source_symlink_rejected(self):
        (self.home / ".agents").mkdir(parents=True)
        (self.home / ".agents/skills").symlink_to(self.root / "outside home", target_is_directory=True)
        self.run_cli(success=False)
        (self.home / ".agents/skills").unlink()
        (self.source / "references/escape").symlink_to(self.root / "outside source")
        self.run_cli(success=False)

    def test_manifest_and_provider_paths(self):
        manifest = self.repo / "selection with spaces.txt"
        manifest.write_text("# selective\n\ndemo-skill # comment\ndemo-skill\n")
        args = ["--manifest", str(manifest), "--apply"]
        for name in installer.PROVIDERS:
            args.extend(["--provider", name])
        self.run_cli(*args, default=False)
        for path in installer.PROVIDERS.values():
            self.assertEqual((self.home / path / "demo-skill/references/test.md").read_text(), "original reference\n")

    def test_invalid_selection_is_atomic(self):
        self.run_cli("--skill", "missing-skill", "--apply", success=False)
        self.assertFalse(self.target.exists())
        self.run_cli("--skill", "../escape", success=False)

    def test_bad_backup_does_not_remove_current_install(self):
        self.run_cli("--apply")
        (self.source / "references/test.md").write_text("update")
        self.run_cli("--apply")
        tx = self.transaction()
        backups = self.home / ".local/state/caiolombello-skills/backups" / tx
        shutil.rmtree(backups / "0")
        self.run_cli("--rollback", tx, "--apply", default=False, success=False)
        self.assertEqual((self.target / "references/test.md").read_text(), "update")

    def test_lock_blocks_concurrent_apply(self):
        (self.home / ".local/state/caiolombello-skills/lock").mkdir(parents=True)
        self.run_cli("--apply", success=False)
        self.assertFalse(self.target.exists())

    def test_cache_redirect_is_refused(self):
        cache = self.home / ".codex/plugins/cache/test"
        cache.mkdir(parents=True)
        (self.home / ".agents").mkdir()
        (self.home / ".agents/skills").symlink_to(cache, target_is_directory=True)
        self.run_cli("--apply", success=False)
        self.assertEqual(list(cache.iterdir()), [])

    def test_interrupted_prepared_transaction_can_restore(self):
        self.run_cli("--apply")
        tx = self.transaction()
        journal = self.home / ".local/state/caiolombello-skills/transactions" / (tx + ".json")
        record = json.loads(journal.read_text())
        record["status"] = "prepared"
        journal.write_text(json.dumps(record))
        self.run_cli("--rollback", tx, "--apply", default=False)
        self.assertFalse(self.target.exists())

    def interrupted_update(self):
        self.run_cli("--apply")
        first = self.transaction()
        (self.source / "references/test.md").write_text("update")
        self.run_cli("--apply")
        tx = self.transaction()
        journal = self.home / ".local/state/caiolombello-skills/transactions" / (tx + ".json")
        record = json.loads(journal.read_text())
        record["status"] = "prepared"
        journal.write_text(json.dumps(record))
        return first, tx, record

    def test_interrupted_removal_recovers_verified_backup(self):
        first, tx, record = self.interrupted_update()
        shutil.rmtree(self.target)
        self.run_cli("--rollback", tx, "--apply", default=False)
        self.assertEqual(self.transaction(), first)
        self.assertEqual((self.target / "references/test.md").read_text(), "original reference\n")

    def test_interrupted_restore_reconciles_ownership(self):
        first, tx, record = self.interrupted_update()
        shutil.rmtree(self.target)
        backup = self.home / ".local/state/caiolombello-skills/backups" / tx / "0"
        shutil.copytree(backup, self.target)
        self.run_cli("--rollback", tx, "--apply", default=False)
        self.assertEqual(self.transaction(), first)
        (self.source / "references/test.md").write_text("original reference\n")
        self.run_cli()

    def test_state_descendant_alias_cannot_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        state = self.home / ".local/state/caiolombello-skills"
        state.mkdir(parents=True)
        (state / "backups").symlink_to(outside)
        self.run_cli("--apply", success=False)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.target.exists())

    def test_tampered_journal_cannot_remove_nonnative_file(self):
        self.run_cli("--apply")
        tx = self.transaction()
        note = self.home / "personal-note.txt"
        note.write_text("preserve")
        journal = self.home / ".local/state/caiolombello-skills/transactions" / (tx + ".json")
        record = json.loads(journal.read_text())
        record["status"] = "prepared"
        record["operations"][0]["target"] = str(note)
        record["operations"][0]["after"] = installer.fingerprint(note)
        journal.write_text(json.dumps(record))
        self.run_cli("--rollback", tx, "--apply", default=False, success=False)
        self.assertEqual(note.read_text(), "preserve")

    def test_malformed_state_has_clean_error(self):
        state = self.home / ".local/state/caiolombello-skills"
        state.mkdir(parents=True)
        (state / "installed.json").write_text("[]")
        result = self.run_cli("--apply", success=False)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.target.exists())

    def test_restore_interruption_points(self):
        # BaseException simulates process termination, bypassing normal recovery.
        class Interrupted(BaseException):
            pass
        for point in ("copy", "retire", "publish", "state", "journal"):
            with self.subTest(point=point):
                if self.home.exists():
                    shutil.rmtree(self.home)
                (self.source / "references/test.md").write_text("original reference\n")
                self.run_cli("--apply")
                first = self.transaction()
                (self.source / "references/test.md").write_text("update")
                self.run_cli("--apply")
                tx = self.transaction()
                state = self.home / ".local/state/caiolombello-skills"
                spec = importlib.util.spec_from_file_location("isolated", self.repo / "setup/install.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                copy, rename, save = module.shutil.copytree, Path.rename, module.save_json
                def interrupted_copy(src, dst, *args, **kwargs):
                    if point == "copy" and str(dst).endswith("-stage"):
                        Path(dst).mkdir()
                        (Path(dst) / "SKILL.md").write_bytes((Path(src) / "SKILL.md").read_bytes()[:7])
                        raise Interrupted()
                    return copy(src, dst, *args, **kwargs)
                def interrupted_rename(src, dst):
                    result = rename(src, dst)
                    if (point == "retire" and str(dst).endswith("-retired")) or (point == "publish" and str(src).endswith("-stage")):
                        raise Interrupted()
                    return result
                def interrupted_save(path, data):
                    result = save(path, data)
                    if (point == "state" and path.name == "installed.json") or (point == "journal" and data.get("status") == "rolled-back"):
                        raise Interrupted()
                    return result
                with mock.patch.object(module.shutil, "copytree", interrupted_copy), mock.patch.object(Path, "rename", interrupted_rename), mock.patch.object(module, "save_json", interrupted_save):
                    with self.assertRaises(Interrupted):
                        module.rollback(tx, state, self.home, True)
                self.assertEqual((state / "backups" / tx / "0/references/test.md").read_text(), "original reference\n")
                if point == "copy":
                    self.assertEqual((self.target / "references/test.md").read_text(), "update")
                if point != "journal":
                    self.run_cli("--rollback", tx, "--apply", default=False)
                else:
                    self.assertEqual(json.loads((state / "transactions" / (tx + ".json")).read_text())["status"], "rolled-back")
                self.assertEqual(self.transaction(), first)
                self.assertEqual((self.target / "references/test.md").read_text(), "original reference\n")

    def test_owned_restore_scratch_drift_is_preserved(self):
        first, tx, record = self.interrupted_update()
        journal = self.home / ".local/state/caiolombello-skills/transactions" / (tx + ".json")
        record["operations"][0]["phase"] = "restoring"
        journal.write_text(json.dumps(record))
        stage = self.target.parent / (".caio-rollback-" + tx + "-0-stage")
        stage.mkdir()
        (stage / "SKILL.md").write_text("manual scratch edit")
        self.run_cli("--rollback", tx, "--apply", default=False, success=False)
        self.assertEqual((stage / "SKILL.md").read_text(), "manual scratch edit")
        self.assertEqual((self.target / "references/test.md").read_text(), "update")


if __name__ == "__main__":
    unittest.main()
