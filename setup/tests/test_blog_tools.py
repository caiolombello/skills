"""Behavior checks for blog-posting lint; slop must fail, human prose must pass."""
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
        result = self.lint(post)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        for rule in ("slop-hard", "not-just-but", "em-dash-density", "triad-overuse",
                     "transition-opener", "low-burstiness", "header-template", "title-template"):
            self.assertEqual(rules.get(rule), "error", rule)
        for rule in ("slop-soft", "no-short-sentence", "repeated-opener"):
            self.assertIn(rule, rules)
        self.assertEqual(report["stats"][str(post)]["language"], "en")

    def test_human_post_passes_clean(self):
        post = self.root / "human.md"
        post.write_text(GOOD_POST_EN)
        result = self.lint(post)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["findings"], [], report)

    def test_portuguese_slop_detected(self):
        post = self.root / "rascunho.md"
        post.write_text(BAD_POST_PT)
        result = self.lint(post)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["stats"][str(post)]["language"], "pt")
        rules = {f["rule"]: f["severity"] for f in report["findings"]}
        self.assertEqual(rules.get("slop-hard"), "error")
        self.assertEqual(rules.get("title-template"), "error")

    def test_forced_language(self):
        post = self.root / "forced.md"
        post.write_text(BAD_POST_PT)
        result = self.lint("--lang", "en", post)
        report = json.loads(result.stdout)
        self.assertEqual(report["stats"][str(post)]["language"], "en")

    def test_stdin_and_missing_file(self):
        result = self.lint("--stdin", stdin=BAD_POST_EN)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(json.loads(result.stdout)["findings"])
        missing = self.lint(self.root / "nope.md")
        self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
