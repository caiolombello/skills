#!/usr/bin/env python3
"""Batch smoke test for skill triggers.

Reads a JSON file mapping skill-name -> eval-set, runs each with
run_eval_opencode.py against a shared model, and summarises pass/fail.

Usage:

    python3 batch_smoke.py \
        --eval-sets /tmp/batches/*.json \
        --skills-root ~/Documents/Personal/skills \
        --model anthropic/claude-haiku-4-5 \
        --timeout 60 \
        --results-out /tmp/smoke-results.json
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_one(
    eval_set_path: Path,
    skill_path: Path,
    model: str,
    timeout: int,
    runs_per_query: int,
) -> dict:
    script = (
        Path(__file__).parent / "run_eval_opencode.py"
    ).resolve()
    cmd = [
        sys.executable,
        str(script),
        "--eval-set",
        str(eval_set_path),
        "--skill-path",
        str(skill_path),
        "--model",
        model,
        "--runs-per-query",
        str(runs_per_query),
        "--num-workers",
        "1",
        "--timeout",
        str(timeout),
    ]
    # Give the full run an outer timeout (per-query timeout * queries + buffer)
    eval_set = json.loads(eval_set_path.read_text())
    outer = max(120, timeout * len(eval_set) * runs_per_query + 30)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=outer,
        )
    except subprocess.TimeoutExpired:
        return {
            "skill_name": skill_path.name,
            "error": f"outer timeout ({outer}s)",
            "stdout": "",
            "stderr": "",
        }

    out = proc.stdout.strip()
    if not out:
        return {
            "skill_name": skill_path.name,
            "error": "no stdout",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        return {
            "skill_name": skill_path.name,
            "error": f"json parse: {exc}",
            "stdout": out,
            "stderr": proc.stderr,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-sets",
        required=True,
        help="glob of JSON files, filename must match <skill-name>.json",
    )
    parser.add_argument(
        "--skills-root",
        required=True,
        help="directory containing skill folders",
    )
    parser.add_argument("--model", required=True, help="provider/model")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--runs-per-query", type=int, default=1)
    parser.add_argument("--results-out", required=True)
    args = parser.parse_args()

    skills_root = Path(args.skills_root).expanduser().resolve()
    eval_sets = sorted(glob.glob(args.eval_sets))
    if not eval_sets:
        print(f"No eval sets matched: {args.eval_sets}", file=sys.stderr)
        sys.exit(1)

    all_results = []
    total_pass = 0
    total_fail = 0
    total_err = 0

    for i, es in enumerate(eval_sets, 1):
        es_path = Path(es)
        skill_name = es_path.stem
        skill_path = skills_root / skill_name
        if not skill_path.is_dir():
            print(
                f"[{i}/{len(eval_sets)}] skip {skill_name}: no directory at {skill_path}",
                file=sys.stderr,
            )
            total_err += 1
            all_results.append(
                {"skill_name": skill_name, "error": "no skill directory"}
            )
            continue

        sys.stderr.write(f"[{i}/{len(eval_sets)}] {skill_name} ... ")
        sys.stderr.flush()
        result = run_one(
            es_path,
            skill_path,
            args.model,
            args.timeout,
            args.runs_per_query,
        )
        if "summary" in result:
            s = result["summary"]
            status = "OK " if s["failed"] == 0 else "FAIL"
            sys.stderr.write(f"{status} {s['passed']}/{s['total']}\n")
            if s["failed"] == 0:
                total_pass += 1
            else:
                total_fail += 1
        else:
            sys.stderr.write(f"ERR {result.get('error', 'unknown')}\n")
            total_err += 1
        all_results.append(result)

    Path(args.results_out).write_text(json.dumps(all_results, indent=2))
    print(
        f"\nTotal: {len(eval_sets)} skills — "
        f"{total_pass} fully passed, {total_fail} had failures, {total_err} errors",
        file=sys.stderr,
    )
    print(f"Results written to {args.results_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
