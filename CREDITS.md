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

### Content-production tool references

`content-production` is an original production/marketing workflow. It references
the following primary sources, reviewed on 2026-10-27, without vendoring their
software, templates, API clients or manuals:

- [Recordly](https://github.com/webadderallorg/Recordly/tree/109ca3a13c362e969d9add25d1f93406c36dba2a),
  snapshot `109ca3a13c362e969d9add25d1f93406c36dba2a`, package 1.4.0;
  its LICENSE.md states AGPL-3.0 and includes branding/attribution summary language.
  No Recordly source is included; use as an editor is distinct from incorporating
  or distributing its code. Native capture/export was not exercised here.
- [Higgsfield Claude integration](https://higgsfield.ai/claude-ai-video-generator),
  [Cinema Studio](https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio),
  [Content Factory](https://higgsfield.ai/blog/higgsfield-introduces-content-factory),
  and [independent API billing](https://higgsfield.ai/blog/higgsfield-api).
  A catalog listing does not establish connected access or a paid entitlement.
- [Claude Motion](https://support.claude.com/en/articles/17454997-get-started-with-claude-motion),
  code-based animation versus realistic video generation.
- [Kdenlive](https://docs.kdenlive.org/en/), [FFmpeg](https://ffmpeg.org/documentation.html),
  [Blender](https://www.blender.org/features/video-editing/) and
  [Remotion's conditional license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
  Optional tool descriptions are not installed dependencies or commercial-rights clearance.

The media-probe helper is original standard-library Python invoking an installed
ffprobe. It does not include FFmpeg code, transcode assets, or judge media quality.

Audio extension references, also reviewed on 2026-10-27:
[Audacity's noise-reduction manual](https://manual.audacityteam.org/man/noise_reduction.html),
[amplitude normalization](https://manual.audacityteam.org/man/amplify_and_normalize.html),
[Piper local TTS](https://github.com/OHF-Voice/piper1-gpl),
[ElevenLabs speech](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)
and [creative terms](https://elevenlabs.io/creative-terms),
[Descript podcasting](https://www.descript.com/podcasting),
and [Suno commercial/download guidance](https://help.suno.com/en/articles/13614785).
No audio engine, voice/model weights, service client or licensed media is bundled.
Software access and rights to the particular audio/voice output remain separate.

### [cursor/plugins pstack](https://github.com/cursor/plugins/tree/519d36aa98955bf680db01bcde5fdfba686dc901/pstack) — MIT

Reviewed snapshot: `519d36aa98955bf680db01bcde5fdfba686dc901` (2026-10-27).
Lauren Tan (poteto) and Cursor contributors. The repository's MIT license is
retained upstream; these are rewritten procedural adaptations, not a vendored
pstack runtime, agent fleet, or executable tool.

| Our skill | Upstream inspiration |
| --- | --- |
| `project-verification` | `create-verification-skill`, `maintain-verification-skill` |
| `formal-verification` | `create-formal-verification-skill`, `maintain-formal-verification-skill`; rewritten with explicit scope/correspondence and a separate original finite-state example |
| `technical-writing` | `technical-writing`, its reader/task distinction and Diataxis organization |
| `zoom-out`, `investigate-before-editing` | `how`, `why`, evidence-backed design rationale |
| `spec-first-planning` | `architect`, caller sketches and empirical comparison |
| `code-review` | `blast-radius`, indirect consumers and falsifiable safety assumptions |
| `diagnose` | `principle-attack-the-premise` |
| `performance-optimization` | `benchmark-checklist`, `principle-explain-the-number` |

Related authored article: [The Complete Guide to pstack Pt. 2](https://x.com/i/article/2094940651607715840),
linked by [poteto's post](https://x.com/poteto/status/2114095305910280363).
The article body was recovered through an X-content mirror when direct access
was blocked, with its title/id corroborated by X's syndication response.
Model presets, compulsory multi-agent choreography, automatic external writes,
blanket comment deletion and the statechart runtime/toolchain were not imported.
Formal creation/maintenance procedures were adapted separately without vendoring
a verifier. [Diataxis](https://diataxis.fr/) is a writing framework reference;
no manual text was copied.

Formal-method technical references reviewed on 2026-10-27:
[TLA+/TLC](https://docs.tlapl.us/using:tlc:start),
[official TLA+ tools](https://github.com/tlaplus/tlaplus) and
[CBMC](https://diffblue.github.io/cbmc/cprover_documentation.html).
These are tool documentation references. The two-actor TLA+/Python fixtures are
original calibration material; no external verifier binary or source is shipped.

### [NousResearch/hermes-agent computer-use](https://github.com/NousResearch/hermes-agent/blob/69f73ec5f11f5a945cc864f29c4e2ad2307eaec3/skills/autonomous-ai-agents/computer-use/SKILL.md) — MIT

Reviewed snapshot: `69f73ec5f11f5a945cc864f29c4e2ad2307eaec3`, skill v2.1.0,
Francesco Bonacci (f-trycua) and Hermes Agent. `computer-use` adapts snapshot
grounding, effect verification and bounded recovery. No driver, wrapper, native
focus guarantee, auxiliary vision setup or blocked-command workaround is
included.

Official technical references reviewed on 2026-10-27:
[OpenAI computer use](https://developers.openai.com/api/docs/guides/tools-computer-use),
[OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model),
and [Anthropic computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
They are documentation references, not software vendored under our license.
The T3 adapter is based on tool contracts actually exposed in the authoring
session; it is dated guidance, not copied SDK schemas or runtime certification.

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

Its user-and-business outcome framing, evidence discipline, value-path
measurement, and ethical monetization guidance inform `ai-interface-design`.
That skill preserves the full upstream terms in its own `LICENSE` and must not
be used for gambling, betting, casino, loot-box, or real-money-gaming work.
`frontend-design` and `frontend-development` remain independently written from
public web standards and official testing documentation. See the upstream
[LICENSE](https://github.com/heliocosta-dev/revenue-centric-design/blob/main/LICENSE).

### [Nutlope/hallmark](https://github.com/Nutlope/hallmark) — MIT

Copyright (c) 2026 Hallmark contributors.
Commit referenced: `aeb42fb`.

`ai-interface-design` adapts Hallmark's brief-led structural variety,
anti-template review posture, and distinction between visual novelty and
meaningful product shape. The local workflow is independently written for
AI-native product interaction and does not vendor Hallmark's themes, component
catalog, or slop-test rule set.

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

### Frontend standards and official testing documentation

`frontend-design` and `frontend-development` were written from scratch using
the [W3C Web Content Accessibility
Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/),
[WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/),
[web.dev responsive-design](https://web.dev/learn/design) and
[Web Vitals](https://web.dev/articles/vitals) guidance, and the official
[Testing Library](https://testing-library.com/docs/),
[Playwright](https://playwright.dev/docs/accessibility-testing), and
[Storybook](https://storybook.js.org/docs/writing-tests/accessibility-testing)
testing documentation as technical sources. These standards and documents were
not vendored, and the local skill text is independently written.

`frontend-design` also reflects reviewed vendor guidance on steering models
toward stronger interfaces: OpenAI's
[Designing delightful frontends with GPT-5.4](https://developers.openai.com/blog/designing-delightful-frontends-with-gpt-5-4)
and [frontend prompt instructions](https://developers.openai.com/api/docs/guides/frontend-prompt)
(reviewed 2026-10-12), and Anthropic's
[Improving frontend design through Skills](https://claude.com/resources/articles/improving-frontend-design-through-skills)
(the distributional-convergence framing). No text, prompts, or assets were
copied; its craft rules, QA scripts (`ui_lint.py`, `ui_audit.js`,
`visual_qa.mjs`, `contrast.py`), starter tokens, and critique rubric are
original work under this repository's MIT license.

The 2026-10-27 frontend refinement also draws on
[Leonxlnx/taste-skill at 12af471](https://github.com/Leonxlnx/taste-skill/tree/12af471f627f866411b4bd785b19646d3672784c)
(MIT): connecting supplied product material to a visual concept, keeping
asset-level provenance, distinguishing dashboard data states, comparing
before/after captures and shipping output, and evaluating rendered variants
without revealing their condition. These instructions, scenarios, and comparison
procedure are independently written. No upstream scripts, wording, visual
libraries, images, or fonts were copied or installed. Its aesthetic bans,
image/motion quotas, and model-rated gallery statistics are not adopted as
universal quality requirements or measured gains for this library.

### Public AI-humanizer prompts and skills

`blog-posting` was written after reviewing how public "AI humanizer" skills
work — the em-dash budget, burstiness, and fact-preservation rules of
[SamaritanOC/humanize](https://github.com/SamaritanOC/humanize) and
[harshaneel/humanize](https://harshaneel.github.io/humanize/) (reviewed
2026-10-25) — plus public writing guides on sentence-length variance. No text,
word lists, or prompts were copied; the workflow, tells catalog, and
`blog_lint.py` are original work under this repository's MIT license.

The 2026-10-26 revision separates `natural-writing` (cross-format voice and
register) from `blog-posting` (articles). It retains that provenance while
removing mandatory punctuation budgets and sentence-variance targets. The
lint's phrase and structure findings are advisory, not evidence of authorship.
The general skill and its message examples are original; optional integration
with the installed `write-like-me` skill uses its own retrieval workflow and
does not copy or vendor plugin code, prompts, or private writing samples.

### Risk-based review, agent scope, and PR follow-up

The 2026-10-27 review-policy update was informed by these public sources and an
audit of this library's existing instructions:

- [How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/) by Addy Osmani, Morgan Westlee Lunt, and Qing Wang.
- [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) by Diane Sarkis.
- Theo's [My AGENTS.md & SKILLS.md Breakdown (Don't copy them)](https://www.youtube.com/watch?v=e1snsuY4lTI), consulted through a public timestamped transcript, with examples cross-checked against [t3dotgg/tstack](https://github.com/t3dotgg/tstack) and [T3 Code's project guidance](https://github.com/pingdotgg/t3code/blob/main/AGENTS.md).

The new `pr-followup`, revised workflows, PT-BR quality snippet, and synthetic
evaluation cases are independently authored adaptations. They do not vendor
Theo's skill payloads or copy private global instructions. Existing upstream
attributions/licenses remain in force. No vendor's model-specific performance
claims are adopted as universal guarantees, and installing these instructions
does not configure CI, branch protection, approvals, or provider accounts.

## Skills with no upstream inspiration

The following skills were written from scratch based on SRE, DevOps, API
design, frontend, accessibility, and testing best practices (Google SRE Book,
DORA, OpenTelemetry specs, OWASP, W3C standards, web.dev, RFC 9457 Problem
Details, semver.org, Helm / ArgoCD / GitLab / GitHub official docs, AWS
Well-Architected Framework, FinOps Foundation principles), not adapted from any
of the upstream projects above. They are noted here only for completeness:

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
- `frontend-design` (W3C WCAG, WAI-ARIA Authoring Practices, and web.dev responsive-design guidance; OpenAI and Anthropic frontend guidance reviewed as described above)
- `frontend-development` (W3C WCAG, WAI-ARIA Authoring Practices, web.dev, Testing Library, Playwright, and Storybook documentation)
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
