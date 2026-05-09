# skills

Personal collection of LLM agent skills used across Claude Code, OpenCode and Codex CLI.

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) and optional scripts / references. When the agent recognizes the task matches the skill `description`, it loads the content as extra context.

## Skills

| Skill | What it does |
|-------|--------------|
| [`awscli-workflows`](./awscli-workflows) | Safety and workflow rules for `aws`: explicit `--profile`/`--region`, read-before-write, dry-run patterns, IAM key rotation order, assume-role chains, and destructive-command checklist. |
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) with correct `${{ ... }}` syntax across all three contexts (parameters / steps / values), conditional parameters, multi-env patterns, and a validation checklist. |
| [`codex-claude-resume`](./codex-claude-resume) | Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent. |
| [`gh-cli-workflows`](./gh-cli-workflows) | Keeps `gh` commands pointed at the right GitHub account when the machine has multiple accounts and SSH host aliases. Pre-flight checks, remote → account mapping, secret set from `pass-cli`. |
| [`git-hygiene`](./git-hygiene) | Baseline git safety: read-before-write, Conventional Commits, safe push/force-push rules, amend guardrails, recovery via reflog, secret checks before commit. |
| [`handoff`](./handoff) | Produces a concise handoff briefing summarising what was done in the session, what is pending, and important context. |
| [`kubectl-workflows`](./kubectl-workflows) | Safety rules for `kubectl`: explicit `--context`/`--namespace`, server-side dry-run + diff before apply, `kubectl debug` over `exec`, safe deletes, minimal secret exposure. |
| [`pass-cli-secrets`](./pass-cli-secrets) | Enforces secrets hygiene: pass-cli (Proton Pass) for local creds, AWS Secrets Manager / SSM for workloads. AI-blind piping so the value never enters the agent's context. |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | When to use [RTK](https://github.com/sigoden/rtk) to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli, etc.) and reduce token usage. |
| [`terraform-iac-expert`](./terraform-iac-expert) | Opinionated Terraform guidance: module design, project structure, state, testing, governance. Ships with a detailed knowledge base in `references/best-practices.md`. |

## Installing

Skills are just folders. Symlink them into the skills directory of the agent you use. Same skills work across all three agents below.

### Claude Code — `~/.claude/skills/`

```bash
git clone https://github.com/caiolombello/skills.git
cd skills
mkdir -p ~/.claude/skills
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         gh-cli-workflows git-hygiene handoff kubectl-workflows \
         pass-cli-secrets rtk-token-optimized-cli terraform-iac-expert; do
  ln -sfn "$PWD/$s" ~/.claude/skills/"$s"
done
```

### OpenCode — `~/.config/opencode/skill/`

```bash
mkdir -p ~/.config/opencode/skill
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         gh-cli-workflows git-hygiene handoff kubectl-workflows \
         pass-cli-secrets rtk-token-optimized-cli terraform-iac-expert; do
  ln -sfn "$PWD/$s" ~/.config/opencode/skill/"$s"
done
```

### Codex CLI — `~/.codex/skills/`

```bash
mkdir -p ~/.codex/skills
for s in awscli-workflows backstage-scaffolder-architect codex-claude-resume \
         gh-cli-workflows git-hygiene handoff kubectl-workflows \
         pass-cli-secrets rtk-token-optimized-cli terraform-iac-expert; do
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

MIT
