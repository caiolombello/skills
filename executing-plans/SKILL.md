---
name: executing-plans
description: "Use when executing an approved plan. Verify scoped increments, diagnose routine obstacles, and stop at the authorized endpoint without expanding scope."
---

<!-- Inspired by obra/superpowers executing-plans (MIT). See ../CREDITS.md -->

# Executing Plans

Execute an approved plan without drifting. A plan is a contract: it captures scope, order, acceptance criteria, and verification. Your job during execution is to complete the next small slice, prove it works, report status, and only then continue.

Pair with `incremental-implementation`, `test-driven-development`, and `git-hygiene`.

## When to use

- A plan file or task breakdown already exists.
- The user explicitly says to execute a plan.
- Work contains several tasks that can be checked off.
- The user wants progress without re-designing.

## When not to use

- No plan exists and requirements are vague — use `spec-first-planning` first.
- The task is a single small edit.
- A live incident is active.
- The plan is obviously stale or conflicts with the codebase — stop and surface the conflict.

## Start by loading the plan

Read the approved plan and extract:

- Goal and non-goals.
- Task list and dependencies.
- Acceptance criteria.
- Verification commands.
- Files likely touched.
- Any human checkpoints.

Then summarize:

```markdown
PLAN LOADED
- Source: <path or ticket>
- Next task: <Task N>
- Verification: <commands>
- Checkpoint cadence: <after each task / after batch>
```

Resolve routine missing commands/dependencies through the repository and current sources before asking. Ask when an essential decision, explicit boundary, or acceptance criterion remains unresolved. Do not invent requirements or stop for a confirmation already given.

## Batch size

Default: one task per batch.

Only group tasks when they are tiny, tightly coupled, and verified by the same test. Never group tasks that touch unrelated areas.

Good batch:

- Add failing test for parser edge case.
- Fix parser edge case.
- Run parser tests.

Bad batch:

- Add API endpoint, refactor auth, update deployment config, and rewrite docs.

## Execution loop

For each task or batch:

1. **Restate scope** — what will change and what will not.
2. **Investigate** — read relevant files and nearest examples.
3. **Red** — write or identify the failing test first when behavior changes.
4. **Green** — implement the minimum code.
5. **Refactor** — simplify only within the touched scope.
6. **Verify** — run applicable plan commands; diagnose environment failures and record unavailable checks. Use a useful bounded substitute where appropriate without pretending it replaces a required gate.
7. **Report** — status, evidence, files changed, next task.

Do not start the next task while the current task is red.

## Handling plan drift

Plans are hypotheses. Code can prove them wrong.

Investigate and surface drift before expanding scope. Ask when a material decision or authorization is actually missing, such as:

- A required change crosses an explicit protected-file/scope boundary.
- A missing API or dependency requires a different approach with unresolved trade-offs.
- Work materially exceeds the approved scope or resources.
- Acceptance criteria conflict with verified behavior and no applicable instruction resolves it.

An unlisted dependency file needed within the approved scope, or a recoverable environment failure, is not automatically a new approval gate. Diagnose first. Continue independent safe work when possible, and keep required unavailable gates unresolved. Never silently weaken acceptance criteria.

Use this format:

```markdown
PLAN CONFLICT
- Task: <Task N>
- Expected by plan: <X>
- Found in code: <Y>
- Options:
  A) Adjust plan to <...>
  B) Keep plan and add compatibility layer <...>
  C) Pause for human decision
```

## Checkpoint report

After each batch, report concisely:

```markdown
Batch complete: <Task N title>

Changed:
- <file>: <why>

Verified:
- `<command>`: pass

Remaining:
- Task N+1: <title>

Proceeding unless you redirect.
```

If commits are part of the workflow, commit only when authorized. Follow `git-hygiene` and preserve authorization already established. Implemented, verified, committed, published, monitored, merged, and deployed are separate states; stop at the requested endpoint without automatically taking the next one.

## Completion

When all tasks are done, switch to `verification-before-completion` and `finishing-a-development-branch` before declaring success.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Re-planning while executing | Scope drift disguised as productivity |
| Skipping tests until the end | Late failures are hard to localize |
| Continuing after a red task | Builds on broken ground |
| Quietly changing acceptance criteria | Breaks trust in the plan |
| Batch too large | Unreviewable and hard to recover |

## Verification checklist

- [ ] The plan source and next task are identified.
- [ ] The current task's scope is restated before editing.
- [ ] Behavior changes follow red-green-refactor.
- [ ] Verification commands are run per task or batch.
- [ ] Plan conflicts are surfaced, not silently resolved.
- [ ] Progress is reported with evidence.
