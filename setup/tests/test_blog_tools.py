"""The blog diagnostic surfaces patterns without treating them as proof of bad prose."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "blog-posting/scripts"

BAD_POST_EN = """# The Ultimate Guide to Observability

In today's fast-paced development landscape, delivering robust and seamless experiences has become more crucial than ever. Whether you're a seasoned engineer or just embarking on your journey, understanding observability is a genuine game-changer. It's not just about collecting metrics — it's about weaving a rich tapestry of logs, traces, and events. Moreover, this powerful approach empowers teams to delve into complex issues with total confidence.

Observability is a discipline that transforms how engineering organizations operate on complex production systems. It is important to note that many teams struggle with fragmented tooling across their existing stack. Furthermore, the challenges of modern distributed systems require a comprehensive strategy covering metrics, logs, and traces. Additionally, the costs of downtime continue to grow every single year across the industry.

## Understanding the Basics

The platform provides fast, flexible, and reliable insights — for every engineering team in the organization. The platform delivers clear, concise, and actionable dashboards for on-call rotations across time zones. The platform offers deep visibility, quick answers, and confident decisions for developers everywhere.

## Key Takeaways

In conclusion, observability is not only a technical investment but also a cultural shift — one that will revolutionize how your team builds software.
"""

GOOD_POST_EN = """# What 2am taught me about observability

The pager went off at 2:14am on a Thursday. The checkout service was timing out for about 4% of requests, which sounds small until you remember what checkout is.

We had three signals open: the latency graph, the trace for one failed request, and one log line. The trace showed a request stuck 40 seconds in the payment client. The log line, from a connection pool we did not even know was involved (nobody could remember who added the client, and the client had no owner, which is its own story), said the pool had been exhausted since 18:02. Someone had shipped a migration at 18:00.

Ten minutes to the answer.

## The part everyone skips

The useful part was not the tool. It was that the pool exhaustion started two minutes after a deploy, and we could see both events on one timeline.

We fixed the pool size that night, at 2:51am, and filed the real fix (a health check on pool saturation) for the morning. That is the honest version of the story: the mitigation was quick, the actual fix took another week.

## Would I do it again

Yes, and I would start with traces, not metrics. Metrics told us something was wrong. The trace told us where.

If you run a small service, start with structured logs. If you run more than two services, add tracing before you add another dashboard.
"""

BAD_POST_PT = """# Guia definitivo de logs estruturados

No cenário atual, garantir entregas robustas e dinâmicas tornou-se cada vez mais essencial para os times de engenharia. Seja você um desenvolvedor experiente ou alguém que está apenas começando, vamos mergulhar no fascinante universo dos logs e explorar como essa poderosa ferramenta pode revolucionar a forma como você depura problemas em produção.

Em resumo, essa é uma abordagem que vai transformar a sua operação para sempre.
"""


class BlogLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="blog lint ")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def lint(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "blog_lint.py"), "--format", "json", *map(str, args)],
            input=stdin, capture_output=True, text=True)

    def test_slop_post_reports_known_defects(self):
        post = self.root / "slop.md"
        post.write_text(BAD_POST_EN)
        result = self.lint("--strict", post)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        for rule in ("slop-hard", "not-just-but", "em-dash-density", "triad-overuse",
                     "transition-opener", "header-template", "title-template"):
            self.assertEqual(rules.get(rule), "warning", rule)
        for rule in ("slop-soft", "repeated-opener"):
            self.assertIn(rule, rules)
        self.assertEqual(report["stats"][str(post)]["language"], "en")

    def test_human_post_passes_clean(self):
        post = self.root / "human.md"
        post.write_text(GOOD_POST_EN)
        result = self.lint(post)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["findings"], [], report)

    def test_style_findings_are_advisory_by_default(self):
        result = self.lint("--stdin", stdin="The tapestry is on display. In conclusion, visit the museum.")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["findings"])
        self.assertEqual(report["errors"], 0)
        self.assertTrue(all(f["severity"] == "warning" for f in report["findings"]))

    def test_regular_sentence_lengths_do_not_require_artificial_variation(self):
        text = "\n\n".join([
            "Users send requests to the service through the gateway.\nThe gateway checks access before passing each request further.",
            "Workers read pending tasks from the shared message queue.\nEach worker stores its current status in the database.",
            "Failed tasks remain visible until an operator reviews them.\nOperators can retry tasks after checking the recorded cause.",
            "Metrics show task counts for each active worker process.\nLogs include task identifiers alongside the relevant status updates.",
            "The dashboard groups results by project and creation date.\nAccess follows the permissions assigned to each project member.",
        ])
        result = self.lint("--stdin", stdin=text)
        report = json.loads(result.stdout)
        self.assertGreaterEqual(report["stats"]["<stdin>"]["sentences"], 10)
        self.assertLess(report["stats"]["<stdin>"]["sentence_words_sd"], 5)
        rules = {f["rule"] for f in report["findings"]}
        self.assertFalse(rules & {"low-burstiness", "no-short-sentence", "uniform-paragraphs"})

    def test_code_and_block_quotes_are_not_reviewed_as_author_prose(self):
        text = """# Notes

Run `realm --dry-run`.
The interface name is `` `tapestry` ``.

> In conclusion, delve into the realm.

````text
```
tapestry realm
```
````
"""
        post = self.root / "literal.md"
        post.write_text(text)
        result = self.lint("--strict", post)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["findings"], [])
        self.assertEqual(post.read_text(), text)

    def test_portuguese_slop_detected(self):
        post = self.root / "rascunho.md"
        post.write_text(BAD_POST_PT)
        result = self.lint("--strict", post)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["stats"][str(post)]["language"], "pt")
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        self.assertEqual(rules.get("slop-hard"), "warning")
        self.assertEqual(rules.get("title-template"), "warning")

    def test_forced_language(self):
        post = self.root / "forced.md"
        post.write_text(BAD_POST_PT)
        result = self.lint("--lang", "en", post)
        report = json.loads(result.stdout)
        self.assertEqual(report["stats"][str(post)]["language"], "en")

    def test_stdin_and_missing_file(self):
        result = self.lint("--strict", "--stdin", stdin=BAD_POST_EN)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(json.loads(result.stdout)["findings"])
        missing = self.lint(self.root / "nope.md")
        self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
