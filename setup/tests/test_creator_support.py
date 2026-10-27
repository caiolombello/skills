"""Regression coverage for skill-creator eval and review boundaries."""
import json
import base64
import http.client
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skill-creator" / "eval-viewer"))
sys.path.insert(0, str(ROOT / "skill-creator"))

import generate_review
from scripts import aggregate_benchmark, run_eval


class CreatorSupportTests(unittest.TestCase):
    def test_embedded_eval_data_cannot_close_the_viewer_script(self):
        attack = '</script><script>window.auditInjected=true</script>'
        page = generate_review.generate_html(
            [{"id": "run", "prompt": attack, "outputs": [], "grading": None}], attack)
        self.assertNotIn(attack, page)
        self.assertIn(r"\u003c/script", page)

    def test_feedback_endpoint_requires_token_and_validates_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            token = "test-only-unguessable-token"
            server = generate_review.create_server(workspace, "skill", 0,
                                                   feedback_token=token)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                page = urlopen(f"http://127.0.0.1:{server.server_port}/").read().decode()
                self.assertIn(token, page)
                url = f"http://127.0.0.1:{server.server_port}/api/feedback"
                origin = f"http://127.0.0.1:{server.server_port}"
                payload = json.dumps({"reviews": [], "status": "complete"}).encode()
                with self.assertRaises(HTTPError) as denied:
                    urlopen(Request(url, data=payload, method="POST",
                                    headers={"Content-Type": "application/json"}))
                self.assertEqual(denied.exception.code, 403)
                denied.exception.close()
                bad = json.dumps({"reviews": [{"run_id": [], "feedback": "x"}]}).encode()
                with self.assertRaises(HTTPError) as invalid:
                    urlopen(Request(url, data=bad, method="POST",
                                    headers={"X-Feedback-Token": token,
                                             "Origin": origin,
                                             "Content-Type": "application/json"}))
                self.assertEqual(invalid.exception.code, 400)
                invalid.exception.close()
                valid = urlopen(Request(url, data=payload, method="POST",
                                        headers={"X-Feedback-Token": token,
                                                 "Origin": origin,
                                                 "Content-Type": "application/json"}))
                self.assertEqual(valid.status, 200)
                self.assertEqual(json.loads((workspace / "feedback.json").read_text()),
                                 {"reviews": [], "status": "complete"})
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
                connection.putrequest("POST", "/api/feedback")
                connection.putheader("Host", f"127.0.0.1:{server.server_port}")
                connection.putheader("Content-Length", str(generate_review.MAX_FEEDBACK_BYTES + 1))
                connection.putheader("X-Feedback-Token", token)
                connection.putheader("Origin", origin)
                connection.endheaders()
                self.assertEqual(connection.getresponse().status, 413)
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_feedback_write_refuses_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            workspace = Path(directory)
            sentinel = Path(outside) / "important.json"
            sentinel.write_text("preserve me")
            (workspace / "feedback.json").symlink_to(sentinel)
            with self.assertRaises((OSError, ValueError)):
                generate_review.write_feedback(workspace, {"reviews": [], "status": "complete"})
            self.assertEqual(sentinel.read_text(), "preserve me")

    def test_viewer_server_uses_ephemeral_port_without_killing_occupant(self):
        occupied = socket.socket()
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        port = occupied.getsockname()[1]
        try:
            server = generate_review.create_server(Path(tempfile.gettempdir()), "skill", port)
            try:
                self.assertNotEqual(server.server_port, port)
                self.assertEqual(occupied.getsockname()[1], port)
            finally:
                server.server_close()
        finally:
            occupied.close()

    def test_trigger_detector_checks_later_skill_after_other_tool(self):
        events = [
            {"type": "content_block_start", "content_block": {"type": "tool_use", "name": "Bash"}},
            {"type": "content_block_stop"},
            {"type": "message_stop"},
            {"type": "content_block_start", "content_block": {"type": "tool_use", "name": "Read"}},
            {"type": "content_block_delta", "delta": {"type": "input_json_delta", "partial_json": '{"file_path":"/x/my-skill.md"}'}},
        ]
        self.assertTrue(run_eval.detect_trigger_from_events(events, "my-skill"))
        message = {"content": [
            {"type": "tool_use", "name": "Bash", "input": {}},
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/x/my-skill.md"}},
        ]}
        self.assertTrue(run_eval.detect_trigger_from_message(message, "my-skill"))

    def test_duplicate_query_cases_are_rejected_before_running_workers(self):
        cases = [{"query": "same", "should_trigger": True},
                 {"query": "same", "should_trigger": False}]
        with patch.object(run_eval, "ProcessPoolExecutor",
                          side_effect=AssertionError("worker creation reached")) as executor:
            with self.assertRaisesRegex(ValueError, "duplicate query"):
                run_eval.run_eval(cases, "skill", "description", 1, 1, Path("/tmp"))
            executor.assert_not_called()

    def test_benchmark_metadata_reports_observed_run_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            grading = root / "eval-1" / "with_skill" / "run-1" / "grading.json"
            grading.parent.mkdir(parents=True)
            grading.write_text(json.dumps({"summary": {"pass_rate": 1, "passed": 1,
                                                          "failed": 0, "total": 1}}))
            benchmark = aggregate_benchmark.generate_benchmark(root)
            self.assertEqual(benchmark["metadata"]["runs_per_configuration"], 1)
            report = aggregate_benchmark.generate_markdown(benchmark)
            self.assertIn("1 run", report)

    def test_benchmark_metadata_lists_missing_and_invalid_grading_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = root / "eval-1" / "with_skill" / "run-1" / "grading.json"
            invalid.parent.mkdir(parents=True)
            invalid.write_text("not json")
            (root / "eval-1/with_skill/run-2").mkdir()
            benchmark = aggregate_benchmark.generate_benchmark(root)
            metadata = benchmark["metadata"]
            self.assertIsNone(metadata["runs_per_configuration"])
            self.assertEqual(metadata["run_counts_per_configuration"], {"with_skill": {"1": 0}})
            self.assertEqual(metadata["missing_grading_files"],
                             ["eval-1/with_skill/run-2/grading.json"])
            self.assertEqual(metadata["skipped_grading_files"],
                             ["eval-1/with_skill/run-1/grading.json"])

    def test_report_and_viewer_escape_untrusted_benchmark_cells(self):
        attack = '<img src=x onerror="window.auditInjected=true">'
        template = (ROOT / "skill-creator/eval-viewer/viewer.html").read_text()
        self.assertIn("escapeHtml(String(metadata.timestamp))", template)
        self.assertIn("escapeHtml(configLabel)", template)
        self.assertIn("escapeHtml(String(run.run_number))", template)
        self.assertNotIn(".innerHTML = htmlStr", template)
        report_module = __import__("scripts.generate_report", fromlist=["generate_html"])
        report = report_module.generate_html({"best_score": attack,
                                             "history": [{"iteration": attack, "results": []}]})
        self.assertNotIn(attack, report)
        self.assertIn("&lt;img", report)
        # The second producer has an executable JSON placeholder as well.
        asset = (ROOT / "skill-creator/assets/eval_review.html").read_text()
        encoded = base64.b64encode(json.dumps([{"query": attack}]).encode()).decode()
        populated = asset.replace("__EVAL_DATA_PLACEHOLDER__", encoded)
        self.assertIn('atob("' + encoded + '")', populated)
        self.assertNotIn(attack, populated)
        self.assertNotIn(attack, asset)


if __name__ == "__main__":
    unittest.main()
