---
name: architecture-decision-records
description: Capture significant technical decisions as short, version-controlled Architecture Decision Records (ADRs). An ADR is 1-2 pages that answer "what did we decide, why, and what else did we consider?". Use WHENEVER (1) the user or the team makes a non-trivial technical decision that will constrain future work — choosing a framework, picking a data store, adopting a pattern, setting a policy, accepting a trade-off; (2) the user asks to "document a decision", "write an ADR", "capture the rationale", "we need to remember why we did X"; (3) onboarding reveals that no one remembers why a load-bearing choice was made; (4) a PR introduces a decision with long-term consequences and the reviewer asks "is this an ADR?"; (5) deprecating or replacing a prior decision — write a new ADR that `Supersedes` the old one instead of editing the old one. Uses MADR (Markdown Architectural Decision Records) as the default format. Pairs with `project-rules-file` (which references ADRs from the rules file).
---

# Architecture Decision Records (ADRs)

An ADR is a short, immutable record of a technical decision: **what we decided, why, what else we considered, and what the consequences are**. Typically 1-2 pages of Markdown under `docs/adr/` (or equivalent), committed with the code it governs.

ADRs exist because the *reasoning* behind a decision usually outlives the people and context that produced it. Six months later the commit author is gone, the spec is gone, the Slack thread is gone — the ADR is still there.

## When to write an ADR

Write an ADR when a decision has **long-term consequences** and no obvious home. Concretely:

- Choosing a framework, database, messaging system, or core library.
- Adopting or rejecting an architectural pattern (event-driven, CQRS, multi-tenancy model, DDD, hexagonal, ...).
- Setting a policy that every service in the org must follow (logging format, auth model, SLO defaults).
- Accepting a deliberate trade-off ("we chose eventual consistency here because...").
- Reversing or replacing a prior decision.
- An outcome of [`spec-first-planning`](../spec-first-planning) or [`doubt-driven-review`](../doubt-driven-review) where the decision is load-bearing.
- A [`throwaway-prototype`](../throwaway-prototype) converged on an answer worth recording before deleting the prototype.

### When NOT to write an ADR

- Bikeshed-level style choices the formatter enforces.
- Temporary workarounds — put a code comment.
- Reversible UI tweaks, copy changes.
- Decisions that affect only one file and will not propagate.
- Personal preferences that the project does not enforce.

If removing the ADR six months later would not change anyone's behavior, it should not exist.

## Where they live

- `docs/adr/` at the repo root, or `docs/architecture/decisions/` — whatever the org standard is.
- Filenames: `NNNN-short-kebab-title.md` — zero-padded numeric prefix + kebab description.
  - `0001-use-postgresql-for-transactional-data.md`
  - `0002-event-driven-with-kafka-for-fanout.md`
- Numbering is **global within the repo**, monotonically increasing. Do not renumber.
- Committed with the change they describe, not after.
- Linked from `AGENTS.md` / `CLAUDE.md` / project rules file so the agent knows they exist — see [`project-rules-file`](../project-rules-file).

## Format — MADR (default)

[MADR — Markdown Architectural Decision Records](https://adr.github.io/madr/) is the de-facto modern format. Predictable, scannable, AI-friendly.

### Minimal MADR

```markdown
# ADR NNNN: <short imperative title>

- Status: <Proposed | Accepted | Deprecated | Superseded by ADR-XXXX>
- Deciders: <names or roles>
- Date: YYYY-MM-DD
- Tags: <optional: e.g. data, security, api>

## Context and problem statement

<Describe the context and the specific question being decided, in 2-4 sentences. What is the situation? Why is a decision needed now?>

## Decision

<One paragraph. The decision in plain language. Use imperative voice: "We use Postgres for transactional data", not "We will consider using Postgres".>

## Consequences

<Positive, negative, and neutral outcomes that follow from this decision. Honest trade-offs — not a marketing brochure.>

- **Positive**: <consequence>
- **Negative**: <consequence>
- **Neutral**: <consequence>
```

### Expanded MADR (use when the decision has real options)

Add these sections between **Context** and **Decision**:

```markdown
## Decision drivers

- <constraint, quality attribute, or goal this decision must satisfy>
- <...>

## Considered options

1. <Option A> — <one-line description>
2. <Option B> — <one-line description>
3. <Option C> — <one-line description>

## Decision outcome

Chosen option: **Option A**, because <primary reason tied to the drivers>.

### Consequences

<as above>

## Pros and cons of the options

### Option A — <name>

- ✓ <pro tied to a decision driver>
- ✓ <pro>
- ✗ <con>
- ✗ <con>

### Option B — <name>

- ✓ <pro>
- ✗ <con>

### Option C — <name>

- ✓ <pro>
- ✗ <con>

## Links

- [Related ADR NNNN: …](./NNNN-…​.md)
- [Spec / RFC / issue / design doc]
- [Upstream / vendor docs if the decision depends on them]
```

## Lifecycle and status

ADRs are append-only. Do not edit a decided ADR. Instead:

| Status | Meaning |
|--------|---------|
| `Proposed` | Under discussion. Not yet in effect. |
| `Accepted` | Effective. The project follows this. |
| `Deprecated` | No longer recommended, but still present. Usually replaced by a newer ADR. |
| `Superseded by ADR-NNNN` | A later ADR replaces this one. Old ADR stays for the history. |

### Superseding an ADR

When a decision changes, **write a new ADR** that supersedes the old one. Do **not** edit the old ADR.

In the old ADR, update only the front matter:

```markdown
- Status: Superseded by [ADR 0017](./0017-switch-to-cockroachdb.md)
```

In the new ADR, include a **Relationship** section pointing back:

```markdown
## Relationship

Supersedes [ADR 0008: Use PostgreSQL for transactional data](./0008-use-postgresql-for-transactional-data.md).

### What changed and why

<2-4 sentences on what forced the replacement>
```

This pattern preserves history. Future readers can follow the chain and understand how the current state evolved.

## Writing a good ADR

### Title

- Imperative or declarative, **not** a question: "Use Postgres for transactional data", not "Which database should we use?".
- Short enough to fit a filename (`<= 60 chars`).
- Specific enough to tell two adjacent ADRs apart.

### Context

- 2-4 sentences. Enough context that a new hire two years from now can understand the situation without asking you.
- State the **forces** or **constraints** — compliance, latency targets, team skill, budget. This is what makes the decision defensible later.
- Include a pointer to the spec / issue / incident that triggered the decision.

### Decision

- One paragraph. Imperative. "We use X." "We adopt Y for Z."
- Specific enough that there is no ambiguity about what "doing it" means.
- If the decision has conditions or exceptions, list them explicitly.

### Consequences

- Be honest about the downsides. An ADR that only lists positives is a sales pitch, not a decision record.
- Tie consequences to the decision drivers — "we accept slower writes (driver: prefer durability over throughput)".
- Include **operational** consequences (cost, ops complexity, on-call load), not only architectural ones.

### Options (when used)

- List at least **two serious alternatives** — "do nothing" is often one of them.
- For each, include 2-4 pros and 2-4 cons tied to the drivers.
- If you only considered one option, do not lie about having considered others. Just say so in the Context: "Given the team's existing Postgres expertise and the 4-week deadline, we did not evaluate other stores."

## Minimal working example

```markdown
# ADR 0004: Use feature flags for all user-visible behavior changes

- Status: Accepted
- Deciders: Platform team, Product engineering leads
- Date: 2024-08-14
- Tags: release, risk-management

## Context and problem statement

Our current release process ships behavior changes as code deploys. Rollback
requires re-deploying the previous version, which takes ~6 minutes and blocks
the deploy pipeline. Two recent SEV-2s (2024-07-02, 2024-07-29) had user
impact that would have been resolved in seconds with a flag flip.

## Decision drivers

- Reduce time-to-mitigate for SEV-1 and SEV-2 product bugs.
- Allow product to A/B test without a code change per experiment.
- Keep operational overhead bounded (we cannot afford a heavyweight platform).

## Considered options

1. LaunchDarkly SaaS.
2. Unleash self-hosted.
3. Home-grown flag table + Redis cache.

## Decision outcome

Chosen option: **Unleash self-hosted**, because it meets all drivers while
staying inside our existing infra envelope and avoids per-seat SaaS costs
that scale badly with our headcount plan. Team has Postgres + Docker
Compose baseline skills to run it.

### Consequences

- **Positive**: flag flip measured in seconds; experiment framework comes for free.
- **Positive**: no per-seat cost growth; self-hosted on existing RDS.
- **Negative**: one more service to run, patch, and monitor.
- **Negative**: flag rot will happen without a cleanup policy — mitigation in ADR 0005.
- **Neutral**: engineering culture shift — code paths must be structured around flags.

## Pros and cons of the options

### Option 1: LaunchDarkly SaaS

- ✓ Fully managed; zero ops.
- ✓ Rich targeting and experimentation UI.
- ✗ Per-seat pricing scales badly with headcount plan (~$NN/seat/month).
- ✗ PII in flag evaluation payload raises compliance review.

### Option 2: Unleash self-hosted

- ✓ Open source; no per-seat cost.
- ✓ Good SDK coverage (Node, Go, Python, Java).
- ✓ Runs on existing Docker + RDS.
- ✗ We own ops, patching, observability.
- ✗ Smaller targeting feature set than LaunchDarkly.

### Option 3: Home-grown flag table

- ✓ Fully under our control.
- ✗ Re-inventing features (variants, targeting rules, kill switches).
- ✗ No SDK ecosystem; each language needs new client code.
- ✗ Operational burden grows with feature requests.

## Links

- [Incident postmortem 2024-07-02](../incidents/2024-07-02-checkout-5xx.md)
- [Unleash documentation](https://docs.getunleash.io/)
- [ADR 0005: Feature-flag lifecycle and cleanup policy](./0005-feature-flag-lifecycle.md)
```

## Tooling

- [`adr-tools`](https://github.com/npryce/adr-tools) — bash-based; creates, links, supersedes.
- [`adr-manager`](https://adr.github.io/adr-manager/) — a GUI / web tool for MADR.
- Any agent with a rules file pointing at `docs/adr/` — the agent can grep, quote, and supersede.

Prefer `adr-tools` or its port for your stack. It automates the numbering and the supersedes link.

## Integration with the rest of the workflow

- The [`project-rules-file`](../project-rules-file) should reference the ADR directory and the convention for writing new ones: a 2-line "Decisions" section pointing at `docs/adr/`.
- [`code-review`](../code-review) — when a PR makes a decision that would have been worth an ADR, block until one is written.
- [`spec-first-planning`](../spec-first-planning) — the Plan phase's technical decisions often become ADRs by the end of the feature.
- [`diagnose`](../diagnose) / [`incident-response`](../incident-response) — "we did not know why X was this way" is almost always an ADR gap.
- [`throwaway-prototype`](../throwaway-prototype) — capture the answer of a prototype in an ADR before deleting the code.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| ADR is 10 pages of background | Nobody reads it. Summarize; link the long version. |
| Mutating an accepted ADR to change the decision | Destroys history; readers cannot tell what changed or when |
| ADR with only "pros" | Signals advocacy, not decision. Low trust. |
| No alternatives listed | Reader cannot judge whether the choice was robust |
| Generic title ("Use a database") | Cannot locate, cannot search |
| No status field | Reader cannot tell if it is still in force |
| ADR exists but not linked from the rules file | Invisible to agents and new hires |
| ADRs stored on a wiki / Confluence outside the repo | Drifts from code, harder to version, often stale |
| Writing ADRs retroactively for every decision ever made | Noise drowns the signal |
| Writing ADRs for trivial choices | Noise drowns the signal |
| Numbering resets (two ADRs with the same number) | Breaks linking |

## Verification checklist

Before merging an ADR:

- [ ] Filename follows `NNNN-kebab-title.md`, with a unique monotonically increasing `NNNN`.
- [ ] Title is imperative and specific; fits on one line.
- [ ] Status, Deciders, Date are filled.
- [ ] Context is 2-4 sentences and names the forces driving the decision.
- [ ] At least two options considered (or the Context explicitly states why not).
- [ ] Consequences include honest negatives, not only positives.
- [ ] Links to the triggering issue / spec / postmortem.
- [ ] If this supersedes an older ADR, both ADRs reference each other and the old one's status is updated.
- [ ] ADR is referenced from the rules file or the architecture doc.
- [ ] The PR that introduces the ADR also includes the code / config change that enacts the decision, or references where it will land.
