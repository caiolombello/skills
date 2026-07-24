# skills

A provider-agnostic library of **agent skills** for LLM coding assistants. Works across Claude Code, OpenCode, Codex CLI, Kiro, Gemini, and any agent that reads `SKILL.md`-style skills.

## What this is, in 30 seconds

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter +
instructions) plus optional scripts or references. The format follows the
[Open Agent Skills specification](https://agentskills.io/specification) and the
[Codex skill-authoring guidance](https://learn.chatgpt.com/docs/build-skills).
Agents typically inject only `name + description + path` at session start
(**progressive disclosure**). When a task matches, the agent loads the full
body.

**Why this library exists**: most public skill collections are Claude-specific and assume subagents, personas, or slash commands that do not exist in other tools. The skills here drop those assumptions, use plural rules-file vocabulary (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` / `.windsurfrules`), and are written to trigger reliably across providers.

**Catalog budget (Codex-class agents):** the initial skill list is capped around **2% of context** (fallback **~8000 characters** for the whole list). If you install dozens of long descriptions, the agent truncates descriptions and then **omits skills**. Prefer a small always-on keep-set; keep the rest in the repo for on-demand install.

## Quickstart (5 minutes)

1. Clone the repo and cd into it:
   ```bash
   git clone https://github.com/caiolombello/skills.git
   cd skills
   ```

2. Install the **public always-on keep-set** (not everything):
   ```bash
   # Codex / Gemini shared path (recommended for Codex)
   mkdir -p ~/.agents/skills
   while IFS= read -r s; do
     [[ -z "$s" || "$s" =~ ^# ]] && continue
     ln -sfn "$PWD/$s" ~/.agents/skills/"$s"
   done < install-manifests/codex-keep.txt

   # Optional machine-local private skills (create from example if needed)
   # cp install-manifests/codex-keep.local.example.txt install-manifests/codex-keep.local.txt
   # edit, then:
   if [[ -f install-manifests/codex-keep.local.txt ]]; then
     while IFS= read -r s; do
       [[ -z "$s" || "$s" =~ ^# ]] && continue
       [[ -d "$PWD/$s" ]] || { echo "skip missing private skill: $s"; continue; }
       ln -sfn "$PWD/$s" ~/.agents/skills/"$s"
     done < install-manifests/codex-keep.local.txt
   fi
   ```

3. Smoke-test in your agent:
   > *"review this PR for correctness and security"*

   If `code-review` loads, the keep-set is working.

### Install paths by agent

| Agent | Always-on install path | Notes |
|-------|------------------------|-------|
| **Codex CLI / Gemini** | `~/.agents/skills/` | Official shared path. **Do not** also install user skills into `~/.codex/skills` (leave `.system` alone). |
| Claude Code | `~/.claude/skills/` | Symlink keep-set; avoid bulk install if you also use Codex. |
| OpenCode | `~/.config/opencode/skill/` | Same keep-set discipline. |
| Kiro | `~/.kiro/skills/` | Same. |

### Suggested starter set (universal)

| Skill | One-liner |
|-------|-----------|
| [`llm-coding-discipline`](./llm-coding-discipline) | Baseline anti-failure-mode behaviors. |
| [`investigate-before-editing`](./investigate-before-editing) | Read code + conventions before editing. |
| [`diagnose`](./diagnose) | Disciplined bug / flaky-test loop. |
| [`code-review`](./code-review) | Multi-axis review before merge. |
| [`git-hygiene`](./git-hygiene) | Safe git defaults, Conventional Commits. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Stop unrequested README/CHANGELOG creation. |
| [`verification-before-completion`](./verification-before-completion) | Prove done with evidence. |

### On-demand (install when the domain is active)

See [`install-manifests/codex-on-demand.txt`](./install-manifests/codex-on-demand.txt) for situational skills (`aidlc-workflow`, `mcp-development`, `deploy-safety`, CI workflows, migrations, FinOps, observability, AWS security, planning, …). Symlink individual folders only when you need them:

```bash
ln -sfn "$PWD/deploy-safety" ~/.agents/skills/deploy-safety
```


### Migrate from an old bulk install

If Claude/OpenCode/Gemini/Kiro still have dozens of skills from a previous "install everything", prune **only** symlinks that point into this repo and are not in the keep manifests (real dirs and external skills are preserved):

```bash
# dry-run
./install-manifests/prune-stale-installs.sh

# apply
./install-manifests/prune-stale-installs.sh --apply
```

Then re-link the keep-set from `install-manifests/codex-keep.txt` (+ optional `codex-keep.local.txt`).

### Anti-pattern: install everything

**Do not bulk-symlink the whole library into Codex.** That recreates description truncation and skill omission. The repo is the library; the agent path is a curated projection.

If you truly need a large set in Claude/OpenCode (no hard 8k list budget), still prefer the keep-set first and grow deliberately.

## Full catalog

Every skill below is independent — pick exactly what you need. Skills marked **tooling-specific** have a hard dependency on a tool other than the agent itself; skip them if you do not use that tool.

### Core coding workflow

| Skill | What it does |
|-------|--------------|
| [`llm-coding-discipline`](./llm-coding-discipline) | Baseline behaviors to prevent the common LLM failure modes: silent assumptions, sycophancy, overengineering, scope creep, skipped verification. Apply before anything non-trivial. |
| [`project-rules-file`](./project-rules-file) | Create, audit, and maintain `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` and friends — the single highest-leverage context for any coding agent. |
| [`context-engineering`](./context-engineering) | Curate the right context at the right time. Hierarchy from rules file → spec → source → errors → history. Anti-patterns for context starvation / flooding / staleness. |
| [`brainstorming`](./brainstorming) | Refine rough ideas before planning or coding. Socratic questions, option tradeoffs, explicit assumptions, recommended next artifact. |
| [`spec-first-planning`](./spec-first-planning) | Specify → Plan → Tasks → Implement. Lightweight spec, dependency map, ordered verifiable tasks. For anything non-trivial. |
| [`aidlc-workflow`](./aidlc-workflow) | Explicit, on-demand AI-DLC coordinator: compose adaptive phases, depth, gates and traceability from the focused skills already in this library. Defers to a complete native upstream runtime when present. |
| [`zoom-out`](./zoom-out) | Produce a higher-level map of an area of code — modules, callers, gotchas — before diving in. |
| [`throwaway-prototype`](./throwaway-prototype) | Build a disposable prototype to answer one design question. Logic branch (terminal) or UI branch (variants on one route). |
| [`docs-verified-coding`](./docs-verified-coding) | Detect version → fetch official docs → implement as documented → cite the source. Prevents the "library API invented from memory" failure mode. |
| [`investigate-before-editing`](./investigate-before-editing) | Forces the agent to read relevant code and learn repo conventions before changing anything. Match house style, never invent symbols. |
| [`incremental-implementation`](./incremental-implementation) | Build in thin vertical slices — implement, test, verify, commit, expand. Tracer-bullet first. Prevents 1000-line-PR failure mode. |
| [`executing-plans`](./executing-plans) | Execute an approved plan task-by-task with TDD, verification, and checkpoints. Stops when the plan conflicts with reality. |
| [`test-driven-development`](./test-driven-development) | Red-green-refactor with vertical slices. Bug fixes via the Prove-It pattern (reproduce with a test before fixing). |
| [`verification-before-completion`](./verification-before-completion) | Prove work is complete before saying done. Records exact checks run, skipped checks, and evidence quality. |
| [`api-and-interface-design`](./api-and-interface-design) | Stable API design — REST / GraphQL / gRPC / webhooks / events / SDK. Versioning, deprecation lifecycle, error shapes, contract testing. |
| [`mcp-development`](./mcp-development) | Secure MCP client/server development — protocol and SDK selection, trust boundaries, strict tool contracts, per-call authorization, sandboxing, poisoning defenses, and adversarial tests. |
| [`diagnose`](./diagnose) | Disciplined debug loop: feedback-loop-first, reproduce, hypothesise, instrument, fix, regression-test, cleanup. For hard bugs, flaky tests, perf regressions. |
| [`performance-optimization`](./performance-optimization) | Measure → identify → fix → verify → guard. Profile before optimizing. Frontend, backend, DB, build. |
| [`code-review`](./code-review) | Multi-axis review across correctness, readability, architecture, security, performance. Before merging any non-trivial change. |
| [`receiving-code-review`](./receiving-code-review) | Process PR/MR review feedback: classify accept/clarify/defer/reject, apply surgically, verify, and respond with evidence. |
| [`code-simplification`](./code-simplification) | Reduce complexity while preserving exact behavior. Chesterton's Fence; rule of three; refactor split from feature work. |
| [`security-hardening`](./security-hardening) | Application-layer security — OWASP Top 10 patterns for input validation, authn/authz, injection, SSRF, CSP. Separate from container/IaC/secret storage. |
| [`doubt-driven-review`](./doubt-driven-review) | In-flight adversarial fresh-context review of non-trivial decisions, BEFORE the PR is open. Provider-agnostic. |
| [`dispatching-parallel-agents`](./dispatching-parallel-agents) | Coordinate parallel subagents or sessions safely with tight briefs, file ownership, worktree isolation, and result synthesis. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Blocks the reflex to create `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md` etc. "to be helpful". Updates to existing docs are fine. |

Workflow precedence: use `brainstorming` to shape vague ideas,
`spec-first-planning` to create the plan, `executing-plans` while working
through approved tasks, `verification-before-completion` before saying done,
and `finishing-a-development-branch` when preparing PR/merge/handoff or
worktree cleanup. Invoke `aidlc-workflow` only when the user explicitly asks
for AI-DLC or an auditable end-to-end lifecycle; it coordinates these skills
rather than replacing them.

### Git & version control

| Skill | What it does |
|-------|--------------|
| [`git-hygiene`](./git-hygiene) | Read-before-write, Conventional Commits, safe push/force-push rules, amend guardrails, reflog recovery, secret checks before commit. |
| [`using-git-worktrees`](./using-git-worktrees) | Isolate parallel branches and risky experiments with git worktrees. Explicit base branch, no secret copying, safe cleanup. |
| [`finishing-a-development-branch`](./finishing-a-development-branch) | Final branch wrap-up: inspect diff, run required checks, summarize evidence, and present merge/PR/keep/discard options. |
| [`setup-pre-commit`](./setup-pre-commit) | Install pre-commit hooks (`pre-commit` / lefthook / Husky). Format, lint, typecheck, secret-scan before every commit. |
| [`gh-cli-workflows`](./gh-cli-workflows) | **tooling-specific: requires `gh`.** Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. |
| [`glab-cli-workflows`](./glab-cli-workflows) | **tooling-specific: requires `glab`.** GitLab CLI companion — correct host + account selection, multi-instance, token scoping. |
| [`atlassian-acli`](./atlassian-acli) | **tooling-specific: requires `acli`.** Jira/Confluence Cloud via Atlassian CLI — Markdown bodies, no hand-pasted ADF, multi-account OAuth. |
| [`pr-workflow`](./pr-workflow) | PRs / MRs that reviewers can actually review. Title + body structure, draft vs ready, pre-flight checklist, merge strategies. Host-agnostic. |

### Infra & cloud

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | **tooling-specific: requires `aws`.** Safety rules: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation, assume-role chains. |
| [`aws-security-architecture`](./aws-security-architecture) | Preventive AWS security architecture and review across accounts, identity, network, data, logging, workloads, and cross-account automation. |
| [`aws-security-posture`](./aws-security-posture) | Security Hub CSPM and compliance-control governance: validate findings, prioritize contextual risk, manage exceptions, plan remediation, and revalidate. |
| [`aws-security-incident-response`](./aws-security-incident-response) | AWS compromise response for GuardDuty/IAM/root/compute/S3/container/data events: preserve evidence, contain reversibly, eradicate, recover, and improve detections. |
| [`cost-optimization-aws`](./cost-optimization-aws) | FinOps discipline for AWS: visibility (CUR + tagging), right-sizing, Savings Plans, NAT/data-transfer waste, CloudWatch Logs hygiene. |
| [`kubectl-workflows`](./kubectl-workflows) | **tooling-specific: requires `kubectl`.** Explicit `--context`/`--namespace`, server-side dry-run + diff, `kubectl debug` over `exec`, safe deletes. |
| [`karpenter-workflows`](./karpenter-workflows) | **tooling-specific: requires `kubectl`; provider docs required; cloud CLI may be needed for provider-side verification.** Safe design, tuning, and troubleshooting of Karpenter `NodePool` / `NodeClass` capacity control. |
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
| [`incident-response`](./incident-response) | Live incident command: declare → triage → stabilize → communicate → resolve → blameless postmortem. Pair with `aws-security-incident-response` for AWS compromise. |
| [`incident-triage`](./incident-triage) | First-response from a pasted PagerDuty/Alertmanager/monitoring alert — normalize, scope, gather Grafana/kubectl/AWS evidence. Not full IC command (use `incident-response`). |
| [`runbook-authoring`](./runbook-authoring) | Write runbooks that on-call can follow at 3am. Scoped per alert, copy-paste commands, verify-after-action, escalation on top. |
| [`architecture-decision-records`](./architecture-decision-records) | Capture significant decisions as short, immutable ADRs (MADR format). Supersede instead of edit. Linked from the rules file. |

### Secrets & services

| Skill | What it does |
|-------|--------------|
| [`pass-cli-secrets`](./pass-cli-secrets) | **tooling-specific: references Proton Pass CLI.** Secrets hygiene: local creds via pass-cli, AWS Secrets Manager / SSM for workloads. Swap the CLI layer for your own secret backend if different (1Password CLI, `pass`, HashiCorp Vault CLI, etc.) — the discipline ("AI-blind piping", "never echo the value") transfers. |
| [`ax`](./ax) | **tooling-specific: requires [`ax`](https://ax.yusuke.run).** AI-era curl — fetch/discover/extract web pages as structured, token-cheap output instead of curl + throwaway parsers. |

### Productivity & meta

| Skill | What it does |
|-------|--------------|
| [`handoff`](./handoff) | Produces a concise handoff briefing: what was done, what's pending, important context. |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | **tooling-specific: requires [RTK](https://github.com/sigoden/rtk).** When to use RTK to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli). |
| [`codex-claude-resume`](./codex-claude-resume) | **tooling-specific: requires Claude Code local session history.** Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent. |
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) with correct `${{ ... }}` syntax across all three contexts. Useful if you run a Backstage developer portal. |
| [`skill-creator`](./skill-creator) | Official Anthropic skill for creating and iteratively improving skills. Vendored from [anthropics/skills](https://github.com/anthropics/skills) under Apache 2.0. |
| [`skill-creator-opencode`](./skill-creator-opencode) | Adapter that runs the skill-creator trigger-eval loop against OpenCode instead of `claude -p`. Works with any provider / model. |

## Install (tiered)

Use the manifests under [`install-manifests/`](./install-manifests/):

| File | Purpose |
|------|---------|
| `codex-keep.txt` | Public always-on subset (safe default for Codex budget) |
| `codex-on-demand.txt` | Situational skills — install per domain |
| `codex-keep.local.txt` | Gitignored private/company skills (see `.example`) |

### Codex / Gemini (`~/.agents/skills`)

```bash
git clone https://github.com/caiolombello/skills.git
cd skills
mkdir -p ~/.agents/skills
while IFS= read -r s; do
  [[ -z "$s" || "$s" =~ ^# ]] && continue
  ln -sfn "$PWD/$s" ~/.agents/skills/"$s"
done < install-manifests/codex-keep.txt
```

Leave `~/.codex/skills` for Codex `.system` skills only. Installing the same user skills into both paths creates duplicates in the catalog.

### Claude Code / OpenCode / Kiro

Same keep-set, different directory:

```bash
# Claude
mkdir -p ~/.claude/skills
while IFS= read -r s; do
  [[ -z "$s" || "$s" =~ ^# ]] && continue
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done < install-manifests/codex-keep.txt

# OpenCode
mkdir -p ~/.config/opencode/skill
while IFS= read -r s; do
  [[ -z "$s" || "$s" =~ ^# ]] && continue
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done < install-manifests/codex-keep.txt

# Kiro
mkdir -p ~/.kiro/skills
while IFS= read -r s; do
  [[ -z "$s" || "$s" =~ ^# ]] && continue
  ln -sfn "$PWD/$s" ~/.kiro/skills/"$s"
done < install-manifests/codex-keep.txt
```

Symlinks mean a single `git pull` updates every agent at once.

## Skill anatomy

```
<skill-name>/
  SKILL.md          # YAML frontmatter (name + description) and instructions
  agents/
    openai.yaml     # optional Codex/ChatGPT UI metadata and dependencies
  scripts/          # optional helpers
  references/       # optional longer docs loaded on demand
```

### Description rules (summary)

- Trigger = **when**, not a workflow essay.
- Distinct branches only; no synonym lists.
- Prefer ~120–220 chars for always-on skills; hard max 1024.
- YAML-safe (quote if needed); no `<`/`>`.
- Aggregate catalog budget matters more than per-skill max — see CONTRIBUTING.

Validate with `skill-creator/scripts/quick_validate.py` and optional trigger evals via `skill-creator-opencode/`.

See [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md) for an earlier trigger quality report.

## Credits

Several skills here are **inspired by** excellent upstream projects — rewritten
to be provider-agnostic and consistent with the rest of the library. See
[CREDITS.md](CREDITS.md) for the complete provenance, including
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[mattpocock/skills](https://github.com/mattpocock/skills),
[obra/superpowers](https://github.com/obra/superpowers),
[aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws),
[awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows),
[heliocosta-dev/revenue-centric-design](https://github.com/heliocosta-dev/revenue-centric-design),
[modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol),
the [NSA MCP security design guide](https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF),
and the other reviewed sources.

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for conventions (skill layout, description style, install tiers, how to propose a new skill, how to suggest cuts or merges).

## License

The skills written here are MIT (see [LICENSE](LICENSE)).

`skill-creator/` is a vendored copy of the [official Anthropic skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) and is licensed under Apache 2.0 — see `skill-creator/LICENSE.txt` and `skill-creator/README.md` for attribution details.
