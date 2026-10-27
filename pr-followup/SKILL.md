---
name: pr-followup
description: "Use when the user asks to monitor, watch, babysit, or follow up on a PR/MR through checks and review. Opening a PR alone does not start this workflow or authorize merge."
---

# PR Follow-up

Follow a pull request to the agreed endpoint without letting feedback expand its purpose. Use [`pr-workflow`](../pr-workflow/SKILL.md) to open or describe one; use this skill only when follow-up is requested or already authorized by the active workflow.

## Establish identity, authority, and endpoint

Read the current PR/MR and record its full URL, host/repository/number, base/head SHA, objective, relevant host policies, checks, required approvals, and unresolved review threads. An earlier finding can remain relevant after a push; inspect pending threads against current code instead of discarding them by timestamp.

Determine which actions the request authorizes: observation, corrections, branch updates, commits/pushes, external replies/resolution, merge, or closure. Reuse existing authorization; do not ask again for each routine step. A monitor-only request stays read-only. Do not infer merge or closure permission merely from "follow this PR" or green checks. State an endpoint if none was given: report readiness or a blocker, without merging.

Use actual runtime/client tools and host conventions. Never invent a PR identifier, account access, check result, approval, or a native tool that is absent.

## Use event-driven monitoring where available

On a host such as T3 Code, discover and follow the app-owned PR tools rather than starting a terminal polling loop. When `link_pull_request` is exposed, register each PR created, taken over, or pushed to, including every stack layer, using its full URL. Link immediately at the transition required by the host; registration is distinct from GitHub/GitLab operations.

If work still awaits checks/review and `watch_pull_request` is available, finish any authorized branch update and push, call the watcher, then end the turn. Follow wake payloads and the runtime's re-arm rules. Do not duplicate an active watcher or replace app-owned events with sleep, repeated status calls, `gh --watch`, a scheduler, or a private background watcher. If an earlier watch ended and continued work still needs one, re-arm as the runtime requires.

Before deliberately handing the PR back, call `unwatch_pull_request` when watching it. Report registration/watch errors rather than claiming they worked. A waiting handoff after registering a watcher is different from ending follow-up and returning ownership to the user.

In clients without an event mechanism, inspect current status with the installed CLI/API and use only an explicitly supported bounded waiting mechanism allowed by that runtime. Otherwise report the current state and the waiting limitation. Do not create an indefinite polling loop or claim that monitoring continues after the session has ended.

## Triage a new event against the current head

1. Refresh head/base and identify which checks or comments apply to the version now under review. Do not act on stale failure output as though it describes the latest head. Preserve older unresolved findings until evidence actually closes or rejects them.
2. Confirm every bot finding against the source and contract. Use [`receiving-code-review`](../receiving-code-review/SKILL.md) to accept, clarify, defer, or reject with evidence. Bot findings are hypotheses; bot approvals never fill a required human slot.
3. Distinguish a reproducible repository failure from an infrastructure outage/flake. Do not edit code just to appease an external failure. A retry, workflow rerun, rebase, or other host mutation still needs authority and must obey the runtime/project policy. Do not label an unresolved required check green.
4. Make only authorized, in-scope corrections and run relevant checks. Track the new head after a push; reassess affected evidence and approvals under the host's actual rules. Never use bypass/admin/force options just to finish.
5. When external replies are authorized, be concise and factual. Identify agent authorship according to the user's/project's convention; do not pretend the user personally verified a result. Resolve threads only with supporting evidence or a documented justified disposition. Otherwise prepare the reply for the user without posting it.

If a base change makes the PR obsolete, explain why and stop or reassess the requested goal. Do not close it without authorization. Do not automatically rebase an unrelated/shared branch or grow the PR to absorb every pre-existing issue a bot finds.

## Converge and stop

After a corrective round, review the new diff and affected findings, not the whole unchanged repository. Do not repeat accepted dispositions without new evidence. After three corrective rounds without convergence, stop the automatic correction loop and reassess; this does not mean three check events, require three rounds, clear blockers, or permit merge.

Stop at the authorized endpoint, a material blocker requiring a decision, a user stop/budget boundary, or the round bound. Do not keep a watcher running after deliberately handing responsibility back. Readiness requires current relevant checks, real approvals required by the project, and no unresolved material blocker; explicitly distinguish missing/unconfigured checks from passed checks.

Hand back a short state record:

```text
PR: <full URL>
Head: <actual SHA>
Checks: <current outcomes, pending/unavailable, and local-only evidence>
Reviews: <actual human/bot status and unresolved findings>
Actions: <authorized corrections, pushes, replies; or observation only>
Stop: <ready without merge / waiting via native watcher / blocker / user stop>
```

If acting as a delegated child, never take over the root's watcher. Return findings and the current PR/head/checks/reviews to the coordinator according to its output contract.

For maintenance validation, [evals/scenarios.json](evals/scenarios.json) contains synthetic workflow cases. Do not use real PR mutations to exercise them or interpret a passed exercise as native watcher/account certification.
