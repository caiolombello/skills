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

Cleanup discipline:

- Shadow + probe setup/teardown happens ONCE per eval in the parent
  process. Workers only invoke `opencode run`. This fixes the
  "concurrent runs for the same skill collide" failure mode.
- Signal handlers (SIGINT / SIGTERM) and atexit ensure the real skill
  is restored even if the parent is killed by `timeout(1)` or Ctrl-C.
- Pre-flight: leftover `.shadow` from a previous crashed run is
  auto-recovered before the new run starts.

This script is usable standalone or as a drop-in replacement for
run_eval.py inside a forked run_loop.py that accepts --cli opencode.
"""

from __future__ import annotations

import argparse
import atexit
import json
import os
import select
import shutil
import signal
import subprocess
import sys
import time
import uuid  # noqa: F401  # retained for potential future use
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


# Module-level state so signal handlers / atexit can find it.
# Tracks the single skill being evaluated by the current process.
_ACTIVE_SHADOW: Path | None = None
_ACTIVE_PROBE: Path | None = None


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


def _remove_path(p: Path) -> None:
    """Best-effort delete of a file, symlink, or directory."""
    if not p.exists() and not p.is_symlink():
        return
    try:
        if p.is_symlink() or p.is_file():
            p.unlink()
        else:
            shutil.rmtree(p)
    except OSError:
        pass


def autoclean_leftovers(skill_name: str) -> None:
    """Recover from a previous crashed run before starting a new one.

    Two leftover shapes are possible:
      1. <name>.shadow exists AND <name> exists (probe never torn down).
         → remove the probe-looking <name>, restore shadow to <name>.
      2. <name>.shadow exists AND <name> does NOT exist (partial cleanup).
         → restore shadow to <name>.

    If <name> is a symlink that does not point at our probe shape
    (a real symlink to the source repo), we leave it alone: there is
    nothing to recover.
    """
    root = opencode_skill_root()
    target = root / skill_name
    shadow = root / f"{skill_name}.shadow"

    if not shadow.exists() and not shadow.is_symlink():
        return

    # Shadow exists. If the live target exists too, it is probe debris.
    if target.exists() or target.is_symlink():
        print(
            f"autoclean: removing leftover probe at {target} and "
            f"restoring shadow {shadow}",
            file=sys.stderr,
        )
        _remove_path(target)

    try:
        shadow.rename(target)
    except OSError as exc:
        print(
            f"autoclean: failed to restore {shadow} -> {target}: {exc}",
            file=sys.stderr,
        )


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
    # (autoclean_leftovers already handled the canonical case; this is a
    # belt-and-suspenders fallback.)
    if shadow.exists() or shadow.is_symlink():
        _remove_path(shadow)
    target.rename(shadow)
    return shadow


def restore_real_skill(shadow: Path | None) -> None:
    """Undo `shadow_real_skill`. Safe to call with None and to call twice."""
    if shadow is None:
        return
    if not shadow.exists() and not shadow.is_symlink():
        return
    original = shadow.with_suffix("")  # drops '.shadow'
    if original.exists() or original.is_symlink():
        # Probe cleanup failed earlier; remove the leftover before restoring.
        _remove_path(original)
    try:
        shadow.rename(original)
    except OSError as exc:
        print(
            f"restore_real_skill: could not restore {shadow} -> {original}: {exc}",
            file=sys.stderr,
        )


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
            f"Run autoclean_leftovers first, or remove manually."
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


def cleanup_probe_skill(probe_dir: Path | None) -> None:
    """Remove a probe skill directory. Safe to call with None / multiple times."""
    if probe_dir is None:
        return
    if probe_dir.exists():
        shutil.rmtree(probe_dir, ignore_errors=True)


def _restore_active() -> None:
    """Restore any in-flight shadow + probe state. Called by atexit and
    signal handlers. Idempotent."""
    global _ACTIVE_SHADOW, _ACTIVE_PROBE
    try:
        cleanup_probe_skill(_ACTIVE_PROBE)
        restore_real_skill(_ACTIVE_SHADOW)
    finally:
        _ACTIVE_SHADOW = None
        _ACTIVE_PROBE = None


def _install_signal_handlers() -> None:
    """Route SIGINT and SIGTERM through the cleanup path before exiting."""

    def _handler(signum: int, _frame) -> None:
        try:
            _restore_active()
        finally:
            # Re-raise the signal's default action by exiting with 128+signum.
            sys.exit(128 + signum)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)


def run_single_query(
    query: str,
    skill_name: str,
    timeout: int,
    model: str | None,
) -> bool:
    """Invoke `opencode run` once and detect whether the probe skill fired.

    This function expects the probe to already be installed by the parent
    process (via `setup_probe`). It does NOT install or tear down the probe
    itself — this is what fixes the concurrent-collision bug and the
    cleanup-on-timeout bug.

    Returns True iff the streamed events contain a `tool_use` entry with
    `tool == "skill"` and `input.name == skill_name`.
    """
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
                    continue
                state = part.get("state", {})
                inp = state.get("input", {})
                if inp.get("name") == skill_name:
                    triggered = True
                    return triggered
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()

    return triggered


def setup_probe(skill_name: str, description: str) -> None:
    """Install the probe skill in the parent process. Records the shadow
    and probe paths in module state so signal handlers can roll them back."""
    global _ACTIVE_SHADOW, _ACTIVE_PROBE
    autoclean_leftovers(skill_name)
    _ACTIVE_SHADOW = shadow_real_skill(skill_name)
    _ACTIVE_PROBE = write_probe_skill(skill_name, description)


def teardown_probe() -> None:
    """Symmetric to `setup_probe`. Idempotent."""
    _restore_active()


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
    setup_probe(skill_name, description)
    try:
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
    finally:
        teardown_probe()


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

    # Install cleanup handlers BEFORE any mutation of the skill dir.
    atexit.register(_restore_active)
    _install_signal_handlers()

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
