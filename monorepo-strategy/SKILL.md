---
name: monorepo-strategy
description: Design, audit, and operate a monorepo — shared tooling, incremental builds, boundary enforcement, cache, CI that only rebuilds changed packages. Use WHENEVER the user (1) considers adopting or migrating to a monorepo (from polyrepo or the other way); (2) sets up or changes build tooling in a monorepo (Turborepo, Nx, Bazel, pnpm workspaces, Yarn workspaces, npm workspaces, Rush, Lage, Moon, Gradle, Cargo workspaces, Go workspaces, uv workspaces, Poetry workspaces); (3) debugs a slow monorepo CI (why is every push rebuilding everything?); (4) enforces package boundaries (imports / dependency rules / ownership / codeowners); (5) mentions "monorepo", "polyrepo", "workspaces", "affected graph", "remote cache", "task graph", "package boundary", "dependency cruiser", "syncpack", "changesets". Covers the practical shape across JS/TS, Python, Go, Rust, and polyglot repos. Does NOT cover Git LFS / large-binary repos — that is a different problem.
---

# Monorepo Strategy

A monorepo works well up to the point its tooling breaks. Beyond that point, every developer spends 30 seconds per command waiting for a full recompile, CI takes 45 minutes on a README change, and nobody knows which package actually owns what. The discipline is about **keeping the tooling ahead of the growth**.

This skill covers the practical layer — package layout, build/test incrementality, boundary enforcement, CI affected-graph, caching, and versioning — across the common JS/TS, Python, Go, Rust, and polyglot stacks.

## Should this be a monorepo at all?

**Polyrepo defaults** when:
- Teams ship independently on different lifecycles.
- Ownership boundaries are clean and stable.
- Shared code is minimal and lives in versioned packages.

**Monorepo defaults** when:
- Refactoring across package boundaries is routine.
- Shared code changes often and you want atomic commits across all consumers.
- You can invest in tooling (Turborepo / Nx / Bazel) to keep builds incremental.

The wrong answer: "polyrepo, but synchronized via CI scripts". The worst answer: "monorepo, but each project runs its own builds without shared tooling". Either commit or don't.

A decision of this magnitude warrants an ADR — see [`architecture-decision-records`](../architecture-decision-records).

## Canonical shapes

### JS/TS — Turborepo + pnpm workspaces (recommended modern default)

```
repo/
├── pnpm-workspace.yaml
├── turbo.json
├── package.json                      # root; workspace root
├── tsconfig.base.json                # shared, extended by packages
├── apps/
│   ├── web/                          # next.js
│   └── api/                          # node
├── packages/
│   ├── ui/                           # shared component lib
│   ├── utils/
│   └── tsconfig/                     # shared TS configs
└── tools/
    └── lint-config/
```

`pnpm-workspace.yaml`:
```yaml
packages:
  - apps/*
  - packages/*
  - tools/*
```

`turbo.json` (Turborepo v2):
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env", "tsconfig.base.json"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "inputs": ["src/**", "package.json", "tsconfig.json"]
    },
    "lint": { "dependsOn": ["^build"], "outputs": [] },
    "typecheck": { "dependsOn": ["^build"], "outputs": [] },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "tests/**", "package.json"]
    },
    "dev": { "cache": false, "persistent": true }
  }
}
```

Key: every task declares **inputs** (what invalidates the cache) and **outputs** (what to cache). `^build` means "build this package's dependencies first".

### JS/TS — Nx

Heavier than Turborepo, more features (generators, project graph UI, code owners at graph level). Use Nx when the org is large enough to justify its config surface.

### Bazel / Pants / Please

For **polyglot + large scale**. Bazel gives reproducible, correct, remote-cached builds across any language. The cost: steep learning curve, verbose `BUILD` files, and the team commits to its discipline forever. Worthwhile at Google / Dropbox / Uber scale; usually overkill below ~50 engineers or ~30 services.

### Python — uv / Poetry / Rye workspaces

[`uv`](https://docs.astral.sh/uv/) is the modern default (fast, cross-platform, one tool).

`pyproject.toml` at the root with `[tool.uv.workspace]`:
```toml
[tool.uv.workspace]
members = ["packages/*", "apps/*"]

[tool.uv.sources]
shared-utils = { workspace = true }
```

Each package has its own `pyproject.toml`; `uv sync` resolves across the workspace.

Pair with Turborepo or Nx (they are language-agnostic for task orchestration) if the repo is polyglot.

### Go — Go workspaces

```
go.work
├── go.work
└── services/
    ├── api/
    │   ├── go.mod
    │   └── ...
    └── worker/
        ├── go.mod
        └── ...
```

`go.work` lets multiple modules resolve together without publishing to a proxy. Good for monorepos where services share internal libraries.

### Rust — Cargo workspaces

`Cargo.toml` at root:
```toml
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
```

Sub-crates reference workspace deps with `serde = { workspace = true }`. Keeps versions in sync automatically.

### Polyglot — Turborepo / Nx over the top

Turborepo and Nx do not care about language — they orchestrate any script. For a JS + Python + Go monorepo, use one of them as the task runner and let each language use its native package manager underneath.

## Incremental builds — the whole point

Without incrementality, a monorepo is a slow polyrepo.

### Affected graph

Every modern monorepo tool computes an **affected graph**: given a set of changed files, which packages are impacted directly and transitively? Only those get rebuilt, tested, and deployed.

Turborepo:
```bash
turbo run build test lint --filter="...[origin/main]"
# "...[X]" = changed since X AND everything that depends on them
```

Nx:
```bash
nx affected -t build test lint --base=origin/main
```

Use this in CI. The difference: a typo in a single package rebuilds 1 package instead of 200.

### Remote caching

Local incrementality is step 1; **shared remote cache** is step 2.

- **Turborepo Remote Cache** — Vercel-hosted or self-hosted (MinIO / S3).
- **Nx Cloud** — hosted; alternatives exist.
- **Bazel Remote Cache** — many implementations.

The win: CI, local developers, and other developers share artifacts. A test that passed on PR #1234 does not need to re-run on a different developer's machine — the cache hit is instant.

Setup invariants:
- **Cache keys include all inputs**. If an input is missed, the cache is unsafe (stale artifacts ship).
- **Cache is read-only for PR builds**; only trusted main-branch builds write.
- **Cache content is signed** in hostile-network environments.

## Package boundaries — enforce them

In a monorepo it is trivially easy for `apps/api` to import `apps/web/internal/utils` — everything is on disk together. This destroys the point of package boundaries.

### JS/TS

- **`eslint-plugin-boundaries`** or **`eslint-plugin-import`** with `no-restricted-paths` — enforce that package A cannot import from package B.
- **`dependency-cruiser`** — rule-based graph checker, runs in CI.
- **Nx tags + `@nx/enforce-module-boundaries`** — built-in for Nx.
- **TypeScript path mapping** — only expose the public entry of a package (`@acme/ui` → `packages/ui/src/index.ts`), not internal paths.

### Python

- [`deptry`](https://github.com/fpgmaas/deptry) / [`import-linter`](https://import-linter.readthedocs.io/) — enforce layered architecture.
- `pyproject.toml` `packages` field defines public surface.

### Go

- Package visibility enforced at language level (`internal/`).
- [`go-arch-lint`](https://github.com/fe3dback/go-arch-lint) for declarative rules.

### Rust

- Language-level module visibility (`pub(crate)`, `pub(super)`).
- Crate-level API is already explicit via `Cargo.toml` exports.

**Rule of thumb**: if a new cross-package import lands, it should require a reviewer with ownership on both sides. Codify this via **CODEOWNERS** at path level.

## CODEOWNERS — ownership without meetings

```
# CODEOWNERS at repo root
/packages/ui/          @org/design-system
/packages/billing/     @org/payments-team
/apps/web/             @org/web-team
/apps/api/             @org/platform-team
/tools/                @org/devex
/infra/                @org/sre

# Critical: anything in CI / build tooling
/.github/              @org/devex
/turbo.json            @org/devex
/pnpm-workspace.yaml   @org/devex
```

Required reviewers from CODEOWNERS. A PR crossing boundaries needs both owners.

## Dependency hygiene

### One version of each external dep

Two versions of React, three versions of lodash — painful. Enforce **single version policy** with:

- [`syncpack`](https://github.com/JamieMason/syncpack) for JS/TS — lint `package.json` versions, fix mismatches.
- `resolutions` field in root `package.json` for pnpm / yarn.
- Workspace-level dep in Cargo workspaces.
- `constraints.pro` in Yarn Berry for constraint-based checks.

### Internal dependencies via workspace protocol

In a pnpm workspace, reference internal packages with `workspace:*`:

```json
{
  "dependencies": {
    "@acme/ui": "workspace:*",
    "@acme/utils": "workspace:^1.0.0"
  }
}
```

`workspace:*` resolves to the local package. On publish, it gets replaced with the actual version. Never use `file:../packages/ui` — broken cache keys.

## Versioning and release

Two main strategies:

### Fixed versioning (lerna publish --fixed)

All packages share a version. Every release bumps everyone. Simple but wasteful — a patch to `@acme/utils` forces `@acme/api` to bump.

### Independent versioning (recommended)

Each package has its own version. Bump only what changed.

- **Changesets** (`@changesets/cli`) — the modern default for JS/TS. Each PR includes a `.changeset/*.md` declaring bump type and summary. On release, all pending changesets are consumed into a version bump + CHANGELOG.
- **Nx Release** — Nx's built-in orchestrator.
- **Release Please** — Google's automation; cross-language.

Workflow (Changesets example):
1. PR author runs `pnpm changeset` → creates a markdown file with bump type + notes.
2. PR lands with the changeset file.
3. "Release" PR is auto-generated when changesets accumulate, bumping versions and consolidating CHANGELOGs.
4. Merging the Release PR publishes to the registry and tags.

## Caching in CI

Without a remote cache, monorepo CI is still slow. Setup:

### GitHub Actions

```yaml
- uses: pnpm/action-setup@...
- uses: actions/setup-node@...
  with:
    node-version-file: .nvmrc
    cache: pnpm

- name: Restore Turborepo cache
  uses: actions/cache@...
  with:
    path: .turbo
    key: turbo-${{ runner.os }}-${{ github.sha }}
    restore-keys: |
      turbo-${{ runner.os }}-

- name: Run affected tasks
  run: pnpm turbo run build test lint --filter="...[origin/main]"
```

Prefer Turborepo Remote Cache for real leverage — local runners share with CI.

### GitLab CI

Same shape with `cache:` blocks keyed by lockfile + workspace config. See [`gitlab-ci-workflows`](../gitlab-ci-workflows).

## Task definitions — make them stable

Most monorepos have a dozen scripts: `build`, `test`, `lint`, `typecheck`, `e2e`, `dev`, `preview`, ...

Rules:
- **Every script is defined in `package.json` of the owning package.** Root scripts delegate to the task runner.
- **Every script has the same name across packages** — `pnpm build`, `pnpm test`, `pnpm lint` work in any package.
- **The task runner (Turbo / Nx) calls these scripts**, not custom shell.
- **Never embed complex shell in the task runner config**. If `build` needs 6 steps, write a `build` script; keep the runner config declarative.

## Dev loop

- **`turbo dev`** / **`nx run-many -t dev`** to run multiple packages in watch mode simultaneously.
- Hot-reload across packages: ensure TypeScript project references or paths are configured so package boundaries do not require rebuild on every change.
- **Don't `pnpm install` per package** — workspace install is at the root.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Monorepo without a task runner | Every push rebuilds everything |
| No remote cache | CI is slow; devs re-run everything locally |
| `pnpm install` per package | Breaks workspace resolution; slow |
| No ESLint / boundary rules | `apps/api` imports `apps/web/internal` silently |
| Shared `tsconfig.json` with `"paths"` pointing everywhere | Circular deps; cold builds |
| Fixed versioning with 100 packages | Every patch re-releases everyone |
| No CODEOWNERS | Refactors cross boundaries without the owner approving |
| Three versions of React in the repo | Diamond dependency → runtime bugs |
| CI runs ALL tests on every PR | Feedback loop dies; people merge without waiting |
| Config sprawl — each package has its own `eslint`, `tsconfig`, `prettier` | Config drift; inconsistent style |
| Going too far with Bazel | Config complexity crushes a small team |
| `file:../../packages/utils` paths | Breaks caching |
| Dev-only `turbo.json` at a sub-package | Task runner config should be at root |
| Scripts that shell out to `turbo` inside other scripts | Recursive runner; wasted work |
| No ADR for the monorepo decision | A year later nobody remembers why |

## Migrating from polyrepo

Minimum viable migration steps:

1. **Single source repo** — merge repos with `git subtree` or `git-filter-repo` to preserve history.
2. **Choose a task runner** — Turborepo for small / medium, Nx for larger / JS-heavy, Bazel only for very large polyglot.
3. **Workspace layout** — `apps/`, `packages/`, `tools/`. Pick conventions and enforce.
4. **One package manager** — pnpm strongly preferred over npm / yarn classic in 2025.
5. **Shared tsconfig / eslint / prettier** at root; packages extend.
6. **CODEOWNERS** + boundary lint rules.
7. **CI uses affected-graph + remote cache** from day one.
8. **ADR** documenting the decision and the cost model.

First PR to land after migration: add a new shared package exercised by at least two apps, to prove the wiring.

## Observability for a monorepo

Unusual but relevant:
- Track **build time per task per package** over time — regressions compound.
- Track **cache hit rate** — falling hit rate means someone broke a cache key.
- Track **PR CI time p50 / p95** — the core developer-productivity SLI.
- Alert on **"build takes > N minutes"** — something regressed.

See [`observability`](../observability) for SLO patterns; same logic applies to devex.

## Interaction with other skills

- [`architecture-decision-records`](../architecture-decision-records) — monorepo vs polyrepo decision warrants an ADR.
- [`project-rules-file`](../project-rules-file) — the rules file captures workspace layout, task names, owner tags.
- [`github-actions-workflows`](../github-actions-workflows) / [`gitlab-ci-workflows`](../gitlab-ci-workflows) — affected-graph + cache setup lives in these workflows.
- [`code-review`](../code-review) — CODEOWNERS + boundary rules are review-time enforcement.
- [`incremental-implementation`](../incremental-implementation) — a slice can span packages; the task runner runs the affected graph.
- [`setup-pre-commit`](../setup-pre-commit) — pre-commit hooks for syncpack, boundary rules, changeset-present check.
- [`performance-optimization`](../performance-optimization) — CI and dev-loop performance is a first-class problem.
- [`docs-verified-coding`](../docs-verified-coding) — task runner + package manager syntax change across major versions; pin and cite docs.

## Verification checklist

Setup:

- [ ] Task runner chosen (Turborepo / Nx / Bazel / Moon) and config at root only.
- [ ] Package manager with native workspace support (pnpm / Yarn Berry / uv / Cargo workspaces).
- [ ] `apps/*` and `packages/*` layout or equivalent.
- [ ] Shared `tsconfig` / `eslint` / `prettier` / formatter at root, extended per package.
- [ ] `turbo.json` / equivalent has inputs + outputs declared per task.
- [ ] Remote cache configured (Turborepo Remote Cache / Nx Cloud / Bazel cache).
- [ ] CODEOWNERS file covers every workspace path.
- [ ] Boundary lint rule (`dependency-cruiser` / `@nx/enforce-module-boundaries` / `eslint-plugin-boundaries` / language equivalent).
- [ ] `syncpack` / workspace deps ensure single version policy.
- [ ] Changeset or equivalent versioning tool configured.
- [ ] ADR documents the choice.

Operating:

- [ ] CI runs only affected packages on PRs (`--filter="...[origin/main]"` / `nx affected`).
- [ ] CI PR time p50 < 10 minutes; p95 < 20 minutes.
- [ ] Cache hit rate tracked and > 70% for main-branch CI.
- [ ] Boundary lint rules fail PRs that violate ownership.
- [ ] Root `package.json` scripts delegate; no business logic there.
- [ ] Every package has the same canonical scripts (`build`, `test`, `lint`, `typecheck`).
- [ ] No `file:../` path inside `dependencies` (use workspace protocol instead).
