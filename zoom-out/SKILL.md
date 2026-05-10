---
name: zoom-out
description: Step back and provide a higher-level map of a section of code instead of diving straight into details. Use WHENEVER (1) the user explicitly says "zoom out", "give me the big picture", "how does this fit together", "where does X live"; (2) the agent is unfamiliar with an area of code and is about to guess; (3) a task requires understanding how several modules interact before picking where to change something; (4) the user asks "what is this codebase", "how is this project structured", "what are the main parts"; (5) after resuming a paused session in an unfamiliar area. The output is a short map — modules, callers, data flow — using the project's own vocabulary, NOT a code change.
---

<!-- Inspired by mattpocock/skills engineering/zoom-out (MIT). Adapted and expanded. See ../CREDITS.md -->

# Zoom Out

Step back. Before diving into details, surface the map.

## When to use

- User says: "zoom out", "big picture", "how does this fit together", "where does X live".
- You do not know this area of code well and are about to guess.
- A task needs cross-module understanding before picking where to change something.
- Resuming an unfamiliar session or a long-paused project.

## The response shape

Produce a **map**, not a code change. The map has four parts — keep the whole thing scannable:

### 1. One-sentence summary

What does this area of the codebase do, in a single sentence, in the project's own vocabulary?

### 2. Module / file map

Bullet list of the relevant modules with one-line purpose each.

```
- src/billing/subscriptions.ts — lifecycle of a subscription (create, cancel, renew).
- src/billing/invoices.ts       — generates invoices from subscription state.
- src/billing/webhooks/stripe.ts — inbound provider events.
- src/billing/queue.ts          — async jobs: renewals, retries, dunning.
```

Limit to ~10 entries. If there are more, pick the load-bearing ones and note the rest exist.

### 3. Callers + data flow

Who calls into this area, and who does this area call?

```
Inbound:
- apps/api/routes/billing.ts  → subscriptions.create/cancel
- apps/web/server-actions/*   → subscriptions.*
- Stripe webhooks             → webhooks/stripe.ts

Outbound:
- db/prisma (tables: subscriptions, invoices)
- stripe SDK
- queue worker for async renewals
```

### 4. Gotchas / load-bearing details

Small list of non-obvious things a first-time reader would miss: invariants, ordering, feature flags, migrations in flight, "we tried X and reverted", "the fence is there because …".

```
Gotchas:
- Subscriptions are NOT deleted — soft-delete via canceledAt. Queries must filter.
- Invoice numbering is per-tenant, enforced in a DB trigger (migrations/005_invoice_seq.sql).
- The webhook endpoint is idempotent via event.id dedup table (events_stripe).
```

## Source the map from the code, not from guesses

- Read file names and top-of-file comments rather than inferring from imports.
- Use the project's rules file (`AGENTS.md` / `CLAUDE.md`) for glossary and architecture section if present.
- Check ADRs (`docs/adr/`) for decisions the files would not reveal.
- Use `git log -- <path>` briefly for modules you do not recognize — last touch often hints at purpose.
- **Use the project's own terms.** If the codebase calls it "tenant", do not rename it "customer" in the map.

## When the area is large

If zoom-out would produce a map longer than ~40 lines, **zoom out further**. Summarize at one level up, and offer to zoom into specific branches.

```
Top-level: billing has three sub-areas: subscriptions, invoices, webhooks.
Which do you want to drill into?
```

## When the area is small

If there are only 2-3 files and the whole thing fits on a screen, just say so and describe them. Do not manufacture structure that is not there.

## Anti-patterns

- Starting a code change without zooming out first in an unfamiliar area.
- Using generic architectural words ("the service layer", "the controller") when the project uses specific ones.
- Zooming out with no sources — confident-sounding maps that are wrong.
- Turning zoom-out into a lecture on software architecture in general.
- Including a map item you have not actually read.

## Interaction with other skills

- [`investigate-before-editing`](../investigate-before-editing) — zoom-out produces the map; investigate-before-editing reads the specific files you will change.
- [`context-engineering`](../context-engineering) — the Level 3 "source files" loading step often starts with zoom-out.
- [`project-rules-file`](../project-rules-file) — a good rules file has an "Architecture" section that is the persistent, committed form of this map.
- [`spec-first-planning`](../spec-first-planning) — the Plan phase's dependency graph is a zoom-out artifact.

## Verification checklist

A good zoom-out response:

- [ ] Fits in one screen (<~40 lines).
- [ ] Uses the project's vocabulary, not invented terms.
- [ ] Every module listed has been confirmed to exist.
- [ ] Named at least one non-obvious gotcha specific to this area.
- [ ] Ended with a prompt: "want me to drill into X?"
- [ ] Did not change any code.
