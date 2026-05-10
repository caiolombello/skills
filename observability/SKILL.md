---
name: observability
description: Design and maintain observability for production systems — metrics, logs, traces, SLIs, SLOs, alerts, dashboards. Use WHENEVER (1) the user is instrumenting a service with Prometheus, Grafana, OpenTelemetry, Datadog, New Relic, CloudWatch, or any observability stack; (2) defining, reviewing, or tuning SLIs, SLOs, error budgets, or alerts; (3) an alert is noisy, flaky, or missing (alert fatigue); (4) a dashboard is cluttered, stale, or lies about reality; (5) the user mentions "SLO", "SLI", "error budget", "golden signals", "RED/USE method", "p99", "burn rate", "cardinality", "alert fatigue", "what should we monitor"; (6) cost of logs/metrics is exploding (high cardinality, retention mismatch); (7) debugging an incident and asking "why did we not know sooner?". Based on Google SRE discipline (SLI/SLO/burn rate), OpenTelemetry conventions, and the RED / USE methods for instrumenting services.
---

# Observability

Observability is the ability to ask **new** questions of a running system **without** deploying new code. If every outage forces you to add logs and redeploy to understand what happened, the system is not observable — it is just logged.

Three signals, in order of value for most services: **metrics** (what, how much, how often), **logs** (why, with context), **traces** (across what path). One signal alone is not enough.

## When to use this skill

- Instrumenting a new service, or reviewing an existing one.
- Defining or tuning SLIs, SLOs, error budgets.
- An alert is noisy, flaky, missing, or woke someone for no reason.
- Dashboards are cluttered, stale, or lying.
- An incident postmortem surfaces "we did not know fast enough".
- Observability cost is exploding (cardinality, retention, sampling).

### When NOT to use

- Pure dev-environment debugging where no production signal exists → [`diagnose`](../diagnose).
- Post-incident action items that are code-only → [`test-driven-development`](../test-driven-development).
- Application-layer security logging → [`security-hardening`](../security-hardening).

## What to measure — start from user impact

**Do not start with "what can we emit". Start with "what would a user feel is broken".**

### Google's four golden signals (for any request-driven service)

| Signal | Question answered | Example metric |
|--------|------------------|----------------|
| **Latency** | How long do requests take? | `http_request_duration_seconds` (histogram) |
| **Traffic** | How much demand? | `http_requests_total` (counter) |
| **Errors** | How many fail? | `http_requests_total{status=~"5.."}` (counter) |
| **Saturation** | How full is the system? | CPU / memory / queue depth / connection-pool usage |

If a service has these four measured correctly, you can detect almost every common failure mode.

### The RED method (for microservices / request handlers)

**Rate, Errors, Duration** per endpoint / handler. Used widely in cloud-native monitoring.

### The USE method (for resources: hosts, disks, queues)

**Utilization, Saturation, Errors** per resource.

Combine both: RED for every service endpoint, USE for every capacity-bounded resource they depend on.

## SLIs, SLOs, error budgets

An SLI is a **measurable signal** that maps to user-visible behavior. An SLO is a **target** on that SLI. The gap between perfect and the SLO is the **error budget**.

### Good SLI examples

| Service type | Good SLI | Bad SLI |
|-------------|----------|---------|
| HTTP API | % of requests with status < 500 AND latency < 500ms, measured at the load balancer | CPU % of backend host |
| Batch pipeline | % of runs that completed within SLA window without retryable failure | Number of errors in the log |
| Storage | % of reads/writes succeeded | Disk IOPS raw |
| Queue / worker | % of messages processed within N seconds of enqueue | Queue depth alone |

### SLI principles

- **Measure at the boundary the user actually hits.** LB, CDN edge, client RUM — not the backend host metrics.
- **Ratio, not raw.** `good_events / total_events`. Easier to reason about over time and load.
- **Keep it small.** 2-5 SLIs per service. More and they contradict; fewer and you miss dimensions.

### SLO examples

- "99.9% of API requests over 30 days return < 500 in under 500ms."
- "99.5% of checkout transactions over 7 days complete end-to-end in under 3 seconds."
- "99.99% of uploads over 28 days are durable."

Pick windows that match customer perception (24h / 7d / 28d / 30d). Rolling windows catch trends; calendar windows are easier to report.

### Error budget

At 99.9% SLO over 30 days → 43 minutes of budget per month. Track burn. If the budget is gone, freeze risky changes until it refills.

### Burn-rate alerting (the modern standard)

Traditional alerts fire on a static threshold ("error rate > 1%"). They are too noisy for fast spikes and too slow for slow leaks.

Burn-rate alerts fire when the **rate of budget consumption** would exhaust the budget before the window ends. Multi-window multi-burn-rate is the robust shape:

```
Fast burn:  error rate over the last 5m and last 1h exceeds 14.4x → page
Slow burn:  error rate over the last 1h and last 6h exceeds 1x → ticket
```

14.4x for a 1h window consumes 2% of a 30-day budget in that hour — catches fast fires. 1x for 6h catches slow leaks that would drain the budget over several hours.

Reference: Google SRE Workbook, "Alerting on SLOs". Implement via Prometheus recording rules + Alertmanager, or the equivalent in Datadog / New Relic / Grafana SLO.

## Alert discipline

Every alert should meet all three:

1. **Actionable** — a human can fix it right now. Otherwise it is a metric, not an alert.
2. **User-impacting** — tied to an SLO or to a user-visible symptom. "CPU high" without latency impact is not actionable.
3. **Survivable** — will not fire 100 times for the same root cause.

### Anti-patterns that cause alert fatigue

- Symptom **and** cause both alert — only symptom alerts should page.
- Same condition alerts twice (raw + aggregated).
- "Informational" alerts that are never acted on. Move to a dashboard.
- Alerts that fire only during deploys — add a deploy-gate or quiet window.
- No runbook link in the alert → pager sees gibberish at 3am.

### Every alert has

- **Name**: what is wrong (`APIHighErrorRate`), not what metric (`HTTP5xxCount`).
- **Severity**: page / ticket / warn.
- **SLO link** or user impact statement.
- **Runbook link** (see [`incident-response`](../incident-response)).
- **Owner / team** label.
- **Annotations**: exact query, threshold, duration.
- **Dashboard link** for context at a glance.

### Tuning discipline

When an alert fires:
- **Real incident** → response + postmortem.
- **True positive but not actionable** → SLO drift, tune the SLO or the service.
- **False positive** → tune the alert immediately, do not let it pile up.

Track "alert noise ratio" — false positives / total firings. Anything above 20% is broken; fix before it desensitizes the on-call.

## Metrics

### Cardinality is the hidden cost

Every unique label combination creates a new time series. Costs scale roughly as:

```
series = base_metrics × labels_1 × labels_2 × ... × labels_N
```

Rules:
- **Bounded labels only.** Status codes, HTTP method, region — yes. User IDs, emails, UUIDs, raw URLs — **no**.
- If a label has >~1000 values, reconsider. >10,000 values is a production-level mistake.
- Use histograms sparingly — every bucket × label combination is a series.
- In Prometheus / Mimir / Thanos, a single mislabeled metric can 10x cost overnight. Guard with recording rules and a cardinality dashboard.

### Metric types and when to use them

| Type | Use for | Example |
|------|---------|---------|
| Counter | Cumulative events | `http_requests_total` |
| Gauge | Current value that goes up and down | `queue_depth`, `memory_bytes` |
| Histogram | Distribution of values over time | `http_request_duration_seconds` |
| Summary | Pre-computed quantiles, fixed | Prefer histogram unless you have a reason |

Prefer **histograms** for latency — you can compute any percentile at query time with `histogram_quantile`.

### Name + label conventions

Follow [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/). Cross-team consistency > local cleverness. `http.server.duration`, `db.operation`, `messaging.system` — the semconv vocabulary is well-designed; do not invent a parallel scheme.

Unit suffix in the metric name: `_seconds`, `_bytes`, `_total`. Makes dashboards self-documenting.

## Logs

### Logs are expensive; structured logs are useful

- **Every log is JSON** (or another structured format). Grepping unstructured text at scale is a losing battle.
- **Include context IDs** on every line: `request_id`, `trace_id`, `user_id` (hashed if PII), `tenant_id`.
- **Log levels**: `ERROR` only for actionable failures. `WARN` for recoverable anomalies. `INFO` for lifecycle (startup, shutdown, config). `DEBUG` off in production unless explicitly enabled.
- **No secrets**, **no PII** in logs. See [`security-hardening`](../security-hardening).
- **Sample aggressively** on high-volume paths. 100% logs on a hot endpoint will bankrupt you.

### What to log

- Every request boundary once — in / out of the service. Method, path, status, duration, size.
- Every error with context (what we were doing, not just the error).
- Every decision that surprised us at dev time.
- Every security-relevant event (auth success/failure, permission change, admin action).

### What NOT to log

- Debug prints ("got here", "user is ...").
- Full request / response bodies (huge, and often contain secrets).
- Stack traces for expected errors.
- Passwords, tokens, session IDs, credit cards, full SSNs.
- High-frequency non-actionable events.

## Traces

Distributed traces show **how one request flowed through N services**. They pay off when:
- The system has >3 services involved per user action.
- Latency is the problem and you need to see which hop is slow.
- A request is failing and the log of one service does not tell you why.

Use [OpenTelemetry](https://opentelemetry.io/) — cross-language, vendor-neutral. Export to whatever backend the org uses (Tempo, Jaeger, Zipkin, Datadog, Honeycomb).

Rules:
- **Propagate `trace_id` everywhere.** Logs include `trace_id`; metrics emit exemplars with `trace_id`.
- **Span names are stable and low-cardinality.** `POST /api/users/:id` is fine; `POST /api/users/42` is a cardinality bomb.
- **Record error + exception on spans.** Failures are traces' killer feature.
- **Sample**. 100% tracing is often too expensive; tail-based sampling (keep all slow / error traces) is the sweet spot.

## Dashboards

Dashboards serve two audiences:

1. **Operators during an incident** — must answer "is it broken, where, how bad" in < 30 seconds.
2. **Owners during steady state** — trends, capacity, SLO compliance.

### Structure

- **Overview panel at the top**: SLO status, error-budget burn, traffic, error rate, latency p95/p99. One screen.
- **Drill-down per area** below: per endpoint, per dependency, per resource.
- **Annotate deploys.** Deploy markers let you correlate metric changes to releases.
- **Link to runbooks and alerts.** A dashboard without outbound links is a dead end at 3am.

### Anti-patterns

- Dashboard with 40 panels, no ordering. Only the author understands it.
- "Gauge" dashboards that are useless during an incident (single current value, no time context).
- No y-axis units.
- No legend.
- Stale dashboards from a project that was cancelled — archive them.

## Cost control

Observability cost can rival compute cost. Watch:

- **Cardinality growth.** Add a monthly review; alert when a metric crosses a threshold.
- **Log volume per service.** One chatty service can drag the whole bill. Sample or structure.
- **Retention mismatch.** 90-day retention on DEBUG logs is almost always wrong. Tier retention: audit (long), errors (medium), info/debug (short).
- **Trace sampling ratio.** Start at 1-10% for high-volume endpoints, use tail-sampling for errors/slow.
- **Dead dashboards / queries.** Expensive queries that no one opens. Audit quarterly.

Cost is a signal for broken telemetry, not just a budget issue.

## Migration to OpenTelemetry

If the project is still on vendor-specific SDKs, plan a move to OpenTelemetry:
- Single instrumentation, any backend.
- Vendor-neutral — avoids re-instrumenting when the backend changes.
- Wide ecosystem of semconv + contrib instrumentations.

Pattern: run dual export for a period (old backend + OTel pipeline). Validate parity. Switch over. Remove old SDK.

## The "did we know fast enough" test

After an incident, every observability gap becomes an action item:

- **Detection time > SLO budget?** SLIs or alerts are broken.
- **MTTR dominated by investigation?** Dashboards or traces are thin.
- **Postmortem reveals a fact no dashboard showed?** Add the panel.
- **Postmortem reveals a fact no log captured?** Add the structured log.
- **Postmortem reveals wrong alert severity?** Tune severity + burn-rate.

See [`incident-response`](../incident-response) — action items from incidents land here.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Alert on everything, dashboards later | Alert fatigue; nobody reads pages |
| SLI = CPU utilization | Does not map to user impact |
| Static-threshold alerts on error rate | Noisy in low traffic, slow in high |
| High-cardinality labels in metrics | Series explosion, cost explosion |
| Unstructured logs in prod | Unsearchable at scale |
| 100% trace sampling on hot paths | Cost + latency impact |
| Dashboard shows raw values, no SLO context | Cannot tell good from bad at a glance |
| No owner on alerts / dashboards | Stale telemetry, nobody prunes |
| Alerts without runbooks | On-call cannot act |
| Same signal alerts + logs + traces with no correlation | Three views, no joining key |

## Interaction with other skills

- [`incident-response`](../incident-response) — observability is the raw material of incident handling. Every action item from a postmortem typically lands in this skill.
- [`deploy-safety`](../deploy-safety) — a deploy is safe only if the SLO / burn-rate alerts are watching. Include "SLOs green" in pre-deploy checklist.
- [`diagnose`](../diagnose) — observability gaps are the common failure: "we could not reproduce" often means the system was underinstrumented.
- [`kubectl-workflows`](../kubectl-workflows) — K8s exposes USE-method signals (node / pod saturation). Scrape them.
- [`awscli-workflows`](../awscli-workflows) — CloudWatch metrics, AWS OTLP, AWS distro of OpenTelemetry.
- [`security-hardening`](../security-hardening) — security logs (authn, authz, sensitive action) live in the observability pipeline.
- [`container-image-hardening`](../container-image-hardening) — container labels feed telemetry (image, version, commit).

## Verification checklist

Per service, before declaring observability done:

- [ ] Four golden signals (latency, traffic, errors, saturation) are measured at the user boundary.
- [ ] 2-5 SLIs / SLOs defined and documented.
- [ ] Error budget is tracked and visible on the main dashboard.
- [ ] Alerts use multi-window multi-burn-rate (fast burn pages, slow burn tickets).
- [ ] Every alert has: severity, runbook link, SLO link, owner label, dashboard link.
- [ ] Structured logs with `request_id` / `trace_id` / tenant on every line.
- [ ] No PII, no secrets, no passwords in logs.
- [ ] Cardinality is bounded; no user-ID-like labels on metrics.
- [ ] Histogram for latency; proper `_seconds` / `_bytes` unit suffix.
- [ ] Traces propagate `trace_id`; spans have stable low-cardinality names; errors / exceptions recorded.
- [ ] Dashboard overview panel answers "broken / where / how bad" in < 30s.
- [ ] Deploy annotations on the dashboard.
- [ ] Alert noise ratio is measured; false positives tuned not ignored.
- [ ] Cost: cardinality, log volume, trace sample rate, retention all reviewed at least quarterly.
