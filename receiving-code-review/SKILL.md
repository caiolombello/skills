---
name: receiving-code-review
description: Process code review feedback without ego, thrash, or scope creep. Use WHENEVER (1) the user pastes PR/MR review comments; (2) a reviewer/subagent returns findings; (3) CI/code review requests changes; (4) you need to decide which review comments to accept, clarify, defer, or reject; (5) applying review feedback across code, tests, docs, or commits. Complements code-review and pr-workflow by turning feedback into verified follow-up changes.
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

## 2. Classify

Use four buckets:

| Bucket | Meaning | Action |
|---|---|---|
| Accept | Correct and in scope | Fix now |
| Clarify | Ambiguous or based on uncertain assumption | Ask/verify before changing |
| Defer | Valid but outside this change | Track as follow-up if user wants |
| Reject | Incorrect or harmful | Explain with evidence |

Default to accepting correctness, security, data-loss, and test-coverage findings unless evidence says otherwise.

## 3. Plan the response

Before editing, produce a short action list:

```markdown
Review response plan:
- Accept: <comment id/topic> -> <change>
- Clarify: <comment id/topic> -> <question/evidence needed>
- Defer: <comment id/topic> -> <why out of scope>
- Reject: <comment id/topic> -> <evidence>
```

If multiple comments affect the same code, resolve them together to avoid churn.

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

Do not mark a review comment resolved without evidence.

## 6. Respond to reviewers

Responses should be concise and factual:

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
- [ ] Each comment is classified as accept/clarify/defer/reject.
- [ ] Accepted comments have targeted changes and tests where needed.
- [ ] Clarifications are asked before speculative edits.
- [ ] Verification commands were run after changes.
- [ ] Reviewer responses are concise and evidence-based.
