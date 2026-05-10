---
name: code-review
description: Multi-axis code review across correctness, readability, architecture, security, and performance. Use BEFORE merging any change, WHENEVER (1) a PR / MR / CR is opened or updated; (2) the user asks to review code — theirs, another agent's output, or a teammate's; (3) an agent has just finished writing a non-trivial change and is about to declare done; (4) the user mentions "review", "PR review", "sanity check this", "look for issues"; (5) a bug fix lands — review both the fix and the regression test; (6) inherited legacy code needs an audit pass. The review standard is "does this definitely improve code health" — not perfection. Applies to any language and stack.
---

<!-- Inspired by addyosmani/agent-skills code-review-and-quality (MIT). See ../CREDITS.md -->

# Code Review

Every non-trivial change gets reviewed before it merges. A review is not a verdict, it is a structured second look across five axes: **correctness, readability, architecture, security, performance**.

## The approval standard

Approve a change when it **definitely improves overall code health**, even if it is not perfect. Perfect code does not exist — the goal is continuous improvement.

- Do not block because "it is not how I would have written it".
- Do not chase stylistic nits the formatter / linter can enforce automatically.
- Do block on correctness regressions, security holes, and violated project conventions.

## The five axes

Evaluate every change across all five. Score each axis as `pass` / `comment` / `block`.

### 1. Correctness

Does the code do what it claims?

- Does it match the spec, task, or issue?
- Are edge cases handled — `null`, empty inputs, zero, negatives, boundary values?
- Are error paths handled, not just the happy path?
- Do tests exist? Do they actually exercise the change?
- Any off-by-one, race condition, or state inconsistency?
- Does it work with the data that exists in production, not just in the unit test?

### 2. Readability & simplicity

Can another engineer (or future agent) read this without an explanation?

- Are names descriptive and consistent with the project? No `tmp`, `data`, `result` without context.
- Is control flow flat, not nested ternaries three deep?
- Is related code grouped? Are module boundaries clear?
- Is there "cleverness" that should be simplified?
- **Could this be done in fewer lines?** If it is 200 lines where 80 would suffice, push back.
- **Are abstractions earning their complexity?** Do not generalize until the third use case.
- Any dead code — `_unused` variables, `// removed` comments, backward-compat shims with no consumer?

### 3. Architecture

Does the change fit the system's design?

- Does it follow an existing pattern? If it introduces a new pattern, is that justified?
- Does it respect module boundaries, or does it reach across them?
- Any duplication that should be shared?
- Dependencies flowing in the right direction — no new cycles?
- Is the abstraction level appropriate — not over-engineered, not too tightly coupled?
- Does it break an existing invariant documented in the code or ADRs?

### 4. Security

Does the change introduce a vulnerability?

- User input validated and sanitized?
- Secrets kept out of code, logs, and commit history?
- Authn / authz checked on every new endpoint or sensitive path?
- SQL queries parameterized — no string concatenation?
- Outputs encoded for the sink (HTML, shell, URL, SQL)?
- External data (API responses, config files, user-uploaded files) treated as untrusted?
- New dependency from a trusted source with no known CVEs?
- Rate limiting / quotas on new public endpoints?

### 5. Performance

Does the change introduce a performance problem?

- Any N+1 queries?
- Unbounded loops, unconstrained data fetching, missing pagination?
- Synchronous operations that should be async?
- Large objects created in hot paths, or inside render loops?
- UI: unnecessary re-renders, missing memoization only where measured?
- Database: missing index on a new `WHERE` or `ORDER BY` column?

Do not optimize speculatively — but do not merge a change that measurably regresses a hot path either. Ask for a benchmark if unsure.

## Change sizing

Small, focused changes are easier to review, faster to merge, safer to deploy.

```
~100 lines    → Good. Reviewable in one sitting.
~300 lines    → Acceptable if it is a single logical change.
~1000 lines   → Too large. Split it.
```

"One change" = a single self-contained modification that addresses one thing, includes related tests, and keeps the system functional after it lands. One part of a feature, not the whole feature.

### Split strategies when a change is too big

| Strategy | How | When |
|----------|-----|------|
| Stack | Submit a small change, open the next one on top | Sequential dependencies |
| By file group | Separate changes for groups needing different reviewers | Cross-cutting concerns |
| Horizontal | Land shared code / stubs first, then consumers | Layered architecture |
| Vertical | Break into smaller full-stack slices | Feature work |

Exceptions where large changes are acceptable:
- Complete file deletions.
- Automated refactors (rename, codemod) where the reviewer verifies intent, not every line.

**Separate refactoring from feature work.** A change that refactors existing code *and* adds new behavior is two changes. Small cleanups (rename a variable) can be folded at reviewer discretion.

## Change description

Every change needs a description that stands alone in version control history.

- **First line**: short, imperative, standalone. "Add rate limiter to /login" not "Added rate limiter to /login". Must be informative enough that someone searching history understands without reading the diff. Follow Conventional Commits if the project uses it: `feat(auth): add rate limiter to /login`.
- **Body**: what is changing and **why**. Context, decisions, reasoning not visible in the diff. Link issues, benchmarks, design docs. Acknowledge shortcomings when they exist.

Anti-patterns: "fix bug", "fix build", "add patch", "phase 1", "moving code from A to B".

## Review process

### 1. Understand the intent

Before reading code:
- What is the change trying to accomplish?
- What spec / issue / ticket does it implement?
- What behavior changes for users?

If the description does not answer this, ask for a better description before reviewing the diff.

### 2. Review the tests first

Tests reveal intent and coverage.

- [ ] Do tests exist for the change?
- [ ] Do they test behavior (public interface), not implementation details?
- [ ] Are edge cases covered?
- [ ] Are test names descriptive sentences?
- [ ] Would the tests catch a regression if the code silently broke?

A PR with no test for a behavioral change is a red flag. Either add the test, or justify the omission in the description.

### 3. Walk through each file with the five axes in mind

For each file touched:
1. **Correctness**: does this do what the test says it should?
2. **Readability**: can I understand this without help?
3. **Architecture**: does this fit the system?
4. **Security**: does this expose or protect a boundary?
5. **Performance**: any obvious regressions?

### 4. Consolidate findings

Group comments by severity:

| Severity | Meaning | Example |
|----------|---------|---------|
| `block` | Must change before merge | Correctness bug, security hole, violated convention |
| `comment` | Worth addressing, not a blocker | Naming, minor refactor, better test coverage |
| `nit` | Stylistic, author's choice | Prefer `const` vs `let` in a case where either works |
| `praise` | Worth calling out | Elegant solution, good test, clear naming |

Mark each comment with its severity. `nit:` and `praise:` prefixes help authors triage quickly.

### 5. Summarize

End the review with:
- Overall verdict: approve / request changes / comment only.
- Count by severity ("3 blocking, 5 comments, 2 nits, 1 praise").
- One-line summary of the change as you understood it — lets the author correct if you misread intent.

## Reviewing AI-generated code

Extra scrutiny. AI output is confident-looking even when wrong.

- **Invented APIs** — did the agent reference library functions that actually exist at the project's pinned version? Check imports and signatures.
- **Hallucinated files / paths** — do referenced files actually exist?
- **Copy-paste without adaptation** — is the code style consistent with the rest of the module?
- **Scope creep** — did the agent "improve" unrelated code? Call this out.
- **Missing tests** — AI frequently ships behavior without tests. Request them.
- **Over-abstraction** — generic helpers for single callers, classes where a function would do, premature interfaces.
- **Silent catches** — `try { … } catch {}` that swallows errors the human review would have flagged.

## Self-review before requesting review from others

Run this on your own PR before hitting "ready for review":

- [ ] Diff reads top-to-bottom? Am I proud of what another engineer will see?
- [ ] Every changed line traces to the task?
- [ ] Tests pass locally? Typecheck clean? Linter clean?
- [ ] Any `TODO`, `FIXME`, `console.log`, `print(...)`, `[DEBUG-...]` left?
- [ ] Description answers "what" and "why"?
- [ ] Screenshots / benchmarks attached for UI / perf changes?

Self-review catches 60-80% of what a human reviewer would.

## Anti-patterns for reviewers

- **Rubber stamp** — "LGTM" with no evidence you read the diff.
- **Nitpick storm** — 40 comments on style while missing a correctness bug.
- **Scope expansion** — "while you're in there, can you also refactor X?". Open a separate ticket.
- **Blocking on preference** — "I would have done it differently" is not a block unless it violates a project rule.
- **Ghost review** — requesting changes without saying what is wrong, or approving without reading.
- **Delayed review** — blocking a PR for days on non-blocking comments. Reply quickly; escalate blockers, let the rest land.

## Interaction with other skills

- `test-driven-development` — a PR with behavioral changes and no tests is a code-review red flag.
- `diagnose` — if review uncovers a bug, drop into diagnosis.
- `security-hardening` (if present) — deep dive for security-heavy PRs.
- `doubt-driven-review` — escalation for non-trivial decisions that need fresh-context adversarial scrutiny.
- `git-hygiene` — commit message quality is part of the review.
- `llm-coding-discipline` — "simplicity first", "surgical changes", "verify don't assume" are review invariants.

## Verification checklist

Before approving / merging:

- [ ] All five axes were evaluated (not just "it looks fine").
- [ ] Tests exist for behavioral changes and actually exercise the new behavior.
- [ ] The description answers what changed and why.
- [ ] No scope creep beyond the stated task.
- [ ] No secrets, debug artifacts, or commented-out blocks in the diff.
- [ ] CI is green (or failures are documented as environmental).
- [ ] For AI-generated code: imports / APIs were verified against the pinned library versions.
- [ ] Blocking comments have responses or fixes; non-blocking comments are either addressed or explicitly deferred.
