---
name: deploy-safety
description: Use when shipping or promoting to production, designing canary/blue-green/rolling rollout, rollback/feature-flag strategy, or production Deployment/ECS/Cloud Run rollout safety. Not routine app code.
---
# Deploy Safety

Shipping is a separate skill from building. A change that passed every unit test can still break production — because health checks lie, rollbacks do not exist, the DB migration is irreversible, or the failure mode was outside the test matrix.

The goal of this skill: **small blast radius, fast rollback, clear abort signal.** Not "hope it works".

## When to use

- Releasing, deploying, shipping, or promoting anything to production.
- Setting up or reviewing a CI/CD deploy stage.
- Writing Kubernetes Deployments, DaemonSets, StatefulSets — or AWS ECS tasks, Cloud Run revisions.
- Planning a production database migration.
- Terms like "canary", "blue/green", "rolling", "rollback", "feature flag", "dark launch", "zero-downtime" come up.
- A just-shipped change is causing damage and you are debating rollback vs forward-fix.

### When NOT to use

- Pure code change in a branch with no deploy on the table → [`incremental-implementation`](../incremental-implementation).
- Image security / SBOM / signing → [`container-image-hardening`](../container-image-hardening).
- The deploy is already broken → stabilize via [`incident-response`](../incident-response) first.

## Core principles

1. **Every deploy is reversible.** If you cannot roll back in under 5 minutes, the deploy is too dangerous. Refactor the deploy shape, do not "hope".
2. **Health checks lie.** A pod that responds 200 on `/health` can be broken. Gate on real signals (SLOs, synthetic transactions, real-request error rate), not on "is up".
3. **Decouple deploy from release.** Deploy the code cold (no users); release it warm (flip a flag, shift traffic). This separation is where all the safety comes from.
4. **Small batches.** Frequent small deploys beat rare large ones on both risk and MTTR. DORA data is clear.
5. **Progressive exposure.** 1% → 10% → 50% → 100%. Each step has an abort signal.
6. **Bake time.** A revision is not "shipped" the moment traffic is at 100%. Give it time to exhibit slow bugs before declaring done.

## Deploy strategies — pick the right one

| Strategy | What it is | Best when | Watch out for |
|----------|-----------|-----------|---------------|
| **Rolling** | Replace N% of instances at a time | Default for stateless services | Mixed versions serving traffic at once; compat matters |
| **Canary** | Route X% of traffic to new version | Risk-averse; changes with uncertain blast radius | Needs good SLI gating to decide go/no-go |
| **Blue/green** | Two full environments; flip router | Fast rollback is the priority, infra cost OK | Double resources during overlap; DB is shared |
| **Shadow / dark launch** | Send traffic to new version but discard response | Validating latency / error profile at real load without impact | Does not test mutating behavior |
| **Feature flag** | Deploy code dark, toggle users on | Product change with user-visible behavior | Flag rot; forgotten flags become config landmines |

Default for a stateless service: **rolling with canary weighting** (1% → 10% → 50% → 100%, SLO-gated).

## Pre-deploy checklist

Before hitting deploy:

- [ ] CI is green — tests, lint, typecheck, security scan, image scan.
- [ ] Image is signed (see [`container-image-hardening`](../container-image-hardening)) and pulled from the expected registry + tag (no `:latest`).
- [ ] Change has been reviewed ([`code-review`](../code-review)).
- [ ] Risk assessed: config change / code change / DB change / infra change — different risk profiles, different caution levels.
- [ ] Rollback plan written down in the PR or deploy ticket. Exact commands.
- [ ] Observability in place: dashboards open, alerts not muted, SLO burn-rate visible.
- [ ] Error budget is healthy enough to absorb a bad deploy. If budget is exhausted, rethink.
- [ ] Change window respected. No risky deploys on Fridays or into holidays unless the budget demands it.
- [ ] Stakeholders notified if SEV-2+ risk (product, support, SRE on-call).
- [ ] Feature flags default-off unless explicitly decided otherwise.
- [ ] Deploy is annotated on dashboards (deploy markers) — see [`observability`](../observability).

## The rollback plan comes FIRST

Write the rollback commands **before** writing the deploy commands. If writing the rollback is hard, the deploy shape is wrong.

### What a real rollback plan looks like

```
Deploy:
  helm upgrade api ./charts/api --set image.tag=v1.42.0

Rollback (under 2 min):
  helm rollback api <previous-revision>
  # OR
  kubectl rollout undo deployment/api -n prod

Data rollback:
  Forward-only migration — no data rollback. Old code is compatible with new schema.
  (See "Database migrations" below.)

Abort criteria (auto or manual):
  - Canary: 5xx rate > 2x baseline for 2 min
  - Canary: p99 latency > 1.5x baseline for 5 min
  - Manual: any unexpected user report from support within 30 min of deploy
```

Rollback plans that say "redeploy the previous version" with no commands are fiction.

## Kubernetes patterns

### Deployment essentials

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: prod
  annotations:
    kubernetes.io/change-cause: "v1.42.0 — PR #847"   # populates `rollout history`
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0     # zero-downtime: never drop below target
  revisionHistoryLimit: 10    # enables rollback
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
        version: v1.42.0
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: registry.example.com/api@sha256:...   # digest, not tag
          readinessProbe:
            httpGet: { path: /healthz/ready, port: 8080 }
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /healthz/live, port: 8080 }
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 6
          startupProbe:
            httpGet: { path: /healthz/live, port: 8080 }
            failureThreshold: 30
            periodSeconds: 5
          lifecycle:
            preStop:
              exec: { command: ["/bin/sh", "-c", "sleep 10"] }   # drain connections
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { memory: 512Mi }                           # no CPU limit by default
```

Key rules:
- **`maxUnavailable: 0`** for a truly zero-downtime rolling deploy. `25%` is the default but is not zero-downtime.
- **`readinessProbe` gates traffic**, not `livenessProbe`. Wrong probe config is the #1 cause of fake "successful" deploys that immediately error.
- **`livenessProbe` restarts the pod** when it is truly stuck. Make it lenient; tight liveness checks cause restart storms.
- **`startupProbe`** for slow-starting apps — do not abuse `initialDelaySeconds` on liveness.
- **`preStop` + `terminationGracePeriodSeconds`** — let the LB notice the pod is going before it dies.
- **Pin the image by digest** (`@sha256:...`), not tag. Tags are mutable; digests are not.
- **`PodDisruptionBudget`** for any workload that must stay available during cluster operations.
- **`revisionHistoryLimit`** > 0 so `kubectl rollout undo` works.

### Probes that actually tell the truth

- `/healthz/live` — process is alive (no deadlock). Returns 200 quickly. **Do not** check downstream dependencies.
- `/healthz/ready` — ready to serve. Checks DB pool, cache connection, required downstreams. Returns 503 when not ready.
- Distinct endpoints. The #1 misconfiguration is using one `/health` for both — a DB blip then restarts every pod.

### Canary via Argo Rollouts / Flagger

If the org is doing progressive delivery on K8s, prefer [Argo Rollouts](https://argo-rollouts.readthedocs.io/) or [Flagger](https://flagger.app/) over hand-rolled canaries.

Minimum canary shape (Argo Rollouts):

```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: { duration: 5m }
      - analysis:
          templates: [{ templateName: canary-slo-gate }]
      - setWeight: 50
      - pause: { duration: 10m }
      - analysis:
          templates: [{ templateName: canary-slo-gate }]
      - setWeight: 100
```

The `analysis` step pulls from Prometheus (or other) and fails the rollout if SLIs cross a threshold. **Never skip the analysis step** — that is what makes it a canary instead of a rolling deploy with extra steps.

## AWS patterns

### ECS

- Use `CodeDeploy` with ECS deployment type `BLUE_GREEN` for zero-downtime + fast rollback.
- Set `DeploymentConfiguration.MinimumHealthyPercent >= 100` and `MaximumPercent >= 200` for surge + zero-drop.
- Health checks on the target group should match the readiness probe philosophy (independent of deep dependencies).
- Use deployment alarms (CloudWatch) so rollback fires automatically on SLO breach.

### Lambda

- Always deploy to an **alias** (e.g. `live`), not `$LATEST` directly.
- Use `CodeDeploy` with `Canary10Percent5Minutes`-style traffic shifting.
- Attach pre-traffic / post-traffic hooks (Lambda functions) for validation.

### Cloud Run (GCP)

- Deploy with `--no-traffic` first. Route traffic with `gcloud run services update-traffic --to-revisions=NEW=10` progressively.
- Revisions are immutable — rollback is just `update-traffic --to-revisions=PREV=100`.

## Database migrations — the risky kind

Database schema changes are the deploys most likely to corner you into a forward-only mess. Follow the **expand / contract** pattern:

### Expand / contract

1. **Expand** — additive change: new column / table / index. Old and new code both work. Deploy schema.
2. **Code** — new code writes to new column; reads prefer new, falls back to old. Deploy. Observe.
3. **Backfill** — populate new column for existing rows. Batched, throttled, idempotent.
4. **Cutover** — all reads/writes now use new. Deploy.
5. **Contract** — drop old column / table / index. Deploy schema.

Each step is independently deployable and reversible. Never do expand + cutover + contract in one deploy — that is the recipe for a rollback that needs a backup restore.

### Rules

- Migrations run **outside** the app container, often in a dedicated job (`kubectl create job`, Flyway, Liquibase, Alembic). Not at app startup — that couples deploy health to DB availability.
- Lock-free migrations (`CREATE INDEX CONCURRENTLY`, `ALTER TABLE ... SET NOT NULL NOT VALID` + `VALIDATE` later). Avoid full-table locks on hot tables.
- Test the migration against a prod-size snapshot in staging. A migration that runs in 2s on a 10k-row staging can take 4h on prod.
- Have a documented **rollback SQL** — even if it is "forward-only; revert to PITR from <time>".
- Backups and point-in-time recovery verified **before** the migration, not discovered broken after.

## Feature flags — the decoupling lever

Feature flags separate deploy from release. Deploy cold code, flip a flag to release.

### Rules

- **Default off** unless the product explicitly wants it on.
- **Kill switch** flag on every risky feature — a boolean to disable instantly without code change.
- **Per-tenant / per-percentage gating** — release to 1 test tenant → 5% users → 100%.
- **Flag has an expiration / cleanup date.** Track in the issue tracker. A flag older than 6 months is almost always dead weight.
- **Audit trail** — who flipped what, when. Flag toggles are production changes.

Tools: LaunchDarkly, Unleash, Flagsmith, OpenFeature, ConfigCat — or a home-grown flag table gated with a cache. Pick one per org, not per service.

### Anti-patterns

- Flag inside another flag. Combinatorial explosion.
- Flag controls security — use auth/authz, not flags.
- Flag read on the hot path without caching. Latency hit + failure mode when flag service is down.

## Deploy abort criteria

The canary must be **abortable** automatically and manually. Every deploy defines its abort criteria up front.

Typical thresholds:

| Signal | Threshold | Window | Action |
|--------|-----------|--------|--------|
| 5xx rate on canary | > 2x baseline | 2 min | auto-abort |
| p99 latency on canary | > 1.5x baseline | 5 min | auto-abort |
| Error-budget burn rate | fast-burn alert fires | any | auto-abort |
| Log-volume anomaly on canary | > 5x baseline | 2 min | human review |
| Manual | any unexpected user report | 30 min post-deploy | manual abort |

Abort by **pulling traffic**, not by rolling the image back. Traffic pull is instant; image rollback takes a minute. Roll back the image **after** traffic is off.

## Bake time

The deploy is not done at 100% traffic. It is done after **bake time** at 100% with SLOs green.

Suggested bake:
- Config-only change: 15-30 minutes.
- Code change: 1-2 hours.
- Database / schema change: 24 hours.
- Platform / infra change: 24-72 hours.

During bake, do not start another risky deploy on top. One variable at a time.

## Post-deploy actions

- [ ] Deploy annotated on dashboards.
- [ ] Rollback plan archived with the deploy ticket.
- [ ] Feature-flag cleanup ticket filed if applicable.
- [ ] On-call notified of any elevated risk window.
- [ ] Observability SLOs / alerts are still appropriate (new endpoints? new dependencies?).
- [ ] Post-deploy validation: synthetic check, happy-path traces, one real user report.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Deploy on Friday afternoon | No one is around to fix it |
| Rolling deploy without canary | Mixed versions serve traffic with no abort signal |
| Liveness probe checks DB | Restart storm when DB blips |
| Readiness probe is the same as liveness | Both lie; deploys look healthy while broken |
| Image tag `:latest` or `v1.42` (tag, not digest) | Tag can change silently |
| Migration runs at app startup | App unhealthy = migration stuck = deploy frozen |
| "Big deploy" — 10 PRs worth of changes | Rollback is all-or-nothing; MTTR worse |
| No feature flag on a product change | Rollback requires re-deploy instead of flag flip |
| Rollback plan "redeploy previous version" | Vague; fails under pressure |
| 100% deploy and walk away | Slow bugs surface hours later |
| Disable alerts during deploy window | Miss real regressions |
| Error budget exhausted, deploy anyway | Pattern of burnout deploys + outages |
| Old feature flags never cleaned up | Landmines; cost of change grows |

## Interaction with other skills

- [`incident-response`](../incident-response) — when a deploy breaks prod, drop into incident response. Rollback is the first stabilization lever.
- [`observability`](../observability) — the SLI/SLO/burn-rate system gates the canary. Without it, you are rolling dice.
- [`container-image-hardening`](../container-image-hardening) — supply-chain side of the same problem. Image integrity + digest pinning.
- [`kubectl-workflows`](../kubectl-workflows) — dry-run-before-apply, explicit `--context`/`--namespace`. Applies to every manifest change in this skill.
- [`awscli-workflows`](../awscli-workflows) — explicit `--profile`, `--region`; safety around `deploy create-deployment` and friends.
- [`terraform-iac-expert`](../terraform-iac-expert) — infra-level deploys (ALB, DNS, RDS parameter groups). Plan + apply, tagged with reason.
- [`github-actions-workflows`](../github-actions-workflows) — CI/CD pipeline patterns that implement this skill.
- [`pr-workflow`](../pr-workflow) — PR template should include deploy risk + rollback plan.

## Verification checklist

Before starting a deploy:

- [ ] Rollback commands are written and tested in a lower environment.
- [ ] Image is pinned by digest and signed.
- [ ] Observability is alive: dashboards open, alerts unmuted, SLOs visible.
- [ ] Abort criteria are written down (thresholds + windows).
- [ ] Canary weights and pause durations are defined, not invented on the fly.
- [ ] DB migration (if any) follows expand/contract; backfill is throttled and resumable.
- [ ] Feature flag is wired and off by default (if applicable).
- [ ] Readiness probe is independent of liveness probe and tells the truth.
- [ ] `PodDisruptionBudget` / equivalent protects the workload.
- [ ] Stakeholders know.
- [ ] Error budget is healthy.

During / after:

- [ ] Each canary step passed its SLI gate before advancing.
- [ ] Bake time elapsed without regression.
- [ ] Deploy annotated on dashboards.
- [ ] No orphan feature flags; cleanup ticket filed if applicable.
- [ ] Post-deploy synthetic / smoke ran green.
