# Product Artifacts

Use only the artifacts needed for the decision. Keep them concise and link to
the authoritative evidence instead of copying entire source documents.

## Contents

1. Product decision brief
2. Evidence ledger
3. Prioritization record
4. Outcome roadmap
5. Decision log
6. Outcome review
7. Primary references

## 1. Product decision brief

```markdown
# Product decision: <name>

## Decision
- Owner:
- Decision deadline:
- Current recommendation:
- Confidence:

## Problem and outcome
- Target user:
- Context/problem:
- Baseline:
- Desired outcome:
- Success measure:
- Guardrails:

## Evidence
| Signal | Type | Source/date | Confidence | What it supports |
|---|---|---|---|---|

## Options
| Option | Outcome contribution | Tradeoffs | Evidence | Reversibility |
|---|---|---|---|---|

## Scope
- In:
- Out:

## Open decisions
| Decision | Owner | Needed by | Consequence if late |
|---|---|---|---|

## Review
- Review date/trigger:
- Evidence expected:
```

## 2. Evidence ledger

Classify each signal:

| Type | Meaning |
|---|---|
| `observed` | Directly measured, read, or heard from a named source |
| `derived` | Calculation or synthesis reproducible from observations |
| `assumed` | Unverified belief that can change the decision |
| `decision` | Chosen direction by an accountable authority |

For every entry, retain source, date, scope, confidence, and possible bias.
Do not convert the number of requests directly into reach without accounting
for duplicates and representativeness.

## 3. Prioritization record

Prefer a decision table over an unexplained aggregate score:

```markdown
| Opportunity | Outcome | Evidence/confidence | Urgency or cost of delay | Risk/compliance | Effort/dependencies | Decision |
|---|---|---|---|---|---|---|
```

Use:

- `do now` — sufficiently evidenced and aligned; delivery capacity approved.
- `discover next` — important, but a named uncertainty blocks commitment.
- `defer` — valid opportunity displaced by a stronger one; include review
  trigger.
- `reject` — does not support the current outcome or has unacceptable
  tradeoffs; preserve rationale.

If using RICE, WSJF, or another scoring method, expose every input and its
source. Do not let a computed value override mandatory constraints or
accountable judgment.

## 4. Outcome roadmap

```markdown
| Horizon | Outcome/theme | Why now | Initiative/experiment | Measure | Confidence | Dependencies |
|---|---|---|---|---|---|---|
```

Rules:

- Keep horizon language distinct from date commitments.
- Show outcome and measure before initiative names.
- Limit work in progress at the initiative level.
- Include discovery work when uncertainty is the main blocker.
- Move an item only with an updated rationale.

## 5. Decision log

```markdown
| Date | Decision | Owner | Evidence | Alternatives | Tradeoff | Review trigger |
|---|---|---|---|---|---|---|
```

Record a new entry when a decision changes. Do not rewrite history.

## 6. Outcome review

```markdown
# Outcome review: <initiative>

- Product goal/outcome:
- Release or experiment window:
- Baseline:
- Result:
- Guardrails:
- Confidence/confounders:
- Customer or operational evidence:
- Decision: continue | iterate | scale | roll back | stop
- Owner:
- Next review:
```

Separate:

- Delivery: what was shipped.
- Adoption: whether intended users used it.
- Behavior: whether user behavior changed.
- Business outcome: whether the target metric moved.
- Operational health: reliability, support, security, and cost effects.

## 7. Primary references

- [Atlassian product management](https://www.atlassian.com/agile/product-management)
- [Atlassian product owner](https://www.atlassian.com/agile/product-management/product-owner)
- [Atlassian product backlog](https://www.atlassian.com/en/agile/scrum/backlogs)
