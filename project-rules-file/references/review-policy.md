# Optional project review policy

Use when a project needs reviewer-specific guidance or has recurring review failures. This is a guide/template, not a policy installed by reading it. Do not create `REVIEW.md` for every change or invent owners, checks, or approval counts.

Keep personal preferences in the user's global instructions. Put verified project invariants and operational context in its existing rules file. Put reviewer-specific priorities in a short `REVIEW.md` only when requested or explicitly part of the approved work.

## What changes a reviewer's decision

- Define failure for this product: incorrect documentation, misrouted config, cross-tenant access, lost offline data, incompatible clients, or other actual concerns. Use the project's real invariants, not this whole example list.
- Name sensitive boundaries, actual owners/approval requirements, and necessary checks with real paths/commands. State unknown/unconfigured controls honestly.
- Explain paths to skip and their reason, such as generated/vendor payloads with a verified source of truth. Exclusions cannot hide a risk introduced by the change; follow sources/consumers where necessary.
- Require supported findings: trigger, consequence, real file/line, reviewed version, and introduced/pre-existing/uncertain status. Keep material questions separate from confirmed defects. Do not require a quota of comments or nits.
- Re-review the incremental diff and affected findings, retain dispositions, and reassess after three corrective rounds without convergence. An ended loop does not approve unresolved risk.

## Small adaptable outline

```markdown
# Review priorities

## Failure and invariants
Describe the specific behavior/data/contracts this project must preserve.

## Sensitive changes and evidence
List actual paths, checks, and owner/approval rules; distinguish unknown controls.

## Scope and exclusions
Identify the source of truth for generated/vendor files and applicable exclusions.

## Findings and follow-up
Report actionable issues with scenario, impact, file/line, and version.
Separate introduced defects from pre-existing issues and open questions.
Review corrections incrementally and retain justified dispositions.
```

Remove irrelevant headings instead of filling a template to reach a length target. A review skill should explicitly read applicable `REVIEW.md` files; a filename alone is not a cross-client autoload mechanism. Check for stale or contradictory instructions against the source.

## Feedback that earns a permanent rule

When a failure recurs, choose the smallest durable prevention: deterministic test/lint/validation for mechanical checks; a concise instruction or good/bad example for a judgment or context problem. Prefer a regression case and a clean counterexample so false positives do not induce harmful edits.

Evaluate meaningful workflow changes against actual task outcomes as well as skill selection, quality, time/cost, and review rounds. Compare like tasks and conditions before attributing a failure to a model. Change one important rule at a time when practical. Do not demand a new evaluation platform for a minor wording edit or scrape personal histories without an authorized need.

Portable evaluation cases for the shared workflow live in [`code-review/evals/scenarios.json`](../../code-review/evals/scenarios.json); they are inputs for behavioral evaluation, not a certification of a client's runtime. The maintainer still needs real project-specific examples.
