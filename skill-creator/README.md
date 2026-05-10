# skill-creator (vendored from anthropics/skills)

This directory is a vendored copy of the official `skill-creator` skill published by Anthropic.

- **Upstream**: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- **License**: Apache License 2.0 (see `LICENSE.txt`)
- **Copyright**: Anthropic, PBC

The skill is included in this collection so that agents configured with this repo's skills can use it to create new skills. It is kept as a verbatim copy — no edits — to make future upstream updates a simple resync.

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

```bash
git clone --depth=1 https://github.com/anthropics/skills.git /tmp/anthropics-skills
rsync -a --delete /tmp/anthropics-skills/skills/skill-creator/ \
  ~/Documents/Personal/skills/skill-creator/
```

Remember to keep this `README.md` file (it is not present upstream).

## Attribution requirements

Apache 2.0 requires retaining the copyright notice, the `LICENSE.txt`, and stating that the files were modified if they have been changed. As of this commit no files under `skill-creator/` have been modified — only this `README.md` was added alongside the upstream content. If anything under `SKILL.md`, `agents/`, `references/`, `scripts/`, `assets/`, or `eval-viewer/` is edited later, add a prominent notice in the modified file per Apache 2.0 §4(b).
