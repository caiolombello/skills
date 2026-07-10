---
name: no-docs-unless-asked
description: Use when about to create a new README, CHANGELOG, AGENTS/CLAUDE.md, ARCHITECTURE, or other standalone docs file the user did not request. Updates to existing docs are fine.
---
# no-docs-unless-asked

Agents have a reflex to summarize their work by writing documentation. This is almost always wrong: it bloats the repo, the doc drifts the moment code changes, and the user did not ask for it.

## The rule

**Do not create new documentation files unless the user explicitly asks.**

Documentation files include, but are not limited to:

- `README.md`, `README.rst`, `README.txt`
- `CHANGELOG.md`, `HISTORY.md`, `RELEASE_NOTES.md`
- `AGENTS.md`, `CLAUDE.md`, `.cursor*` / `.cursorrules`
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `ARCHITECTURE.md`, `DESIGN.md`, `ADR*.md`, `docs/adr/**`
- Runbooks, playbooks, migration guides, upgrade notes
- Any file under `docs/`, `doc/`, `documentation/`, `handbook/`
- `POSTMORTEM.md`, incident reports
- "Summary of changes" files handed to the user as a deliverable

This applies to suggesting creation as well. Do not offer to create a README "if it would help" when the task was to fix a bug.

## What is allowed

Always allowed:

- Updating **existing** documentation when the task requires it (e.g., user asks you to fix a feature and the behavior is documented — update the doc to match).
- Editing an existing `README.md` section that contradicts the change you just made.
- Inline code comments (docstrings, JSDoc, Go doc comments, etc.) when the local codebase style uses them.
- A commit message or PR body describing the change — that lives in git, not in a new file.
- A chat response summarizing what you did — that is conversation, not a file.

Allowed only with explicit user request:

- Any of the file types listed above.
- Expanding inline comments into a dedicated doc file.
- Writing an ADR even when the change is significant — unless the repo's convention is that every non-trivial PR ships with one.

## Why this matters

1. **Drift.** A doc created today is wrong by next month. If no one asked for it, no one will update it.
2. **Noise.** Repos accumulate stale READMEs at the top of every subfolder. Readers start ignoring them.
3. **Scope creep.** A bug-fix PR that also adds a 200-line ARCHITECTURE.md is harder to review and merge.
4. **False authority.** AI-generated docs sound authoritative but often reflect what the agent assumed, not what is actually true about the system.

## Edge cases

### The repo has a convention that every new module ships a README

Follow the convention. That counts as implicit consent because the repo explicitly requires it. Match the existing READMEs in tone, length, and section structure.

### The user asks for "a summary of the changes"

Put the summary in your reply and in the PR body. Do not create `SUMMARY.md` or `CHANGES.md`.

### The user asks to "document X"

Ask whether they want:
- Inline comments / docstrings, or
- An existing doc file updated, or
- A new doc file created.

Do not assume the third.

### Proactively adding `AGENTS.md` / `CLAUDE.md`

Never. These are user configuration files. Only the user decides what goes in them.

### A new `CHANGELOG.md` or version file

Only when the user explicitly asks, or when the repo already has one and your change requires an entry.

### An architecture doc for a complex refactor

Write one only if asked. If the change is genuinely hard to review without a diagram, put the diagram in the PR body instead.

### `docs/` is empty / missing

Leave it that way unless asked.

## Safe responses when tempted

- **Tempted to add a top-level README** because the repo doesn't have one: do not. Not your call.
- **Tempted to add `CONTRIBUTING.md`** because you noticed the repo lacks one: do not.
- **Tempted to add `SECURITY.md`** because you fixed a vulnerability: update the fix, note the security implication in the PR body, do not create a file.
- **Tempted to add `MIGRATION.md`** because your change is breaking: put migration notes in the PR body and release notes.
- **Tempted to add `docs/<feature>.md`** because the feature is interesting: comment the code, do not write a doc.

## If you think this skill is wrong for the task

If the task genuinely requires new documentation (e.g., the user asked for an "onboarding doc"), then by definition it was explicitly asked. Proceed normally.

If you believe new docs would help but the user did not ask, **say so in your reply and let the user decide** — do not create the file unilaterally:

> "I noticed this repo has no README. Want me to add one?"

Then wait for a yes.

## Pre-flight before creating any `.md` file

Ask:

- [ ] Did the user explicitly name this file or ask me to create it?
- [ ] Is there a repo convention (enforced or documented) that requires this file?
- [ ] Would updating an existing file instead satisfy the request?
- [ ] Could this belong in the PR body or a code comment instead?

If the answer to all four is "no", do not create the file.
