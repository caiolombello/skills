---
name: skill-creator-opencode
description: 'Adapter that lets the official Anthropic skill-creator evaluation loop run against OpenCode instead of Claude Code. Use when the user wants to run `run_eval` / trigger benchmarks against OpenCode (opencode run --format json) using whichever model they are currently using, instead of depending on the `claude` CLI. Ships a drop-in `run_eval_opencode.py` that mirrors the upstream run_eval.py API (--eval-set, --skill-path, --model, --runs-per-query, --trigger-threshold), detects skill triggering by scanning OpenCode''s JSON event stream for `tool_use` events with `tool: "skill"`, and manages a disposable probe skill under ~/.config/opencode/skill/ for description overrides. Does NOT cover the rest of the skill-creator loop (improve_description, run_loop, eval-viewer) — those still need adaptation.'
---

# skill-creator-opencode

Companion to the vendored `skill-creator/` directory. Provides an OpenCode-backed equivalent of `skill-creator/scripts/run_eval.py` so the trigger-evaluation half of the skill-creator loop can run without `claude -p`.

## Why this exists

The upstream skill-creator assumes the Claude Code CLI:

- `scripts/run_eval.py` shells out to `claude -p <query> --output-format stream-json`.
- Description overrides are injected by writing a command file into the active `.claude/commands/` directory.
- Trigger detection watches the Claude stream-json event shape (`stream_event` / `content_block_start` with `tool_use` where `name == "Skill"`).

None of that works for an OpenCode-based workflow. This adapter swaps:

| Concern | Upstream (Claude) | OpenCode |
|---|---|---|
| Invocation | `claude -p <query> --output-format stream-json` | `opencode run --format json <query>` |
| Description override | `.claude/commands/<id>.md` in project root | Disposable skill dir under `~/.config/opencode/skill/<name>-probe-<id>/` |
| Trigger signal | `tool_use.name == "Skill"` + probe id in `input.skill` | `tool_use` event `part.tool == "skill"` + `part.state.input.name` matches probe name |
| Model selection | `--model <id>` | `--model provider/model` (e.g. `anthropic/claude-haiku-4-5`) |

## When to use

Trigger this skill whenever the user asks to:

- Run a **trigger eval** (quantitative pass/fail against a set of queries) for a skill in their OpenCode setup.
- Score whether a description triggers appropriately for should-trigger / should-not-trigger cases.
- Reuse the skill-creator eval format (`[{"query": "...", "should_trigger": true/false}, ...]`) without depending on `claude -p`.

Do **not** use when:

- The user wants the full upstream loop with `improve_description` and HTML viewer — that still needs a port of `run_loop.py` + `improve_description.py`. Those scripts call Claude-specific APIs for the model-driven description rewrites.
- The user explicitly wants to keep Claude Code as the evaluator.

## How to run

```bash
# 1. Write an eval set (same schema as skill-creator)
cat > /tmp/eval.json <<'EOF'
[
  {"query": "preciso escrever um Dockerfile seguro para um servico node em producao", "should_trigger": true},
  {"query": "como faco um diagrama ER para postgres", "should_trigger": false}
]
EOF

# 2. Run against the currently-active OpenCode model
python3 skill-creator-opencode/scripts/run_eval_opencode.py \
  --eval-set /tmp/eval.json \
  --skill-path ~/Documents/Personal/skills/container-image-hardening \
  --model anthropic/claude-haiku-4-5 \
  --runs-per-query 3 \
  --trigger-threshold 0.5 \
  --verbose
```

Output is the same JSON shape as upstream `run_eval.py`:

```json
{
  "skill_name": "container-image-hardening",
  "description": "...",
  "results": [
    {"query": "...", "should_trigger": true, "trigger_rate": 1.0, "triggers": 3, "runs": 3, "pass": true}
  ],
  "summary": {"total": N, "passed": N, "failed": 0}
}
```

Plug the JSON back into any tooling that already speaks the upstream shape (for example, to build your own `run_loop` variant).

## How triggering is detected

One call to `opencode run --format json` produces newline-delimited JSON events. The event this adapter watches for:

```json
{
  "type": "tool_use",
  "part": {
    "tool": "skill",
    "state": {
      "input": { "name": "<skill-name>" }
    }
  }
}
```

If any line in the stream matches that shape **and** `name` equals the skill being probed, the run is counted as triggered.

### Probe installation model — important

Agents select a skill by its **exact name**. That means the probe description must be installed under the real skill's name. This adapter:

1. Moves the real `~/.config/opencode/skill/<name>` directory aside to `<name>.shadow` (symlinks and directories both handled).
2. Writes the probe `SKILL.md` with the description being tested at `~/.config/opencode/skill/<name>`.
3. Runs `opencode run --format json <query>`.
4. Restores the real directory in `finally`, whether or not the run triggered or crashed.

One consequence: concurrent runs for the **same skill name** race on the single-slot probe. Run serially per skill (`--num-workers 1`) when probing the same skill repeatedly. Different skills can be probed in parallel.

## Limits and known gaps

1. **No `run_loop.py` / `improve_description.py` port yet.** The description rewrite step in the upstream loop is a Claude-only call; porting it means either using the local OpenCode model for rewrites (via another `opencode run` call) or accepting that description optimization stays manual.
2. **Single-slot probe.** Because the probe must land at the real skill's exact name, only one probe can exist per skill at a time. Runs against the same skill must be serialized (`--num-workers 1`). Different skills can run in parallel across workers safely.
3. **Timeout.** OpenCode's TUI-oriented `run` has more overhead than `claude -p`; 60s default is safer than the 30s upstream default. Very long-model cold starts can exceed even that — raise `--timeout` if a known-good query reports false negatives.
4. **Session reuse.** `opencode run` starts a new session per call. That is what we want for clean trigger evaluation — do not add `-c` / `--continue`.
5. **Cost.** `opencode run` against `anthropic/*` or any direct-API provider bills per call. 20 queries × 3 runs = 60 calls, not free. Prefer cheap models (haiku family, mimo, glm, kimi) for trigger eval; reserve the Sonnet/Opus tier for evaluating qualitative skill output, not for measuring whether the description triggers.
6. **Crash recovery.** If the adapter crashes between `shadow_real_skill` and `restore_real_skill`, the real skill will be at `<name>.shadow` on disk. Rename it back manually (or rerun — the shadow handler detects and cleans stale shadows at start of the next run against the same name).

## Extending to a full loop

If you want a `run_loop_opencode.py` later:

1. Copy `skill-creator/scripts/run_loop.py` and replace the import of `run_eval` with this adapter's.
2. Replace `improve_description` with a function that calls `opencode run --format json` against a rewrite prompt and parses the returned text, instead of calling `claude -p`.
3. The eval-viewer (`eval-viewer/generate_review.py`) is CLI-agnostic — it reads a benchmark JSON — so no changes needed there.
