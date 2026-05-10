---
name: project-rules-file
description: Create, audit, and maintain the project's AI rules file — `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.windsurfrules`, `.github/copilot-instructions.md`, or equivalent. This is the single highest-leverage context a project can provide to any coding agent. Use WHENEVER (1) the user asks to write, generate, or update a rules file for AI agents; (2) starting work on a new repo that has no rules file, or a stale one; (3) agent output drifts from project conventions (wrong import style, wrong test runner, wrong commit format); (4) the user mentions AGENTS.md, CLAUDE.md, Cursor rules, Windsurf rules, Copilot instructions, or "how should the agent know X about this repo"; (5) onboarding an agent to an unfamiliar codebase. Applies to any language or stack.
---

<!-- Inspired by addyosmani/agent-skills context-engineering (MIT). See ../CREDITS.md -->

# Project Rules File

The rules file is the persistent, session-level context every coding agent reads first. Get it right once and every future session in that repo starts aligned. Get it wrong and every session starts with the agent hallucinating conventions.

This skill covers: **which file, what goes in it, what stays out, how to keep it current**.

## Which file to use

Different agents read different filenames. Same format (Markdown). Pick the right one for the project's primary agent; add aliases for the rest.

| Agent / tool | Rules file |
|--------------|-----------|
| OpenAI Codex, OpenCode, generic | `AGENTS.md` (root) |
| Claude Code | `CLAUDE.md` (root) |
| Cursor | `.cursor/rules/*.mdc` (scoped rules) or legacy `.cursorrules` |
| Windsurf | `.windsurfrules` |
| GitHub Copilot (VS Code) | `.github/copilot-instructions.md` |
| Kiro | `.kiro/steering/*.md` |
| Gemini / Google | `GEMINI.md` |

**Recommended pattern**: write canonical rules in **`AGENTS.md`** (the emerging standard, read by most agents), then make each agent-specific file a one-line redirect:

```markdown
<!-- CLAUDE.md -->
See [AGENTS.md](AGENTS.md).
```

```markdown
<!-- .github/copilot-instructions.md -->
See [AGENTS.md](../AGENTS.md).
```

For Cursor `.cursor/rules/*.mdc` (which supports glob-scoped rules), split: one file per concern with `globs:` frontmatter. The root rules still live in `AGENTS.md`.

Check `.gitignore` and commit the rules file. A rules file outside version control cannot be shared with teammates or CI.

## What goes in it

A rules file answers the questions every coding agent needs resolved before writing a line of code. In order of leverage:

### 1. Tech stack + versions (mandatory)

Specific versions, not "latest". "React 18" beats "React". `Node 20.11` beats "Node".

```markdown
## Tech Stack
- Runtime: Node 20.11, npm 10
- Language: TypeScript 5.4, strict mode, no `any`
- Framework: Next.js 14 (App Router, RSC)
- Styling: Tailwind CSS 3.4, `cn()` utility from `@/lib/cn`
- Data: PostgreSQL 15, Prisma 5.10
- Testing: Vitest 1.4, Playwright 1.42
```

### 2. Commands (mandatory)

The **exact** commands. Agents guess wrong often; telling them saves a bad `npm test` followed by "command failed".

```markdown
## Commands
- Install:        `pnpm install --frozen-lockfile`
- Dev server:     `pnpm dev`
- Build:          `pnpm build`
- Typecheck:      `pnpm typecheck`
- Lint:           `pnpm lint --fix`
- Unit tests:     `pnpm test`
- E2E:            `pnpm test:e2e`
- Single test:    `pnpm test -- path/to/test.spec.ts`
- Format:         `pnpm format`
```

If the project uses `make`, `task`, `just`, or `mise run`, surface those too and note which is the source of truth.

### 3. Code conventions (high leverage)

Short, declarative, scannable. No essays.

```markdown
## Conventions
- Functional components only. No classes.
- Named exports. No default exports.
- Colocate tests: `Button.tsx` → `Button.test.tsx`.
- Use `@/` path alias for imports under `src/`.
- Validation with `zod`. Never hand-roll type guards.
- HTTP errors: throw `AppError(code, message)`, not raw `Error`.
- Prefer `satisfies` over `as` for type narrowing.
```

### 4. Boundaries — what the agent must NOT do (highest leverage)

Rules framed as prohibitions prevent more bad output than rules framed as preferences.

```markdown
## Boundaries
- Never commit `.env*` or files matching `*secret*`, `*credential*`.
- Never modify database schema without explicit approval (ask first).
- Never add runtime dependencies without checking bundle-size impact.
- Never bypass validation on `/api/*` routes.
- Never run `git push --force` on `main`.
- Never edit files under `src/generated/` — they're regenerated from schema.
```

### 5. Patterns / prior art (medium leverage)

Point at one existing example for each recurring pattern. Concrete > abstract.

```markdown
## Patterns
- New API route: model after `src/app/api/users/route.ts`.
- New form: model after `src/components/forms/LoginForm.tsx` (uses `react-hook-form` + `zod`).
- DB query with pagination: `src/lib/db/queries/listUsers.ts`.
- Error boundary: wrap routes with `<AppErrorBoundary>` from `src/components/error-boundary.tsx`.
```

### 6. Architecture (for large repos)

A 5-10 line map so the agent knows where to look without grep-crawling the whole tree.

```markdown
## Architecture
- `src/app/` — Next.js routes (App Router). One folder per route.
- `src/components/` — React components. `ui/` is primitives, `forms/` is form widgets.
- `src/lib/` — Cross-cutting utilities: `db/` (Prisma), `auth/`, `validation/`, `errors.ts`.
- `src/server/` — Server-only code (never imported from client components).
- `prisma/schema.prisma` — Single source of truth for DB schema.
- `scripts/` — One-off scripts. Run via `pnpm tsx scripts/<name>.ts`.
```

### 7. Commit / PR conventions (if enforced)

```markdown
## Commits & PRs
- Conventional Commits: `feat(scope): …`, `fix(scope): …`.
- Subject <= 72 chars, imperative mood.
- One logical change per PR. No drive-by refactors.
- Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
```

### 8. Domain glossary (if the domain is non-obvious)

```markdown
## Glossary
- **Tenant** — a customer organization. Top-level isolation boundary.
- **Workspace** — a project within a tenant. Users belong to one tenant, N workspaces.
- **Seat** — a paid user slot. Distinct from "user" (unpaid guests can exist).
```

## What stays OUT

Every line in the rules file competes for the agent's attention on every turn. Ruthlessly exclude:

- **General programming advice.** "Write clean code" — already baked into the model.
- **Things covered by the type system / linter / formatter.** The tooling enforces them; restating is noise.
- **Historical context.** "We used to use X but migrated to Y in 2023." Irrelevant unless it affects current decisions.
- **One-off decisions that already happened.** Put those in ADRs under `docs/adr/`, not the rules file.
- **Long explanations.** If a rule needs 3 paragraphs to justify, it is really an ADR. Link it: `See docs/adr/012-validation.md`.
- **Personal preferences that the project doesn't actually enforce.** If the codebase mixes both styles, do not lie in the rules file.
- **Secrets, tokens, connection strings, private URLs.** The rules file is committed.

Rule of thumb: **every line must change the agent's output**. If removing the line would not change any future session's behavior, remove it.

## Length target

Aim for **80-200 lines**. Under 80 usually means missing critical context. Over 200 usually means essays where bullets would do, or content that belongs in `references/` / ADRs.

If the file grows past 200 lines, split:
- `AGENTS.md` — stack, commands, conventions, boundaries, pointers.
- `docs/architecture.md` — architecture map + patterns.
- `docs/adr/NNNN-*.md` — one decision per file, linked from the rules file.

## Audit: symptoms of a bad rules file

| Symptom | Cause | Fix |
|---------|-------|-----|
| Agent runs the wrong test command | Missing or outdated `Commands` section | Add exact commands; run them once to confirm |
| Agent uses default exports in a named-export codebase | Conventions not stated, or stated vaguely | Make it a hard rule: "Named exports only. No default exports." |
| Agent invents API signatures | Rules file has no pointer to the real source | Add `Patterns` with file paths |
| Agent keeps "improving" unrelated files | No scope-discipline rule | Add to Boundaries: "Touch only files required by the task" |
| Agent commits `.env` files | Secrets rule missing | Add to Boundaries; also check `.gitignore` |
| File is 600 lines long | Essays instead of bullets; history instead of rules | Split into ADRs; keep only what changes output |
| File says one thing, code does another | Rules rotted | Run the audit loop below |

## Audit loop

Run this when output drift is suspected, or every ~6 months.

1. **Read the current rules file end-to-end.** Note every claim it makes about the codebase.
2. **Verify each claim against the code.** Does the project actually use X? Is command Y still the right one?
3. **Delete stale claims.** Do not "update" — if it was wrong, the correction may also be wrong. Delete, then re-add what you verified.
4. **Add missing rules.** For each convention you see in recent PRs that is not in the rules file, consider adding it.
5. **Cut length.** If you added 10 lines, look for 10 to cut. Signal density matters.
6. **Commit the diff with a clear message:** `docs(agents): audit AGENTS.md — remove stale commands, add validation rule`.

## Generating a rules file from scratch

When bootstrapping in a new repo:

1. **Read the repo first.** Run `ls`, open `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod`, open the README, open 2-3 representative source files, open the test config.
2. **Interview the user** for the 20% that cannot be inferred:
   - Which conventions are strict vs. suggested?
   - Which files are off-limits (generated, vendored)?
   - What workflow (branches, PRs, commit format)?
   - Any domain glossary?
3. **Draft** using the sections above. Mark uncertainties with `<!-- CONFIRM: … -->`.
4. **Run the commands you listed** to confirm they work on this machine. Fix any that fail.
5. **Show the draft** to the user before writing. Resolve `CONFIRM` markers.
6. **Write `AGENTS.md` at the repo root** and optional aliases (`CLAUDE.md`, etc.) as redirects.

## Minimal working template

Keep this small and concrete. Expand only with rules the project actually enforces.

```markdown
# <Project Name>

<1-sentence description of what this codebase is.>

## Tech Stack
- <Runtime + version>
- <Language + version + strictness flags>
- <Framework + version>
- <Datastore + version>
- <Test runner + version>

## Commands
- Install:   `<cmd>`
- Dev:       `<cmd>`
- Build:     `<cmd>`
- Typecheck: `<cmd>`
- Lint:      `<cmd>`
- Test:      `<cmd>`
- Format:    `<cmd>`

## Conventions
- <rule 1>
- <rule 2>
- <rule 3>

## Boundaries
- Never <thing 1>
- Never <thing 2>
- Ask before <thing 3>

## Patterns
- <Pattern name>: see `<path/to/example>`.

## Commits
- <format, e.g. Conventional Commits>
- <subject length cap>
```

## Interaction with other skills

- `context-engineering` — this skill is Level 1 of the context hierarchy. `context-engineering` covers the full stack (specs, source files, error output, history).
- `investigate-before-editing` — run it to **read** the code before writing the rules file.
- `no-docs-unless-asked` — exception: the rules file **is** a documentation file the user is asking for, so the rule to avoid creating docs does not apply here.
- `git-hygiene` — the commit that introduces the rules file should follow Conventional Commits (`docs(agents): ...`).

## Verification checklist

Before declaring the rules file done:

- [ ] The file exists at the right path for the project's primary agent (`AGENTS.md` unless otherwise justified).
- [ ] Every command listed was executed on this machine and succeeded.
- [ ] Tech stack includes specific versions, not "latest".
- [ ] Boundaries section lists at least one "never" rule appropriate to this project.
- [ ] At least one `Patterns` entry points at a real, existing file in the repo.
- [ ] No secrets, tokens, or private URLs are in the file.
- [ ] Total length is between 80 and 200 lines (or split with clear links to overflow docs).
- [ ] Aliases for other agents in use (e.g. `CLAUDE.md` if the team uses Claude Code) point back to the canonical file.
- [ ] File is committed and not in `.gitignore`.
