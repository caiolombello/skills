# CREDITS

This repository is a curated, provider-agnostic library of Agent Skills. Several of our skills are **inspired by** — not copied from — excellent upstream projects. We rewrote and adapted each one to:

- Remove Claude-specific assumptions (subagents, personas, `agents/` directories) so the skill works in Claude Code, OpenCode, Codex CLI, Kiro, Cursor, and other agents.
- Use a plural rules-file vocabulary (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` / `.windsurfrules`) instead of hard-coding one.
- Keep descriptions dense and trigger-rich per the [Anthropic skill-creator](https://github.com/anthropics/skills) heuristics.
- Match the tone and structure of the rest of this repo.

Rewriting — not vendoring — keeps the library maintainable and self-consistent. The upstream authors deserve credit regardless.

All upstream projects used are under the MIT license. Our modifications are MIT as well (see [LICENSE](LICENSE)). MIT does not require attribution on derivative work, but we choose to acknowledge the sources because it is the right thing to do.

## Upstream projects referenced

### [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — MIT

Copyright (c) 2025 Addy Osmani.
Commit referenced: `3ff4b51`.

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `llm-coding-discipline` | `using-agent-skills` (Core Operating Behaviors) |
| `project-rules-file` | `context-engineering` (Level 1: Rules Files) |
| `context-engineering` | `context-engineering` |
| `docs-verified-coding` | `source-driven-development` |
| `security-hardening` | `security-and-hardening` |
| `incremental-implementation` | `incremental-implementation` |
| `code-simplification` | `code-simplification` (which itself cites Anthropic's code-simplifier plugin) |
| `diagnose` | `debugging-and-error-recovery` |
| `test-driven-development` | `test-driven-development` |
| `code-review` | `code-review-and-quality` |
| `doubt-driven-review` | `doubt-driven-development` |

### [mattpocock/skills](https://github.com/mattpocock/skills) — MIT

Copyright (c) 2026 Matt Pocock.
Commit referenced: `733d312`.

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `diagnose` | `engineering/diagnose` |
| `test-driven-development` | `engineering/tdd` |
| `incremental-implementation` | tracer-bullet principle in `engineering/tdd` |

### [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — MIT

Copyright (c) forrestchang and contributors. Derived from [Andrej Karpathy's observations on LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876).
Commit referenced: `2c60614`.

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `llm-coding-discipline` | `karpathy-guidelines` |

### [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) — MIT

Copyright (c) 2025 Context Engineering Agent Skills Contributors.
Commit referenced: `7a95d94`.

Reviewed during research; no skills currently adapted from this project (its scope is agent-building / multi-agent systems, orthogonal to the coding-workflow focus of this repo). We may revisit later.

## Vendored verbatim (distinct from the above)

Some skills in this repository are **vendored verbatim** from upstream projects under their original license. Those directories include the upstream `LICENSE` and a `README.md` documenting modifications (if any). As of this writing:

- [`skill-creator/`](skill-creator/) — vendored from [anthropics/skills](https://github.com/anthropics/skills), Apache 2.0. See [`skill-creator/README.md`](skill-creator/README.md) for details.

The difference matters: vendored projects keep their upstream license file and we avoid modifying them. Inspired skills are new works under our MIT license.

## How to acknowledge in individual skills

Each inspired skill carries an HTML comment just below the frontmatter:

```
<!-- Inspired by <upstream>/<project> (MIT). See ../CREDITS.md -->
```

This keeps attribution discoverable without cluttering the skill content.
