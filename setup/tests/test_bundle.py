"""Local artifact invariants; native runtime checks are reported separately."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "plugins/caio-frontend"


class BundleTests(unittest.TestCase):
    def load(self, path):
        return json.loads(path.read_text())

    def test_sources_and_licenses_are_synchronized(self):
        result = subprocess.run([sys.executable, str(ROOT / "setup/build_frontend.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((ROOT / "ai-interface-design/LICENSE").read_bytes(),
                         (PACKAGE / "skills/ai-interface-design/LICENSE").read_bytes())

    def test_provider_manifests_agree_on_identity(self):
        paths = [PACKAGE / "plugin.json"] + [PACKAGE / name / "plugin.json"
                 for name in (".codex-plugin", ".claude-plugin", ".cursor-plugin")]
        versions = set()
        for path in paths:
            manifest = self.load(path)
            self.assertEqual(manifest["name"], PACKAGE.name)
            self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
            versions.add(manifest["version"])
            self.assertTrue(manifest["author"]["name"])
            self.assertFalse(set(manifest) & {"hooks", "mcpServers", "apps"})
        self.assertEqual(len(versions), 1)

    def test_marketplace_roots_resolve_inside_repo(self):
        for directory in (".agents/plugins", ".claude-plugin", ".cursor-plugin"):
            manifest = self.load(ROOT / directory / "marketplace.json")
            self.assertEqual(manifest["name"], "caio-skills")
            self.assertEqual(len(manifest["plugins"]), 1)
            entry = manifest["plugins"][0]
            self.assertEqual(entry["name"], PACKAGE.name)
            source = entry["source"]
            rel = source["path"] if isinstance(source, dict) else source
            self.assertNotIn("..", Path(rel).parts)
            self.assertEqual((ROOT / rel).resolve(), PACKAGE.resolve())

    def test_codex_paths_prompts_and_no_fake_assets(self):
        manifest = self.load(PACKAGE / ".codex-plugin/plugin.json")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((PACKAGE / manifest["skills"]).is_dir())
        interface = manifest["interface"]
        self.assertTrue(interface["displayName"])
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        for prompt in interface["defaultPrompt"]:
            self.assertLessEqual(len(prompt), 128)
        self.assertFalse(set(interface) & {"privacyPolicyURL", "termsOfServiceURL", "logo", "composerIcon"})

    def test_payload_is_only_three_skills_without_runtime_hooks(self):
        names = {p.name for p in (PACKAGE / "skills").iterdir()}
        self.assertEqual(names, {"frontend-design", "frontend-development", "ai-interface-design"})
        for path in PACKAGE.rglob("*"):
            self.assertFalse(path.is_symlink())
            self.assertNotIn(path.name, {"hooks.json", ".mcp.json", "mcp.json", ".app.json"})
        for name in names:
            self.assertTrue((PACKAGE / "skills" / name / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
