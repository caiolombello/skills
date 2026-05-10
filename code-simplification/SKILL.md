---
name: code-simplification
description: Reduce code complexity while preserving exact behavior. The goal is comprehension, not fewer lines. Use WHENEVER (1) a feature is working and tests pass but the implementation feels heavier than it needs to be; (2) code review flags readability, nesting, or complexity issues; (3) the agent encounters deep nesting, long functions, chained ternaries, or generic names; (4) refactoring code written under time pressure; (5) the user asks to "clean up", "simplify", "reduce complexity", "refactor for clarity", "make this more readable". Does NOT apply when: code is already clean; you have not fully understood what the code does yet; the "simpler" version would be measurably slower in a hot path; you are about to rewrite the module entirely. Refactor-only — never combined with a feature or bug fix in the same change.
---

<!-- Inspired by addyosmani/agent-skills code-simplification (MIT), which in turn is inspired by Anthropic's code-simplifier plugin. See ../CREDITS.md -->

# Code Simplification

Reduce complexity while preserving exact behavior. Goal: a new teammate understands it faster than the original. Fewer lines is **not** the goal — clearer lines is.

## When to use

- After a feature lands and tests pass, but the implementation feels heavier than it needs to be.
- During review when readability / complexity issues are flagged.
- When you encounter deep nesting, long functions, unclear names.
- When refactoring code written under time pressure.
- After a merge that introduced duplication or inconsistency.

### When NOT to use

- Code is already clean — do not simplify for the sake of it.
- You do not yet understand what the code does — comprehend before you simplify.
- Performance-critical hot path where the "simpler" version is measurably slower.
- About to rewrite the module entirely — simplifying throwaway code wastes effort.

## The five principles

### 1. Preserve behavior exactly

Change **how** the code expresses the behavior, never **what** it does. Inputs, outputs, side effects, ordering, error behavior — all identical. If unsure, do not simplify.

Ask before every change:
- Does this produce the same output for every input?
- Same error behavior?
- Same side effects and ordering?
- Do existing tests still pass **unchanged**?

### 2. Follow project conventions

Simplification means **more consistent with the codebase**, not "what I would do". Before simplifying, read the project rules file (see [`project-rules-file`](../project-rules-file)) and scan neighbouring code for:

- Import ordering and module system.
- Function declaration style.
- Naming conventions.
- Error handling patterns.
- Type annotation depth.

Simplification that breaks project consistency is not simplification — it is churn.

### 3. Prefer clarity over cleverness

Explicit code beats compact code when the compact version requires a mental pause.

```ts
// UNCLEAR: dense ternary chain
const label = isNew ? 'New' : isUpdated ? 'Updated' : isArchived ? 'Archived' : 'Active';

// CLEAR: readable mapping
function statusLabel(item: Item): string {
  if (item.isNew) return 'New';
  if (item.isUpdated) return 'Updated';
  if (item.isArchived) return 'Archived';
  return 'Active';
}
```

```ts
// UNCLEAR: chained reduce with inline logic
const result = items.reduce((acc, item) => ({
  ...acc,
  [item.id]: { ...acc[item.id], count: (acc[item.id]?.count ?? 0) + 1 }
}), {});

// CLEAR: named intermediate
const countById = new Map<string, number>();
for (const item of items) {
  countById.set(item.id, (countById.get(item.id) ?? 0) + 1);
}
```

### 4. Maintain balance

Simplification has a failure mode: **over-simplification**. Watch for:

- **Inlining too aggressively** — removing a helper that gave a concept a name makes the call site harder to read.
- **Combining unrelated logic** — two simple functions merged into one complex function is not simpler.
- **Removing "unnecessary" abstractions** — some exist for extensibility or testability, not complexity.
- **Optimizing for line count** — fewer lines is not the goal.

### 5. Scope to what changed

Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code unless explicitly asked. Unscoped simplification creates diff noise and risks unintended regressions.

## Process

### Step 1: Understand before touching (Chesterton's Fence)

Before removing or changing anything, understand **why it exists**. If there is a fence across the road and you do not know why, do not tear it down. Understand the reason, then decide if it still applies.

Before simplifying, answer:
- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that pin the expected behavior?
- Is there a historical reason? (Performance? Platform constraint? Migration?)
- Check `git blame` / `git log -p` — what was the original context?

If you cannot answer these, read more context first.

### Step 2: Identify simplification opportunities

Each row below is a **concrete signal** — not a vague smell.

#### Structural complexity

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Deep nesting (3+ levels) | Hard to follow control flow | Extract guard clauses, early returns, or helper functions |
| Long functions (50+ lines) | Multiple responsibilities | Split into focused functions with descriptive names |
| Nested ternaries | Requires a mental stack to parse | if/else chain, `switch`, or lookup map |
| Boolean flag parameters | `doThing(true, false, true)` | Options object, or two separate functions |
| Repeated conditionals | Same `if` in multiple places | Extract into a well-named predicate |

#### Naming and readability

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Generic names | `data`, `result`, `tmp`, `val`, `item` | Rename to describe content: `userProfile`, `validationErrors` |
| Abbreviated names | `usr`, `cfg`, `btn`, `evt` | Full words, unless abbreviation is universal (`id`, `url`, `api`) |
| Misleading names | `get` that also mutates | Rename to match actual behavior |
| Comments explaining **what** | `// increment counter` above `count++` | Delete — the code is clear enough |
| Comments explaining **why** | `// retry because upstream is flaky under load` | Keep — they carry intent the code cannot express |

#### Redundancy

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Duplicated logic | Same 5+ lines in multiple places | Extract into a shared function |
| Dead code | Unreachable branches, commented blocks | Remove (after confirming it is truly dead) |
| Unnecessary wrapper | Wrapper that adds no value | Inline, call underlying directly |
| Over-engineering | Factory-for-a-factory, one-strategy strategy | Replace with the direct approach |
| Redundant type assertions | Casting to an inferred type | Remove the assertion |

**Rule of three:** do not extract a helper for the first two duplications. Extract only when a third appears — otherwise the abstraction is premature.

### Step 3: Apply incrementally

**One simplification at a time. Tests after each.**

```
For each simplification:
1. Make one focused change.
2. Run the test suite.
3. If green → commit (or continue to the next).
4. If red → revert and reconsider.
```

**Never batch** multiple simplifications into a single untested change. If something breaks you need to know which one caused it.

**Split refactor from feature / bug fix.** A change that simplifies **and** adds behavior is two changes — submit them separately. See [`code-review`](../code-review).

**The rule of 500:** if a refactor touches more than 500 lines, invest in automation — codemods, AST transforms, `sed` with care. Manual edits at that scale are error-prone and exhausting to review.

### Step 4: Verify the result

After the simplifications, step back:

- Is the new version genuinely easier to understand?
- Would a new teammate read this faster?
- Do **all** existing tests still pass **unchanged**?
- Did you preserve every edge case the original handled?
- Did you match the project's existing style?

If the answer to any of these is no, revert the change — the simplification was not an improvement.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| "I made it shorter" without asking if it is clearer | Dense one-liners are not simpler |
| Extracting a helper used exactly once | Premature abstraction |
| Merging two simple functions into one complex one | Inverse of simplification |
| Renaming variables across unrelated files | Scope creep |
| Inlining a well-named helper because it is "one line" | Removes a concept name |
| Deleting comments that explain **why** | Drops intent |
| Bundling refactor with feature / fix | Unreviewable; bisect hell later |
| Over-reliance on functional chains (`.map(...).filter(...).reduce(...)`) when a loop reads better | Cleverness over clarity |
| Over-reliance on `try/catch` to "simplify" error paths | Swallows bugs |

## Interaction with other skills

- [`llm-coding-discipline`](../llm-coding-discipline) — "simplicity first", "surgical changes" are the principles this skill operationalizes.
- [`investigate-before-editing`](../investigate-before-editing) — read the code end-to-end and check `git blame` before changing anything.
- [`test-driven-development`](../test-driven-development) — existing tests are your oracle for "did behavior change?".
- [`code-review`](../code-review) — simplification PRs should be reviewed with the same five axes; special attention to correctness (same edge cases) and scope discipline.
- [`git-hygiene`](../git-hygiene) — one commit per simplification, Conventional Commits (`refactor(scope): …`).
- [`incremental-implementation`](../incremental-implementation) — applies to refactors too: small slices, green between.

## Verification checklist

Before declaring a simplification done:

- [ ] I understood why the original code existed before touching it.
- [ ] The change matches the project's existing conventions (not my preferences).
- [ ] Every change was made and tested in isolation.
- [ ] All existing tests pass unchanged (no tests modified to accommodate the refactor).
- [ ] The new version is genuinely easier to read — not just shorter.
- [ ] No behavior changed (inputs, outputs, side effects, error handling, ordering).
- [ ] The refactor is in its own commit / PR, not bundled with a feature or bug fix.
- [ ] For >500 lines touched, I used automation or split the refactor.
- [ ] I kept "why" comments; I deleted "what" comments only when the code was already clear.
