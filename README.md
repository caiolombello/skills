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
| [`investigate-before-editing`](./investigate-before-editing) | Forces the agent to read relevant code and learn repo conventions before changing anything. Match house style, never invent symbols. |
| [`test-driven-development`](./test-driven-development) | Red-green-refactor with vertical slices. Bug fixes via the Prove-It pattern (reproduce with a test before fixing). |
| [`diagnose`](./diagnose) | Disciplined debug loop: feedback-loop-first, reproduce, hypothesise, instrument, fix, regression-test, cleanup. For hard bugs, flaky tests, perf regressions. |
| [`code-review`](./code-review) | Multi-axis review across correctness, readability, architecture, security, performance. Before merging any non-trivial change. |
| [`doubt-driven-review`](./doubt-driven-review) | In-flight adversarial fresh-context review of non-trivial decisions, BEFORE the PR is open. Provider-agnostic. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Blocks the reflex to create `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md` etc. "to be helpful". Updates to existing docs are fine. |

### Git & version control

| Skill | What it does |
|-------|--------------|
| [`git-hygiene`](./git-hygiene) | Read-before-write, Conventional Commits, safe push/force-push rules, amend guardrails, reflog recovery, secret checks before commit. |
| [`gh-cli-workflows`](./gh-cli-workflows) | Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. |
| [`pr-workflow`](./pr-workflow) | PRs / MRs that reviewers can actually review. Title + body structure, draft vs ready, pre-flight checklist, merge strategies. Host-agnostic. |

### Infra & cloud

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | Safety rules for `aws`: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation, assume-role chains, destructive-command checklist. |
| [`kubectl-workflows`](./kubectl-workflows) | Safety rules for `kubectl`: explicit `--context`/`--namespace`, server-side dry-run + diff before apply, `kubectl debug` over `exec`, safe deletes. |
| [`terraform-iac-expert`](./terraform-iac-expert) | Opinionated Terraform guidance: module design, project structure, state, testing, governance. Detailed knowledge base in `references/best-practices.md`. |
| [`container-image-hardening`](./container-image-hardening) | Secure, fast, small container images. Dockerfile structure, BuildKit cache mounts, multi-arch, Trivy/Grype scan, Syft SBOM, cosign, Copacetic. |

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
for s in awscli-workflows backstage-scaffolder-architect code-review \
         codex-claude-resume container-image-hardening diagnose \
         doubt-driven-review gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows llm-coding-discipline \
         no-docs-unless-asked pass-cli-secrets pr-workflow \
         project-rules-file rtk-token-optimized-cli skill-creator \
         skill-creator-opencode terraform-iac-expert \
         test-driven-development; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done
```

### OpenCode — `~/.config/opencode/skill/`

```bash
mkdir -p ~/.config/opencode/skill
for s in awscli-workflows backstage-scaffolder-architect code-review \
         codex-claude-resume container-image-hardening diagnose \
         doubt-driven-review gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows llm-coding-discipline \
         no-docs-unless-asked pass-cli-secrets pr-workflow \
         project-rules-file rtk-token-optimized-cli skill-creator \
         skill-creator-opencode terraform-iac-expert \
         test-driven-development; do
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done
```

### Codex CLI — `~/.codex/skills/`

```bash
mkdir -p ~/.codex/skills
for s in awscli-workflows backstage-scaffolder-architect code-review \
         codex-claude-resume container-image-hardening diagnose \
         doubt-driven-review gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows llm-coding-discipline \
         no-docs-unless-asked pass-cli-secrets pr-workflow \
         project-rules-file rtk-token-optimized-cli skill-creator \
         skill-creator-opencode terraform-iac-expert \
         test-driven-development; do
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"
done
```

### Kiro — `~/.kiro/skills/`

```bash
mkdir -p ~/.kiro/skills
for s in awscli-workflows backstage-scaffolder-architect code-review \
         codex-claude-resume container-image-hardening diagnose \
         doubt-driven-review gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows llm-coding-discipline \
         no-docs-unless-asked pass-cli-secrets pr-workflow \
         project-rules-file rtk-token-optimized-cli skill-creator \
         skill-creator-opencode terraform-iac-expert \
         test-driven-development; do
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
