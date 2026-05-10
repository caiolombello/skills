---
name: setup-pre-commit
description: Install and configure pre-commit hooks in a repo — fast, reliable, safe checks that run before every commit. Supports three ecosystems with a decision table — `pre-commit` (Python, language-agnostic, CI-friendly), `lefthook` (Go, fast, multi-language), Husky + lint-staged (JS/TS ecosystem). Use WHENEVER the user asks to (1) "add pre-commit hooks", "set up Husky", "set up lefthook", "configure lint-staged"; (2) add commit-time linting, formatting, typechecking, or test-running; (3) prevent bad commits from landing (secrets, format drift, broken builds); (4) enforce project conventions at commit time instead of relying on CI to catch them. Pairs with `git-hygiene` (commit discipline) and `project-rules-file` (convention definitions).
---

<!-- Inspired by mattpocock/skills misc/setup-pre-commit (MIT). Expanded to be multi-ecosystem. See ../CREDITS.md -->

# Setup Pre-Commit

Install pre-commit hooks in a repo so fast, reliable, safe checks run before every commit. Stops bad commits before they land — formatting drift, secrets, broken types, failing tests, trailing whitespace.

Three ecosystems dominate. Pick one per project; do not stack.

## Which tool to pick

| Tool | Runtime | Best for | Shines when |
|------|---------|----------|-------------|
| [**pre-commit**](https://pre-commit.com/) | Python | Polyglot repos, Python projects, anything CI-friendly | Multi-language repos; hooks need to run in CI identically |
| [**lefthook**](https://github.com/evilmartians/lefthook) | Go, single binary | Speed-critical, multi-language | Large repos where parallel hooks matter |
| **Husky + lint-staged** | Node | JS / TS projects | Frontend monorepo, already has `package.json` |

**Recommendation**: default to `pre-commit` for most projects — it has the richest hook ecosystem, runs identically in CI, and does not require a JS runtime. Use Husky if the repo is clearly JS/TS only and you want to stay in one package manager. Use lefthook when hook speed is a measured bottleneck.

## What the hooks should do

At a minimum, every pre-commit config should:

1. **Format** staged files (Prettier, Black, Ruff format, gofmt — whatever the project uses).
2. **Lint** staged files (ESLint, Ruff, golangci-lint, Clippy).
3. **Typecheck** the whole project when types changed (TypeScript, mypy, etc.).
4. **Run fast tests** on changed code (optional — skip if slow).
5. **Detect secrets** (pre-commit has a built-in hook for this, or use `gitleaks`, `detect-secrets`).
6. **Block common footguns** — trailing whitespace, merge conflict markers, large files, debug statements.

Slow hooks (full type checks, full test suite) go on `pre-push`, not `pre-commit`. The pre-commit should finish in **under 10 seconds** on a typical change. Longer, and developers start using `--no-verify`.

## Option A: `pre-commit` (recommended default)

### Install

```bash
# macOS / Linux
pip install pre-commit         # or brew install pre-commit
# or pipx install pre-commit    # isolated, preferred

# Inside the repo:
pre-commit install              # wires .git/hooks/pre-commit
pre-commit install --hook-type commit-msg    # if you want commit-msg hooks too
pre-commit install --hook-type pre-push      # if you want pre-push hooks
```

### Create `.pre-commit-config.yaml`

Generic starter suitable for most repos. Adjust language hooks to the stack.

```yaml
# .pre-commit-config.yaml
# Run on commit; run all hooks on all files with: pre-commit run --all-files
repos:
  # General hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ['--maxkb=1024']
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: mixed-line-ending
        args: ['--fix=lf']

  # Secret detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks

  # Markdown / Prose (optional)
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.42.0
    hooks:
      - id: markdownlint
        args: ['--disable', 'MD013']   # line-length

  # ---- Python stack ----
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ['--fix']
      - id: ruff-format

  # ---- JS / TS stack ----
  # - repo: https://github.com/pre-commit/mirrors-prettier
  #   rev: v4.0.0-alpha.8
  #   hooks:
  #     - id: prettier
  #       additional_dependencies:
  #         - prettier@3.3.3

  # ---- Terraform ----
  # - repo: https://github.com/antonbabenko/pre-commit-terraform
  #   rev: v1.96.1
  #   hooks:
  #     - id: terraform_fmt
  #     - id: terraform_validate
  #     - id: terraform_tflint

  # ---- Shell scripts ----
  # - repo: https://github.com/shellcheck-py/shellcheck-py
  #   rev: v0.10.0.1
  #   hooks:
  #     - id: shellcheck
```

### Local hooks (custom commands)

If you want to run a project-specific script (e.g. `make typecheck`):

```yaml
  - repo: local
    hooks:
      - id: typecheck
        name: typecheck
        entry: make typecheck
        language: system
        pass_filenames: false
        stages: [pre-push]       # slow — run only on push
```

### CI parity

In CI, run `pre-commit run --all-files --show-diff-on-failure`. Same config, same hooks — so anything the hook catches locally is caught identically in CI, and vice versa.

## Option B: lefthook

### Install

```bash
# macOS
brew install lefthook
# Or via go install
go install github.com/evilmartians/lefthook@latest
# Or via npm (for JS projects)
npm i -D lefthook

# Inside the repo:
lefthook install
```

### Create `lefthook.yml`

```yaml
# lefthook.yml
pre-commit:
  parallel: true            # fast
  commands:
    lint:
      run: pnpm eslint {staged_files}
      glob: "*.{ts,tsx,js,jsx}"
    format:
      run: pnpm prettier --write {staged_files}
      glob: "*.{ts,tsx,json,md,yaml,yml}"
      stage_fixed: true     # re-stage after fix
    gitleaks:
      run: gitleaks protect --staged --redact -v

pre-push:
  commands:
    typecheck:
      run: pnpm tsc --noEmit
    test:
      run: pnpm test
```

`stage_fixed: true` is useful — if a formatter rewrites a file, lefthook re-stages it automatically.

## Option C: Husky + lint-staged (JS/TS)

Use when the repo is clearly Node-based and already has `package.json`.

### Install

```bash
# Replace npm with pnpm / yarn / bun as appropriate
npm i -D husky lint-staged prettier
npx husky init                # creates .husky/ and adds "prepare": "husky"
```

### Configure `.lintstagedrc.json`

```json
{
  "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
  "*.{json,md,yaml,yml,css}": ["prettier --write"],
  "*": ["prettier --ignore-unknown --write"]
}
```

### Configure `.husky/pre-commit`

Husky v9+ does not need a shebang:

```
npx lint-staged
```

### Optional `.husky/pre-push`

Slow checks go here:

```
npm run typecheck
npm test
```

### Prettier config (only if missing)

`.prettierrc.json`:

```json
{
  "tabWidth": 2,
  "printWidth": 100,
  "singleQuote": true,
  "trailingComma": "all",
  "semi": true
}
```

## Secrets: make `gitleaks` (or similar) non-optional

Every config above includes a secret-scan hook. Do **not** skip it. One accidental `git commit -a` can push an API key to a public repo in seconds.

Free options: `gitleaks`, `detect-secrets`, `trufflehog`.

If a hook is too noisy on a legacy repo, fix the false positives via an allowlist — do not disable the hook. Example for gitleaks:

```toml
# .gitleaks.toml
[[rules.allowlist]]
description = "Test fixtures"
paths = ['''tests/fixtures/.*''']
```

## Bypassing hooks

- Never use `--no-verify` out of habit. It defeats the whole point.
- Valid reasons: emergency production hotfix where CI will catch it; hook is broken and blocking unrelated work. In both cases, document why in the commit body.
- Hooks in the `commit-msg` stage (checking message format) are OK to bypass occasionally; `pre-commit` / `pre-push` checks are less OK.

See [`git-hygiene`](../git-hygiene) — "preserve hooks unless the user explicitly asks to skip them".

## Rolling out to a team

1. Land the hook config on a feature branch.
2. Run `pre-commit run --all-files` (or equivalent) to fix existing violations; commit the diff separately as `chore: apply pre-commit auto-fixes`.
3. Announce in the team channel / team doc: "Pre-commit hooks added — run `<install command>` once to enable locally."
4. Wire the same config into CI so the hook enforcement is not optional.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Pre-commit runs full test suite | Slow hooks train developers to use `--no-verify` |
| Hook disabled in CI but enabled locally | Drift; local devs angry when CI catches what the hook missed |
| Per-developer hook scripts outside the repo | Not reproducible; new hire has no hooks |
| Commenting out gitleaks "temporarily" | Temporary becomes permanent; secret leaks |
| Husky v4 patterns copied into v9 | v9+ syntax is different (no shebang, different API) |
| Stacking Husky + pre-commit + lefthook | Pick one. |
| No allowlist in gitleaks for fixture data | Devs learn to `--no-verify` to commit tests |
| Hooks that modify files but do not re-stage | Commit is landed without the fix |

## Interaction with other skills

- [`git-hygiene`](../git-hygiene) — baseline discipline around hooks, force-push, amend. Pre-commit hooks enforce some of those rules mechanically.
- [`project-rules-file`](../project-rules-file) — the conventions the hooks enforce (format, lint, commit-msg pattern) belong in the rules file too.
- [`pass-cli-secrets`](../pass-cli-secrets) — secrets never belong in the repo; gitleaks is a safety net. Pair with the discipline from `pass-cli-secrets`.
- [`code-review`](../code-review) — hooks catch the mechanical stuff so reviewers can focus on the five axes.
- [`container-image-hardening`](../container-image-hardening) — `hadolint` can run as a pre-commit hook for Dockerfiles.

## Verification checklist

After setup:

- [ ] `git commit` on a known-bad file (unformatted / with trailing whitespace / with a fake secret) is blocked.
- [ ] `pre-commit run --all-files` (or equivalent) is green on the current main.
- [ ] CI runs the same config; output of a broken hook is identical to local.
- [ ] Hook duration < 10 seconds on a typical commit.
- [ ] Secret-scan hook is installed and not allowlisted beyond known-fixture paths.
- [ ] Team documentation (README / onboarding) includes the one-liner to install hooks locally.
- [ ] Only one hook framework is installed — not two overlapping.
