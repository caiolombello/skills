---
name: delivery-coordination
description: "Use when coordinating delivery: intake, card quality, Jira issue creation, refinement, ownership, dependencies, sprint or Kanban readiness, blockers, status, and follow-up. Not product strategy or code execution."
---

# Delivery Coordination

Turn approved outcomes and incoming work into a healthy, traceable delivery
flow. Keep cards actionable, ownership explicit, dependencies visible, and
status useful for decisions.

## Scope boundaries

Use this skill to:

- Triage requests and decide whether they are ready for the backlog.
- Draft, create, split, link, refine, or audit cards.
- Maintain backlog hygiene and readiness.
- Coordinate dependencies, owners, blockers, and follow-ups.
- Prepare refinement, planning, review, and delivery status.
- Separate product backlog from active sprint or Kanban commitments.

Do not use it as the primary workflow to:

- Decide product strategy, outcomes, or roadmap priorities — use
  [`product-management`](../product-management).
- Invent technical implementation details — use
  [`spec-first-planning`](../spec-first-planning) after approval.
- Execute an approved engineering plan — use
  [`executing-plans`](../executing-plans).
- Operate Jira commands without loading the relevant tool workflow — use
  [`atlassian-acli`](../atlassian-acli).

## Non-negotiables

1. Read the real board, backlog, workflow, fields, and existing card patterns
   before proposing changes.
2. Keep one authoritative card for one delivery outcome; link evidence and
   supporting tasks instead of creating duplicates.
3. Never invent priority, owner, estimate, due date, sprint commitment, client
   routing value, or acceptance.
4. Distinguish requester/reporter, accountable owner, implementers, reviewers,
   and decision owners.
5. Do not move work into an active commitment silently.
6. Do not mark work ready when a decision-changing question remains open.
7. Do not mark work done from status alone; require acceptance and verification
   evidence appropriate to the card.
8. Preserve history: update the card with decisions and changed scope rather
   than hiding why delivery moved.

## Workflow

### 1. Establish scope and authority

Record:

- Board/project, workflow type, team, cadence, and time horizon.
- Product goal or operational outcome this work serves.
- Whether the request is read-only audit, drafting, or authorized tracker
  mutation.
- Who can set priority, commit capacity, assign owners, accept scope, and close
  work.

If Jira is involved, read
[references/workspace-jira-conventions.md](references/workspace-jira-conventions.md)
before drafting or writing client-scoped cards.

### 2. Read current state

Inspect before editing:

- Board filter, projects, issue types, statuses, and transitions.
- Required fields, field options, components, labels, and routing fields.
- Active sprint or Kanban WIP, backlog order, blockers, and stale items.
- One or two recent high-quality cards of the same type.
- Existing epics, duplicates, dependencies, and linked incidents or decisions.

Report unavailable permissions or missing data. Do not infer a workflow from a
screenshot when the tracker is readable.

### 3. Triage intake

Classify each request as:

- `ready for refinement`
- `needs product decision`
- `needs discovery/evidence`
- `duplicate/link to existing`
- `operational incident`
- `not actionable`

Capture the source, problem/outcome, affected user/client, urgency reason,
requested timing, and decision owner. A requested due date is not a committed
date.

### 4. Make the card actionable

Use the card as a concise shared contract, not a transcript. Include:

- Outcome/problem and context/evidence.
- Scope and explicit non-goals.
- Acceptance criteria observable by the requester or user.
- Dependencies, risks, constraints, and required decisions.
- Accountable owner and contributors when known.
- Priority rationale and source of authority.
- Validation/evidence expected before closure.

Read
[references/card-and-backlog-practices.md](references/card-and-backlog-practices.md)
for card templates, readiness checks, splitting rules, and status formats.

### 5. Organize without duplicating

Use this traceability shape where the tracker supports it:

```text
goal/outcome -> initiative/epic -> story/task/bug -> validation evidence
```

- Link blockers and dependencies with directional semantics.
- Split cards that contain independent outcomes, owners, release paths, or
  acceptance decisions.
- Keep subtasks for execution steps that do not need independent priority.
- Link incidents, decisions, designs, pull requests, and runbooks instead of
  copying their full contents.

### 6. Govern readiness and commitment

Before moving work into a sprint or active Kanban commitment:

- Confirm outcome, scope, acceptance, dependencies, and owner.
- Confirm the team supplied or accepted the estimate/capacity view.
- Confirm external dependencies have owners and expected decision dates.
- Check WIP/capacity and displaced work.
- Record who authorized the priority or commitment change.

Keep the product backlog dynamic. Treat the sprint backlog or active WIP as a
team commitment that requires explicit renegotiation.

### 7. Run the coordination cadence

Use the smallest cadence that closes decision loops:

- `Intake/triage` — classify new work and route incomplete requests.
- `Refinement` — clarify, split, estimate with the team, and check readiness.
- `Planning/replenishment` — select work against goal, capacity, and WIP.
- `Blocker follow-up` — name owner, next action, and decision time.
- `Review` — demonstrate outcome and collect acceptance/evidence.
- `Retrospective` — create owned improvement actions, not generic sentiments.
- `Backlog hygiene` — review stale, duplicate, unowned, and obsolete work.

Every meeting or async pass must produce decisions, owners, and follow-up
dates—or be skipped.

### 8. Communicate for decisions

Lead status with:

1. Outcome/goal and current confidence.
2. Delivered and verified since the last update.
3. In progress, with owner and expected next evidence.
4. Blockers, impact, owner, and decision needed.
5. Scope, priority, or date changes and who approved them.
6. Risks and the next review point.

Do not report ticket counts as progress without explaining the delivered
outcome.

### 9. Apply tracker changes safely

For Jira:

1. Load [`atlassian-acli`](../atlassian-acli).
2. Confirm the active account and exact board/project.
3. Read an analogous card and current field metadata.
4. Present the proposed create/edit/transition set when judgment is involved.
5. Apply only authorized mutations.
6. Re-read the affected cards and verify fields, links, and status.

Bulk archive, bulk edit, bulk transition, sprint mutation, and destructive
operations require explicit scope and confirmation. Never hide work to make a
board or report appear healthier.

## Required output

Lead with:

1. `Delivery snapshot` — goal, board, active work, and confidence.
2. `Blockers/decisions` — owner, impact, and required date.
3. `Backlog health` — ready, unclear, duplicate, stale, and unowned work.
4. `Proposed changes` — creates, edits, links, splits, or transitions.
5. `Commitment impact` — capacity/WIP and displaced work.
6. `Follow-up` — owners, dates, and verification evidence.

## Interaction with other skills

- [`product-management`](../product-management) — owns product outcomes,
  prioritization, and roadmap tradeoffs.
- [`atlassian-acli`](../atlassian-acli) — executes Jira reads and authorized
  writes; this skill supplies coordination judgment.
- [`spec-first-planning`](../spec-first-planning) — creates the approved
  technical specification and task plan.
- [`executing-plans`](../executing-plans) — performs engineering work after
  planning.
- [`incident-response`](../incident-response) — takes over when the work is an
  active production incident.
- [`aidlc-workflow`](../aidlc-workflow) — coordinates a complete auditable
  lifecycle when explicitly requested.

## Verification checklist

- [ ] Board, project, workflow, field options, and authority were inspected.
- [ ] Every card has an outcome, bounded scope, acceptance, and validation.
- [ ] Priority, owner, estimate, and date are sourced rather than invented.
- [ ] Duplicates, dependencies, blockers, and stale work are visible.
- [ ] Active commitments changed only with explicit authority.
- [ ] Tracker writes were re-read and verified.
- [ ] Status communicates decisions and outcomes, not ticket volume alone.
