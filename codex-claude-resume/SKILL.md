---
name: codex-claude-resume
description: Use when the user wants to recover, inspect, list, or continue a Claude Code conversation from local session history in the current repository or by session id/name.
---

# codex-claude-resume

Use this skill to bridge local Claude Code session history into the current AI coding tool.

## When to use

- The user wants to continue work here that started in Claude Code
- The user gives a Claude session id or renamed session title
- The user wants to list Claude sessions related to the current repository
- The user wants a compact continuation brief instead of manually reading raw `jsonl`

Do not use this skill for remote Claude APIs or web conversations. This skill only reads local Claude Code history from `~/.claude/projects`.

## Helper

Run the helper script (path depends on where you installed the skill):

```bash
# Claude Code / generic install
python3 ~/.claude/skills/codex-claude-resume/claude_resume.py

# OpenCode install
python3 ~/.config/opencode/skill/codex-claude-resume/claude_resume.py
```

Always pass the current repository path:

```bash
--cwd "$PWD"
```

Prefer machine-readable output:

```bash
--json
```

## Workflow

### 1. No selector provided

If the user did not provide a session id or name, list sessions for the current repository:

```bash
python3 <skill-path>/claude_resume.py list --cwd "$PWD" --json
```

Present the sessions with:

- title
- relative last-updated time
- last message preview
- session id
- branch/path when useful

Do not auto-import in this case. Let the user choose.

### 2. Explicit session id or name

If the user provided an id, id prefix, or name, import directly:

```bash
python3 <skill-path>/claude_resume.py import --cwd "$PWD" --id "<session-id>" --json
```

or:

```bash
python3 <skill-path>/claude_resume.py import --cwd "$PWD" --name "<session-name>" --json
```

If the selector is ambiguous, show the returned candidates and ask the user which one to use.

### 3. Inspect without importing

If the user wants details first, use:

```bash
python3 <skill-path>/claude_resume.py show --cwd "$PWD" --id "<session-id>" --json
```

## After import

Treat the returned brief as the imported Claude context and continue the work in the current Codex session.

By default:

- continue from the imported goal
- respect the decisions already taken in Claude unless the user wants to revisit them
- use the extracted files, commands, and next steps to avoid re-discovery work

Do not dump the whole raw transcript back to the user unless they ask for it.
