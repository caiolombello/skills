# skill-creator (vendored from anthropics/skills)

This directory is a vendored copy of the official `skill-creator` skill published by Anthropic.

- **Upstream**: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- **License**: Apache License 2.0 (see `LICENSE.txt`)
- **Copyright**: Anthropic, PBC

The skill is included so that agents configured with this collection can create and evaluate skills. It is vendored with local modifications under its Apache 2.0 license. The 2026-10-27 patches harden report HTML, feedback persistence, port ownership and evaluator/benchmark correctness; modified files carry a notice. These patches are local changes, not an assertion of upstream endorsement.

## Agent compatibility notes

The skill references tooling that is not uniformly available across all agents:

| Feature | Claude Code | OpenCode / Codex CLI |
|---|---|---|
| Subagents (parallel `Task` tool) | Yes | Claude Code-native; other agents vary. |
| `claude -p` CLI (for description optimization) | Yes | Only if the `claude` CLI is installed locally. |
| `present_files` tool | Claude.ai only | Skipped automatically. |
| `eval-viewer/generate_review.py` | Works (needs Python + browser for local serve mode; use `--static` otherwise) | Same. |
| `scripts/package_skill.py` | Works (Python only) | Works. |

The `SKILL.md` itself includes a "Claude.ai-specific instructions" section and a "Cowork-Specific Instructions" section that handle the fallback paths (no subagents, no browser). For OpenCode or Codex CLI, follow the Claude.ai or Cowork notes as closest analogues.

## Re-syncing from upstream

Compare the intended upstream revision in a separate temporary source tree and
review its delta against the local patches before updating this directory. Do
not blindly rsync with `--delete`: that would remove local safety fixes and this
README. Preserve `LICENSE.txt`, copyright, modification notices and the offline
regressions in `setup/tests/test_creator_support.py`; rerun affected checks.

## Attribution requirements

Retain Anthropic's copyright and `LICENSE.txt`. Local modifications in `SKILL.md`,
`agents/`, `references/`, `scripts/`, `assets/` and `eval-viewer/` must remain
identified in each changed file, following Apache 2.0 §4(b).
