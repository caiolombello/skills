---
name: investigate-before-editing
description: Read the relevant code and understand the repository conventions before changing anything. Use WHENEVER the agent is about to (1) edit, add, rename, move, or delete files; (2) introduce or change a dependency; (3) add a new pattern, abstraction, or library; (4) answer a question that depends on how something is actually implemented in this repo. Enforces "match the house style, do not invent a new one" and "never guess an API — verify it".
---

# investigate-before-editing

A code change only lands well if it matches the repository's existing conventions. This skill encodes the minimum investigation an agent must do before writing or modifying code.

The goal is not to read the whole codebase. It is to read **enough** to avoid the three common failure modes:

1. Introducing a pattern, library, or abstraction that already exists in another form in the repo.
2. Guessing an API and producing code that references functions / types / fields that do not exist or have different signatures.
3. Using a style (naming, error handling, testing, file layout) that clashes with what the project already does.

## Non-negotiables

1. **Never invent.** Every function, type, field, import path, config key, and environment variable the edit references must have been verified to exist in the repository or in the pinned dependency version — not guessed from memory.
2. **Never introduce a new dependency, framework, or pattern** without first searching the repo for an existing equivalent.
3. **Match the file's own style.** Indentation, quoting, line length, error handling, logging library — copy from the file being edited, not from your training data.
4. **Read the file you are editing, end-to-end, before the first change** — not just the target lines.
5. **Read the neighbouring files** (same directory, same package/module) to confirm the conventions generalize.
6. **When in doubt about "how does this project do X?", search first, ask second, never guess.**

## Standard investigation sequence

Before touching code, run a variant of this sequence. Skip stages only when they are obviously irrelevant.

### 1. Read the task anchor

The user's request names something — a file, a function, a feature, a bug. Start there:

- Read the named file in full (not just the mentioned function).
- If a symbol is named, locate it with search and read its definition plus one or two call sites.
- If a feature is named but no symbol given, search for it by likely keywords and read the entry point.

### 2. Learn the repo shape

Small, cheap checks:

- **Root inventory** — `ls` of the repository root, plus any obvious top-level directories (`src/`, `lib/`, `pkg/`, `cmd/`, `app/`, `internal/`, `modules/`). You are looking for a mental map, not details.
- **Package manifest** — `package.json`, `pyproject.toml` / `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `build.gradle`, `Makefile`. Tells you language(s), dependencies, scripts.
- **Build + test scripts** — the manifest plus `Makefile` / `justfile` / `Taskfile` tell you how to run tests, lint, build. Do not invent commands; use what is defined.
- **CI config** — `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, etc. Shows you what is required to pass and in what order.
- **Conventions docs** — `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`, `docs/architecture*`. If any exist, read them before coding.
- **Lint / formatter config** — `.editorconfig`, `.prettierrc`, `eslint*`, `.rubocop.yml`, `pyproject.toml [tool.ruff]`, `rustfmt.toml`. Governs surface style.

### 3. Learn how the project does this kind of thing

Before writing a new X (endpoint, model, test, job, module, CLI command), find at least one existing X in the repo and read it. Grep patterns such as:

- For a new endpoint: search route registration files.
- For a new model / entity: search the existing entities in the same layer.
- For a new test: find the closest existing test and copy its structure.
- For a new module / package: find a sibling module and match its file layout and public surface.

Copy the **pattern**, not the content.

### 4. Verify every external symbol

Before writing code that uses library function `x.y.z()`:

- Confirm the dependency exists in the manifest and at what version.
- Verify the symbol exists at that version (search the repo's vendored copy, `node_modules/`, installed package, or `go doc`, `python -c "import x; help(x.y)"`, `cargo doc --open`, etc. when available).
- If you cannot verify, say so in your response and either ask or choose a symbol you can verify.

Do the same for internal symbols — read the definition, do not infer it from the call.

### 5. Look for prior art inside the repo

Before creating a helper, check if one already exists:

- `rg` for the concept, not only the exact name (`retry`, `Retry`, `backoff`, `withRetry`).
- Check common locations: `utils/`, `lib/`, `internal/shared/`, `common/`, `pkg/`.
- If you find an existing helper that is 70% right, extend or rename it rather than creating a parallel one.

### 6. Confirm build/test commands

Before running verification:

- Look at the manifest / Makefile / CI to find the project's real `build`, `test`, `lint`, `typecheck` commands.
- Use those commands. Do not substitute a generic one.
- If the project uses a custom runner (e.g., `bazel`, `pants`, `nx`, `turbo`), use it.

## How much investigation is "enough"

Scale investigation to change size:

| Change | Minimum investigation |
|---|---|
| Rename, typo fix, comment | Read the file. |
| Small bug fix in one function | Read the file + one or two callers. |
| New feature inside existing module | Read the module's files + one sibling feature for shape. |
| New module / package | Repo shape + nearest sibling module + conventions doc. |
| New dependency / framework / pattern | All of the above + explicit search for existing equivalent. |
| Cross-cutting refactor | All of the above + a grep for all call sites and a short written plan. |

Err toward more investigation for anything that touches public APIs, build tooling, CI, or data schemas.

## What to capture (internally) before editing

Hold in memory (or state briefly in your response) the answers to:

- Which files are in scope for the change?
- What style does this file follow (indent, quotes, naming, error handling, logging)?
- What existing pattern is the nearest analogue to what I am about to add?
- Which external symbols will my change call, and have I verified each?
- Which build/test commands will I run to verify?
- Are there conventions files (`AGENTS.md`, etc.) with directives that apply here?

If any of these have no answer yet, do more investigation.

## When the repo is actively inconsistent

Real repos often have two styles (legacy vs new). When that happens:

1. Match the style of the file / module you are touching, even if it is the older one. Do not "modernize" adjacent code unrelated to the request.
2. If the task requires picking a side, pick the style used by the most recent commits in that area (check `git log`), or ask the user.
3. Do not mix — never start a file in style A and end it in style B.

## Anti-patterns

- **Guessing import paths.** `from foo import bar` when you have not opened `foo`. Open the package index or `__init__.py` first.
- **Copying a snippet from memory** of a different framework version. Versions matter; check the manifest.
- **Introducing a utility named `utils.ts` / `helpers.py`** when the repo already has `lib/internal/util.ts`. Extend what exists.
- **Using a new logging / HTTP / validation library** because you prefer it. Use the one the repo uses.
- **Writing "defensive" wrappers** around functions you did not read. If you read the function, you know whether the wrapper is needed.
- **Editing a file without reading the lines around your change.** Local context determines whether the edit makes sense.

## Exit criteria before writing

Before the first `Edit` / `Write`:

- [ ] The file being edited has been read fully.
- [ ] The immediate neighbours (same directory) have been scanned.
- [ ] The nearest existing analogue of what I am adding has been located and read.
- [ ] Every external API being called has been verified to exist at the pinned version.
- [ ] No new dependency, framework, or pattern is being introduced without confirming no existing equivalent.
- [ ] Build / test commands for this project are known.
- [ ] Any `AGENTS.md` / `CLAUDE.md` / `CONTRIBUTING.md` directives have been read.
