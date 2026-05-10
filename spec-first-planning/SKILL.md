---
name: spec-first-planning
description: Write a lightweight spec, then break it into ordered verifiable tasks, BEFORE writing code. The spec is the shared source of truth between agent and human. Use WHENEVER (1) starting a new project, feature, or significant change with no spec; (2) requirements are vague, ambiguous, or exist only as a sentence the user typed; (3) the change will touch multiple files or modules; (4) the task would take more than ~30 minutes to implement; (5) the user asks to "plan", "break down", "design", "scope out", "estimate"; (6) work needs to be parallelized across agents or sessions. DOES NOT APPLY to: one-line fixes, typo corrections, rename-only refactors, tasks whose scope is already obvious and self-contained. The gated workflow — specify → plan → tasks → implement — catches misunderstandings while they are cheap to fix.
---

<!-- Inspired by addyosmani/agent-skills spec-driven-development + planning-and-task-breakdown (MIT). See ../CREDITS.md -->

# Spec-First Planning

Write a lightweight spec, then break it into ordered verifiable tasks, **before** writing code. The spec is the shared source of truth between agent and human. Code without a spec is guessing.

This skill fuses two disciplines: **specify what we are building** and **break it into tasks we can verify one at a time**.

## When to use

- Starting a new project or feature.
- Requirements are ambiguous or incomplete.
- The change touches multiple files or modules.
- About to make an architectural decision.
- Task would take more than ~30 minutes to implement.
- User says "plan", "break down", "design", "scope out", "estimate".

### When NOT to use

- One-line fixes, typo corrections.
- Rename-only refactors.
- Requirements already unambiguous and self-contained.
- Task fits in a single file, single function, <30 minutes.

## The gated workflow

```
SPECIFY ──▶ PLAN ──▶ TASKS ──▶ IMPLEMENT
   │          │       │          │
   ▼          ▼       ▼          ▼
 Human      Human   Human      Human
 reviews    reviews reviews    reviews
```

Do **not** advance to the next phase until the current one is validated by the human. Each phase is cheap; each phase catches misunderstandings while they are cheaper than code.

## Phase 1: Specify

### Surface assumptions first

Before writing any spec content, list what you are assuming. Assumptions are the most dangerous form of misunderstanding.

```
ASSUMPTIONS I'M MAKING:
1. This is a web app (not native mobile).
2. Auth uses session cookies, not JWT.
3. DB is Postgres (inferred from existing Prisma schema).
4. Modern browsers only (no IE11).
Correct me now or I'll proceed with these.
```

### The 7-section spec

A good spec is short and scannable — not a novel. Target 1-2 pages.

```markdown
# Spec: <Feature / Project Name>

## 1. Objective
<What we are building and why. Who is the user. What success looks like.
 Acceptance criteria from the user's POV.>

## 2. Scope
### In scope
- <thing 1>
- <thing 2>

### Out of scope (explicitly)
- <thing the reader might expect but we are NOT doing>
- <thing postponed to a follow-up>

## 3. Constraints
- <Tech stack + versions (reference project-rules-file for the stable part)>
- <Performance / latency / size budgets>
- <Compliance / security requirements>
- <Deadlines, if hard>

## 4. Open questions
- <Explicit list of questions the human must answer before we move to Plan>
- <Any ambiguity you surfaced but did not resolve>

## 5. Success criteria
- <Measurable signal 1: "p95 request latency under 200ms">
- <Measurable signal 2: "test coverage on new code >= 80%">
- <Measurable signal 3: "zero CVEs flagged high/critical in dependency audit">

## 6. Risks
- <Risk: description / likelihood / mitigation>

## 7. References
- <Link to issue / ticket / design doc / ADR>
- <Link to related prior art in the repo>
```

**Exit criterion**: the human has signed off on the spec. Do not proceed until they have.

## Phase 2: Plan

With the spec agreed, plan the **approach** — not the tasks yet.

### Read-only mode

Operate read-only in this phase. No code.

- Read the relevant codebase sections.
- Identify existing patterns and conventions you will follow.
- Map dependencies between components you will change.
- Note risks, unknowns, and pre-investigation items.

Use [`investigate-before-editing`](../investigate-before-editing) to structure the read.

### Dependency map

Sketch what depends on what. Implementation order follows dependencies bottom-up.

```
DB schema
  ├── API models / types
  │     ├── API endpoints ── Frontend client ── UI components
  │     └── Validation
  └── Seed data / migrations
```

### Approach document

```markdown
# Plan: <Feature>

## Approach
<3-5 sentences describing how we will solve it. Name the key design decisions.>

## Dependency graph
<The map from above, or a list>

## Technical decisions
- <Decision 1: chose X over Y because ...>
- <Decision 2: reusing existing pattern from src/...>

## Testing strategy
<Unit / integration / e2e mix. Where tests will live. What each layer validates.>

## Rollout
<Feature flags? Migrations? Sequenced deploys? Backfills?>

## Risks revisited
<Anything the codebase reading revealed that was not in the spec>
```

**Exit criterion**: human has signed off on the approach. Still no code.

## Phase 3: Tasks

Decompose the plan into small, ordered, verifiable tasks. Prefer **vertical slices** (one full path through the stack per task) over horizontal slices (all DB → all API → all UI).

### Task size

- **Ideal**: a focused 30-90 minute unit; reviewable PR under ~200 lines.
- **Too big**: cannot be described in one imperative sentence, or >400 lines.
- **Too small**: typo fixes, rename only — bundle them.

### Task template

```markdown
## Task N: <imperative title>

**Description**: one paragraph — what this accomplishes.

**Acceptance criteria** (observable, testable):
- [ ] <specific condition>
- [ ] <specific condition>

**Verification**:
- [ ] Tests pass: `<exact test command>`
- [ ] Build succeeds: `<exact build command>`
- [ ] Manual check: <what to look at>

**Dependencies**: <task numbers this depends on, or "None">

**Files likely touched**:
- `<path>`
- `<path>`
```

### Ordering heuristics

1. **Dependencies first** — DB / schema / types before consumers.
2. **Risk first** — the scariest or most uncertain slice before the easy CRUD. If it fails, you waste one slice, not the whole feature.
3. **Tracer bullet** — first task proves the full stack wires up, even if almost empty. See [`incremental-implementation`](../incremental-implementation).
4. **Parallel-friendly** — mark tasks that can run independently so they can be handed to different sessions.

### Example: "user creates and lists tasks"

```markdown
## Task 1: Tracer — render "No tasks" page
- Route /tasks returns page with "No tasks yet" (empty state).
- Verification: `curl localhost:3000/tasks | grep "No tasks"`.
- Deps: none.

## Task 2: DB migration — tasks table
- Columns: id, user_id, title, status, created_at, completed_at.
- Indexes: (user_id, created_at DESC).
- Verification: `pnpm prisma migrate dev` succeeds; `prisma.task.create` in REPL works.
- Deps: none.

## Task 3: POST /tasks (create)
- Zod body schema, ownership-scoped insert.
- Returns 201 + row; 422 on invalid body.
- Tests: happy path + validation error.
- Verification: unit test + curl happy path.
- Deps: 2.

## Task 4: GET /tasks (list, paginated, owned)
- Tests: empty / populated / pagination / cross-user isolation.
- Deps: 2.

## Task 5: UI — NewTaskForm + submission
- Uses React Hook Form + Zod; optimistic insert.
- Deps: 3.

## Task 6: UI — TaskList renders real data
- Loading / empty / populated states.
- Deps: 4.

## Task 7: Integration test covering full flow
- Deps: 5, 6.
```

**Exit criterion**: task list agreed with the human, and todos exist in the agent's task tracker (TodoWrite or similar).

## Phase 4: Implement

Now code. One task at a time. Do **not** mix tasks in one commit.

- Use [`incremental-implementation`](../incremental-implementation) for the per-slice loop.
- Use [`test-driven-development`](../test-driven-development) inside each task.
- Mark the todo `in_progress` at start, `completed` at commit. Update at real time, not in batches.
- If a task explodes (depends on something not planned), **stop**, update the task list, re-align with the human — do not silently expand the task.

## Re-planning

Plans are hypotheses. When you learn something mid-flight:

- Surface it to the human explicitly: "Task 4 depends on something not in the plan: ...".
- Revise the task list, not the code. Add tasks, reorder, or split.
- Keep the spec as-is unless the objective actually changed. A revised spec is a heavy event — it re-opens Phase 1.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Skip the spec, "it's obvious" | Silent assumptions ship wrong features |
| Write 10 pages of spec before any sign-off | Review cycle collapses; humans skim and miss issues |
| Plan = tasks (no approach phase) | Wrong approach wastes the whole task list |
| Horizontal slicing by default | Nothing is demoable until the end |
| Tasks without verification criteria | "Done" becomes subjective |
| Batch completing todos after 5 tasks | You lose the checkpoint discipline |
| Silently add a task mid-implementation | Scope drift; estimate rots |
| Spec written in prose with no measurable success criteria | "Make it fast" is not a success criterion |
| Assumptions buried in the spec body | Human does not notice; they should be the first section |
| Task list that does not include the tracer / risk-first slice | Risks surface late and hurt |

## Interaction with other skills

- [`project-rules-file`](../project-rules-file) — the stable tech-stack + conventions section of the spec references the rules file, does not duplicate it.
- [`investigate-before-editing`](../investigate-before-editing) — the read-only reading in Phase 2.
- [`incremental-implementation`](../incremental-implementation) — Phase 4 execution per task.
- [`test-driven-development`](../test-driven-development) — each task's verification criteria map to a test.
- [`llm-coding-discipline`](../llm-coding-discipline) — "surface assumptions" is the first action in Phase 1.
- [`doubt-driven-review`](../doubt-driven-review) — for architectural decisions in Phase 2, run a fresh-context review before sign-off.

## Verification checklist

Before moving from a phase to the next:

**Leaving Specify → Plan**
- [ ] Assumptions listed explicitly and the human did not correct them.
- [ ] "In scope" and "Out of scope" are both filled.
- [ ] At least one measurable success criterion.
- [ ] Open questions either resolved or explicitly deferred.
- [ ] Human signed off.

**Leaving Plan → Tasks**
- [ ] Read the relevant code end-to-end.
- [ ] Dependency map exists.
- [ ] Testing strategy stated.
- [ ] Human signed off.

**Leaving Tasks → Implement**
- [ ] Every task has description, acceptance criteria, verification, dependencies, files.
- [ ] Task 1 is a tracer bullet.
- [ ] Dependencies form a DAG (no cycles).
- [ ] Risk-first or scary-part-first is respected.
- [ ] Human agreed on the task list.
- [ ] Todos are in the agent's task tracker.

**During Implement**
- [ ] One task `in_progress` at a time.
- [ ] Each task commits separately with Conventional Commits.
- [ ] Task scope is not expanded silently.
- [ ] Re-planning happens visibly, not inside a single commit.
