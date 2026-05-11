---
name: executing-plans
description: Execute an approved implementation plan in controlled batches with checkpoints. Use WHENEVER (1) the user says to implement an existing plan; (2) a docs/plans/* plan, task list, spec, or ticket breakdown already exists; (3) work should proceed task-by-task instead of improvising; (4) the user says "go", "execute the plan", "work through these tasks", or "continue from Task N"; (5) multiple implementation tasks need verification and status tracking. Enforces plan adherence, TDD, small batches, and human checkpoints.
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

If the plan has placeholders, missing verification, or unclear dependencies, ask for correction before coding.

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
6. **Verify** — run the exact commands from the plan.
7. **Report** — status, evidence, files changed, next task.

Do not start the next task while the current task is red.

## Handling plan drift

Plans are hypotheses. Code can prove them wrong.

Stop and ask when:

- A task requires files not mentioned by the plan.
- The plan's API or symbol does not exist.
- The task is much larger than expected.
- Acceptance criteria conflict with existing behavior.
- Verification commands are missing or fail for unrelated reasons.

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

If commits are part of the workflow, commit only when the user requested commits. Follow `git-hygiene`.

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
