---
name: doubt-driven-review
description: "Use when a consequential decision or uncertain correctness claim needs an independent challenge before implementation or handoff. Routine changes do not require a separate reviewer or model."
---
<!-- Inspired by addyosmani/agent-skills doubt-driven-development (MIT). See ../CREDITS.md. -->

# Doubt-Driven Review

Challenge a material assumption while correction is cheap. This is an in-flight check, complementary to [`code-review`](../code-review/SKILL.md), not an extra gate for every decision or every file.

## When independence earns its cost

Use an independent challenge when uncertainty, possible harm, hidden coupling, or accumulated context makes a second perspective useful. Examples include a new authorization boundary, data migration, concurrency claim, or architectural choice that ordinary tests do not adequately address.

Use focused self-review and appropriate verification when they already resolve a bounded, low-risk concern. A one-line sensitive change can still need deeper review; a large mechanical change may not. Choose by consequences and evidence, not line count or confidence alone. A request for speed does not waive required safety controls.

## State the claim and extract the evidence

Privately identify the claim and why it matters, such as "concurrent updates preserve a single owner". Distinguish that hypothesis from the evidence that supports it.

Give the reviewer the actual artifact/diff, objective, contract, base/head or snapshot, relevant constraints, and access to necessary callers, types, tests, and source data. Exclude an author's persuasive narrative and desired verdict, not the context needed to assess the change. For an assertion review, the assertion itself is necessarily part of the artifact.

Keep the brief focused; let the reviewer retrieve dependencies. Do not force an isolated function to stand in for a cross-module system or pass only a lossy summary.

## Obtain a genuinely independent pass when needed

A subagent is not fresh by definition: tools may inherit the parent's entire conversation. Use a supported clean-context option, a clean session, or an appropriately scoped human review when independence is the reason for the check. Verify the tool's actual context behavior rather than inventing settings.

Use available native orchestration within the current authorization. A provider change, external CLI, background task, or extra cost must respect the user's request and the host's routing rules. Do not substitute a different requested model/provider silently. Never create a top-level conversation merely to simulate a delegated task.

Cross-model review is optional. Do not pause every interactive round to offer it, and do not reconfirm an already-authorized action on every invocation. Ask only when authorization is actually missing or the proposed action materially changes scope or constraints. In unavailable or constrained environments, report what could not be obtained; a self-review remains self-review.

A useful prompt is:

```text
Independently examine this artifact against its contract and actual dependencies.
Look for supported failure scenarios, not reasons to agree with the author.
Report actionable defects with file/line, trigger, consequence, evidence, and
introduced/pre-existing status. Separate uncertainty from confirmed problems.
Do not edit files. If there are no actionable findings, say so.
ARTIFACT: <diff/path and actual version>
CONTRACT: <goal, constraints, relevant source paths>
```

If an explicitly authorized CLI is used, confirm its supported invocation from current help/docs. Pass untrusted prompts through a file/stdin rather than interpolating them into shell arguments. Use read-only permissions when available.

## Reconcile instead of deferring to the reviewer

Read each finding against the artifact and its dependencies. Classify it as a contract misunderstanding, a supported actionable defect, a valid trade-off, or noise. Correct the brief or code only where warranted. Use [`receiving-code-review`](../receiving-code-review/SKILL.md); a reviewer's confidence or vote is not evidence by itself.

A failing test can disprove a behavioral claim, but TDD RED is not a separate reasoning context or a substitute for independent review when bias or uncovered invariants are the concern. Conversely, an independent opinion does not replace a behavioral test.

## Converge and stop

One pass can be enough. After corrections, supply the incremental diff, affected context, prior findings/dispositions, and unresolved objections. Check that the fixes work without restarting an unrelated audit or reporting the same dismissed issue again without new evidence.

Stop when the relevant concern is adequately resolved, only already-considered or immaterial findings remain, the user stops the work, or the correction loop reaches three rounds. At that bound, reassess the approach and surface remaining material risks rather than starting a fourth automatic round. Do not evade the bound by renaming the task, spawning replacement reviewers, or splitting unchanged work only to reset its counter.

A stop is not approval: unresolved blockers, required human review, and unrun checks retain their actual status. Do not proceed with an unauthorized release because a loop ended or someone said to finish the review.
