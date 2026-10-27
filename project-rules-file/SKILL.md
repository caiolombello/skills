---
name: project-rules-file
description: "Use when creating or auditing applicable agent rules or project review guidance. Keep verified context and invariants concise; preserve personal preferences and authorization boundaries."
---

<!-- Inspired by addyosmani/agent-skills context-engineering (MIT). See ../CREDITS.md -->

# Project Rules File

The rules file is the persistent, session-level context every coding agent reads first. Get it right once and every future session in that repo starts aligned. Get it wrong and every session starts with the agent hallucinating conventions.

This skill covers: **which file, what goes in it, what stays out, how to keep it current**.

Preserve existing user preferences, provider adaptations, and project policies. A rules audit is not authorization to migrate models, change permissions, set up CI, publish, or create extra documentation. For authorized global quality preferences, [assets/quality-core.pt-BR.md](assets/quality-core.pt-BR.md) supplies a small reusable output snippet; do not install it merely because this skill was read.

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

Check `.gitignore` and the requested sharing scope. Commit project rules when version-control publication is authorized. Personal global files remain local unless the user explicitly approves publishing their contents. A redirect must be followed explicitly when the client's native loading does not guarantee it.

## What goes in it

A rules file answers the questions every coding agent needs resolved before writing a line of code. In order of leverage:

### 1. Verified stack and useful versions

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

### 2. Commands the task actually needs

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

Prioritize verified invariants, a small domain glossary, and recurring failure paths. Where relevant, identify multiple clients/entry points/providers, shared contracts, remote/local modes, and reverse states such as close/reopen. Do not copy another product's architecture or every possible checklist into a small project.

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

Use the shortest file that supplies the context this project actually needs. There is no minimum line count or universal token quota. Keep important constraints visible and load substantial details through relevant references.

When a file becomes hard to navigate, use existing focused sources or split within the authorized documentation scope:
- `AGENTS.md` — stack, commands, conventions, boundaries, pointers.
- `docs/architecture.md` — architecture map + patterns.
- `docs/adr/NNNN-*.md` — one decision per file, linked from the rules file.

## Audit: symptoms of a bad rules file

For reviewer-specific rules, optional `REVIEW.md`, recurring failure prevention, and behavioral evaluation examples, read [references/review-policy.md](references/review-policy.md). This does not configure host gates: required CI, CODEOWNERS, branch protection, scanners, merge queues, and staged rollout need separately authorized project changes and real verification.

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
5. **Cut redundancy.** Keep useful constraints and remove stale/repeated material rather than trading lines against an arbitrary quota.
6. **When commits are authorized**, use a clear message such as `docs(agents): audit AGENTS.md`. Otherwise leave the verified edits uncommitted at the requested endpoint.

## Generating a rules file from scratch

When bootstrapping in a new repo:

1. **Read the repo first.** Run `ls`, open `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod`, open the README, open 2-3 representative source files, open the test config.
2. **Interview the user** for the 20% that cannot be inferred:
   - Which conventions are strict vs. suggested?
   - Which files are off-limits (generated, vendored)?
   - What workflow (branches, PRs, commit format)?
   - Any domain glossary?
3. **Draft** using the sections above. Mark uncertainties with `<!-- CONFIRM: … -->`.
4. **Verify commands against current tooling/source.** Run safe authorized checks, diagnose failures, and record unrun or unavailable scope. Do not execute production/mutating commands or repair unrelated infrastructure just to complete the draft.
5. **Resolve essential uncertainties.** Show a draft when the user asked to approve it first. If the changes are already approved and the facts verified, write within that scope without asking for the same permission again. Do not leave unresolved markers in active instructions.
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
- [ ] Commands match current source/tooling; safe authorized checks were exercised and any unrun or unavailable scope is identified. Production/mutating commands were not run just to fill a checklist.
- [ ] Tech stack includes specific versions, not "latest".
- [ ] Boundaries section lists at least one "never" rule appropriate to this project.
- [ ] At least one `Patterns` entry points at a real, existing file in the repo.
- [ ] No secrets, tokens, or private URLs are in the file.
- [ ] The file is concise and relevant, with conditional detail behind clear references rather than a length quota.
- [ ] Aliases for other agents in use (e.g. `CLAUDE.md` if the team uses Claude Code) point back to the canonical file.
- [ ] Sharing/version-control actions match the requested scope; local personal instructions were not published by default.
