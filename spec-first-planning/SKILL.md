---
name: spec-first-planning
description: 'Use when starting a non-trivial or vague feature: write a lightweight spec and ordered tasks before code. Skip one-line fixes, renames, and obvious single-file changes.'
---
<!-- Inspired by addyosmani/agent-skills spec-driven-development + planning-and-task-breakdown (MIT) and awslabs/aidlc-workflows adaptive depth and traceability (MIT-0). See ../CREDITS.md -->

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

## Choose planning depth

Scale the artifact, not the discipline:

| Depth | Use when | Expected treatment |
|---|---|---|
| Minimal | Isolated, reversible, well-specified change | Intent, scope, acceptance criteria, tasks, exact verification |
| Standard | Multi-file feature, migration, or meaningful NFR | Full spec, dependency map, risks, rollout, task traceability |
| Comprehensive | High blast radius, regulated data, cross-team or architectural change | Full traceability, security/compliance evidence, rollback, ownership, operational readiness |

State the chosen depth and rationale. A short task can still need comprehensive
security or rollout treatment; document depth and test depth are independent.

## The workflow and decision points

```
SPECIFY ──▶ PLAN ──▶ TASKS ──▶ IMPLEMENT
```

Use checkpoints where a user decision is needed. The request or an already approved plan can authorize the phases it clearly covers; do not ask for the same approval again. Continue with reversible choices inside the authorized scope, and pause only for missing authority or a material unresolved trade-off. For a planning-only request, stop at the plan and do not begin implementation.

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

**Exit criterion**: the spec is consistent with the request and any decisions needed to proceed are resolved or explicitly recorded. Ask for sign-off only when requested or when a material ambiguity remains; treat prior approval as covering the scope it explicitly approved.

## Phase 2: Plan

With the spec agreed, plan the **approach** — not the tasks yet.

### Read-only mode

Operate read-only by default in this phase. Do not start production implementation during a planning-only request. Inline caller examples and type/signature sketches are planning artifacts. When a runnable experiment is within the current authorization, use an isolated [throwaway prototype](../throwaway-prototype/SKILL.md) to answer a specific empirical question; otherwise record the untested assumption rather than presenting it as evidence.

- Read the relevant codebase sections.
- Identify existing patterns and conventions you will follow.
- Map dependencies between components you will change.
- Note risks, unknowns, and pre-investigation items.

Use [`investigate-before-editing`](../investigate-before-editing) to structure the read.

### Dependency map

For a consequential interface, start from a concrete caller example, core data shape, signatures, failure behavior, and observable result. Work backward to ownership and dependencies. These sketches expose a wrong boundary earlier than a long task list; they do not require adding a README or speculative implementation.

Compare materially different alternatives when the decision is uncertain, costly to reverse, and the comparison can change the choice. State a discriminating check before a prototype or design experiment. Use evidence from that check to choose, and revise the design if implementation repeatedly needs unexplained parameters, hidden state, or escape hatches. Do not require a fixed number of designs, models, or reviewers for every change. Product preferences remain the user's decision; measurements can settle factual questions.

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

## Lifecycle coverage
<Security, compliance, rollback, observability, support and ownership.
 Mark irrelevant concerns N/A with a reason.>

## Traceability
| Requirement / risk | Task | Verification | Status |
|---|---|---|---|

## Risks revisited
<Anything the codebase reading revealed that was not in the spec>
```

**Exit criterion**: the approach is consistent with the approved scope and required decisions are resolved or recorded. Ask for sign-off only when requested or when a material ambiguity remains; this phase remains planning-only and does not authorize code by itself.

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

**Traces to**: <requirement, success criterion, or risk ID>

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

**Exit criterion**: tasks cover the approved result, essential decisions are resolved, and progress is recorded in the available task tracker. An approved request/plan can already supply this agreement; ask again only for a material unresolved decision.

## Phase 4: Implement

Now implement the scoped tasks in useful, verifiable increments. If commits are authorized, group related changes into coherent commits; task boundaries do not mandate a commit.

- Use [`incremental-implementation`](../incremental-implementation) for the per-slice loop.
- Use [`test-driven-development`](../test-driven-development) inside each task.
- Mark work `in_progress` at start and `completed` when its result is verified, independently of whether a commit was requested.
- When an unexpected dependency appears, update the plan and investigate routine obstacles within scope. Ask only if the dependency introduces a material decision or needs authority not already supplied; do not silently expand the result.

## Re-planning

Plans are hypotheses. When you learn something mid-flight:

- Surface it to the human explicitly: "Task 4 depends on something not in the plan: ...".
- Revise the task list, not the code. Add tasks, reorder, or split.
- Keep the spec as-is unless the objective actually changed. A revised spec is a heavy event — it re-opens Phase 1.
- Back-propagate accepted discoveries to the affected requirement, traceability
  row, ADR, rollout, or operations check before resuming implementation.

## Anti-patterns

| Anti-pattern | Why it fails |
|--------------|--------------|
| Skip the spec, "it's obvious" | Silent assumptions ship wrong features |
| Write 10 pages of spec before a needed decision | Review cycle collapses; humans skim and miss issues |
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
- [`doubt-driven-review`](../doubt-driven-review) — use a fresh-context challenge for consequential uncertain architectural decisions when it improves the evidence; it is not a gate for every plan.
- [`aidlc-workflow`](../aidlc-workflow) — composes this planning discipline into
  an explicit adaptive lifecycle when the user asks for AI-DLC.

## Verification checklist

Before moving from a phase to the next:

**Leaving Specify → Plan**
- [ ] Planning depth is stated and justified.
- [ ] Assumptions are explicit; essential ones are resolved or tested. Silence is not approval or evidence.
- [ ] "In scope" and "Out of scope" are both filled.
- [ ] At least one measurable success criterion.
- [ ] Open questions either resolved or explicitly deferred.
- [ ] Required user decisions are resolved; prior approval covers this phase or a checkpoint was requested.

**Leaving Plan → Tasks**
- [ ] Read the relevant code end-to-end.
- [ ] Dependency map exists.
- [ ] Testing strategy stated.
- [ ] Required user decisions are resolved; prior approval covers this phase or a checkpoint was requested.

**Leaving Tasks → Implement**
- [ ] Every task has description, acceptance criteria, verification, dependencies, files.
- [ ] Every task traces to a requirement, success criterion, or risk.
- [ ] Task 1 is a tracer bullet.
- [ ] Dependencies form a DAG (no cycles).
- [ ] Risk-first or scary-part-first is respected.
- [ ] Required user decisions are resolved; prior approval covers this phase or a checkpoint was requested.
- [ ] Todos are in the agent's task tracker.

**During Implement**
- [ ] One task `in_progress` at a time.
- [ ] Keep task progress and verification visible. Commit coherent units only when committing is already authorized; do not create a commit per task by default.
- [ ] Task scope is not expanded silently.
- [ ] Re-planning happens visibly; keep history coherent when an authorized commit is made.
