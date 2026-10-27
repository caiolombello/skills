---
name: project-verification
description: "Use to create, repair, or maintain a reusable project-specific verification harness/skill for real UI, CLI, library, or service journeys. Routine test runs and final completion reports belong to verification-before-completion."
---

<!-- Inspired by cursor/plugins pstack create/maintain-verification-skill (MIT). See ../CREDITS.md. -->

# Project Verification

Leave a repeatable way for the next agent to exercise a real project behavior and inspect the result. Use existing project checks first. Do not generate a harness, feature inventory, or local skill merely because an ordinary edit needs testing.

## Define the boundary

Identify the requested create/repair/maintenance task, target project/area, allowed writes, runtime surface, and useful completion evidence. Reuse existing authorization. A request for a reusable project skill authorizes its necessary instructions/helpers; it does not authorize product fixes, dependency installation, external sends, production changes, or broader documentation by default.

Inspect repository rules, native build/test scripts, nearest integration tests, app entry points and any existing verification skill. Determine commands, supported versions, data/auth prerequisites, readiness signal, control interface, observable effects, and isolation/teardown. Do not invent commands or selectors from a generic stack recipe. Reuse Playwright/PTY/HTTP/test tooling already present when suitable and permitted; no universal browser dependency.

## Create or repair

Write in the project's actual skill/harness location, preserving its native metadata and conventions. When a new location is needed, choose the applicable discoverable project-local path; do not assume `.cursor/skills` in every client. Keep these parts executable or grounded in observed behavior:

1. **Launch and ready:** exact command and a usable-state check, including initialization required for the chosen journey. A listening port or healthy DB alone may precede readiness. Record the build/revision actually served.
2. **Doctor:** a read-only check for the right instance, version, owned port/process or session, relevant access, and prerequisites. Run it before driving and after a surprising failure; a healthy process may still need a UI reset to a known state.
3. **Drive:** one useful user/API/library journey using supported stable handles and real public interfaces. Do not prove a user workflow solely through internal setters, a test-only bypass endpoint, or a final screen preloaded with the answer. Existing mocks are appropriate only for the boundary they isolate; identify what they leave unverified.
4. **Evidence:** the action and resulting state, suitable persistent-effect readback, exact command/outcome, checked snapshot, and durable artifact paths. A dry-run name is not proof of no effects: inspect its behavior before using it with real resources.
5. **Cleanup:** stop only instances/sessions this task created, using exact handles. Never kill by process-name match. Remove temporary test state, preserve evidence, and clean failed attempts as well as successful ones.

Prefer a disposable data directory/profile, explicit test database and non-conflicting port to the user's active instance. If isolation is unavailable, report that boundary instead of writing to real state. Use [computer-use](../computer-use/SKILL.md) for UI driving and the current host's rules, including restrictions on browser checks. A generated recipe cannot override those restrictions.

Keep a small journey index only when multiple entry points/features need navigation. Start with the requested area; expand to related journeys when they change coverage. Do not generate a file for every route or pretend a partial map covers the whole product. Each maintained journey needs prerequisites, entry path, actions, observable success, important failure cases, and known coverage gaps.

## Prove the procedure

Run the generated launch, doctor, selected journey, evidence capture and cleanup in an authorized isolated environment. Confirm evidence survives cleanup. Fix procedure defects and rerun affected steps; do not keep changing the journey's expected behavior until it passes. An impossible precondition is a coverage gap, not a passed path.

For a regression detector, validate a realistic failure case when useful and permitted, using disposable fixture/code state. Do not inject failures into active data. A harness that only prints success without checking an observable result has not been validated.

If the environment prevents execution, deliver the procedure as a draft with the exact blocker and unrun steps. A substitute environment establishes only what it exercised; list target prerequisites it did not cover. General reporting follows [verification-before-completion](../verification-before-completion/SKILL.md).

## Maintain against the current project

Read the existing procedure and the covered code changes since its recorded snapshot. Identify moved/added entry points, changed prerequisites, selectors, contracts and cleanup. Reconcile source with observable behavior; do not assume a green old harness still describes the product.

Choose coverage proportional to changes and consequences. For a requested full audit, enumerate the promised journeys and report source/runtime coverage for each; otherwise focus on changed and affected paths. Parallel read-only source work can help, but retain one controller per app instance or use independently isolated instances. There is no mandatory agent per feature.

Classify **instruction drift**, **harness defect**, **product regression**, and **unavailable prerequisite** separately. Under maintenance-only scope edit the verification artifacts, not product code. Do not rewrite documented expected behavior to hide a regression or silently drop an unreachable journey. Re-drive affected harness fixes and preserve unresolved gaps.

## Handoff

Give the checked revision/environment, covered journeys, commands/results, artifact paths, cleanup outcome, unresolved scope, and one command or procedure to rerun. Report draft/blocked, verified within named coverage, or updated with remaining gaps accurately. Installation/discovery, actual execution, CI, and production are separate claims. Do not create a recurring maintenance job or publish a PR unless authorized.

[Evaluation cases](evals/scenarios.json) include incomplete runs and maintenance drift; they do not certify an app integration.
