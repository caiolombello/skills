"""Generated catalog behavior: deterministic output and explicit writes only."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "build_catalog.py"


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        skill = self.repo / "demo-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text('---\nname: demo-skill\ndescription: "Use for tables | and [text]."\n---\nBody\n')
        (self.repo / "install-manifests").mkdir()
        (self.repo / "install-manifests/writing.txt").write_text("demo-skill\n")

    def run_cli(self, *args, code=0):
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def test_missing_catalog_check_does_not_create_it(self):
        self.run_cli(code=1)
        self.assertFalse((self.repo / "CATALOG.md").exists())

    def test_explicit_generation_and_stale_check(self):
        self.run_cli("--apply")
        catalog = self.repo / "CATALOG.md"
        first, mtime = catalog.read_text(), catalog.stat().st_mtime_ns
        self.assertIn("writing", first)
        self.assertIn("tables &#124; and", first)
        self.run_cli()
        self.run_cli("--apply")
        self.assertEqual(catalog.stat().st_mtime_ns, mtime)
        (self.repo / "install-manifests/writing.txt").write_text("")
        self.run_cli(code=1)
        self.assertEqual(catalog.read_text(), first)

    def test_catalog_symlink_is_refused(self):
        outside = self.repo / "private"
        outside.write_text("preserve")
        (self.repo / "CATALOG.md").symlink_to(outside)
        self.run_cli("--apply", code=2)
        self.assertEqual(outside.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
