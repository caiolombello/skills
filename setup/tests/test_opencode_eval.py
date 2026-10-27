"""Safety regressions for the OpenCode skill evaluator (no model calls)."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
import yaml
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[2] / "skill-creator-opencode/scripts/run_eval_opencode.py"
spec = importlib.util.spec_from_file_location("run_eval_opencode", SCRIPT)
evaluator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = evaluator
spec.loader.exec_module(evaluator)


class OpenCodeEvalSafetyTests(unittest.TestCase):
    def test_skill_names_are_safe_single_path_components(self):
        for invalid in ("../outside", "/tmp/outside", "a/b", "a.shadow", "UPPER", "a" * 65):
            with self.subTest(name=invalid), self.assertRaises(ValueError):
                evaluator.validate_skill_name(invalid)
        self.assertEqual(evaluator.validate_skill_name("safe-skill-2"), "safe-skill-2")

    def test_legacy_config_paths_and_urls_are_preserved_without_mutation(self):
        original = {"skills": {"paths": ["/existing/path"], "urls": ["https://example.com/skills"]},
                    "model": "provider/selected-model"}
        serialized = json.dumps(original)
        with evaluator.isolated_probe("sample-skill", 'A: quoted "description"\nnew line') as probe:
            with mock.patch.dict(evaluator.os.environ, {"OPENCODE_CONFIG_CONTENT": serialized}):
                env = evaluator._opencode_env(probe.config_dir, probe.skill_dir)
                self.assertEqual(evaluator.os.environ["OPENCODE_CONFIG_CONTENT"], serialized)
            configured = json.loads(env["OPENCODE_CONFIG_CONTENT"])
            self.assertEqual(configured["skills"]["paths"], ["/existing/path", str(probe.skill_dir.parent)])
            self.assertEqual(configured["skills"]["urls"], original["skills"]["urls"])
            self.assertEqual(configured["model"], original["model"])
            metadata = yaml.safe_load((probe.skill_dir / "SKILL.md").read_text().split("---", 2)[1])
            self.assertEqual(metadata["description"], 'A: quoted "description"\nnew line')

    def test_probe_is_created_in_private_project_and_does_not_touch_live_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            live_root = Path(tmp) / "live"
            live_root.mkdir()
            sentinel = live_root / "sample-skill"
            sentinel.mkdir()
            (sentinel / "user-data.txt").write_text("preserve")
            with evaluator.isolated_probe("sample-skill", "candidate description", live_root=live_root) as probe:
                self.assertTrue(probe.project.is_relative_to(probe.root))
                self.assertTrue(probe.skill_dir.is_relative_to(probe.project / ".opencode" / "skills"))
                data = (probe.skill_dir / "SKILL.md").read_text()
                self.assertIn("candidate description", data)
                self.assertEqual((sentinel / "user-data.txt").read_text(), "preserve")
            self.assertTrue(sentinel.exists())

    def test_legacy_live_and_shadow_paths_are_never_touched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            live = root / "sample-skill"
            shadow = root / "sample-skill.shadow"
            live.mkdir()
            shadow.mkdir()
            (live / "user-data.txt").write_text("live")
            (shadow / "user-data.txt").write_text("ambiguous")
            with evaluator.isolated_probe("sample-skill", "desc", live_root=root):
                self.assertEqual((live / "user-data.txt").read_text(), "live")
                self.assertEqual((shadow / "user-data.txt").read_text(), "ambiguous")

    def test_invocations_use_isolated_project_cwd_and_config_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            captured = {}
            class FakeProcess:
                stdout = io.BytesIO()
                def __init__(self, cmd, **kwargs):
                    captured.update(kwargs)
                    captured["cmd"] = cmd
                def poll(self): return 0
            with evaluator.isolated_probe("sample-skill", "desc") as probe:
                with mock.patch.object(evaluator.subprocess, "Popen", FakeProcess):
                    evaluator.run_single_query("query", "sample-skill", 2, None, probe=probe)
            self.assertEqual(Path(captured["cwd"]), probe.project)
            self.assertEqual(Path(captured["env"]["OPENCODE_CONFIG_DIR"]), probe.config_dir)
            inline = json.loads(captured["env"]["OPENCODE_CONFIG_CONTENT"])
            self.assertEqual(inline["skills"], [str(probe.skill_dir.parent)])

    def test_parallel_evaluations_get_distinct_isolated_roots(self):
        with evaluator.isolated_probe("same-skill", "one") as first:
            with evaluator.isolated_probe("same-skill", "two") as second:
                self.assertNotEqual(first.root, second.root)
                for probe, description in ((first, "one"), (second, "two")):
                    metadata = yaml.safe_load((probe.skill_dir / "SKILL.md").read_text().split("---", 2)[1])
                    self.assertEqual(metadata["description"], description)

    def test_timeout_terminates_then_escalates_to_kill(self):
        class FakeProcess:
            stdout = None
            def __init__(self, *args, **kwargs): self.terminated = self.killed = False
            def poll(self): return None
            def terminate(self): self.terminated = True
            def kill(self): self.killed = True
            def wait(self, timeout=None):
                if not self.terminated: raise AssertionError("terminate was not requested")
                if timeout is not None: raise evaluator.subprocess.TimeoutExpired("opencode", timeout)
                return -9
        proc = FakeProcess()
        with evaluator.isolated_probe("sample-skill", "desc") as probe, \
             mock.patch.object(evaluator.subprocess, "Popen", return_value=proc), \
             mock.patch.object(evaluator.select, "select", return_value=([], [], [])), \
             mock.patch.object(evaluator.time, "monotonic", side_effect=[0, 2, 2, 2]):
            evaluator.run_single_query("query", "sample-skill", 1, None, probe=probe)
        self.assertTrue(proc.terminated)
        self.assertTrue(proc.killed)

    def test_batch_outer_timeout_terminates_then_kills_process_group(self):
        batch_path = SCRIPT.with_name("batch_smoke.py")
        batch_spec = importlib.util.spec_from_file_location("batch_smoke", batch_path)
        batch = importlib.util.module_from_spec(batch_spec)
        assert batch_spec and batch_spec.loader
        sys.modules[batch_spec.name] = batch
        batch_spec.loader.exec_module(batch)

        class FakeProcess:
            pid = 12345
            calls = 0
            def __init__(self, *args, **kwargs): pass
            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls <= 2:
                    raise batch.subprocess.TimeoutExpired("evaluator", timeout)
                return ("", "")

        proc = FakeProcess()
        with tempfile.TemporaryDirectory() as tmp:
            eval_path = Path(tmp) / "sample-skill.json"
            eval_path.write_text(json.dumps([{"query": "q", "should_trigger": True}]))
            with mock.patch.object(batch.subprocess, "Popen", return_value=proc), \
                 mock.patch.object(batch.os, "killpg") as killpg:
                result = batch.run_one(eval_path, Path(tmp) / "sample-skill", "provider/model", 1, 1)
        self.assertEqual(result["error"], "outer timeout (120s)")
        self.assertEqual([call.args[1] for call in killpg.call_args_list], [batch.signal.SIGTERM, batch.signal.SIGKILL])


if __name__ == "__main__":
    unittest.main()
