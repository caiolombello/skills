# Card and Backlog Practices

Use these templates when drafting, refining, auditing, or reporting delivery
work. Adapt field names to the real tracker configuration.

## Contents

1. Card template
2. Card conversation and confirmation
3. Definition of Ready
4. Splitting rules
5. Definition of Done
6. Backlog health review
7. Delivery status
8. Primary references

## 1. Card template

```markdown
# <Outcome-oriented summary>

## Context
<Who is affected, what happens today, and evidence/source.>

## Outcome
<Observable change expected for the user, client, system, or business.>

## Scope
- In:
- Out:

## Acceptance criteria
- [ ] <Observable condition>
- [ ] <Failure/edge condition when relevant>

## Dependencies and risks
- <Directionally linked dependency, owner, and decision date>

## Validation
- <Evidence required before acceptance/closure>

## Ownership
- Accountable owner:
- Contributors/reviewers:
- Decision owner:

## Traceability
- Goal/initiative:
- Related cards/incident/design:
- Priority authority/rationale:
```

Use a concise card, retain unresolved questions in the conversation, and
encode confirmation as observable acceptance criteria. Do not paste a meeting
transcript into the description.

## 2. Card conversation and confirmation

Before declaring a card ready:

- Confirm the requester and affected user/client are not being conflated.
- Resolve terms with different meanings across teams.
- Identify who can accept the outcome.
- Record decisions from comments or meetings back into the card.
- Convert examples into acceptance criteria without overfitting to one sample.
- Keep implementation choices open unless they are true constraints.

## 3. Definition of Ready

A card is ready only when:

- [ ] Problem/outcome and affected user/client are clear.
- [ ] Scope and non-goals are bounded.
- [ ] Acceptance criteria are observable.
- [ ] Required routing fields and issue type are valid.
- [ ] Dependencies and decision owners are known.
- [ ] External blockers have an owner and follow-up date.
- [ ] Priority source is explicit.
- [ ] Team supplied/accepted the estimate when estimation is required.
- [ ] Validation evidence is defined.
- [ ] No unresolved question would materially change the commitment.

`Not ready` is a useful state. Report the exact missing decision instead of
padding the card with assumptions.

## 4. Splitting rules

Split when a card has:

- Multiple independently valuable outcomes.
- Different accountable owners or acceptance authorities.
- Separate release or rollback paths.
- A discovery question mixed with committed implementation.
- Acceptance criteria that can complete independently.
- A scope too large to reason about in one delivery cycle.

Do not split purely by architecture layer when the resulting cards deliver no
independent outcome. Use subtasks for internal execution steps that share one
priority and acceptance decision.

## 5. Definition of Done

Adapt to the work type, but require:

- [ ] Acceptance criteria demonstrated or evidenced.
- [ ] Required tests/checks completed.
- [ ] Operational, security, documentation, or support obligations addressed
      when relevant.
- [ ] Linked dependencies and follow-ups updated.
- [ ] Requester/acceptance owner informed when required.
- [ ] Outcome measurement or post-release review scheduled.
- [ ] Remaining work represented honestly, not hidden in comments.

Status `Done` is not evidence by itself.

## 6. Backlog health review

Classify:

```markdown
| Card | Outcome/goal | Ready? | Owner | Blocker/dependency | Last meaningful update | Proposed action |
|---|---|---|---|---|---|---|
```

Look for:

- Duplicate outcomes.
- Stale or obsolete cards.
- Work without owner, goal, or acceptance.
- Dependency chains with no coordinating owner.
- Active work above team WIP/capacity.
- Repeatedly carried work that should be split or re-decided.
- Closed cards with untracked follow-up.

Archive or close only with authority and a preserved rationale.

## 7. Delivery status

```markdown
# Delivery status: <goal/team/date>

## Snapshot
- Goal/outcome:
- Confidence:
- Current commitment:

## Delivered and verified
- <outcome/evidence>

## In progress
| Work | Owner | Next evidence | Expected review |
|---|---|---|---|

## Blockers and decisions
| Blocker/decision | Impact | Owner | Needed by | Next action |
|---|---|---|---|---|

## Changes
- Scope/priority/date change:
- Authority/rationale:
- Displaced work:

## Risks and follow-up
- <risk, owner, trigger>
```

## 8. Primary references

- [Atlassian user stories](https://www.atlassian.com/agile/project-management/user-stories)
- [Atlassian backlog refinement](https://www.atlassian.com/agile/project-management/backlog-refinement-meeting)
- [Atlassian product and sprint backlogs](https://www.atlassian.com/agile/project-management/sprint-backlog-product-backlog)
