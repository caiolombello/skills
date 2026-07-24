# CREDITS

This repository is a curated, provider-agnostic library of Agent Skills. Several of our skills are **inspired by** — not copied from — excellent upstream projects. We rewrote and adapted each one to:

- Remove Claude-specific assumptions (subagents, personas, `agents/` directories) so the skill works in Claude Code, OpenCode, Codex CLI, Kiro, Cursor, and other agents.
- Use a plural rules-file vocabulary (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` / `.windsurfrules`) instead of hard-coding one.
- Keep descriptions dense and trigger-rich per the [Anthropic skill-creator](https://github.com/anthropics/skills) heuristics.
- Match the tone and structure of the rest of this repo.

Rewriting — not vendoring — keeps the library maintainable and self-consistent. The upstream authors deserve credit regardless.

Most non-vendored upstream projects used as inspiration are under the MIT
license. Exceptions are called out explicitly below: AWS Agent Toolkit is
Apache-2.0, AI-DLC uses MIT-0, and Revenue-Centric Design uses custom
source-available terms. Authoritative standards and government publications
used as technical sources are identified separately. Our original and adapted
skill text is MIT unless a skill directory says otherwise (see
[LICENSE](LICENSE)). Vendored projects retain their original license; see
[Vendored verbatim](#vendored-verbatim-distinct-from-the-above) below. We
acknowledge every source because provenance matters even when attribution is not
required.

## Upstream projects referenced

### [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — MIT

Copyright (c) 2025 Addy Osmani.
Commit referenced: `3ff4b51`.
Latest review snapshot: `fefc407`.

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
| `spec-first-planning` | `spec-driven-development` + `planning-and-task-breakdown` |
| `performance-optimization` | `performance-optimization` |
| `diagnose` | `debugging-and-error-recovery` |
| `test-driven-development` | `test-driven-development` |
| `code-review` | `code-review-and-quality` |
| `doubt-driven-review` | `doubt-driven-development` |

### [mattpocock/skills](https://github.com/mattpocock/skills) — MIT

Copyright (c) 2026 Matt Pocock.
Commit referenced: `733d312`.
Latest review snapshot: `ed37663`.

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `diagnose` | `engineering/diagnosing-bugs` (renamed from `engineering/diagnose`) |
| `test-driven-development` | `engineering/tdd` |
| `incremental-implementation` | tracer-bullet principle in `engineering/tdd` |
| `zoom-out` | `engineering/zoom-out` |
| `throwaway-prototype` | `engineering/prototype` |
| `setup-pre-commit` | `misc/setup-pre-commit` |

### [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — MIT

Copyright (c) forrestchang and contributors. Derived from [Andrej Karpathy's observations on LLM coding pitfalls](https://x.com/karpathy/status/2015883857489522876).
Commit referenced: `2c60614`.

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `llm-coding-discipline` | `karpathy-guidelines` |

### [obra/superpowers](https://github.com/obra/superpowers) — MIT

Copyright (c) Jesse Vincent and contributors.
Commit referenced: `f2cbfbe`.
Latest review snapshot: `3dcbd5c` (Superpowers v6.2.0).

Skills inspired by this project:

| Our skill | Upstream skill(s) |
|-----------|-------------------|
| `brainstorming` | `brainstorming` |
| `using-git-worktrees` | `using-git-worktrees` |
| `executing-plans` | `executing-plans` |
| `dispatching-parallel-agents` | `dispatching-parallel-agents` + `subagent-driven-development` |
| `receiving-code-review` | `receiving-code-review` |
| `finishing-a-development-branch` | `finishing-a-development-branch` |
| `verification-before-completion` | `verification-before-completion` |
| `test-driven-development` reference on falsifiable, behavior-focused tests | `test-driven-development/writing-good-tests.md` |

### [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) — Apache-2.0

Copyright Amazon.com, Inc. or its affiliates.
Latest review snapshot: `b4416dd`.

The toolkit is the official AWS-supported collection of MCP configuration,
plugins, rules, and task-specific skills. We use its "verify AWS details rather
than guess", infrastructure-as-code, secret-safety, read-before-write,
post-remediation validation, and non-auto-execution guardrails as reference.
The AWS documentation linked by each local skill remains the primary source for
service behavior.

| Our skill | Upstream reference(s) |
|-----------|-----------------------|
| `aws-security-architecture` | `rules/aws-agent-rules.md`, `aws-iam`, `setting-up-cloudtrail-multi-region`, `securing-s3-buckets` |
| `aws-security-posture` | audit/remediation workflow constraints, current-state verification, postcheck discipline |
| `aws-security-incident-response` | agent recommendation non-execution guardrail; AWS incident-response documentation is the primary workflow source |

### [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) — MIT-0

Copyright Amazon.com, Inc. or its affiliates.
Stable `main` snapshot: `114ef4d`.
AI-DLC 2.x snapshot: `c38ba24`.
Latest tagged release reviewed: `v2.3.0` (`29a31f7`).

AI-DLC is an adaptive, gated development-lifecycle methodology. We use its
scope/depth composition, explicit stage decisions, human gates, traceability,
state continuity, and back-propagation principles as reference. We do not
vendor its native Codex runtime, 32-stage graph, agents, hooks, Bun tooling,
Bedrock integration, or raw-prompt audit model.

| Our skill | Upstream reference(s) |
|-----------|-----------------------|
| `aidlc-workflow` | stable `core-workflow.md`; v2 orchestrator, scope grid, stage graph, gates, state and traceability |
| `spec-first-planning` | adaptive depth, stage selection, requirement-to-task-to-evidence traceability |

### [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) — MIT

Copyright (c) 2025 Context Engineering Agent Skills Contributors.
Commit referenced: `7a95d94`.
Latest review snapshot: `c578e85`.

Reviewed during research; no skills currently adapted from this project (its scope is agent-building / multi-agent systems, orthogonal to the coding-workflow focus of this repo). We may revisit later.

### [otaviof/gosmith](https://github.com/otaviof/gosmith) — MIT

Latest review snapshot: `d434c83`.

Reviewed as a Go-focused agent and skill reference. No skill is currently
adapted from this project; the local library keeps language-specific coding
guidance on demand rather than expanding the default catalog.

### [heliocosta-dev/revenue-centric-design](https://github.com/heliocosta-dev/revenue-centric-design) — source-available custom terms

Latest review snapshot: `6fa20cb`.

Downloaded as a local reference only; no skill from this repository has been adapted into this library yet. It contains a product-design, conversion, retention, pricing and behavioral-science playbook for SaaS/startups. Any future copy or derivative must retain attribution to Richard (@richardrx), preserve the full license terms, and must not be used for gambling, betting, casino, loot-box or real-money-gaming work. See the upstream [LICENSE](https://github.com/heliocosta-dev/revenue-centric-design/blob/main/LICENSE).

### [modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol) — MIT

Stable specification reviewed: `2025-11-25` (checked 2026-07-23).

The official specification, security best practices, SDK catalog, client
guidance, and Inspector documentation are the primary protocol sources for
`mcp-development`. The official Python and TypeScript SDK repositories were
also reviewed to distinguish supported production lines from prereleases. The
skill requires a fresh live version check because the protocol and SDKs evolve
quickly.

| Our skill | Upstream reference(s) |
|-----------|-----------------------|
| `mcp-development` | protocol specification, lifecycle, tools/resources/prompts, transports, authorization, security best practices, client guidance, SDK catalog, Inspector |

### [NSA Model Context Protocol security design guide](https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF) — official U.S. Government publication

Publication reviewed: *Model Context Protocol (MCP): Security Design
Considerations for AI-Driven Automation*, May 2026 Ver. 1.0.

`mcp-development` translates its trust-boundary, validation, sandboxing,
untrusted-output, observability, vulnerability-management, and deployment
inventory recommendations into testable controls. The local text is newly
written and does not reproduce the report. Where the report suggests exact
parameter logging or message signing, the skill adds secret-safe redaction and
clarifies that signing is a high-assurance application extension rather than a
standard interoperable MCP requirement.

## Skills with no upstream inspiration

The following skills were written from scratch based on SRE / DevOps / API-design best practices (Google SRE Book, DORA, OpenTelemetry specs, OWASP, RFC 9457 Problem Details, semver.org, Helm / ArgoCD / GitLab / GitHub official docs, AWS Well-Architected Framework, FinOps Foundation principles), not adapted from any of the upstream projects above. They are noted here only for completeness:

- `incident-response`
- `observability`
- `deploy-safety`
- `architecture-decision-records` (format follows MADR — [adr.github.io/madr](https://adr.github.io/madr/))
- `github-actions-workflows` (follows GitHub's own documentation)
- `gitlab-ci-workflows` (follows GitLab's own documentation)
- `glab-cli-workflows` (follows GitLab CLI's own documentation)
- `helm-workflows` (follows Helm's official chart best-practices + ArgoCD / Helmfile docs)
- `runbook-authoring` (Google SRE Book's runbook guidance + RFC 8594 / 9745 Deprecation/Sunset headers)
- `api-and-interface-design` (RFC 9457 Problem Details, Semver.org, Relay Cursor Connections, gRPC + Protobuf style guides)
- `database-migrations` (expand/contract pattern; pt-osc, gh-ost, Atlas, Alembic, Flyway, Liquibase docs)
- `disaster-recovery` (AWS Well-Architected DR pillar + Google SRE discipline for backup testing)
- `karpenter-workflows` (follows Karpenter core + provider docs, especially NodePools, NodeClasses, disruption, drift, consolidation, and provider-specific node supply)
- `cost-optimization-aws` (FinOps Foundation principles + AWS CUR + AWS Cost Optimization Pillar)
- `monorepo-strategy` (Turborepo / Nx / Bazel official docs + pnpm / Yarn / uv / Cargo workspace docs)
- `awscli-workflows`, `kubectl-workflows`, `gh-cli-workflows`, `git-hygiene`, `pr-workflow`, `no-docs-unless-asked`, `container-image-hardening`, `pass-cli-secrets`, `terraform-iac-expert`, `backstage-scaffolder-architect`, `codex-claude-resume`, `handoff`, `investigate-before-editing`, `rtk-token-optimized-cli`

## Vendored verbatim (distinct from the above)

Some skills in this repository are **vendored verbatim** from upstream projects under their original license. Those directories include the upstream `LICENSE` and a `README.md` documenting modifications (if any). As of this writing:

- [`skill-creator/`](skill-creator/) — vendored from [anthropics/skills](https://github.com/anthropics/skills), Apache 2.0. See [`skill-creator/README.md`](skill-creator/README.md) for details.

The difference matters: vendored projects keep their upstream license file and we avoid modifying them. Inspired skills are new works under our MIT license.

## How to acknowledge in individual skills

Each inspired skill carries an HTML comment just below the frontmatter:

```
<!-- Inspired by <upstream>/<project> <upstream-skill(s)> (MIT). See ../CREDITS.md -->
```

This keeps attribution discoverable without cluttering the skill content.

## ax

- Source: [yusukebe/ax](https://github.com/yusukebe/ax) (MIT)
- Site: https://ax.yusuke.run/
- Local skill: [`ax/`](./ax) — vendored skill wrapper for the `ax` CLI (fetch/discover/extract for agents).
