---
name: incremental-implementation
description: Build features in thin vertical slices — implement one piece, test it, verify it, commit, then expand. Do not implement an entire feature in one pass. Use WHENEVER (1) a change will touch more than one file; (2) the agent is about to write more than ~100 lines before testing; (3) the task is a new feature, migration, or refactor with multiple steps; (4) the user asks for "build", "implement", or "add" something non-trivial; (5) a task feels too big to land in one step. Each increment leaves the system in a working, testable state. This is the execution discipline that makes large features manageable and prevents the "1000-line PR that almost works" failure mode.
---

<!-- Inspired by addyosmani/agent-skills incremental-implementation (MIT) and mattpocock/skills engineering/tdd tracer-bullet principle (MIT). See ../CREDITS.md -->

# Incremental Implementation

Build in thin vertical slices. Implement one piece, test it, verify it, commit it, then expand. Avoid implementing an entire feature in one pass.

Each increment must leave the system in a **working, testable state**. Broken-for-hours branches turn into broken-for-days branches.

## When to use

- Any multi-file change.
- Building a new feature from a task breakdown.
- Refactoring existing code.
- Whenever you are tempted to write more than ~100 lines before running a test.

### When NOT to use

- Single-file, single-function change where scope is already minimal.
- Automated refactor (rename, codemod) applied atomically.
- Pure configuration or doc change.

## The cycle

```
Implement ──▶ Test ──▶ Verify ──▶ Commit ──▶ Next slice
    ▲                                           │
    └───────────────────────────────────────────┘
```

For each slice:

1. **Implement** the smallest complete piece of functionality.
2. **Test** — run the existing suite, or write a test if none applies yet. See [`test-driven-development`](../test-driven-development).
3. **Verify** — tests pass, build succeeds, typecheck clean, manual check if UI.
4. **Commit** — descriptive message (see [`git-hygiene`](../git-hygiene) for Conventional Commits).
5. **Next slice** — carry forward; do not restart.

**Never stack new work on a failing slice.** Red means stop, fix, then proceed.

## Slicing strategies

### Vertical slices (preferred)

Build one complete path through the stack per slice. Each slice delivers working end-to-end functionality.

```
Slice 1: Create a task (DB + API + minimal UI)
   → tests pass; user can create a task via UI.

Slice 2: List tasks (query + API + UI)
   → tests pass; user can see their tasks.

Slice 3: Edit a task (update + API + UI)
   → tests pass; user can modify.

Slice 4: Delete a task (delete + API + UI + confirmation)
   → full CRUD complete.
```

Preferred over horizontal slicing because each merged slice is demoable and usable.

### Contract-first slicing

When backend and frontend develop in parallel:

```
Slice 0: Define the API contract (types, OpenAPI, GraphQL schema).
Slice 1a: Backend implements against the contract + tests.
Slice 1b: Frontend implements against a mock matching the contract.
Slice 2:  Integrate and test end-to-end.
```

Lock the contract in writing. Divergence between Slice 1a and 1b is the most common integration pain.

### Risk-first slicing

Tackle the uncertain piece first. If it does not pan out, you have wasted one slice — not the whole project.

```
Slice 1: Prove the third-party API rate limit is acceptable.
Slice 2: Prove the new algorithm handles our worst-case input.
Slice 3: Build the easy CRUD around the validated core.
```

### Horizontal slicing (use sparingly)

Only justifiable when a whole layer genuinely blocks all vertical slices (e.g. you must introduce a new persistence layer). Even then, prefer to ship the layer with one vertical slice that exercises it.

### The tracer bullet

The first slice should be the **tracer** — a minimal end-to-end path that proves the wiring works. Interface, routing, data layer, test runner, CI, deploy. Everything else is filling in what the tracer traced.

If you spent two hours and the tracer is not demoable, the approach is wrong — stop and re-plan.

## Slice sizing

| Size | Lines changed | Guidance |
|------|---------------|----------|
| Ideal | 50-200 | Reviewable in one sitting, commits in one go |
| Acceptable | 200-400 | Still OK if a single logical change |
| Too big | 400+ | Decompose further; slice again |

Rule: if you cannot describe the slice in one imperative sentence ("Add the create-task endpoint + happy-path test"), it is too big.

## When a slice explodes mid-flight

You picked a slice, started implementing, and discovered it depends on something not yet built. Options:

1. **Stop, pivot, pick a smaller slice first.** Preferred.
2. **Stub the missing piece** — return a hardcoded value, raise `NotImplementedError`, log-only behavior. Document the stub in the commit message and track the follow-up.
3. **Never**: silently expand the slice to "just include it too". That is how 1000-line PRs happen.

Two tactical stops and a re-plan is cheaper than one massive slice that turns into a two-day rebase.

## State between slices

Leave every slice in a state where:

- [ ] Tests pass.
- [ ] Build / typecheck clean.
- [ ] The main branch could deploy if necessary.
- [ ] No temporary `TODO: REMOVE` / `FIXME: stub` hidden in production paths (a stub is allowed if it fails loudly or is gated by a feature flag).

Commits between slices use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(tasks): add create-task endpoint and happy-path test
feat(tasks): add list-tasks endpoint (paginated)
feat(tasks): wire list-tasks into TaskList UI
test(tasks): cover empty-list and loading states
```

Each message describes **what changed and why** — future you / reviewers / bisect will thank you.

## Pair with a task breakdown

Before starting the slicing loop, produce a task list. Each item should map to one slice.

- The [`project-rules-file`](../project-rules-file) rules should already define commands; run them per slice.
- If no task list exists yet, pause and write one. One-line-per-slice is enough.

Example:

```
TASKS (tracer-first)
[ ] 1. Tracer: empty /tasks route renders "No tasks" (RSC + test).
[ ] 2. DB: tasks table migration + Prisma model.
[ ] 3. API: POST /tasks (auth, validation, 201 + row).
[ ] 4. API: GET /tasks (paginated, ownership-scoped).
[ ] 5. UI: NewTaskForm (happy path).
[ ] 6. UI: TaskList renders real data.
[ ] 7. UI: edit + delete.
[ ] 8. Nice-to-have: optimistic updates.
```

Work top-down. Tick as you commit each slice. Revise the list when you learn something mid-flight — plans are hypotheses.

## Using a todo list

If your agent has a `TodoWrite`-style tool, use it:

- One todo per slice. Mark `in_progress` when you start.
- Mark `completed` the moment the slice is committed. Do not batch completions.
- Add new todos if the current slice surfaces follow-ups.
- Do not flip multiple todos `in_progress` at once.

The todo list is the shared record of where you are — both for you and for any future session that picks this up.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|-------------|
| "Let me implement the whole feature then test" | 60% done with no signal whether any of it works |
| Horizontal slicing by default | Every layer delayed until all layers land |
| Starting with the easy slice | Risk stays unknown; late surprises cost more |
| 800-line commit "initial implementation" | Unreviewable, unbisectable, unmergeable |
| Ignoring a red test to keep making progress | Compounds. Next slices are built on broken ground. |
| Committing stubs without markers | Ships placeholder behavior to prod |
| Abandoning a slice halfway to start another | Two half-finished slices are worse than one done |
| Not running the full suite between slices | Regression in slice 3 looks like a slice-7 bug |

## Interaction with other skills

- [`test-driven-development`](../test-driven-development) — each slice is one red → green cycle (or several).
- [`llm-coding-discipline`](../llm-coding-discipline) — "surgical changes", "verify don't assume" apply per slice.
- [`investigate-before-editing`](../investigate-before-editing) — read the files the slice will touch **before** starting the slice.
- [`git-hygiene`](../git-hygiene) — commit per slice, Conventional Commits, no drive-by refactors.
- [`diagnose`](../diagnose) — when a slice breaks, drop into diagnosis instead of layering more slices.
- [`code-review`](../code-review) — small slices = reviewable PRs; 400+ line slices are the reviewer's nightmare.

## Verification checklist

Per slice:

- [ ] Slice is describable in one imperative sentence.
- [ ] Slice is under ~200 lines changed (or a single logical unit).
- [ ] Tests pass locally.
- [ ] Build / typecheck / lint clean.
- [ ] No speculative code beyond what this slice needs.
- [ ] Commit message uses Conventional Commits and states **why** when non-obvious.
- [ ] The todo list / task list is updated.
- [ ] No broken state is being pushed (main would still deploy).
- [ ] Any stubs are clearly marked (`TODO:`, feature-flagged, or loudly fail).
