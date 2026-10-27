---
name: skill-creator-opencode
description: 'Adapter that lets the official Anthropic skill-creator evaluation loop run against OpenCode instead of Claude Code. Use when the user wants to run `run_eval` / trigger benchmarks against OpenCode (opencode run --format json) using whichever model they are currently using, instead of depending on the `claude` CLI. Ships a drop-in `run_eval_opencode.py` that mirrors the upstream run_eval.py API (--eval-set, --skill-path, --model, --runs-per-query, --trigger-threshold), detects skill triggering by scanning OpenCode''s JSON event stream for `tool_use` events with `tool: "skill"`, and creates a disposable probe in a unique temporary OpenCode project for description overrides. Does NOT cover the rest of the skill-creator loop (improve_description, run_loop, eval-viewer) — those still need adaptation.'
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
| Description override | `.claude/commands/<id>.md` in project root | Disposable project-local skill under a unique temporary OpenCode project |
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

### Probe isolation and recovery

The evaluator validates the frontmatter name (`^[a-z0-9]+(?:-[a-z0-9]+)*$`) before creating any paths. Each evaluator invocation creates a unique temporary project and config directory, then places the candidate at `.opencode/skills/<name>/SKILL.md`. The subprocess runs with that project as its working directory and `OPENCODE_CONFIG_DIR` set to the private config directory. OpenCode project skills have higher precedence than global skill roots, so the probe overrides the same ID without renaming or removing the installed skill. The evaluator also disables external `.agents` and `.claude` skill discovery for that run.

Concurrent evaluations of the same skill use separate project roots. Query workers within one evaluation share only that evaluation's probe. A per-query timeout sends SIGTERM, waits five seconds, then escalates to SIGKILL. On POSIX, the batch harness uses a separate process group and the same graceful-then-forced shutdown for its outer timeout. A forced kill can leave a temporary directory under the system temp root, but cannot strand or overwrite an installed skill.

The evaluator never attempts to recover legacy `<name>.shadow` files. If an older run left `<name>` and `<name>.shadow` together, inspect both manually and restore the intended skill only after confirming their contents. The evaluator will not delete either path.

## Extending to a full loop

If you want a `run_loop_opencode.py` later:

1. Copy `skill-creator/scripts/run_loop.py` and replace the import of `run_eval` with this adapter's.
2. Replace `improve_description` with a function that calls `opencode run --format json` against a rewrite prompt and parses the returned text, instead of calling `claude -p`.
3. The eval-viewer (`eval-viewer/generate_review.py`) is CLI-agnostic — it reads a benchmark JSON — so no changes needed there.
