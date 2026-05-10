#!/usr/bin/env python3
"""Run trigger evaluation for a skill description against OpenCode.

Mirrors anthropics/skills/scripts/run_eval.py but targets `opencode run`
instead of `claude -p`. Detects triggering by scanning the streamed JSON
events from OpenCode for a `tool_use` event with `tool: "skill"` and the
skill `name` matching our temporary probe skill.

Key differences vs the claude adapter:

- OpenCode reads skills from ~/.config/opencode/skill/<name>/SKILL.md.
  There is no equivalent to Claude's in-session ".claude/commands/"
  override, so this script temporarily writes a probe skill directory
  under ~/.config/opencode/skill/ and removes it afterwards.
- OpenCode's event stream is one JSON object per line, same as claude's,
  but event shape is { "type": "tool_use", "part": { "tool": "skill",
  "state": { "input": { "name": "<skill-name>" } } } }.
- OpenCode accepts "--model provider/model"; pass whatever the user is
  currently using (e.g. "anthropic/claude-haiku-4-5").

This script is usable standalone or as a drop-in replacement for
run_eval.py inside a forked run_loop.py that accepts --cli opencode.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import shutil
import subprocess
import sys
import time
import uuid  # noqa: F401  # retained for potential future use
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


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


def opencode_skill_root() -> Path:
    """Root where OpenCode discovers user skills."""
    return Path.home() / ".config" / "opencode" / "skill"


def shadow_real_skill(name: str) -> Path | None:
    """If a skill with the same name is installed, move it aside for the
    duration of the probe. Returns the original path (now renamed) so we
    can restore it in `restore_real_skill`. Returns None if no collision.

    The probe skill must be the only candidate for its name during the
    evaluation; otherwise the agent will load the real skill and the probe
    will never fire, producing false negatives for should_trigger queries.
    """
    target = opencode_skill_root() / name
    if not target.exists() and not target.is_symlink():
        return None
    shadow = target.with_suffix(".shadow")
    # If a stale shadow somehow exists from a previous crashed run, drop it.
    if shadow.exists() or shadow.is_symlink():
        if shadow.is_symlink() or shadow.is_file():
            shadow.unlink()
        else:
            shutil.rmtree(shadow)
    target.rename(shadow)
    return shadow


def restore_real_skill(shadow: Path | None) -> None:
    """Undo `shadow_real_skill`. Safe to call with None."""
    if shadow is None:
        return
    original = shadow.with_suffix("")  # drops '.shadow'
    if original.exists() or original.is_symlink():
        # Probe cleanup failed earlier; remove the leftover before restoring.
        if original.is_symlink() or original.is_file():
            original.unlink()
        else:
            shutil.rmtree(original)
    shadow.rename(original)


def write_probe_skill(name: str, description: str) -> Path:
    """Create a disposable probe skill under the OpenCode skill root.

    Returns the absolute path to the newly-created skill directory.
    """
    root = opencode_skill_root()
    root.mkdir(parents=True, exist_ok=True)
    probe_dir = root / name
    if probe_dir.exists():
        raise RuntimeError(
            f"Probe skill dir already exists: {probe_dir}. "
            f"Refusing to clobber."
        )
    probe_dir.mkdir()
    skill_md = (
        f"---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"---\n\n"
        f"# {name}\n\n"
        f"Probe skill used by run_eval_opencode.py. Safe to delete.\n"
    )
    (probe_dir / "SKILL.md").write_text(skill_md)
    return probe_dir


def cleanup_probe_skill(probe_dir: Path) -> None:
    """Remove a probe skill directory. Safe to call multiple times."""
    if probe_dir.exists():
        shutil.rmtree(probe_dir, ignore_errors=True)


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    model: str | None,
) -> bool:
    """Invoke `opencode run` once and detect whether the probe skill fired.

    Returns True iff the streamed events contain a `tool_use` entry with
    `tool == "skill"` and `input.name == skill_name`.

    The probe is installed under the real skill's name — an agent picks a
    skill by its exact name, so a suffixed probe like `<name>-probe-<id>`
    would never be selected. To avoid colliding with any real skill
    installed at the same path, we move the real one aside for the
    duration of the run and restore it in `finally`.

    NOTE: multiple concurrent runs for the same `skill_name` on this
    machine race on the single-slot probe directory. Serialize per-skill
    or run with `--num-workers 1` when probing the same skill repeatedly.
    """
    probe_name = skill_name
    shadow = shadow_real_skill(skill_name)
    probe_dir = write_probe_skill(probe_name, skill_description)

    try:
        cmd = ["opencode", "run", "--format", "json"]
        if model:
            cmd.extend(["--model", model])
        cmd.append(query)

        env = os.environ.copy()

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env,
        )

        triggered = False
        start = time.time()
        buffer = ""

        try:
            while time.time() - start < timeout:
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
                        # A non-skill tool fired first; by the time a
                        # real skill is loaded it would be in the same
                        # or a later event. Keep scanning.
                        continue
                    state = part.get("state", {})
                    inp = state.get("input", {})
                    if inp.get("name") == probe_name:
                        triggered = True
                        return triggered
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

        return triggered
    finally:
        cleanup_probe_skill(probe_dir)
        restore_real_skill(shadow)


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
    """Run the full eval set and return aggregated results."""
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    model,
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
