---
name: aidlc-workflow
description: Use only when the user explicitly asks for AI-DLC or AIDLC, or for an auditable end-to-end delivery workflow with adaptive stages and approval gates. Coordinate existing discovery, planning, implementation, security, deployment, and operations skills; do not use for ordinary coding, one-off fixes, or live incidents.
---

<!-- Inspired by awslabs/aidlc-workflows (MIT-0). See ../CREDITS.md -->

# AI-DLC Workflow

Coordinate an adaptive development lifecycle without duplicating the native
AI-DLC runtime or the focused skills already in this library. Select only the
stages that add value, make skipped stages explicit, preserve traceability, and
keep the user in control of consequential decisions.

## Choose native or adapted mode

Inspect the project before composing a workflow.

Use the project's native AI-DLC runtime when all of these are true:

- The project contains the upstream runtime, such as
  `.agents/skills/aidlc/SKILL.md`, `.codex/tools/aidlc-orchestrate.ts`, and an
  `aidlc/` workspace.
- Its doctor or validation command succeeds.
- The user asks to run the native or strict AI-DLC workflow.

Invoke the project's `$aidlc` entrypoint and follow its engine-owned routing.
Do not mix native state, hooks, audit events, or stage transitions with this
adapted coordinator.

Use the adapted mode when no complete native runtime exists. If a partial or
broken installation exists, report the gap and ask whether to repair it or use
adapted mode; never create a second state tree silently.

## Preserve boundaries

- Treat gates as decision checkpoints, not new authority to commit, deploy,
  message people, or mutate external systems.
- Route a live outage to [`incident-response`](../incident-response), and a
  suspected AWS compromise to
  [`aws-security-incident-response`](../aws-security-incident-response).
- Never record raw prompts by default. Persist decisions, evidence, and
  redacted references; never duplicate secrets, credentials, personal data, or
  incident evidence into a lifecycle log.
- Keep artifacts proportional. Use the agent's plan tracker for short work.
  Persist lifecycle documents only when the user asks, the work spans sessions,
  or auditability requires versioned evidence.
- Do not install the upstream Bun, Bedrock, hooks, agents, or runtime globally
  from this skill. Native installation is a separate, project-scoped decision.

## 1. Classify scope and depth

Choose a scope from evidence, not keyword matching alone. State the selection
and why it fits.

| Scope | Default depth | Typical lifecycle |
|---|---|---|
| `poc` | Minimal | Intent, feasibility, thin implementation, proof |
| `bugfix` | Minimal | Reproduce, inspect, define fixed behavior, patch, test |
| `refactor` | Minimal | Preserve behavior, map dependencies, change, regress |
| `security-patch` | Minimal | Scope vulnerability, constrain fix, test, release verification |
| `infra` | Standard | Current topology, NFRs, IaC design, preview, deploy, observe |
| `mvp` | Standard | Scope, essential journeys, design, slices, deploy feedback loop |
| `feature` | Standard | Intent through operation with conditional stages |
| `enterprise` | Comprehensive | Full traceability, security, compliance, resilience, rollout, ownership |

Raise depth when blast radius, irreversibility, data sensitivity, regulatory
scope, cross-account trust, migration risk, or organizational coordination
increases. Lower it when the work is isolated, reversible, and already
specified. Choose test strategy independently from document depth.

## 2. Compose the stage plan

Build a plan before implementation. For every candidate stage, mark
`EXECUTE` or `SKIP` and give a concrete reason.

Use this shape:

| Phase | Stage | Decision | Depth | Skill or owner | Artifact or evidence | Gate |
|---|---|---|---|---|---|---|
| Initialization | Workspace and context | EXECUTE | Minimal | `investigate-before-editing` | Confirmed repo state | No |
| Ideation | Intent and scope | EXECUTE | Standard | `brainstorming` | Validated direction | Yes |
| Inception | Requirements and design | EXECUTE | Standard | `spec-first-planning` | Approved plan | Yes |
| Construction | Implement and verify | EXECUTE | Standard | `executing-plans` | Tests and review | Batch |
| Operation | Release and observe | SKIP | — | — | Not requested | — |

Apply these phase boundaries:

1. **Initialization** — detect greenfield or brownfield, read project rules,
   inspect current state, and identify resumable work.
2. **Ideation** — clarify intent, value, feasibility, scope, and constraints
   only when the request is not already settled.
3. **Inception** — establish requirements, architecture, NFRs, units of work,
   delivery order, risks, and verification strategy.
4. **Construction** — design and implement one unit at a time, test, review,
   integrate, and validate CI.
5. **Operation** — provision, deploy, observe, validate performance, define
   rollback, and capture feedback only when the requested outcome includes
   production operation.

Do not force product discovery onto a targeted bug fix, or skip deployment
evidence for a security patch whose requested outcome is production
remediation.

## 3. Map stages to focused skills

Delegate stage discipline to existing skills instead of restating their
instructions:

| Need | Use |
|---|---|
| Workspace and brownfield discovery | `investigate-before-editing`, `context-engineering`, `zoom-out` |
| Intent, options, and feasibility | `brainstorming`, `throwaway-prototype` |
| Requirements, plan, tasks, traceability | `spec-first-planning` |
| Significant architecture decisions | `architecture-decision-records`, `doubt-driven-review` |
| AWS architecture or CSPM controls | `aws-security-architecture`, `aws-security-posture` |
| Application security constraints | `security-hardening` |
| Task execution and progress | `executing-plans`, `incremental-implementation` |
| Behavioral implementation | `test-driven-development` |
| Parallel units | `dispatching-parallel-agents`, `using-git-worktrees` |
| Quality gate | `code-review`, `verification-before-completion` |
| Infrastructure implementation | `terraform-iac-expert`, `helm-workflows` |
| Release and runtime readiness | `deploy-safety`, `observability`, `disaster-recovery` |
| Branch delivery | `finishing-a-development-branch`, `pr-workflow` |

Load only the skills needed by stages marked `EXECUTE`.

## 4. Gate decisions deliberately

In adapted mode, require approval:

- After the scope, depth, stage plan, and non-goals are proposed.
- Before accepting a consequential architecture, security, compliance, data,
  or migration decision.
- Before an externally visible or hard-to-reverse mutation.
- Before declaring the lifecycle complete or proceeding to release when
  release authority is not already explicit.

Do not interrupt every read, edit, test, or reversible implementation step.
Honor an already approved plan and the user's existing authority. If the user
explicitly requests strict AI-DLC gates, stop after every executed stage and
wait for approval.

## 5. Maintain traceability and state

Keep one current plan with at most one step in progress. Track:

| Requirement or risk | Unit or task | Implementation | Test or evidence | Status |
|---|---|---|---|---|

Update status in the same interaction that produces the evidence. When
implementation invalidates a design assumption:

1. Stop the affected unit.
2. Explain what the plan expected and what the repository or environment
   proved.
3. Update the plan, requirement, ADR, rollout, or operations check that became
   stale.
4. Re-run impacted validation before continuing.

Never rewrite a decision trail to make execution look linear. Record the
current decision and supersede stale decisions explicitly.

## 6. Close the lifecycle with evidence

Report:

1. Scope and depth used.
2. Executed and skipped stages, with reasons.
3. Artifacts or state updated.
4. Exact verification evidence.
5. Unverified assumptions, residual risks, and operational follow-ups.
6. Current release, deployment, or incident status without implying work that
   was not performed.

## Verification checklist

- [ ] Native and adapted modes were not mixed.
- [ ] Scope and depth match complexity and blast radius.
- [ ] Every candidate stage is `EXECUTE` or `SKIP` with rationale.
- [ ] Only stage-relevant skills were loaded.
- [ ] Consequential decisions passed the appropriate gate.
- [ ] Requirements, tasks, implementation, and evidence are traceable.
- [ ] Plan changes were back-propagated to stale artifacts.
- [ ] No raw prompts, secrets, or sensitive evidence were copied into logs.
- [ ] Completion reports exact evidence and remaining risk.
