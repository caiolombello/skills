---
name: product-management
description: "Use when deciding what product work should happen and why: frame problems, outcomes, metrics, goals, roadmap themes, priorities, discovery evidence, and stakeholder tradeoffs. Not delivery tracking."
---

# Product Management

Turn product signals into explicit outcome, priority, and investment decisions.
Keep strategy evidence-backed and hand approved work to delivery without
pretending that activity or shipped scope is the outcome.

## Scope boundaries

Use this skill to:

- Frame customer or business problems and opportunities.
- Define product goals, outcomes, success metrics, and guardrails.
- Synthesize discovery evidence and identify evidence gaps.
- Compare options and make explicit prioritization tradeoffs.
- Build outcome-oriented roadmap themes and initiatives.
- Record product decisions, assumptions, and review dates.
- Review whether shipped work changed the intended outcome.

Do not use it as the primary workflow to:

- Maintain cards, sprints, dependencies, or delivery status — use
  [`delivery-coordination`](../delivery-coordination).
- Explore one vague idea before a direction exists — use
  [`brainstorming`](../brainstorming).
- Turn an approved initiative into a technical specification — use
  [`spec-first-planning`](../spec-first-planning).
- Design interface behavior — use [`frontend-design`](../frontend-design).

## Non-negotiables

1. Start from a problem or outcome, not a requested feature.
2. Separate evidence, inference, assumption, and decision.
3. Do not invent customer demand, market facts, revenue impact, urgency, or
   deadlines.
4. Do not treat stakeholder seniority as the priority model.
5. Treat scoring as decision support, not objective truth.
6. Do not promise dates or assign delivery capacity without the accountable
   team.
7. Preserve rejected and deferred options with the rationale and review
   condition.
8. Measure outcome and guardrails after release; shipping is not validation.

## Workflow

### 1. Establish the decision

Record:

- Product area, target users, business context, and decision owner.
- Decision to make and the deadline for making it.
- Current product goal and the outcome the decision should advance.
- Constraints, non-goals, and authority available to the agent.

If no accountable human can resolve conflicting priorities, report that as a
governance blocker rather than manufacturing consensus.

### 2. Build the evidence base

Collect the smallest useful set of:

- Customer interviews, support signals, usage data, and observed behavior.
- Commercial, operational, security, compliance, and strategic constraints.
- Existing experiments, shipped behavior, and prior decisions.
- Confidence, recency, representativeness, and known bias of each signal.

Label every statement as `observed`, `derived`, `assumed`, or `decision`.
Group duplicate requests by root problem instead of counting every request as a
separate opportunity.

### 3. Frame the opportunity

Write:

```text
For <target user>
who experiences <problem in context>,
improve <measurable outcome>
from <baseline> toward <target or direction>
while protecting <guardrail>.
```

If the baseline or target is unknown, state the measurement task needed before
committing to a target.

### 4. Compare options

Include the no-change option. For each option, evaluate:

- Expected outcome contribution.
- Evidence strength and confidence.
- Reach and affected users.
- Strategic, revenue, risk, or compliance relevance.
- Delivery effort and opportunity cost, supplied by the responsible team.
- Dependencies, reversibility, and learning value.
- Risks and guardrail impact.

Recommend one option when authority and evidence allow it. Otherwise identify
the exact decision owner, missing evidence, and decision date.

### 5. Prioritize transparently

Choose criteria that fit the decision. Do not combine incomparable numbers into
a decorative score. A useful priority record includes:

```text
decision = do now | discover next | defer | reject
rationale = outcome + evidence + tradeoff
confidence = high | medium | low
owner = accountable human
review trigger = date, metric, dependency, or new evidence
```

Keep mandatory security, compliance, or contractual work visible as explicit
constraints; do not disguise it as customer delight or revenue.

### 6. Build the roadmap

Organize the roadmap as:

```text
product goal -> outcome/theme -> initiative or experiment -> measure
```

Use time horizons only when they communicate confidence and sequencing. A
roadmap is not a list of every requested feature and not a date promise.
Capture dependencies and assumptions that could change sequencing.

### 7. Hand off for delivery

For each approved initiative, provide:

- Problem, target user, outcome, and success measure.
- Evidence and decision rationale.
- Scope boundaries and non-goals.
- Guardrails, risks, and unresolved questions.
- Product owner and decision owner.
- Review date and expected learning.

Then use [`delivery-coordination`](../delivery-coordination) to create or refine
the delivery structure. Keep product acceptance separate from technical task
completion.

### 8. Review outcomes

After release or experiment completion:

- Compare the metric with its baseline and guardrails.
- Distinguish adoption, behavior, business result, and operational health.
- Record confounders and confidence.
- Decide to continue, iterate, roll back, scale, or stop.
- Update the roadmap and decision log with learned evidence.

Read [references/product-artifacts.md](references/product-artifacts.md) when
drafting a product brief, prioritization record, roadmap, decision log, or
outcome review.

## Required output

Lead with:

1. `Decision snapshot` — decision, owner, deadline, and current recommendation.
2. `Outcome` — target user, problem, measure, baseline/target, and guardrails.
3. `Evidence` — observed signals, confidence, and gaps.
4. `Options and tradeoffs` — including no change.
5. `Priority/roadmap impact` — now, next discovery, defer, or reject.
6. `Delivery handoff` — approved initiative context, not an invented task list.
7. `Review plan` — measure, date, and decision trigger.

## Interaction with other skills

- [`brainstorming`](../brainstorming) — shapes one rough idea before product
  commitment.
- [`delivery-coordination`](../delivery-coordination) — governs the operational
  backlog and delivery flow after a product decision.
- [`spec-first-planning`](../spec-first-planning) — creates the technical spec
  and implementation tasks for approved work.
- [`frontend-design`](../frontend-design) — designs user-facing flows and
  interaction details.
- [`aidlc-workflow`](../aidlc-workflow) — coordinates a complete auditable
  lifecycle when explicitly requested.

## Verification checklist

- [ ] The decision owner, target user, and outcome are explicit.
- [ ] Evidence, assumptions, and decisions are distinguishable.
- [ ] At least one alternative and the no-change option were considered.
- [ ] Priority rationale includes opportunity cost and confidence.
- [ ] The roadmap is outcome-oriented and does not fabricate commitments.
- [ ] Approved work has a bounded delivery handoff.
- [ ] Outcome review has a measure, owner, and trigger.
