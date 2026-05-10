# skills

Personal collection of LLM agent skills used across Claude Code, OpenCode and Codex CLI.

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) and optional scripts / references. When the agent recognizes the task matches the skill `description`, it loads the content as extra context.

## Skills

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | Safety and workflow rules for `aws`: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation order, assume-role chains, and destructive-command checklist. |
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) with correct `${{ ... }}` syntax across all three contexts (parameters / steps / values), conditional parameters, multi-env patterns, and a validation checklist. |
| [`codex-claude-resume`](./codex-claude-resume) | Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent. |
| [`container-image-hardening`](./container-image-hardening) | Canonical workflow for secure, fast, small container images. Dockerfile structure, BuildKit cache mounts, multi-arch, Trivy/Grype scan, Syft SBOM, cosign signing, Copacetic in-place CVE patching. |
| [`gh-cli-workflows`](./gh-cli-workflows) | Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. Pre-flight checks, remote → account mapping, secret set from `pass-cli`. |
| [`git-hygiene`](./git-hygiene) | Baseline git safety: read-before-write, Conventional Commits, safe push/force-push rules, amend guardrails, recovery via reflog, secret checks before commit. |
| [`handoff`](./handoff) | Produces a concise handoff briefing summarising what was done in the session, what is pending, and important context. |
| [`investigate-before-editing`](./investigate-before-editing) | Forces the agent to read the relevant code and learn repo conventions before changing anything. Match the house style, never invent symbols, search for prior art before adding helpers. |
| [`kubectl-workflows`](./kubectl-workflows) | Safety rules for `kubectl`: explicit `--context`/`--namespace`, server-side dry-run + diff before apply, `kubectl debug` over `exec`, safe deletes, minimal secret exposure. |
| [`no-docs-unless-asked`](./no-docs-unless-asked) | Blocks the reflex to create `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, etc. "to be helpful". Updates to existing docs and inline code comments are fine. |
| [`pass-cli-secrets`](./pass-cli-secrets) | Enforces secrets hygiene: pass-cli (Proton Pass) for local creds, AWS Secrets Manager / SSM for workloads. AI-blind piping so the value never enters the agent's context. |
| [`pr-workflow`](./pr-workflow) | Opens PRs / MRs that reviewers can actually review. Title + body structure, draft vs ready, pre-flight checklist, merge strategies. Host-agnostic (GitHub, GitLab, Bitbucket). |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | When to use [RTK](https://github.com/sigoden/rtk) to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli, etc.) and reduce token usage. |
| [`skill-creator`](./skill-creator) | Official Anthropic skill for creating and iteratively improving skills (draft → test → evaluate → refine loop, with benchmarking and description optimization). Vendored from [anthropics/skills](https://github.com/anthropics/skills) under Apache 2.0. |
| [`terraform-iac-expert`](./terraform-iac-expert) | Opinionated Terraform guidance: module design, project structure, state, testing, governance. Ships with a detailed knowledge base in `references/best-practices.md`. |

## Installing

Skills are just folders. Symlink them into the skills directory of the agent you use. Same skills work across all three agents below.

### Claude Code — `~/.claude/skills/`

```bash
git clone https://github.com/caiolombello/skills.git
cd skills
mkdir -p ~/.claude/skills
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         container-image-hardening gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows no-docs-unless-asked \
         pass-cli-secrets pr-workflow rtk-token-optimized-cli skill-creator \
         terraform-iac-expert; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done
```

### OpenCode — `~/.config/opencode/skill/`

```bash
mkdir -p ~/.config/opencode/skill
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         container-image-hardening gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows no-docs-unless-asked \
         pass-cli-secrets pr-workflow rtk-token-optimized-cli skill-creator \
         terraform-iac-expert; do
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done
```

### Codex CLI — `~/.codex/skills/`

```bash
mkdir -p ~/.codex/skills
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         container-image-hardening gh-cli-workflows git-hygiene handoff \
         investigate-before-editing kubectl-workflows no-docs-unless-asked \
         pass-cli-secrets pr-workflow rtk-token-optimized-cli skill-creator \
         terraform-iac-expert; do
  ln -sfn "$PWD/$s" ~/.codex/skills/"$s"
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

The `description` field in the frontmatter is the trigger: keep it specific so the agent only loads the skill when relevant.

## Contributing / forking

Feel free to fork. Two things to keep in mind when adapting:

- `pass-cli-secrets` references Proton Pass CLI. Swap for your own secret backend if different.
- `codex-claude-resume` reads `~/.claude/projects/**`. Only useful if you run Claude Code locally.

## License

The skills written here are MIT (see `LICENSE`).

`skill-creator/` is a vendored copy of the [official Anthropic skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) and is licensed under Apache 2.0 — see `skill-creator/LICENSE.txt` and `skill-creator/README.md` for attribution details.
