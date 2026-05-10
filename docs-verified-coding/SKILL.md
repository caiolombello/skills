---
name: docs-verified-coding
description: Ground every framework-specific code decision in official, version-matched documentation. Fetch the docs for the feature you are about to write — do not implement from memory. Use WHENEVER the agent is about to (1) write framework- or library-specific code (React hooks, Django views, Rails controllers, Spring annotations, Terraform resources, Kubernetes APIs, SDK calls); (2) introduce a pattern that will be copied across the codebase (auth, routing, data fetching, forms, state); (3) the user asks for "current best practice", "the right way", "modern pattern", "up-to-date"; (4) working with a library the user names explicitly; (5) editing code that already uses version-sensitive APIs. Training data is stale; APIs get deprecated; best practices change between minor versions. The skill enforces detect-version → fetch-docs → implement-as-documented → cite-source.
---

<!-- Inspired by addyosmani/agent-skills source-driven-development (MIT). See ../CREDITS.md -->

# Docs-Verified Coding

Every framework- or library-specific decision must be backed by **official, version-matched documentation**. Do not implement from memory. Verify, cite, and let the user see the source.

Training data goes stale. APIs get deprecated. Best practices evolve between minor versions. This skill ensures the code you ship traces back to an authoritative source the user can click on and check.

## When to use

- The user wants code that follows current best practices for a given framework or library.
- Building boilerplate, starter code, or a pattern that will be copied across the project.
- The user explicitly asks for "documented", "verified", "correct", "modern", "up-to-date" implementation.
- Implementing features where the framework's recommended approach matters — auth, routing, data fetching, forms, state, error boundaries.
- Calling a library API the agent has not verified.
- Reviewing or improving code that uses version-sensitive patterns.

### When NOT to use

- Correctness does not depend on version (rename variable, fix typo, move file).
- Pure logic that works across all versions (loops, conditionals, data structure operations).
- The user explicitly trades verification for speed ("just do it quickly").
- Code you already verified earlier in this same session against the same version.

## The process

```
DETECT ──→ FETCH ──→ IMPLEMENT ──→ CITE
  │         │           │            │
  ▼         ▼           ▼            ▼
 stack +   the exact  match the   show the
 versions  relevant   documented  URL and
           page       pattern     version
```

### Step 1: Detect stack and versions

Read the dependency manifest. Specific versions, not "latest".

| File | Typical stacks |
|------|---------------|
| `package.json` + lockfile | Node, React, Vue, Angular, Svelte, Next.js, TypeScript |
| `pyproject.toml` / `requirements.txt` / `uv.lock` / `poetry.lock` | Python, Django, Flask, FastAPI |
| `go.mod` | Go |
| `Cargo.toml` + `Cargo.lock` | Rust |
| `Gemfile` + `Gemfile.lock` | Ruby, Rails |
| `composer.json` + `composer.lock` | PHP, Symfony, Laravel |
| `pom.xml` / `build.gradle` | Java, Spring, Kotlin |
| `*.csproj` / `packages.lock.json` | C#, .NET |
| `Podfile.lock` / `Package.resolved` | iOS, Swift |
| `terraform.lock.hcl` + `versions.tf` | Terraform providers |

State what you found:

```
STACK DETECTED:
- React 19.1.0 (package.json + lockfile)
- Next.js 15.2.0 (App Router)
- Tailwind CSS 4.0.3
- TypeScript 5.6 (strict)
Fetching docs for: App Router server actions + React 19 form state.
```

If the version is missing or ambiguous, **ask** — do not guess. The version determines which patterns are correct.

For indirect dependencies (the function you are calling belongs to a transitive library), check the lockfile for the actual resolved version before fetching docs.

### Step 2: Fetch the right page

Fetch the **specific page** for the feature. Not the homepage, not the whole docs site — the one page that answers the question.

**Source hierarchy (most authoritative first):**

| Priority | Source | Examples |
|----------|--------|----------|
| 1 | Official API reference / docs for the pinned version | `react.dev/reference`, `docs.djangoproject.com/en/5.1`, `nextjs.org/docs/app` |
| 2 | Official migration guide for that version | "Upgrading to v5", release blog post |
| 3 | Official changelog / release notes | `CHANGELOG.md` in the upstream repo |
| 4 | Web-standards references | MDN, `web.dev`, `html.spec.whatwg.org` |
| 5 | Runtime / browser compatibility tables | `caniuse.com`, `node.green` |

**Not authoritative — never cite as the primary source:**

- Stack Overflow answers.
- Blog posts and tutorials (even popular ones).
- AI-generated summaries or wrapped docs.
- Your own training data — the whole point is to verify it.
- READMEs of **example** projects on GitHub.

**Be precise:**

| Bad | Good |
|-----|------|
| Fetch the React homepage | Fetch `react.dev/reference/react/useActionState` |
| Search "django auth best practices" | Fetch `docs.djangoproject.com/en/5.1/topics/auth/` |
| Read the Kubernetes docs | Fetch `kubernetes.io/docs/concepts/workloads/controllers/deployment/` for v1.29 |

**Version-matching the docs URL:**

Most official doc sites version their URLs — use the version that matches the lockfile. `docs.djangoproject.com/en/5.1/` not `/en/dev/`. `kubernetes.io/docs/concepts/…` implicitly "latest" — switch to the correct release if an older one is pinned.

If the doc site does not version, fetch release notes for the pinned version to confirm the API has not changed since.

### Step 3: Extract patterns and deprecations

After fetching:

- Identify the **documented pattern** for the feature.
- Note any **deprecation warnings** or "since vX, prefer Y".
- Flag any **version-specific conditionals** (e.g. "required in v6+").
- If two official pages conflict (migration guide contradicts API reference), surface the discrepancy to the user.

### Step 4: Implement as documented

- Use the API signatures **from the docs**, not from memory.
- If the docs show a new way to do something, use the new way.
- If the docs mark a pattern deprecated, do not use it.
- If the docs do not cover your case, **flag it as unverified** — do not silently fall back to memory.

### Conflict with existing code

When the documented pattern contradicts the project's existing pattern, do **not** silently pick one:

```
CONFLICT DETECTED:
- Project uses useState + useEffect for form submission state.
- React 19 docs recommend useActionState for this exact pattern.
  (Source: https://react.dev/reference/react/useActionState)

Options:
A) Modern pattern (useActionState) — consistent with current docs.
B) Match existing code (useState) — consistent with codebase style.
→ Which do you prefer?
```

Either is defensible. The wrong answer is picking silently.

### Step 5: Cite the source

Every non-trivial decision comes with a citation. The user should be able to click and verify.

Format:

```
Pattern: Server Action with form state
Source:  https://react.dev/reference/react/useActionState (React 19.1)

<code goes here>
```

For IaC / infra code, cite the provider doc for the exact provider version:

```
Resource: aws_s3_bucket_server_side_encryption_configuration
Source:   registry.terraform.io/providers/hashicorp/aws/5.83.0/docs/resources/s3_bucket_server_side_encryption_configuration
```

If you had to combine multiple sources, list each one.

## MCP / doc-fetch tooling

Many agents ship with tools that make this fast:

- **Context7** — autofetches library docs for the version referenced by the lockfile. If installed, prefer it over manual fetching.
- **WebFetch** / built-in doc fetchers — work fine if the URL is specific.
- **GitHub source** — for small libraries without dedicated doc sites, fetching the source file at the exact tag works.

If no doc-fetch tool is available, use `curl` to pull the page content, or ask the user to paste it.

## When docs disagree with the runtime

Occasionally the docs describe an API that does not behave as documented in the installed version. If you have a working feedback loop (see `diagnose`):

1. Write a minimal repro that exercises the documented pattern.
2. Run it against the pinned version.
3. If the docs are wrong, prefer what the runtime does; note the discrepancy in the commit message.

This is rare. When it happens, file an issue upstream so the docs get fixed.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|-------------|
| "React has always done it this way" | Training data does not know about v19, v20, v21 |
| Fetch the homepage or generic "getting started" | Irrelevant to the specific API call |
| Use a Stack Overflow snippet from 2019 as the source | High chance it calls deprecated APIs |
| Copy from a blog post without version matching | Tutorial was for v17; you are on v19 |
| Generate plausible API signatures from memory | This is literally how hallucinated APIs ship |
| Cite "the docs" without a URL | Unverifiable |
| Skip citation because "I remember this well" | Confidence ≠ correctness |

## Interaction with other skills

- `investigate-before-editing` — read the project's existing code first; docs tell you what the library supports, the repo tells you which subset the project uses.
- `llm-coding-discipline` — "verify don't assume", "surface assumptions". Docs-verified coding is the concrete form of "verify".
- `code-review` — reviewers can check citations. PR descriptions should link the doc for version-sensitive decisions.
- `diagnose` — if doc-pattern disagrees with runtime, drop into diagnosis.
- `terraform-iac-expert` — same discipline for provider docs: pin provider version, fetch the provider registry page for the resource.

## Verification checklist

Before using a framework-specific pattern:

- [ ] I identified the exact version from the lockfile (not "the latest").
- [ ] I fetched the specific doc page for the feature (not the homepage).
- [ ] The doc URL version matches the project version (or is verified unchanged via changelog).
- [ ] I noted any deprecation warnings or "prefer X since vY" hints.
- [ ] The code uses the API signature shown in the docs, not from memory.
- [ ] Citations are inline in the PR description or commit body with clickable URLs.
- [ ] If docs conflict with existing project code, I surfaced the conflict to the user rather than silently picking.
- [ ] If a pattern is unverifiable from docs, I flagged it as unverified rather than guessing.
