# skills

A provider-agnostic library of **45 agent skills** for LLM coding assistants. Works across Claude Code, OpenCode, Codex CLI, Kiro, and any other agent that reads `SKILL.md`-style skills.

## What this is, in 30 seconds

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) plus optional scripts or references. The agent reads the frontmatter `description` on every turn and, if the task matches, loads the full content as extra context. Think of each skill as an on-demand expert the agent consults only when relevant.

**Why this library exists**: most public skill collections are Claude-specific and assume subagents, personas, or slash commands that do not exist in other tools. The skills here were written or rewritten to drop those assumptions, use plural rules-file vocabulary (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` / `.windsurfrules`), and trigger reliably across providers.

If you have ever watched an AI coding agent hallucinate a library API, ignore your project's conventions, or commit without tests — these skills are the shape of what you wish the agent had read **before** starting.

## Quickstart (5 minutes)

1. Clone the repo and cd into it:
   ```bash
   git clone https://github.com/caiolombello/skills.git
   cd skills
   ```

2. Symlink **one** skill into your agent's skills directory to smoke-test:
   ```bash
   # Claude Code
   mkdir -p ~/.claude/skills && ln -sfn "$PWD/project-rules-file" ~/.claude/skills/project-rules-file

   # OpenCode
   mkdir -p ~/.config/opencode/skill && ln -sfn "$PWD/project-rules-file" ~/.config/opencode/skill/project-rules-file
   ```

3. Open your agent in any repo and try:
   > *"audit our AGENTS.md for stale or missing rules"*

   If `project-rules-file` loads and the agent walks through the audit loop, you're good. Install more skills from the [Suggested starter set](#suggested-starter-set) or go all-in with the [Install everything](#install-everything) loops below.

## Suggested starter set

New to skills? These seven are universal across languages, stacks, and agents. Start here; add more as you notice gaps.

| Skill | One-liner |
|-------|-----------|
| [`llm-coding-discipline`](./llm-coding-discipline) | Baseline anti-failure-mode behaviors (assumptions, scope, verification). |
| [`project-rules-file`](./project-rules-file) | Generate & audit the project's `AGENTS.md` / `CLAUDE.md`. |
| [`investigate-before-editing`](./investigate-before-editing) | Read code + conventions before editing. |
| [`diagnose`](./diagnose) | Disciplined bug / flaky-test debugging loop. |
| [`code-review`](./code-review) | Five-axis review before merge. |
| [`git-hygiene`](./git-hygiene) | Safe git defaults, Conventional Commits. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Stop the reflex to create unrequested README / CHANGELOG files. |

Symlink just these seven to try the library with a small footprint:

```bash
cd skills   # this repo
for s in llm-coding-discipline project-rules-file investigate-before-editing \
         diagnose code-review git-hygiene no-docs-unless-asked; do
  # Claude Code
  mkdir -p ~/.claude/skills && ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
  # OpenCode
  mkdir -p ~/.config/opencode/skill && ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
  # Codex CLI
  mkdir -p ~/.codex/skills && ln -sfn "$PWD/$s" ~/.codex/skills/"$s"
  # Kiro
  mkdir -p ~/.kiro/skills && ln -sfn "$PWD/$s" ~/.kiro/skills/"$s"
done
```

## Full catalog

Every skill below is independent — pick exactly what you need. Skills marked **tooling-specific** have a hard dependency on a tool other than the agent itself; skip them if you do not use that tool.

### Core coding workflow

| Skill | What it does |
|-------|--------------|
| [`llm-coding-discipline`](./llm-coding-discipline) | Baseline behaviors to prevent the common LLM failure modes: silent assumptions, sycophancy, overengineering, scope creep, skipped verification. Apply before anything non-trivial. |
| [`project-rules-file`](./project-rules-file) | Create, audit, and maintain `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` and friends — the single highest-leverage context for any coding agent. |
| [`context-engineering`](./context-engineering) | Curate the right context at the right time. Hierarchy from rules file → spec → source → errors → history. Anti-patterns for context starvation / flooding / staleness. |
| [`spec-first-planning`](./spec-first-planning) | Specify → Plan → Tasks → Implement. Lightweight spec, dependency map, ordered verifiable tasks. For anything non-trivial. |
| [`zoom-out`](./zoom-out) | Produce a higher-level map of an area of code — modules, callers, gotchas — before diving in. |
| [`throwaway-prototype`](./throwaway-prototype) | Build a disposable prototype to answer one design question. Logic branch (terminal) or UI branch (variants on one route). |
| [`docs-verified-coding`](./docs-verified-coding) | Detect version → fetch official docs → implement as documented → cite the source. Prevents the "library API invented from memory" failure mode. |
| [`investigate-before-editing`](./investigate-before-editing) | Forces the agent to read relevant code and learn repo conventions before changing anything. Match house style, never invent symbols. |
| [`incremental-implementation`](./incremental-implementation) | Build in thin vertical slices — implement, test, verify, commit, expand. Tracer-bullet first. Prevents 1000-line-PR failure mode. |
| [`test-driven-development`](./test-driven-development) | Red-green-refactor with vertical slices. Bug fixes via the Prove-It pattern (reproduce with a test before fixing). |
| [`api-and-interface-design`](./api-and-interface-design) | Stable API design — REST / GraphQL / gRPC / webhooks / events / SDK. Versioning, deprecation lifecycle, error shapes, contract testing. |
| [`diagnose`](./diagnose) | Disciplined debug loop: feedback-loop-first, reproduce, hypothesise, instrument, fix, regression-test, cleanup. For hard bugs, flaky tests, perf regressions. |
| [`performance-optimization`](./performance-optimization) | Measure → identify → fix → verify → guard. Profile before optimizing. Frontend, backend, DB, build. |
| [`code-review`](./code-review) | Multi-axis review across correctness, readability, architecture, security, performance. Before merging any non-trivial change. |
| [`code-simplification`](./code-simplification) | Reduce complexity while preserving exact behavior. Chesterton's Fence; rule of three; refactor split from feature work. |
| [`security-hardening`](./security-hardening) | Application-layer security — OWASP Top 10 patterns for input validation, authn/authz, injection, SSRF, CSP. Separate from container/IaC/secret storage. |
| [`doubt-driven-review`](./doubt-driven-review) | In-flight adversarial fresh-context review of non-trivial decisions, BEFORE the PR is open. Provider-agnostic. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Blocks the reflex to create `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md` etc. "to be helpful". Updates to existing docs are fine. |

### Git & version control

| Skill | What it does |
|-------|--------------|
| [`git-hygiene`](./git-hygiene) | Read-before-write, Conventional Commits, safe push/force-push rules, amend guardrails, reflog recovery, secret checks before commit. |
| [`setup-pre-commit`](./setup-pre-commit) | Install pre-commit hooks (`pre-commit` / lefthook / Husky). Format, lint, typecheck, secret-scan before every commit. |
| [`gh-cli-workflows`](./gh-cli-workflows) | **tooling-specific: requires `gh`.** Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. |
| [`glab-cli-workflows`](./glab-cli-workflows) | **tooling-specific: requires `glab`.** GitLab CLI companion — correct host + account selection, multi-instance, token scoping. |
| [`pr-workflow`](./pr-workflow) | PRs / MRs that reviewers can actually review. Title + body structure, draft vs ready, pre-flight checklist, merge strategies. Host-agnostic. |

### Infra & cloud

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | **tooling-specific: requires `aws`.** Safety rules: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation, assume-role chains. |
| [`cost-optimization-aws`](./cost-optimization-aws) | FinOps discipline for AWS: visibility (CUR + tagging), right-sizing, Savings Plans, NAT/data-transfer waste, CloudWatch Logs hygiene. |
| [`kubectl-workflows`](./kubectl-workflows) | **tooling-specific: requires `kubectl`.** Explicit `--context`/`--namespace`, server-side dry-run + diff, `kubectl debug` over `exec`, safe deletes. |
| [`helm-workflows`](./helm-workflows) | **tooling-specific: requires `helm`.** Chart authoring + safe upgrade. `helm diff` before upgrade, `--atomic --wait`, values hierarchy, ArgoCD/Helmfile patterns. |
| [`terraform-iac-expert`](./terraform-iac-expert) | **tooling-specific: requires Terraform/OpenTofu.** Module design, project structure, state, testing, governance. Detailed knowledge base in `references/best-practices.md`. |
| [`container-image-hardening`](./container-image-hardening) | Secure, fast, small container images. Dockerfile structure, BuildKit cache mounts, multi-arch, Trivy/Grype scan, Syft SBOM, cosign, Copacetic. |
| [`monorepo-strategy`](./monorepo-strategy) | Task runner + affected-graph + remote cache + boundary enforcement. Turborepo / Nx / Bazel / pnpm-Yarn-uv-Cargo workspaces. Polyglot-ready. |

### Release & production operations (SRE)

| Skill | What it does |
|-------|--------------|
| [`github-actions-workflows`](./github-actions-workflows) | **tooling-specific: requires GitHub Actions.** OIDC, SHA-pinned actions, least-privilege permissions, caching, concurrency, path filters, composite vs reusable. |
| [`gitlab-ci-workflows`](./gitlab-ci-workflows) | **tooling-specific: requires GitLab CI.** `rules:` + `needs:` DAGs, OIDC federated cloud auth, `include:` templates, parent-child pipelines. |
| [`deploy-safety`](./deploy-safety) | Progressive delivery: canary / blue-green / rolling / feature flags. Rollback-first, SLO-gated, DB expand-contract migrations, Kubernetes probe discipline. |
| [`database-migrations`](./database-migrations) | Safe production schema changes. Expand/contract, online DDL, `CONCURRENTLY`, `NOT VALID`, throttled backfills, lock timeouts, ORM + `pt-osc` / `gh-ost` / Atlas. |
| [`disaster-recovery`](./disaster-recovery) | Backups that restore, RTO/RPO per domain, 3-2-1-1-0, restore tests as SLIs, quarterly drills, ransomware-specific hardening. |
| [`observability`](./observability) | Golden signals, SLIs/SLOs, burn-rate alerts, cardinality control, structured logs, OpenTelemetry traces, dashboards that work at 3am. |
| [`incident-response`](./incident-response) | Live incident discipline: declare → triage → stabilize → communicate → resolve → blameless postmortem. Stabilize first; root-cause later. |
| [`runbook-authoring`](./runbook-authoring) | Write runbooks that on-call can follow at 3am. Scoped per alert, copy-paste commands, verify-after-action, escalation on top. |
| [`architecture-decision-records`](./architecture-decision-records) | Capture significant decisions as short, immutable ADRs (MADR format). Supersede instead of edit. Linked from the rules file. |

### Secrets & services

| Skill | What it does |
|-------|--------------|
| [`pass-cli-secrets`](./pass-cli-secrets) | **tooling-specific: references Proton Pass CLI.** Secrets hygiene: local creds via pass-cli, AWS Secrets Manager / SSM for workloads. Swap the CLI layer for your own secret backend if different (1Password CLI, `pass`, HashiCorp Vault CLI, etc.) — the discipline ("AI-blind piping", "never echo the value") transfers. |

### Productivity & meta

| Skill | What it does |
|-------|--------------|
| [`handoff`](./handoff) | Produces a concise handoff briefing: what was done, what's pending, important context. |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | **tooling-specific: requires [RTK](https://github.com/sigoden/rtk).** When to use RTK to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli). |
| [`codex-claude-resume`](./codex-claude-resume) | **tooling-specific: requires Claude Code local session history.** Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent. |
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) with correct `${{ ... }}` syntax across all three contexts. Useful if you run a Backstage developer portal. |
| [`skill-creator`](./skill-creator) | Official Anthropic skill for creating and iteratively improving skills. Vendored from [anthropics/skills](https://github.com/anthropics/skills) under Apache 2.0. |
| [`skill-creator-opencode`](./skill-creator-opencode) | Adapter that runs the skill-creator trigger-eval loop against OpenCode instead of `claude -p`. Works with any provider / model. |

## Install everything

Same skills work in all four agents below. Clone once; symlink into the agent(s) you use. Symlinks mean a single `git pull` updates every agent at once.

<details>
<summary><strong>Claude Code — <code>~/.claude/skills/</code></strong></summary>

```bash
git clone https://github.com/caiolombello/skills.git
cd skills
mkdir -p ~/.claude/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering cost-optimization-aws database-migrations \
         deploy-safety diagnose disaster-recovery docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows glab-cli-workflows \
         handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline monorepo-strategy no-docs-unless-asked \
         observability pass-cli-secrets performance-optimization \
         pr-workflow project-rules-file rtk-token-optimized-cli \
         runbook-authoring security-hardening setup-pre-commit \
         skill-creator skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done
```
</details>

<details>
<summary><strong>OpenCode — <code>~/.config/opencode/skill/</code></strong></summary>

```bash
mkdir -p ~/.config/opencode/skill
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering cost-optimization-aws database-migrations \
         deploy-safety diagnose disaster-recovery docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows glab-cli-workflows \
         handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline monorepo-strategy no-docs-unless-asked \
         observability pass-cli-secrets performance-optimization \
         pr-workflow project-rules-file rtk-token-optimized-cli \
         runbook-authoring security-hardening setup-pre-commit \
         skill-creator skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done
```
</details>

<details>
<summary><strong>Codex CLI — <code>~/.codex/skills/</code></strong></summary>

```bash
mkdir -p ~/.codex/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering cost-optimization-aws database-migrations \
         deploy-safety diagnose disaster-recovery docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows glab-cli-workflows \
         handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline monorepo-strategy no-docs-unless-asked \
         observability pass-cli-secrets performance-optimization \
         pr-workflow project-rules-file rtk-token-optimized-cli \
         runbook-authoring security-hardening setup-pre-commit \
         skill-creator skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"
done
```
</details>

<details>
<summary><strong>Kiro — <code>~/.kiro/skills/</code></strong></summary>

```bash
mkdir -p ~/.kiro/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering cost-optimization-aws database-migrations \
         deploy-safety diagnose disaster-recovery docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows glab-cli-workflows \
         handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline monorepo-strategy no-docs-unless-asked \
         observability pass-cli-secrets performance-optimization \
         pr-workflow project-rules-file rtk-token-optimized-cli \
         runbook-authoring security-hardening setup-pre-commit \
         skill-creator skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.kiro/skills/"$s"
done
```
</details>

## Skill anatomy

```
<skill-name>/
  SKILL.md          # YAML frontmatter (name + description) and instructions
  <script>.py       # optional helper scripts
  references/       # optional longer docs loaded on demand
```

The `description` field in the frontmatter is the trigger: keep it specific so the agent only loads the skill when relevant. Use `skill-creator` + `skill-creator-opencode` to iteratively evaluate and improve descriptions.

See [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md) for the latest trigger quality report across the library.

## Credits

Several skills here are **inspired by** excellent upstream projects — rewritten to be provider-agnostic and consistent with the rest of the library. See [CREDITS.md](CREDITS.md) for attribution to [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), [mattpocock/skills](https://github.com/mattpocock/skills), [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), and [anthropics/skills](https://github.com/anthropics/skills).

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions (skill layout, description style, how to propose a new skill, how to suggest cuts or merges).

## License

The skills written here are MIT (see [LICENSE](LICENSE)).

`skill-creator/` is a vendored copy of the [official Anthropic skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) and is licensed under Apache 2.0 — see `skill-creator/LICENSE.txt` and `skill-creator/README.md` for attribution details.
