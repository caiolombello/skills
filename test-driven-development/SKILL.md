---
name: test-driven-development
description: Red-green-refactor with vertical slices. Write a failing test first, the minimum code to pass, then refactor with tests as the safety net. Use WHENEVER (1) implementing new business logic, a new API endpoint, or any behavior change; (2) fixing a bug — reproduce with a failing test before attempting a fix (the Prove-It pattern); (3) the user mentions TDD, red-green-refactor, "test first", or "write a test"; (4) modifying existing functionality where a regression would hurt; (5) the codebase has a test runner configured and the change is behavioral. Applies to any language with a test framework. Skip only for pure config/docs/static-content changes with no behavioral impact.
---

<!-- Inspired by mattpocock/skills engineering/tdd (MIT) and addyosmani/agent-skills test-driven-development (MIT). See ../CREDITS.md -->

# Test-Driven Development

Write the failing test before the code. Tests are **proof** — "seems right" is not done. A codebase with good tests is an AI agent's superpower; a codebase without them is a liability every change compounds.

## Philosophy

**Test behavior through public interfaces, not implementation details.**

- Good tests describe **what** the system does, not **how**. They read like a spec.
- Good tests survive refactors because they do not care about internal structure.
- Bad tests mock internal collaborators, poke private methods, or query state directly instead of going through the interface. Warning sign: the test breaks when you rename an internal function but behavior is unchanged.

If renaming a private helper breaks a test, that test is coupled to implementation. Fix the test (or delete it), not the rename.

## The cycle

```
    RED              GREEN             REFACTOR
 Write a test    Minimal code to      Clean up with
 that fails  ──→  make it pass  ──→    tests as net  ──→ (repeat)
     │                 │                    │
     ▼                 ▼                    ▼
  FAILS            PASSES              STILL PASSES
```

1. **RED** — write a test. Run it. It must fail. A test that passes on first run proves nothing.
2. **GREEN** — write the minimum code that makes it pass. No speculative features, no abstractions for a second caller that does not exist yet.
3. **REFACTOR** — improve the code. Run tests after each change. Never refactor while red.

**Never refactor while red.** Get to green first, then change the code structure with tests as your safety net.

## Anti-pattern: horizontal slicing

**Do NOT write all tests first, then all implementation.** This is horizontal slicing — treating RED as "write all tests" and GREEN as "write all code".

It produces crap tests:
- Tests written in bulk test **imagined** behavior, not **actual** behavior.
- You end up testing the **shape** of things (data structures, signatures) instead of user-facing behavior.
- Tests become insensitive to real changes — they pass when behavior breaks, fail when behavior is fine.
- You outrun your headlights, committing to test structure before understanding the implementation.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical — tracer bullets):
  RED→GREEN: test1 → impl1
  RED→GREEN: test2 → impl2
  RED→GREEN: test3 → impl3
```

Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

## The Prove-It pattern (bug fixes)

When a bug report arrives, **do not start by fixing it**. Start by reproducing it with a test.

```
Bug report
     │
     ▼
Write a test that demonstrates the bug
     │
     ▼
Test FAILS (bug confirmed)
     │
     ▼
Implement the fix
     │
     ▼
Test PASSES (fix proven)
     │
     ▼
Run full suite (no regressions)
```

Example:

```typescript
// Bug: "Completing a task doesn't update completedAt"

// 1. Reproduction test — must FAIL
it('sets completedAt when a task is completed', async () => {
  const task = await taskService.createTask({ title: 'Test' });
  const done = await taskService.completeTask(task.id);

  expect(done.status).toBe('completed');
  expect(done.completedAt).toBeInstanceOf(Date); // ← fails, bug confirmed
});

// 2. Minimal fix
export async function completeTask(id: string) {
  return db.tasks.update(id, {
    status: 'completed',
    completedAt: new Date(), // ← was missing
  });
}

// 3. Test passes → fix proven, regression guarded
```

Without the reproduction test you cannot prove the fix worked and cannot prevent the bug from returning. **Skipping this step is a false economy.**

## Workflow

### 1. Plan (5 minutes)

Before writing any test:

- [ ] Confirm **which behaviors** matter most. You cannot test everything — pick the critical paths and the hard logic.
- [ ] Sketch the **public interface** (function signature, endpoint shape, event payload). Design for testability: pure functions and dependency injection beat deep mocking every time.
- [ ] List behaviors as **observable outcomes**, not implementation steps.
- [ ] Agree the plan with the user if the interface is new.

Question to ask: *"What should the public interface look like? Which behaviors are most important to test?"*

### 2. Tracer bullet

Write **one** test for the most important behavior. Make it pass with minimal code. This proves the path works end-to-end — interface, wiring, test runner, fixtures.

### 3. Incremental loop

For each remaining behavior:

```
RED → GREEN → refactor-if-needed → commit
```

Rules:
- One test at a time.
- Only enough code to pass the current test.
- Do not anticipate future tests.
- Keep tests focused on observable behavior.
- Commit after each green so the history shows the spec growing.

### 4. Refactor

After all required tests pass:

- [ ] Extract duplication **only if it exists** (rule of three, not rule of two).
- [ ] Improve naming.
- [ ] Collapse abstractions that do not earn their complexity.
- [ ] Run tests after each refactor step.

**Never refactor while red.**

## What makes a good test

| Good | Bad |
|------|-----|
| Asserts on observable output | Asserts on internal state |
| Exercises code through the public API | Calls private methods |
| Names describe behavior ("rejects negative amounts") | Names describe structure ("calls validateAmount") |
| Sets up minimal data | Copies production fixtures wholesale |
| Fails for the right reason when behavior regresses | Fails when you rename an internal variable |
| One clear behavior per test | Asserts 10 unrelated things |

Name tests as **sentences** describing behavior: `it('returns 422 for invalid email')`, not `it('validation')`.

## Mocking — use sparingly

**Mock at boundaries, not internals.** Mocks that replace internal collaborators couple your tests to the wrong thing.

| Mock it | Do not mock it |
|---------|----------------|
| Network / HTTP calls | Your own pure functions |
| Databases (unless a real test DB is trivial) | Internal service classes |
| Time (`Date.now`, `setTimeout`) | Business logic |
| Random / UUID generation | Data structures |
| Third-party SDKs at the boundary | Your own domain types |

Prefer real collaborators wherever fast. An integration test with a real in-memory SQLite beats a unit test with 10 mocks.

If a test needs >3 mocks to run, the code is probably coupled — consider refactoring the code, not the test.

## Test pyramid — rough guide

```
        /\\
       /E2E\\       small — expensive, slow, flakier
      /------\\
     / Integ. \\    medium — real DB / filesystem, mocked external APIs
    /----------\\
   /   Unit     \\  many — pure logic, fast, deterministic
  /--------------\\
```

- **Unit tests** cover pure logic. Fast, many, deterministic.
- **Integration tests** exercise real boundaries (DB, filesystem). Fewer, slower, higher value per test.
- **E2E tests** prove full user flows. Expensive and flaky — keep to smoke-level coverage of critical journeys.

If a unit test suffices, do not write an integration test. If an integration test suffices, do not write an e2e.

## Running tests fast

- Run a single failing test first: `pytest path/to/test.py::test_name`, `vitest run -t "name"`, `go test ./pkg -run TestName`.
- Use the project's watch mode for the inner loop.
- Isolate flaky tests with `--runInBand` / `--forks=1` to rule out parallel pollution.
- In CI, fail fast on the first test failure when debugging locally; run full suite before merge.

## When NOT to use TDD

- Pure config changes (YAML, JSON, .env) with no behavioral branch.
- Documentation updates.
- Rename-only refactors (the existing tests are the safety net).
- Spikes / prototypes to validate an approach — **but** convert to TDD before the spike becomes production code.
- Throwaway scripts run once and deleted.

If in doubt, write the test. The cost is low; the cost of shipping behavior without a test is high.

## Interaction with other skills

- `diagnose` — Phase 5 of diagnosis **is** TDD's red → green for the regression. Same discipline.
- `investigate-before-editing` — read the existing tests before writing new ones. Match naming / structure conventions.
- `code-review` — a PR without tests for behavioral changes is a red flag the reviewer should surface.
- `llm-coding-discipline` — "verify, don't assume". TDD is verification made concrete.
- `incremental-implementation` — TDD drives the increment size. One test = one slice.

## Verification checklist

Per cycle:

- [ ] Test describes behavior, not implementation.
- [ ] Test uses the public interface only.
- [ ] Test would survive an internal refactor.
- [ ] Test name is a sentence describing the behavior.
- [ ] The test was observed to FAIL before the fix (red).
- [ ] The code is the minimum to make it pass (no speculative features).
- [ ] Test PASSES after the fix (green).
- [ ] Full suite runs clean — no regressions.
- [ ] Refactoring happened only while green.
