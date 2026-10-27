"""Execute the documented IAM transfer with fake CLIs, never real credentials."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_SECRET = "PUBLIC_FAKE_SECRET_FOR_TEST_ONLY"
FAKE_CLI = r'''
import json, os, stat, sys, tempfile
from pathlib import Path
args = sys.argv[1:]
name = Path(sys.argv[0]).name
if name == "mktemp":
    print(tempfile.mkdtemp(prefix="transfer-", dir=os.environ["FIXTURE_ROOT"]))
    raise SystemExit(0)
event = {"command": name, "argv": args}
reply = {}
if name == "aws" and "create-access-key" in args:
    reply = {"AccessKey": {"AccessKeyId": "PUBLIC_FAKE_ACCESS_KEY", "SecretAccessKey": os.environ["FIXTURE_SECRET"]}}
    if "--output" not in args or args[args.index("--output") + 1] != "json":
        reply = "PUBLIC PROFILE DEFAULT IS TEXT, NOT JSON"
if name == "pass-cli":
    if "--from-template" not in args:
        raise SystemExit("Only the fake template consumer is permitted")
    source = Path(args[args.index("--from-template") + 1])
    event["received"] = json.loads(source.read_text())
    event["file_mode"] = stat.S_IMODE(source.stat().st_mode)
    event["directory_mode"] = stat.S_IMODE(source.parent.stat().st_mode)
    event["private_path"] = str(source.parent)
    reply = event["received"]  # A consumer may echo the supplied fields.
with open(os.environ["FIXTURE_LOG"], "a") as log:
    log.write(json.dumps(event) + "\n")
if name == "pass-cli" and os.environ.get("FIXTURE_IMPORT_FAILURE") == "1":
    print(os.environ["FIXTURE_SECRET"], file=sys.stderr)
    raise SystemExit(9)
print(json.dumps(reply))
'''


def creation_recipe(document):
    section = document.split("### IAM rotation pattern (access keys)", 1)[1]
    code = section.split("```bash\n", 1)[1].split("\n```", 1)[0]
    return re.sub(r"<[^>\n]+>", "public-fixture", code)


@unittest.skipUnless(shutil.which("bash") and shutil.which("mktemp"), "shell tools unavailable")
class SecretTransferTests(unittest.TestCase):
    def run_recipe(self, recipe, fail_import=False):
        with tempfile.TemporaryDirectory(prefix="secret transfer fixtures ") as folder:
            base = Path(folder)
            binaries = base / "fake-bin"
            binaries.mkdir()
            for name in ("aws", "pass-cli", "mktemp"):
                executable = binaries / name
                executable.write_text("#!" + sys.executable + "\n" + FAKE_CLI)
                executable.chmod(0o700)
            # No other credential/provider executable can be reached by PATH.
            for name in ("rm", "python3"):
                resolved = sys.executable if name == "python3" else shutil.which(name)
                if not resolved:
                    self.skipTest(name + " unavailable")
                (binaries / name).symlink_to(resolved)
            log = base / "calls.jsonl"
            env = {key: value for key, value in os.environ.items()
                   if key not in {"BASH_ENV", "ENV"} and not key.startswith("BASH_FUNC_")}
            env.update(PATH=str(binaries),
                       FIXTURE_LOG=str(log), FIXTURE_SECRET=PUBLIC_SECRET,
                       FIXTURE_ROOT=str(base), FIXTURE_IMPORT_FAILURE=str(int(fail_import)))
            result = subprocess.run([shutil.which("bash"), "--noprofile", "--norc", "-c", recipe],
                                    cwd=base, env=env, capture_output=True, text=True, timeout=15)
            events = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            for event in events:
                if "private_path" in event:
                    retained = Path(event["private_path"])
                    event["retained_after_exit"] = retained.exists()
                    response = retained / "aws-response.json"
                    event["key_recoverable_after_exit"] = response.exists() and (
                        json.loads(response.read_text())["AccessKey"]["SecretAccessKey"] == PUBLIC_SECRET)
            return result, events

    def test_key_is_transferred_privately_and_old_key_is_not_changed(self):
        document = (ROOT / "awscli-workflows/SKILL.md").read_text()
        result, events = self.run_recipe(creation_recipe(document))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(PUBLIC_SECRET, result.stdout + result.stderr)
        self.assertNotIn(PUBLIC_SECRET, json.dumps([e["argv"] for e in events]))
        imports = [e for e in events if e["command"] == "pass-cli"]
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0]["received"]["password"], PUBLIC_SECRET)
        self.assertEqual(imports[0]["file_mode"], 0o600)
        self.assertEqual(imports[0]["directory_mode"], 0o700)
        self.assertFalse(imports[0]["retained_after_exit"], "private transfer files survived successful cleanup")
        self.assertFalse(any("update-access-key" in e["argv"] or "delete-access-key" in e["argv"] for e in events),
                         "creation/import silently changed the old key before cutover verification")

    def test_failed_import_preserves_the_one_time_response_without_printing_it(self):
        document = (ROOT / "awscli-workflows/SKILL.md").read_text()
        result, events = self.run_recipe(creation_recipe(document), fail_import=True)
        self.assertEqual(result.returncode, 9)
        self.assertNotIn(PUBLIC_SECRET, result.stdout + result.stderr)
        imported = next(e for e in events if e["command"] == "pass-cli")
        self.assertTrue(imported["retained_after_exit"])
        self.assertTrue(imported["key_recoverable_after_exit"])
        self.assertIn(imported["private_path"], result.stderr)
        self.assertEqual(imported["directory_mode"], 0o700)
        self.assertFalse(any("update-access-key" in e["argv"] or "delete-access-key" in e["argv"] for e in events))


if __name__ == "__main__":
    unittest.main()
