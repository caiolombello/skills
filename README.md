# skills

Personal collection of LLM agent skills used across Claude Code, OpenCode, Codex CLI and Kiro.

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) and optional scripts / references. When the agent recognizes the task matches the skill `description`, it loads the content as extra context.

All skills in this repo are written to be **provider-agnostic** — they work in any coding agent that reads `SKILL.md`-style skills, not only Claude Code.

## Skills

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
| [`gh-cli-workflows`](./gh-cli-workflows) | Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. |
| [`pr-workflow`](./pr-workflow) | PRs / MRs that reviewers can actually review. Title + body structure, draft vs ready, pre-flight checklist, merge strategies. Host-agnostic. |

### Infra & cloud

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | Safety rules for `aws`: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation, assume-role chains, destructive-command checklist. |
| [`kubectl-workflows`](./kubectl-workflows) | Safety rules for `kubectl`: explicit `--context`/`--namespace`, server-side dry-run + diff before apply, `kubectl debug` over `exec`, safe deletes. |
| [`helm-workflows`](./helm-workflows) | Chart authoring + safe operation. `helm diff` before upgrade, `--atomic --wait`, values hierarchy, subcharts, OCI publishing, ArgoCD/Helmfile patterns. |
| [`terraform-iac-expert`](./terraform-iac-expert) | Opinionated Terraform guidance: module design, project structure, state, testing, governance. Detailed knowledge base in `references/best-practices.md`. |
| [`container-image-hardening`](./container-image-hardening) | Secure, fast, small container images. Dockerfile structure, BuildKit cache mounts, multi-arch, Trivy/Grype scan, Syft SBOM, cosign, Copacetic. |

### Release & production operations (SRE)

| Skill | What it does |
|-------|--------------|
| [`github-actions-workflows`](./github-actions-workflows) | Design GitHub Actions workflows with security (OIDC, SHA-pinned actions, least-privilege permissions) and performance (caching, concurrency, path filters, composite vs reusable). |
| [`gitlab-ci-workflows`](./gitlab-ci-workflows) | Design GitLab pipelines with `rules:` + `needs:` DAGs, OIDC federated cloud auth, `include:` templates, parent-child pipelines for monorepos, built-in security scanners. |
| [`deploy-safety`](./deploy-safety) | Progressive delivery: canary / blue-green / rolling / feature flags. Rollback-first, SLO-gated, DB expand-contract migrations, Kubernetes probe discipline. |
| [`observability`](./observability) | Golden signals, SLIs/SLOs, burn-rate alerts, cardinality control, structured logs, OpenTelemetry traces, dashboards that work at 3am. |
| [`incident-response`](./incident-response) | Live incident discipline: declare → triage → stabilize → communicate → resolve → blameless postmortem. Stabilize first; root-cause later. |
| [`runbook-authoring`](./runbook-authoring) | Write runbooks that on-call can follow at 3am. Scoped per alert, copy-paste commands, verify-after-action, escalation on top. |
| [`architecture-decision-records`](./architecture-decision-records) | Capture significant decisions as short, immutable ADRs (MADR format). Supersede instead of edit. Linked from the rules file. |

### Secrets & services

| Skill | What it does |
|-------|--------------|
| [`pass-cli-secrets`](./pass-cli-secrets) | Secrets hygiene: pass-cli (Proton Pass) for local creds, AWS Secrets Manager / SSM for workloads. AI-blind piping so values never enter the agent's context. |

### Productivity & meta

| Skill | What it does |
|-------|--------------|
| [`handoff`](./handoff) | Produces a concise handoff briefing: what was done, what's pending, important context. |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | When to use [RTK](https://github.com/sigoden/rtk) to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli) and reduce token usage. |
| [`codex-claude-resume`](./codex-claude-resume) | Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent. |
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) with correct `${{ ... }}` syntax across all three contexts. |
| [`skill-creator`](./skill-creator) | Official Anthropic skill for creating and iteratively improving skills. Vendored from [anthropics/skills](https://github.com/anthropics/skills) under Apache 2.0. |
| [`skill-creator-opencode`](./skill-creator-opencode) | Adapter that runs the skill-creator trigger-eval loop against OpenCode instead of `claude -p`. Works with any provider / model. |

## Installing

Skills are just folders. Symlink them into the skills directory of the agent you use. Same skills work across all four agents below.

### Claude Code — `~/.claude/skills/`

```bash
git clone https://github.com/caiolombello/skills.git
cd skills
mkdir -p ~/.claude/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering deploy-safety diagnose docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline no-docs-unless-asked observability \
         pass-cli-secrets performance-optimization pr-workflow \
         project-rules-file rtk-token-optimized-cli runbook-authoring \
         security-hardening setup-pre-commit skill-creator \
         skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done
```

### OpenCode — `~/.config/opencode/skill/`

```bash
mkdir -p ~/.config/opencode/skill
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering deploy-safety diagnose docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline no-docs-unless-asked observability \
         pass-cli-secrets performance-optimization pr-workflow \
         project-rules-file rtk-token-optimized-cli runbook-authoring \
         security-hardening setup-pre-commit skill-creator \
         skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done
```

### Codex CLI — `~/.codex/skills/`

```bash
mkdir -p ~/.codex/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering deploy-safety diagnose docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline no-docs-unless-asked observability \
         pass-cli-secrets performance-optimization pr-workflow \
         project-rules-file rtk-token-optimized-cli runbook-authoring \
         security-hardening setup-pre-commit skill-creator \
         skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"
done
```

### Kiro — `~/.kiro/skills/`

```bash
mkdir -p ~/.kiro/skills
for s in api-and-interface-design architecture-decision-records \
         awscli-workflows backstage-scaffolder-architect code-review \
         code-simplification codex-claude-resume container-image-hardening \
         context-engineering deploy-safety diagnose docs-verified-coding \
         doubt-driven-review gh-cli-workflows git-hygiene \
         github-actions-workflows gitlab-ci-workflows handoff helm-workflows \
         incident-response incremental-implementation \
         investigate-before-editing kubectl-workflows \
         llm-coding-discipline no-docs-unless-asked observability \
         pass-cli-secrets performance-optimization pr-workflow \
         project-rules-file rtk-token-optimized-cli runbook-authoring \
         security-hardening setup-pre-commit skill-creator \
         skill-creator-opencode spec-first-planning \
         terraform-iac-expert test-driven-development \
         throwaway-prototype zoom-out; do
  ln -sfn "$PWD/$s" ~/.kiro/skills/"$s"
done
```

Pick any subset — each skill is independent. Prefer symlinks over copies so a single `git pull` updates every agent at once.

## Skill anatomy

```
<skill-name>/
  SKILL.md          # YAML frontmatter (name + description) and instructions
  <script>.py       # optional helper scripts
  references/       # optional longer docs loaded on demand
```

The `description` field in the frontmatter is the trigger: keep it specific so the agent only loads the skill when relevant. Use `skill-creator` + `skill-creator-opencode` to iteratively optimize descriptions.

## Credits

Several skills in this repo are **inspired by** excellent upstream projects — rewritten to be provider-agnostic and consistent with the rest of the library. See [CREDITS.md](CREDITS.md) for attribution to [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), [mattpocock/skills](https://github.com/mattpocock/skills), [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills), and [anthropics/skills](https://github.com/anthropics/skills).

## Contributing / forking

Feel free to fork. Two things to keep in mind when adapting:

- `pass-cli-secrets` references Proton Pass CLI. Swap for your own secret backend if different.
- `codex-claude-resume` reads `~/.claude/projects/**`. Only useful if you run Claude Code locally.

## License

The skills written here are MIT (see [LICENSE](LICENSE)).

`skill-creator/` is a vendored copy of the [official Anthropic skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) and is licensed under Apache 2.0 — see `skill-creator/LICENSE.txt` and `skill-creator/README.md` for attribution details.
