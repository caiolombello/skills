# skills

Personal collection of LLM agent skills used across Claude Code and OpenCode.

A "skill" is a self-contained folder with a `SKILL.md` (YAML frontmatter + instructions) and optional scripts/references. When the agent recognises the task matches the skill `description`, it loads the content as extra context.

## Skills

| Skill | What it does |
|-------|--------------|
| [`backstage-scaffolder-architect`](./backstage-scaffolder-architect) | Generates Backstage Scaffolder templates (template.yaml + skeleton) following best practices. |
| [`codex-claude-resume`](./codex-claude-resume) | Lists, inspects and imports local Claude Code sessions so you can continue the work in another agent (e.g. OpenCode, Codex). |
| [`handoff`](./handoff) | Produces a concise handoff briefing summarising what was done in the session, what is pending, and important context. |
| [`pass-cli-secrets`](./pass-cli-secrets) | Enforces secrets hygiene: pass-cli (Proton Pass) for local creds, AWS Secrets Manager / SSM for workloads. No literal secrets in files, commits or agent context. |
| [`rtk-token-optimized-cli`](./rtk-token-optimized-cli) | When to use [RTK](https://github.com/sigoden/rtk) to compress noisy CLI output (git diff, kubectl logs, test runners, aws cli, etc.) and reduce token usage. |
| [`terraform-iac-expert`](./terraform-iac-expert) | Opinionated Terraform guidance: module design, project structure, state, testing, governance. |

## Installing

Skills are just folders. Copy or symlink them into the skills directory of the agent you use.

### Claude Code

```bash
git clone https://github.com/caiolombello/skills.git
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/handoff"                  ~/.claude/skills/handoff
ln -s "$PWD/skills/pass-cli-secrets"         ~/.claude/skills/pass-cli-secrets
ln -s "$PWD/skills/terraform-iac-expert"     ~/.claude/skills/terraform-iac-expert
ln -s "$PWD/skills/backstage-scaffolder-architect" ~/.claude/skills/backstage-scaffolder-architect
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skill
ln -s "$PWD/skills/codex-claude-resume"      ~/.config/opencode/skill/codex-claude-resume
ln -s "$PWD/skills/rtk-token-optimized-cli"  ~/.config/opencode/skill/rtk-token-optimized-cli
```

Adjust to your own layout. Either location works for both agents as long as the host reads from that path.

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

- `pass-cli-secrets` references Proton Pass CLI; swap for your own secret backend if different.
- `codex-claude-resume` reads `~/.claude/projects/**`; only useful if you run Claude Code locally.

## License

MIT
