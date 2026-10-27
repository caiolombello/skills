#!/usr/bin/env python3
"""Run trigger evaluation for a skill description against OpenCode.

Mirrors anthropics/skills/scripts/run_eval.py but targets `opencode run`
instead of `claude -p`. Detects triggering by scanning the streamed JSON
events from OpenCode for a `tool_use` event with `tool: "skill"` and the
skill `name` matching our temporary probe skill.

Key differences vs the claude adapter:

- Each evaluation creates a unique temporary OpenCode project with its probe
  in `.opencode/skills/<name>/SKILL.md`; installed skills are never moved or
  deleted. `OPENCODE_CONFIG_DIR` points to a private temporary config folder.
- OpenCode's event stream is one JSON object per line, same as claude's,
  but event shape is { "type": "tool_use", "part": { "tool": "skill",
  "state": { "input": { "name": "<skill-name>" } } } }.
- OpenCode accepts "--model provider/model"; pass whatever the user is
  currently using (e.g. "anthropic/claude-haiku-4-5").

Isolation discipline:

- Each evaluator process gets an exclusive temporary project/config root, so
  separate evaluations never share a probe path. Probe files are confined there;
  provider authentication, session storage and other runtime effects are separate.
- Timeout sends SIGTERM to OpenCode, waits briefly, then escalates to SIGKILL.
  A forced outer timeout can leave only an isolated temporary directory; it
  cannot strand or overwrite an installed skill.
- Legacy `<name>.shadow` paths are never read, renamed, or deleted. Inspect and
  recover any old leftovers manually after confirming their contents.

This script is usable standalone or as a drop-in replacement for
run_eval.py inside a forked run_loop.py that accepts --cli opencode.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import tempfile
from dataclasses import dataclass
import os
import select
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


# Evaluations use private project/config roots. No installed skill is renamed,
# replaced, or cleaned up, so stale leftovers are harmless and never auto-recovered.
_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class IsolatedProbe:
    root: Path
    project: Path
    config_dir: Path
    skill_dir: Path


def validate_skill_name(name: str) -> str:
    """Require a canonical, single-component skill identifier."""
    if not isinstance(name, str) or len(name) > 64 or not _NAME_RE.fullmatch(name):
        raise ValueError(
            "Invalid skill name; expected lowercase letters, digits, and "
            "single hyphen-separated components"
        )
    return name


@contextlib.contextmanager
def isolated_probe(
    skill_name: str,
    description: str,
    *,
    live_root: Path | None = None,
):
    """Create an exclusive temporary OpenCode project containing only this probe.

    ``live_root`` is accepted for regression tests and deliberately never read or
    mutated. The temporary root is outside OpenCode's active skill directories.
    """
    validate_skill_name(skill_name)
    with tempfile.TemporaryDirectory(prefix="opencode-skill-eval-") as temp:
        root = Path(temp).resolve(strict=True)
        project = root / "project"
        config_dir = root / "config"
        skill_dir = project / ".opencode" / "skills" / skill_name
        for path in (project, config_dir, skill_dir):
            path.mkdir(parents=True, exist_ok=True)
            resolved = path.resolve(strict=True)
            if resolved.parent != path.parent.resolve(strict=True) and path != project:
                raise RuntimeError(f"Unexpected path while creating isolated probe: {path}")
            if not resolved.is_relative_to(root):
                raise RuntimeError(f"Probe escaped isolated root: {path}")
        skill_md = (
            f"---\nname: {skill_name}\ndescription: {json.dumps(description)}\n---\n\n"
            f"# {skill_name}\n\n"
            "Probe skill used by run_eval_opencode.py.\n"
        )
        (skill_dir / "SKILL.md").write_text(skill_md)
        yield IsolatedProbe(root, project, config_dir, skill_dir)


def _opencode_env(config_dir: Path, skill_dir: Path) -> dict[str, str]:
    """Add the private probe without editing caller config or installed skills."""
    env = os.environ.copy()
    # Preserve user config and provider credentials; project-local skill
    # discovery has higher priority and overrides only the probed skill ID.
    env["OPENCODE_CONFIG_DIR"] = str(config_dir)
    # Inline config has higher priority than global/project config. Preserve
    # caller settings and append the private source last; OpenCode combines
    # skill sources, so it takes precedence for an identical skill ID.
    try:
        inline_config = json.loads(env.get("OPENCODE_CONFIG_CONTENT", "{}"))
    except json.JSONDecodeError as exc:
        raise ValueError("OPENCODE_CONFIG_CONTENT must contain valid JSON") from exc
    if not isinstance(inline_config, dict):
        raise ValueError("OPENCODE_CONFIG_CONTENT must be a JSON object")
    skill_sources = inline_config.setdefault("skills", [])
    if isinstance(skill_sources, dict):
        # OpenCode also accepts the older {paths, urls} object form.
        paths = skill_sources.setdefault("paths", [])
        if not isinstance(paths, list):
            raise ValueError("OPENCODE_CONFIG_CONTENT 'skills.paths' must be an array")
        paths.append(str(skill_dir.parent))
    elif isinstance(skill_sources, list):
        skill_sources.append(str(skill_dir.parent))
    else:
        raise ValueError("OPENCODE_CONFIG_CONTENT 'skills' must be an array or object")
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(inline_config)
    env["OPENCODE_DISABLE_EXTERNAL_SKILLS"] = "1"
    return env


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file into (name, description, body).

    Minimal YAML frontmatter parser — does not depend on PyYAML. Expects
    the frontmatter delimited by '---' lines and the name/description
    fields on their own lines. If either field spans multiple lines,
    the value is collected until the next key or the closing '---'.
    """
    raw = (skill_path / "SKILL.md").read_text()
    if not raw.startswith("---\n"):
        raise ValueError(f"{skill_path}/SKILL.md missing YAML frontmatter")

    body_split = raw.split("---\n", 2)
    if len(body_split) < 3:
        raise ValueError(f"{skill_path}/SKILL.md frontmatter not closed")
    _, fm, body = body_split

    name = None
    description = None
    current_key = None
    for line in fm.splitlines():
        if line.startswith("name:"):
            current_key = "name"
            name = line[len("name:") :].strip()
        elif line.startswith("description:"):
            current_key = "description"
            description = line[len("description:") :].strip()
        elif current_key == "description" and line.startswith("  "):
            # Continuation of a multi-line scalar (rare but possible).
            description = (description or "") + " " + line.strip()
        else:
            current_key = None

    if not name or not description:
        raise ValueError(f"{skill_path}/SKILL.md missing name or description")
    return name, description, body


def run_single_query(
    query: str,
    skill_name: str,
    timeout: int,
    model: str | None,
    *,
    probe: IsolatedProbe,
) -> bool:
    """Invoke `opencode run` once and detect whether the probe skill fired.

    The probe is already installed in the evaluation's private project. It
    does not alter skill files. Separate evaluator processes use separate roots.

    Returns True iff the streamed events contain a `tool_use` entry with
    `tool == "skill"` and `input.name == skill_name`.
    """
    cmd = ["opencode", "run", "--standalone", "--format", "json"]
    if model:
        cmd.extend(["--model", model])
    cmd.append(query)

    env = _opencode_env(probe.config_dir, probe.skill_dir)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
        cwd=probe.project,
    )

    triggered = False
    start = time.monotonic()
    buffer = ""

    try:
        while time.monotonic() - start < timeout:
            if process.poll() is not None:
                remaining = process.stdout.read()
                if remaining:
                    buffer += remaining.decode("utf-8", errors="replace")
                break

            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                continue

            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if event.get("type") != "tool_use":
                    continue
                part = event.get("part", {})
                if part.get("tool") != "skill":
                    continue
                state = part.get("state", {})
                inp = state.get("input", {})
                if inp.get("name") == skill_name:
                    triggered = True
                    return triggered
    finally:
        if process.poll() is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                process.wait()

    return triggered


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    runs_per_query: int,
    trigger_threshold: float,
    model: str | None,
) -> dict:
    """Run the full eval set and return aggregated results.

    Installs the probe once, fans out queries to workers, then tears the
    probe down. Handles exceptions so that teardown always runs.
    """
    validate_skill_name(skill_name)
    with isolated_probe(skill_name, description) as probe:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_info = {}
            for item in eval_set:
                for run_idx in range(runs_per_query):
                    future = executor.submit(
                        run_single_query,
                        item["query"],
                        skill_name,
                        timeout,
                        model,
                        probe=probe,
                    )
                    future_to_info[future] = (item, run_idx)

            query_triggers: dict[str, list[bool]] = {}
            query_items: dict[str, dict] = {}
            for future in as_completed(future_to_info):
                item, _ = future_to_info[future]
                query = item["query"]
                query_items[query] = item
                query_triggers.setdefault(query, [])
                try:
                    query_triggers[query].append(future.result())
                except Exception as e:
                    print(f"Warning: query failed: {e}", file=sys.stderr)
                    query_triggers[query].append(False)

        results = []
        for query, triggers in query_triggers.items():
            item = query_items[query]
            trigger_rate = sum(triggers) / len(triggers) if triggers else 0.0
            should_trigger = item["should_trigger"]
            if should_trigger:
                did_pass = trigger_rate >= trigger_threshold
            else:
                did_pass = trigger_rate < trigger_threshold
            results.append(
                {
                    "query": query,
                    "should_trigger": should_trigger,
                    "trigger_rate": trigger_rate,
                    "triggers": sum(triggers),
                    "runs": len(triggers),
                    "pass": did_pass,
                }
            )

        passed = sum(1 for r in results if r["pass"])
        total = len(results)
        return {
            "skill_name": skill_name,
            "description": description,
            "results": results,
            "summary": {"total": total, "passed": passed, "failed": total - passed},
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run trigger evaluation against OpenCode."
    )
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--skill-path", required=True)
    parser.add_argument("--description", default=None)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--trigger-threshold", type=float, default=0.5)
    parser.add_argument("--model", required=True, help="provider/model")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path).expanduser().resolve()
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description

    if args.verbose:
        print(f"Evaluating skill '{name}' against {args.model}", file=sys.stderr)
        print(f"Description: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(
            f"Results: {summary['passed']}/{summary['total']} passed",
            file=sys.stderr,
        )
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate = f"{r['triggers']}/{r['runs']}"
            print(
                f"  [{status}] rate={rate} expected={r['should_trigger']}: "
                f"{r['query'][:80]}",
                file=sys.stderr,
            )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
