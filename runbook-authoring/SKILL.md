---
name: runbook-authoring
description: Write runbooks that an on-call engineer can follow at 3am — alert-driven, step-by-step, copy-pasteable, with a verify step for every action. Use WHENEVER the user (1) creates or updates a runbook for an alert, service, or recurring incident class; (2) the user mentions "runbook", "playbook", "on-call docs", "incident response guide", "mitigation steps"; (3) a postmortem has an action item "add / update runbook for X"; (4) an alert fires without a linked runbook and the on-call has to guess; (5) onboarding new on-call rotation and the existing runbooks are missing, stale, or unusable. A runbook is NOT documentation about the system — it is a procedure for surviving a specific alert / failure mode. Pairs with `incident-response` (the live incident discipline) and `observability` (every alert must link to a runbook).
---

# Runbook Authoring

A runbook is a **procedure for surviving a specific failure mode**, written so an on-call engineer at 3am can follow it without thinking. It is not documentation about how a system works, not a design doc, not a philosophy essay. It answers one question: **"The alert fired / customers are reporting X — what do I do right now?"**

Good runbooks halve MTTR. Bad runbooks (or none) are why the same incident recurs for months.

## When to use this skill

- An alert fires and has no runbook link.
- An incident postmortem includes "write/update runbook" as an action item.
- A new alert is being designed — the runbook is part of the alert, not an afterthought.
- On-call rotation onboarding reveals the existing runbooks are stale or unusable.
- A recurring incident class needs a documented mitigation.

### When NOT to use

- Architecture / design documentation → [`architecture-decision-records`](../architecture-decision-records).
- Application-side rules → [`project-rules-file`](../project-rules-file).
- The incident is happening RIGHT NOW and no runbook exists → work the incident with [`incident-response`](../incident-response); draft the runbook as a postmortem action item.

## What makes a runbook "3am-proof"

| Property | Why it matters |
|----------|----------------|
| **Scoped to one alert / symptom** | The on-call finds the right one by searching the alert name |
| **Linked from the alert** | No search; click and read |
| **Starts with "Is this real?"** | Cuts false alarms fast |
| **Every command is copy-pasteable** | Typos at 3am cost minutes |
| **Every step has a verify** | "Did that work?" answered before moving on |
| **No prose paragraphs** | Bullets / numbered steps only |
| **Escalation path at the top** | If runbook fails, next action is visible |
| **Owned by a team** | Stale runbooks have no owner. Owned runbooks get reviewed. |
| **Dated; last-reviewed field** | Readers can tell if it is trustworthy |

## The template

Keep every runbook in the same shape. Predictability is the whole point — on-call should never have to figure out *where the mitigation steps live*.

```markdown
# Runbook: <Alert name or symptom, exact match to the alert rule>

- **Owner**: <team / channel>
- **Escalation**: <next person / channel if this runbook does not resolve>
- **Last reviewed**: YYYY-MM-DD (bump on every real use)
- **Related dashboards**: <Grafana / Datadog URLs>
- **Related alerts**: <sibling alerts that may fire together>

## 1. Verify the alert is real

<1-3 checks. Graph link, curl, kubectl get, query a metric. Goal: decide real vs noise within 60 seconds.>

```bash
# example: confirm 5xx rate on the LB is actually elevated
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB ...
```

**If false alarm**: <silence steps, link to alert tuning issue>. Go no further.

## 2. Understand impact

<Which users? Which tenants? Which region? One or two queries that answer this.>

```bash
# Count affected tenants from the last 5 minutes
logcli query '{app="api"} | json | status>=500' --limit 100 | ...
```

## 3. Stabilize — known-good mitigations

<In order of preference. Most reversible / cheapest first.>

### 3.1 Rollback most-recent deploy (most common fix)

```bash
# Verify there was a recent deploy
argocd app get api-prod -o json | jq '.status.operationState.startedAt'
# If < 30 min ago and symptom started around then:
argocd app rollback api-prod <previous-revision>
```

**Verify**: 5xx rate returns to baseline within 5 min. Dashboard: <URL>.

### 3.2 Shed load

```bash
kubectl -n prod patch deployment api -p '{"spec":{"replicas":12}}'
```

**Verify**: `kubectl -n prod get pods -l app=api -w` until all Ready; latency drops.

### 3.3 Enable circuit-breaker feature flag

```bash
# If downstream X is the source:
unleash-cli toggle-on circuit-breaker-X --env prod
```

**Verify**: 5xx rate drops within 2 min of flip.

## 4. Investigate cause

<Only after stabilization. Link to the `diagnose` skill's feedback-loop approach.>

- Recent deploys: `<link to deploy dashboard>`
- Related changes: `<link to change log or Jira filter>`
- Downstream health: `<URLs>`
- Logs: `<exact query>`
- Traces: `<exact Tempo/Jaeger query>`

## 5. Communicate

- [ ] Update the incident channel every 15 min (SEV-1/2).
- [ ] Status page update (SEV-1): <template link>
- [ ] Stakeholder notify if > 30 min: <list>

## 6. Resolve

- [ ] Primary symptom gone, confirmed against the alert's SLI.
- [ ] Monitoring stable for one SLO window.
- [ ] Incident channel updated with "Resolved".
- [ ] Postmortem scheduled if SEV-1 or SEV-2.

## 7. Known gotchas

- <Non-obvious thing that bites on-call; e.g., "pod restart is 2 min, not 30s; don't re-trigger">
- <...>

## 8. History

- YYYY-MM-DD — Used in [incident XYZ]. Mitigation 3.1 worked.
- YYYY-MM-DD — Step 3.3 added after [postmortem].
```

## Authoring rules

### 1. Scope to one alert / symptom

One runbook = one alert rule (or one very specific symptom). **Not** "runbook for the API service" — that is too broad and nobody reads it under pressure. `api.high.5xx.rate` is one runbook; `api.slow.p99.latency` is another.

Linked at the alert:

```yaml
# Prometheus alert with runbook URL annotation
- alert: APIHighErrorRate
  expr: sum(rate(http_requests_total{job="api",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="api"}[5m])) > 0.02
  for: 2m
  labels:
    severity: page
    team: platform
  annotations:
    summary: "API 5xx rate > 2% for 2m"
    runbook: "https://runbooks.example.com/api/high-5xx-rate"
    dashboard: "https://grafana.example.com/d/api-overview?from=now-1h"
```

### 2. Start with "is this real?"

Half the time the alert is noise — a flaky dependency, a clock skew, a bad threshold. Before any mitigation, a step to decide real vs noise. Cuts false work fast.

### 3. Copy-pasteable commands

- Full commands, not pseudo-code. `kubectl -n prod ...` not "look at pod logs".
- Placeholders in angle brackets: `<tenant-id>`. On-call fills them in.
- Cloud CLI commands include `--profile` / `--region` (see [`awscli-workflows`](../awscli-workflows)).
- `kubectl` commands include `-n` / `--context` (see [`kubectl-workflows`](../kubectl-workflows)).
- Never put `rm -rf` or `delete --all` in a runbook unless there is a hard guard.

### 4. Every action has a verify

After "run this command", include "how you know it worked". Without it, on-call executes 10 steps and still does not know if the mitigation landed.

Verify options (any one is enough):
- A metric that returns to baseline.
- A `kubectl` command that shows expected state.
- A `curl` that returns 200.
- A graph link with the expected shape.

### 5. Mitigations in order of preference

- Fastest, most reversible first — rollback, feature-flag flip, traffic shift.
- Scaling and restart next.
- Manual data fixes and schema changes last and only if the runbook authorizes them.

### 6. Escalation path at the top

If the runbook does not resolve in N minutes, who gets called next, in which channel? Make that visible before step 1 so a cold on-call can escalate immediately if the alert is beyond them.

### 7. Dated; last-reviewed

A runbook that was last reviewed 3 years ago probably lies. Bump `Last reviewed:` every time someone actually uses it in production. Review all runbooks every 6 months; delete the ones nobody uses (alerts should fire once a year at least, or they are either miracles or lies).

## Storing runbooks

- **In git.** Same repo as the service, or a shared `runbooks/` repo. Versioned, diffable, reviewable.
- **Rendered on a static site** (MkDocs / Docusaurus / Backstage TechDocs) with search. On-call searches faster than they navigate.
- **Linked from every alert.** The annotation / description of the alert carries the URL. No clickthrough, no runbook.
- **Indexed by alert name.** URL path mirrors alert name: `/runbooks/api/high-5xx-rate`. Predictable.

## Alert-less runbooks

Some runbooks are not triggered by a single alert but by a symptom or a recurring task:

- "Customer reports login loop" — runbook for user report triage.
- "Monthly certificate renewal" — scheduled runbook.
- "Restore from backup" — rare but critical; must be practiced.

Same shape, different index. Keep them together.

## Game-day validation

A runbook that has never been followed is a hypothesis, not a runbook. Validate:

1. **Dry-run** — new on-call reads and walks through the commands in a staging env.
2. **Tabletop** — IC walks the team through an imaginary incident using this runbook; mark steps that fail.
3. **Chaos** — inject the failure in staging; make someone on-call work the runbook live.

Every game-day exposes a gap (stale URL, missing step, tool they do not have, permission they do not have). Fix the runbook on the spot.

## AI-assisted runbook authoring

If the agent is helping write a runbook:

- Ask the owner: "What is the exact alert name? What has historically fixed this?"
- Pull the most recent incident postmortems that matched this alert — paste the mitigation steps.
- Produce the template filled in; mark every verify step with `# VERIFY: …` so the owner can confirm or correct.
- Never invent cloud / kubectl commands. If unsure, ask the owner or leave `<FILL IN>` so a human fills it with the real command.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Runbook is prose ("you will want to check...") | On-call skims under pressure; prose gets skipped |
| "See the architecture doc" | On-call clicks away; loses context |
| Commands without `-n`, `--context`, `--profile`, `--region` | Acts in the wrong env; production incident #2 |
| No verify step | On-call runs commands, does not know what changed |
| One runbook for an entire service | Cannot find the right section at 3am |
| No escalation path | On-call stuck, impact grows |
| Runbook in a wiki that nobody searches | Alert link points to nothing useful |
| Runbook dated 3 years ago, references deprecated tools | Wastes the on-call's time mid-incident |
| Commands that require tools the on-call does not have installed | Fails at step 1 |
| Paragraph-length "why it happens" theory | Irrelevant during the incident; put in the postmortem |
| Multiple runbooks duplicating mitigations | Fix applied to one, not the others |
| Runbook full of "TODO" sections | Worse than no runbook — raises false hope |

## Interaction with other skills

- [`incident-response`](../incident-response) — the incident discipline uses runbooks. Every `page`-severity alert must have one.
- [`observability`](../observability) — every alert rule has `runbook: <url>` annotation. Missing URLs are a bug in the alert.
- [`diagnose`](../diagnose) — runbook's "investigate cause" section points back at the diagnose loop.
- [`awscli-workflows`](../awscli-workflows), [`kubectl-workflows`](../kubectl-workflows) — every CLI command in a runbook follows those safety rules.
- [`deploy-safety`](../deploy-safety) — rollback-first mitigations are specified by the deploy design; the runbook is the operator's view.
- [`architecture-decision-records`](../architecture-decision-records) — a runbook references ADRs when the mitigation is "follow ADR-0017 rollback plan".
- [`project-rules-file`](../project-rules-file) — service rules file points at the service's runbooks index.

## Verification checklist

Before publishing a runbook:

- [ ] Title exactly matches the alert name (or the symptom name for alert-less runbooks).
- [ ] Owner team and escalation channel are named at the top.
- [ ] Linked from the alert rule's `runbook:` annotation (or equivalent for the monitoring tool).
- [ ] "Is this real?" step takes less than 60 seconds.
- [ ] At least one stabilization path is present; reversible ones come first.
- [ ] Every command has full flags (`--profile`, `--region`, `-n`, `--context`).
- [ ] Every action has a verify step.
- [ ] "Resolve" checklist confirms the original symptom, not a proxy.
- [ ] `Last reviewed:` is within the last 6 months (or the runbook notes why review is overdue).
- [ ] At least one game-day or real incident has exercised the runbook.
- [ ] All linked dashboards, queries, tools actually exist and work.
