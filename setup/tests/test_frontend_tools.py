"""Behavior checks for frontend-design QA scripts; browser test skips without Playwright."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "frontend-design/scripts"

BAD_COMPONENT = """\
export function Hero() {
  return (
    <section className="h-screen bg-gradient-to-br from-purple-600 via-indigo-500 to-pink-500">
      <h1 className="bg-gradient-to-r from-violet-200 to-pink-200 bg-clip-text text-transparent">Supercharge your workflow</h1>
      <p>Lorem ipsum dolor sit amet.</p>
      <a href="#" className="rounded-full px-6 py-3 outline-none">Get started 🚀</a>
      <button className="p-1"><svg viewBox="0 0 16 16" /></button>
      <div className="p-6" onClick={() => open()}><h3>Card</h3></div>
      <img src="/hero.png" />
      <div tabIndex={2}>Skip</div>
    </section>
  );
}
"""
BAD_CSS = "button:focus { outline: none; }\n.title { -webkit-background-clip: text; color: transparent; }\n"
BAD_HTML = '<!doctype html><html><head><meta name="viewport" content="width=device-width, user-scalable=no"></head><body></body></html>\n'
GOOD_COMPONENT = """\
import { Download } from "lucide-react";

export function Invoices({ rows }) {
  if (!rows.length) return <p className="text-muted-foreground">No invoices yet. Create one from a client page.</p>;
  return (
    <div>
      <button type="button" aria-label="Download CSV" className="h-9 w-9 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-ring">
        <Download className="h-4 w-4" aria-hidden="true" />
      </button>
      <a href="/invoices/new">New invoice</a>
      <img src="/empty.svg" alt="" width={120} height={80} />
    </div>
  );
}
"""


class FrontendToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="frontend tools ")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def lint(self, *paths):
        result = subprocess.run([sys.executable, str(SCRIPTS / "ui_lint.py"), *map(str, paths), "--format", "json"],
                                capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_lint_reports_known_defects(self):
        bad = self.root / "bad"
        (bad / "src").mkdir(parents=True)
        (bad / "src/Hero.tsx").write_text(BAD_COMPONENT)
        (bad / "src/styles.css").write_text(BAD_CSS)
        (bad / "index.html").write_text(BAD_HTML)
        code, report = self.lint(bad)
        self.assertEqual(code, 1)
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        for rule in ("outline-removed", "icon-button-unnamed", "fake-control", "img-alt-missing",
                     "positive-tabindex", "zoom-disabled"):
            self.assertEqual(rules.get(rule), "error", rule)
        for rule in ("purple-gradient", "gradient-text", "placeholder-copy", "emoji-ui", "dead-link",
                     "outline-removed-unverified", "html-lang-missing"):
            self.assertIn(rule, rules)
        self.assertIn("cliche-copy", rules)

    def test_lint_accepts_clean_component(self):
        good = self.root / "good"
        good.mkdir()
        (good / "Invoices.tsx").write_text(GOOD_COMPONENT)
        (good / "tokens.css").write_text(":focus-visible { outline: 2px solid var(--focus); }\n"
                                         "button:focus:not(:focus-visible) { outline: none; }\n")
        code, report = self.lint(good)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["findings"], [])

    def test_lint_skips_dependency_and_build_folders(self):
        (self.root / "node_modules/pkg").mkdir(parents=True)
        (self.root / "node_modules/pkg/x.tsx").write_text(BAD_COMPONENT)
        (self.root / "dist").mkdir()
        (self.root / "dist/app.css").write_text(BAD_CSS)
        code, report = self.lint(self.root)
        self.assertEqual((code, report["files"]), (0, 0))

    def test_lint_changed_reports_only_touched_lines(self):
        if not shutil.which("git"):
            self.skipTest("git unavailable")
        repo = self.root / "repo"
        repo.mkdir()
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *a],
                                        cwd=repo, check=True, capture_output=True)
        git("init", "-q")
        (repo / "Legacy.tsx").write_text('<img src="/legacy.png" />\n')
        git("add", ".")
        git("commit", "-q", "-m", "legacy")
        (repo / "Legacy.tsx").write_text('<img src="/legacy.png" />\n<a href="#">x</a>\n')
        (repo / "New.tsx").write_text("export const A = () => <div onClick={go}><h3>Card</h3></div>;\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "ui_lint.py"), ".", "--changed", "--format", "json"],
                                cwd=repo, capture_output=True, text=True)
        report = json.loads(result.stdout)
        rules = {f["rule"] for f in report["findings"]}
        self.assertEqual(rules, {"fake-control", "dead-link"}, report)
        self.assertEqual(report["hiddenPreexisting"], 1)
        outside = subprocess.run([sys.executable, str(SCRIPTS / "ui_lint.py"), ".", "--changed"],
                                 cwd=self.root, capture_output=True, text=True)
        self.assertEqual(outside.returncode, 2)

    def test_contrast_cli(self):
        def run(*pair):
            return subprocess.run([sys.executable, str(SCRIPTS / "contrast.py"), *pair], capture_output=True, text=True)
        passing = run("#767676", "#ffffff")
        self.assertEqual(passing.returncode, 0, passing.stdout)
        self.assertIn("4.54:1", passing.stdout)
        self.assertEqual(run("#777777", "#ffffff").returncode, 1)
        tokens = run("oklch(0.48 0.012 250)", "oklch(0.985 0.002 250)", "oklch(0.95 0.004 250)", "oklch(0.17 0.006 250)")
        self.assertEqual(tokens.returncode, 0, tokens.stdout)
        self.assertEqual(run("not-a-color", "#fff").returncode, 2)

    def test_visual_qa_renders_and_audits(self):
        if not shutil.which("node"):
            self.skipTest("node unavailable")
        page = self.root / "page.html"
        page.write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>t</title></head>'
            '<body><main><h1>Settings</h1><input placeholder="Email">'
            '<div style="width:640px;height:10px;background:#ccc"></div></main></body></html>')
        out = self.root / "qa out"
        result = subprocess.run(["node", str(SCRIPTS / "visual_qa.mjs"), "--file", str(page), "--widths", "390",
                                 "--audit-widths", "320", "--themes", "light", "--no-full-page", "--focus-steps", "3",
                                 "--out", str(out), "--json"], capture_output=True, text=True, cwd=self.root, timeout=180)
        if result.returncode == 2 and ("Playwright not found" in result.stderr or "could not launch" in result.stderr):
            self.skipTest("Playwright/Chromium unavailable")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        report = json.loads((self.root / summary["report"]).read_text())
        ids = {f["id"] for f in report["targets"][0]["findings"]}
        self.assertTrue({"horizontal-overflow", "placeholder-as-label"} <= ids, ids)
        shot = self.root / summary["viewOrder"][0]
        self.assertTrue(shot.is_file() and shot.stat().st_size > 1000)


    def test_visual_qa_starts_server_and_captures_mocked_states(self):
        if not shutil.which("node"):
            self.skipTest("node unavailable")
        site = self.root / "site"
        (site / "api").mkdir(parents=True)
        (site / "api/items").write_text('[{"name": "Alpha"}]')
        (site / "index.html").write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Items</title></head>'
            '<body><main><h1>Items</h1><p id="out">Loading</p><div style="height:2400px"></div></main>'
            "<script>fetch('/api/items').then(r => r.json()).then(i => { document.getElementById('out').textContent ="
            " i.length ? i[0].name : 'No items yet'; });</script></body></html>")
        steps = self.root / "steps.json"
        steps.write_text(json.dumps([{"action": "route", "url": "**/api/items", "json": []},
                                     {"action": "reload"}, {"action": "wait", "ms": 150},
                                     {"action": "capture", "name": "empty"}]))
        import socket
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        start = f'"{sys.executable}" -m http.server {port} --bind 127.0.0.1 --directory "{site}"'
        out = self.root / "qa"
        result = subprocess.run(["node", str(SCRIPTS / "visual_qa.mjs"), "--start", start, "--url", f"http://127.0.0.1:{port}/",
                                 "--steps", str(steps), "--widths", "390", "--audit-widths", "", "--themes", "light",
                                 "--focus-steps", "0", "--max-tiles", "2", "--out", str(out), "--json"],
                                capture_output=True, text=True, cwd=self.root, timeout=240)
        if result.returncode == 2 and ("Playwright not found" in result.stderr or "could not launch" in result.stderr):
            self.skipTest("Playwright/Chromium unavailable")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        names = [Path(p).name for p in summary["viewOrder"]]
        self.assertIn("home-390-empty.png", names)
        self.assertEqual(sum(n.startswith("home-390-light-part-") for n in names), 2)
        with socket.socket() as sock:
            self.assertNotEqual(sock.connect_ex(("127.0.0.1", port)), 0, "dev server left running")


if __name__ == "__main__":
    unittest.main()
