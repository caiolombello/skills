---
name: incident-response
description: Run a live production incident with discipline — declare, triage, stabilize, communicate, resolve, learn. Use WHENEVER (1) the user reports production is broken, slow, or misbehaving ("site down", "5xx spiking", "DB is hot", "queue backed up", "customers can't log in"); (2) an alert fires and must be acknowledged, triaged, and worked; (3) the user mentions "incident", "outage", "on-call", "paged", "SEV", "P0/P1/P2", "war room", "postmortem"; (4) a deploy just went out and looks like it caused damage; (5) a third party is down and is affecting this service; (6) the user asks to write or lead a postmortem. This skill is for LIVE production ops — not for bug fixing in a dev branch (for that see `diagnose`). The first job is to stop the bleeding; root-cause analysis comes after.
---

# Incident Response

When production is on fire, do not debug — **stabilize first, investigate second**.

This skill covers the operational discipline of running a live incident. It is distinct from [`diagnose`](../diagnose), which is about root-causing a bug in isolation. In an incident, reducing user impact takes precedence over finding the true cause. You can always dig deeper after the fire is out.

## When to apply

- Production is broken, degraded, or slower than SLO.
- An alert has fired and the agent or user is expected to work it.
- A user report indicates customer impact (can't log in, errors, data missing).
- A recent deploy caused visible damage.
- The user uses words like "incident", "outage", "paged", "SEV", "P0", "war room".
- The user asks for a postmortem or incident report.

### When NOT to apply

- Debugging in dev / staging with no user impact → [`diagnose`](../diagnose).
- Pre-incident capacity planning → [`observability`](../observability).
- Feature work under normal development → [`incremental-implementation`](../incremental-implementation).

## The phases

```
1. DECLARE      → someone is responsible
2. TRIAGE       → severity + user impact
3. STABILIZE    → stop the bleeding (ideally in under 30 min)
4. COMMUNICATE  → stakeholders + status page, in a steady cadence
5. RESOLVE      → confirm restored, close the incident
6. LEARN        → blameless postmortem + action items
```

Go in order. Do not jump to root-cause analysis before stabilizing.

## Phase 1: Declare

The first person who sees the problem declares the incident. Declaration is cheap — you can downgrade or cancel later.

State, in this order:

```
INCIDENT DECLARED
- Title:        <one-line: "API 5xx spiking in us-east-1">
- Detected at:  <UTC timestamp>
- Detected by:  <alert / user report / manual observation>
- Symptoms:     <what users see — 500s, slow responses, missing data>
- Initial severity guess: <SEV-1 / SEV-2 / SEV-3>
- Incident commander (IC): <name — required>
- Scribe: <name — optional but recommended>
- Comms lead: <name — only if public/customer comms needed>
```

**One IC at a time.** The IC is not the person who fixes it; the IC coordinates. In a one-person incident (solo on-call, small team), the same person is IC **and** fixer — but explicitly switches roles.

Open a dedicated channel / war room. Everything said there becomes the timeline.

## Phase 2: Triage

Assign severity. Severity maps to required response — the biggest lever you have against the temptation to over- or under-escalate.

Canonical SRE-style scale (adjust to the org):

| SEV | Impact | Response |
|-----|--------|----------|
| SEV-1 | Full outage or data loss. Revenue-impacting. Most or all users affected. | All hands; page on-call + leadership; public status page update within 15 min; 24/7 until mitigated |
| SEV-2 | Major feature broken or severe performance degradation. A subset of users affected. | On-call + team lead; internal status within 30 min; fix within hours |
| SEV-3 | Minor feature broken, workaround exists, or edge-case users affected. | Normal hours; fix within the day or two |
| SEV-4 | Cosmetic / no user impact (e.g. internal dashboard stale). | Normal backlog |

**Communicate severity.** Silent severity guessing is a common failure.

Checks before settling on severity:
- [ ] Is there a user-visible error right now? How many users? What fraction?
- [ ] Is data being lost, corrupted, or mis-delivered?
- [ ] Is there a workaround for affected users?
- [ ] Is the impact stable, growing, or shrinking?
- [ ] Is this correlated with a recent deploy, config change, or infra event?

Downgrade severity when impact shrinks. Upgrade when it grows. Announce the change in the channel.

## Phase 3: Stabilize

**Goal: reduce user impact as fast as possible.** Not find the root cause. Not write the perfect fix. Stabilize.

### The four stabilization levers

Try them in roughly this order. Each is faster than the next.

1. **Rollback.** If a deploy went out in the last N hours and the symptom started after, roll it back. Do this **before** reading any logs — a rollback takes 2 minutes and tells you whether the deploy was the cause. If the symptom clears, you have both stabilized and located the cause.
2. **Feature flag off.** If the bad code path is behind a flag, flip it off. Often reversible in seconds.
3. **Scale out / shed load.** If the symptom is load-driven (DB CPU pinned, queue growing, rate-limited downstream), increase replicas, widen queues, raise rate limits, **or** enable load shedding — return 503 to non-critical traffic to save the critical path. Shed before the system collapses entirely.
4. **Re-route / failover.** DNS to a healthy region, active-passive failover, serve cached responses, switch to a maintenance page. Last resort before "tell everyone we are down".

### What NOT to do while stabilizing

- **No big rewrites.** Apply the smallest change that restores service. Write the proper fix after.
- **No speculation-driven changes.** If you have not confirmed the theory, the "fix" can make it worse. Rollback > speculation.
- **No silent changes.** Every mitigation goes in the channel with a timestamp.
- **Do not debug the fix.** If the mitigation shows signs of working, let it. Watch the metrics; do not keep tweaking.

### Capture evidence before you fix

Between "confirmed cause" and "applied fix", grab evidence that will survive the fix:

- Save the offending log window to a file.
- Screenshot the dashboards.
- Export the slow query / stack trace.
- Note the config / version that was live.

Once you roll back or restart, that evidence may be gone.

## Phase 4: Communicate

Stakeholders need a predictable cadence. Silence is worse than bad news.

### Cadence

| SEV | Internal update | External (status page) |
|-----|-----------------|------------------------|
| SEV-1 | Every 15 min | Every 30 min until mitigated |
| SEV-2 | Every 30 min | When first meaningful info |
| SEV-3 | Once per hour or on change | Usually none |

**Update even if nothing changed.** "Still investigating, no new info" is a valid update. Stakeholders fear silence more than they fear ongoing investigation.

### What goes in an update

```
[HH:MM UTC] Update #<N>
Status: Investigating | Identified | Monitoring | Resolved
Impact: <who is affected and how>
Current actions: <what we are trying right now>
Next update: <time>
```

Do not announce root cause until confirmed. "We are seeing DB CPU at 100%" is a fact; "it is caused by the new query" is a hypothesis until proven.

### Public language

- Neutral voice. No blame on people, products, or vendors.
- Avoid internal jargon on customer-facing updates.
- Say what customers can do ("retrying usually succeeds", "please stop submitting new orders for now").

## Phase 5: Resolve

Mark resolved only when:

- [ ] The original symptom is gone (verify with the alert, the dashboard, a real request, or a synthetic check).
- [ ] Monitoring for the symptom has been stable for at least one SLO window (for a 99.9% SLO on a 5-min burn rate, that is typically 15-30 min of stability).
- [ ] The mitigation is durable, or a follow-up is scheduled to make it durable.
- [ ] Customer-facing comm says "Resolved" with a clear mitigation note.

Do **not** resolve on vibes. A flaky recovery that later re-breaks costs more trust than a 30-minute extra monitoring window.

## Phase 6: Learn — blameless postmortem

Every SEV-1 and SEV-2 gets a postmortem. SEV-3 at the owner's discretion.

### Blameless principle

Assume everyone acted in good faith with the information they had. **Ask "what system allowed this?" not "who messed up?"** A postmortem that names individuals as the cause is broken — the cause is always that the system let the individual act incorrectly.

### Postmortem template

```markdown
# Postmortem: <Title>

## Summary
<2-3 sentences. What happened, what was the impact, what was the duration.>

## Impact
- Users affected: <count / percentage / tier>
- Duration: <HH:MM UTC to HH:MM UTC — total duration>
- SLO / error-budget impact: <burn rate impact>
- Revenue / business impact: <if known>

## Timeline (UTC)
- HH:MM — <detection event>
- HH:MM — <first action>
- HH:MM — <turning point>
- HH:MM — <mitigation applied>
- HH:MM — <verified resolved>

## Root cause
<Analysis. Include the chain of events and why each safeguard did not catch it.>

## What went well
- <specific thing, not platitudes>

## What went badly
- <specific thing — "alert fired 40 min after symptom started because X">

## Lucky / unlucky
<Things that were coincidentally fortunate or unfortunate. Surfaces hidden fragility.>

## Action items
- [ ] <Owner>: <specific, dated, tracked in issue tracker> — DD-MMM
- [ ] <Owner>: <...>
```

### Action-item rules

- Every action has an **owner** and a **due date**. Orphan actions do not ship.
- Actions are **tracked in the issue tracker**, not only in the postmortem doc.
- Prefer **systemic** actions over **procedural** ones. "Add a test" beats "everyone please remember". "Put a safeguard in CI" beats "be more careful".
- Split **repeat-prevention** (systemic) from **impact-reduction** (faster detection, faster mitigation). Both matter.

The [`opsteam-docs`](../../.config/opencode/skill/opsteam-docs) skill (local) can render this postmortem to the OpsTeam `.docx` template for client delivery.

## Solo-on-call mode

When you are both IC and fixer:

- Still declare explicitly. Even a one-line Slack message helps the timeline.
- Keep a running log — a plain text file with timestamps. You will thank yourself at postmortem time.
- Ask for help early. If you cannot stabilize in 30 min, escalate. Pride does not buy uptime.
- Do not drink the troubleshooting coffee and forget food / water. Four-hour incidents start here.

## AI-assisted incident response

If the agent is helping live:

- **Read-only by default.** No production writes without explicit user confirmation for each write.
- **Summarize before acting.** "Here is what the logs show. Want me to restart the pods?" — do not restart on your own.
- **Never invent symptoms.** If a dashboard is ambiguous, say so.
- **Preserve evidence.** Suggest snapshotting before mitigation steps.
- **Keep the timeline.** Emit timestamped summaries the user can paste into the channel.

See [`awscli-workflows`](../awscli-workflows) and [`kubectl-workflows`](../kubectl-workflows) for the safety rules that apply to any write in production.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Debug first, stabilize second | Users keep suffering while you theorize |
| Silent channel during a SEV-1 | Stakeholders assume no one is working it |
| No IC named | Everyone acts; no one coordinates; actions conflict |
| "We rolled it back, incident over" without monitoring | Flaky recovery re-breaks 20 min later |
| Big fix instead of mitigation | Longer outage; risk of new breakage |
| Postmortem names people as the cause | Team learns to hide incidents |
| Action items with no owner / no date | Nothing changes; same incident recurs |
| Public status page says "Investigating" for 2 hours with no update | Worse than "we don't know yet, checking every 15 min" |
| Declaring lower severity to avoid the paperwork | Under-response; impact grows |
| Closing incident during a deploy window | Rollback may be needed; keep the channel hot |
| Reusing the same channel for two overlapping incidents | Timeline unusable |

## Interaction with other skills

- [`diagnose`](../diagnose) — after stabilization, use `diagnose` to root-cause properly. The regression test from `diagnose` becomes the "add a test" action item.
- [`observability`](../observability) — if detection took too long, action items come from here (SLI gaps, alert misses, missing dashboards).
- [`deploy-safety`](../deploy-safety) — "rollback first" is the core mitigation; `deploy-safety` defines what "safe rollback" actually means per deploy.
- [`awscli-workflows`](../awscli-workflows), [`kubectl-workflows`](../kubectl-workflows) — every write during mitigation follows these safety rules (explicit context, read-before-write).
- [`git-hygiene`](../git-hygiene) — incident fixes follow Conventional Commits (`fix(incident-YYYY-MM-DD): ...`).
- [`opsteam-docs`](../../.config/opencode/skill/opsteam-docs) (local) — renders the final postmortem for client delivery.

## Verification checklist

**During the incident:**

- [ ] Incident was declared, with title, timestamp, IC, severity.
- [ ] A dedicated channel / war room exists.
- [ ] Severity matches impact (upgraded or downgraded as impact changed).
- [ ] Stabilization tried the four levers in order (rollback first where possible).
- [ ] Evidence captured before mitigation erased it.
- [ ] Stakeholder updates on cadence (even "no new info" updates).
- [ ] Every write in production was explicit and captured in the timeline.

**Before closing:**

- [ ] Original symptom gone, verified with a real signal.
- [ ] Monitoring stable for at least one SLO window.
- [ ] Customer-facing comm says "Resolved" with a mitigation note.

**After resolution:**

- [ ] Postmortem exists (SEV-1 / SEV-2 mandatory).
- [ ] Postmortem is blameless — no individuals named as cause.
- [ ] Every action item has owner + date + tracker link.
- [ ] Systemic actions outnumber procedural ones.
- [ ] Timeline saved and archived.
