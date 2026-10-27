---
name: t3-workflows
description: "Use for T3 Code-specific orchestration, scheduled tasks/webhooks, thread continuation, preview/device control, or artifacts/secrets through its exposed tools. Ordinary coding and non-T3 runtimes do not need this skill."
---

# T3 Workflows

Use the app's capabilities when they advance the requested result. Read the current T3 instructions and relevant tool descriptions; they govern over examples or an older reference. This skill does not enable tools, authorize external actions, or change account/model settings.

## Load the relevant procedure

| Need | Read |
| --- | --- |
| Parallel work, another provider/model, isolated child checkout, or background delegate | [Delegation](references/delegation.md) and [dispatching-parallel-agents](../dispatching-parallel-agents/SKILL.md) |
| Recurring work, fixed time, interval, webhook, pause/update/delete | [Schedules and webhooks](references/schedules.md) |
| Browser/device operation, continuation, thread links, visuals, attachments, credentials | [Surfaces and context](references/surfaces-and-context.md) |
| PR checks/review still in progress | [pr-followup](../pr-followup/SKILL.md); preserve app-owned events |

Do not load every reference for an ordinary coding task. Prefer existing focused skills for the engineering work itself. Use [computer-use](../computer-use/SKILL.md) for UI execution and [project-verification](../project-verification/SKILL.md) for a reusable app verification procedure.

## Common decisions

- Establish whether the user wants work now, a schedule, a child task, or a new top-level thread. These are distinct actions. A request to consider a feature does not create it; a request only to schedule does not run its prompt now.
- Preserve current authorizations and the agreed endpoint. Do not lower approvals, raise runtime access, change persistent preferences, send external messages, or merge because another tool makes it possible.
- Discover a tool from the live surface, including late-loaded tools as the host directs. Do not fabricate tool names or replace a missing app-owned operation with a private CLI/loop.
- Record actual returned identifiers and state. Creation, queued, running, waiting, completed, failed, and cancelled have different meanings. Honor a delegate's returned next step instead of polling it.
- Keep active user data and sessions out of write tests. Use synthetic scenarios to assess instructions; actual provider, browser, schedule, or webhook certification requires a separately authorized integration run.

Give the user the concrete outcome and the next run, child/thread link, evidence, or blocker relevant to it. Do not imply work continues after handback without a real app-owned continuation mechanism.

The references reflect tool contracts inspected on 2026-10-27 and deliberately omit full schemas. Recheck live contracts before use. [Evaluation cases](evals/scenarios.json) test routing and reporting, not server integration.
