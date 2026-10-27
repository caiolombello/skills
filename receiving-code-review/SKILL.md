---
name: receiving-code-review
description: "Use when handling human, bot, or subagent review feedback. Verify findings, classify them, and make only authorized, in-scope corrections with evidence."
---

<!-- Inspired by obra/superpowers receiving-code-review (MIT). See ../CREDITS.md -->

# Receiving Code Review

Good review handling is a workflow: understand the feedback, classify it, respond professionally, change only what is warranted, and verify again. Do not reflexively implement every comment; do not defensively reject real problems.

## When to use

- Review comments arrive on a PR/MR.
- A subagent reviewer reports findings.
- CI or static analysis produces actionable feedback.
- The user asks to address review feedback.
- You need to decide whether a comment is a blocker, follow-up, or misunderstanding.

## The loop

```
COLLECT -> CLASSIFY -> PLAN -> APPLY -> VERIFY -> RESPOND
```

## 1. Collect all feedback

Read every comment before changing anything. Group duplicates.

Capture:

- Source: human reviewer, automated check, subagent, CI.
- Location: file/line or topic.
- Requested change.
- Severity, if provided.
- Whether it blocks merge.
- Reviewed head/base or snapshot, triggering scenario, evidence, and whether the issue is introduced, pre-existing, or uncertain.

## 2. Classify

Use four buckets:

| Bucket | Meaning | Action |
|---|---|---|
| Accept | Correct and in scope | Fix now |
| Clarify | Ambiguous or based on uncertain assumption | Ask/verify before changing |
| Defer | Valid but outside this change | Track as follow-up if user wants |
| Reject | Incorrect or harmful | Explain with evidence |

Treat every finding as a hypothesis, including comments labeled security, correctness, data loss, or missing coverage. Inspect the current artifact and contract before accepting it. A plausible risk deserves investigation; a label, confident bot, or majority vote does not prove the defect. Separate an unconfirmed question from a supported finding.

Compare against the base when relevant. A pre-existing issue unrelated to the change does not authorize a drive-by fix. Respect an applicable policy that requires resolving a material issue, without pretending this PR introduced it.

## 3. Plan the response

Before editing, establish the dispositions and scope. A short action list is useful for several findings; keep it internal for a routine correction unless the user asks for the plan:

```markdown
Review response plan:
- Accept: <comment id/topic> -> <change>
- Clarify: <comment id/topic> -> <question/evidence needed>
- Defer: <comment id/topic> -> <why out of scope>
- Reject: <comment id/topic> -> <evidence>
```

If multiple comments affect the same code, resolve them together to avoid churn.

Verify missing context from available sources first. Ask only when an essential decision cannot be resolved within the existing authorization; do not turn every ambiguity into a routine confirmation.

## 4. Apply surgically

Only change lines needed to address accepted feedback. Do not sneak in unrelated improvements.

For each accepted comment:

- Add or adjust tests when behavior changes.
- Keep style consistent with the touched file.
- Preserve public API compatibility unless the review explicitly calls for a breaking change and the user approves.
- Update docs only if the review asks or existing docs become wrong.

## 5. Verify again

Run the smallest relevant verification first, then the broader suite if appropriate:

- Targeted test for changed behavior.
- Lint/typecheck if code shape changed.
- Full test/build command required by the repo or PR.

Do not mark a review comment resolved without evidence and authority to update the host. Revalidate checks affected by new changes and identify the head they cover. Bot approval does not replace a human approval required by the project.

## Re-review and convergence

Use the incremental diff, affected dependencies, and unresolved findings after a correction. Carry forward dispositions so rejected/resolved feedback is not reopened without new evidence. Do not widen scope to chase historical bugs. Follow the bounded corrective loop in [`code-review`](../code-review/SKILL.md): one pass may suffice; after three corrective rounds without convergence, reassess rather than continuing automatically. Ending the loop does not clear a blocker.

## 6. Respond to reviewers

Responses should be concise and factual:

Post external replies or resolve threads only when authorized by the request or active workflow. Otherwise provide the proposed response to the user. Reuse existing authorization rather than requesting it again for every routine action.

- Accepted: "Fixed in `<commit/file>`; added coverage for `<case>`."
- Clarify: "I may be missing context. Do you mean `<A>` or `<B>`?"
- Deferred: "Agreed this is valuable, but it is outside this PR because `<reason>`. Proposed follow-up: `<ticket/task>`."
- Rejected: "I don't think this change is safe because `<evidence>`. Current behavior is covered by `<test/spec>`."

Never argue from preference. Use evidence.

## Handling conflicting reviews

When reviewers disagree:

1. Identify the actual decision.
2. List both positions and their tradeoffs.
3. Check project conventions or ADRs.
4. Ask the owner/maintainer to choose if no rule exists.

Do not pick the easier change silently.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Implementing every comment blindly | Can make code worse or expand scope |
| Dismissing comments defensively | Misses real defects |
| Fixing one comment at a time without reading all | Creates churn and contradictory edits |
| Resolving without tests | No evidence the feedback was addressed |
| Drive-by refactors | Makes review harder |

## Verification checklist

- [ ] All comments were read before editing.
- [ ] Findings were checked against the current version and their triggering scenarios, not accepted by label or reviewer authority.
- [ ] Each comment is classified as accept/clarify/defer/reject.
- [ ] Accepted comments have targeted changes and tests where needed.
- [ ] Clarifications are asked before speculative edits.
- [ ] Verification commands were run after changes.
- [ ] Reviewer responses are concise and evidence-based.
