---
name: disaster-recovery
description: Design, test, and operate disaster-recovery capability — backups that restore, RTO/RPO targets tied to business impact, failover drills, data-integrity verification, region-loss scenarios. Use WHENEVER the user (1) designs or reviews a backup strategy (RDS snapshots, PITR, S3 versioning, EBS snapshots, Velero, pg_dump schedules); (2) sets RTO (recovery time) or RPO (recovery point) targets; (3) runs a DR drill / game-day / chaos experiment / failover test; (4) audits whether backups actually work (untested backup = no backup); (5) plans multi-region / multi-AZ / cold-standby / warm-standby / hot-standby architecture; (6) mentions "backup", "restore", "DR", "disaster recovery", "RTO", "RPO", "pilot light", "warm standby", "failover", "region down", "data loss", "chaos engineering". Pairs with `incident-response` (a DR event IS an incident) and `observability` (backup-age and restore-success are themselves SLIs).
---

# Disaster Recovery

A backup you have never restored is not a backup — it is a prayer. DR is the discipline of turning that prayer into a tested, timed, documented capability.

The fundamental question: **if the primary region / cluster / database disappears in the next five minutes, how long until service is restored, and how much data is lost?** Those two numbers — **RTO** and **RPO** — are business decisions expressed in seconds and dollars.

This skill is about the full loop: **define targets → design to meet them → test → operate → audit**. It pairs with [`incident-response`](../incident-response) (a DR event is an incident), [`observability`](../observability) (backup age is an SLI), [`database-migrations`](../database-migrations) (backups are the only real rollback for irreversible DDL).

## When to use

- Designing a backup strategy for a new service or system.
- Reviewing an existing backup strategy that has never been tested.
- Setting or negotiating RTO / RPO with the business.
- Planning a DR drill / failover game-day / chaos experiment.
- Auditing whether backups actually restore.
- Architecting multi-region / multi-AZ fallback.
- After an incident revealed a gap in recovery.

### When NOT to use

- Application-layer rollback of a single deploy → [`deploy-safety`](../deploy-safety).
- Schema migrations → [`database-migrations`](../database-migrations).
- In-process failures with no data-loss risk → [`diagnose`](../diagnose).

## RTO and RPO — make them concrete

**RPO (Recovery Point Objective)** — the maximum tolerable data loss, measured in time. "We can lose at most 5 minutes of writes."

**RTO (Recovery Time Objective)** — the maximum tolerable downtime, measured in time. "Service restored within 1 hour."

These are not technical numbers; they are business decisions. They drive architecture and cost.

### Typical tiers

| Tier | RPO | RTO | Pattern | Cost multiplier |
|------|-----|-----|---------|-----------------|
| **Cold standby** | hours | hours - day | Periodic backup; rebuild on failure | 1x |
| **Pilot light** | minutes | < 1h | Core data replicated; compute scaled on demand | 1.5-2x |
| **Warm standby** | seconds-minutes | minutes | Running replica at reduced capacity | 2-3x |
| **Hot standby / active-active** | near-zero | seconds | Two primaries in sync | 3-5x |

Pick per system, not per company. A user-facing checkout likely needs warm; a nightly report pipeline likely does cold.

### RTO/RPO per domain

Break down the system into RTO/RPO-distinct units:

```
Checkout API        → RPO 1 min,    RTO 10 min   (revenue impact)
User profile        → RPO 1 hour,   RTO 1 hour   (login still works)
Analytics pipeline  → RPO 1 day,    RTO 1 day    (reports delayed)
Logs / observability → RPO 1 hour,  RTO 4 hours  (post-incident review)
Documents / S3      → RPO 15 min,   RTO 30 min   (compliance)
```

Never claim a single global RTO/RPO. The number hides the weak link.

## Backup types — know the trade-offs

### Application / database

| Type | Captures | Restore time | Typical RPO |
|------|----------|-------------|-------------|
| **Logical dump** (`pg_dump`, `mysqldump`) | Schema + data as SQL | Slow; proportional to data size | Last dump — usually daily |
| **Physical snapshot** (RDS, EBS, VolumeSnapshot) | Block-level state | Fast (attach volume) | Last snapshot — usually hourly |
| **Continuous WAL / binlog shipping** | Every transaction | PITR possible | Seconds |
| **Logical replication** (streaming) | Every transaction | Already hot | Seconds - zero |
| **Hot standby / multi-AZ** | Every transaction, synchronous | Already hot | Zero |

Most production systems combine: **physical snapshot for baseline + WAL for PITR + replica for HA**.

### Object storage

- **Versioning on S3 / GCS / Azure Blob** + lifecycle policies + Object Lock / retention policies for compliance.
- **Cross-region replication** for regional redundancy.
- **Do not rely on soft-delete** — configure MFA Delete or Object Lock for true immutability.

### Configuration / secrets / infra

- **GitOps** — infra is code; restore = re-apply from git. Terraform state itself needs backup (versioned S3 + DynamoDB lock state).
- **Secrets**: AWS Secrets Manager / HashiCorp Vault have their own replication model; verify for your vendor.
- **Kubernetes state**: [Velero](https://velero.io/) backs up etcd + PV snapshots. `etcdctl snapshot save` for self-managed clusters.

### Logs / metrics / traces

Often overlooked:
- **Metric series**: Prometheus remote-write to a long-term store (Thanos / Mimir / Cortex / vendor).
- **Logs**: ship to S3 / GCS with lifecycle rules; replicate across regions.
- **Traces**: same, though retention is usually shorter.

Without these during a DR event you fly blind.

## 3-2-1-1-0 rule (modern)

Classic "3-2-1" backup rule, updated for ransomware / supply-chain:

- **3** copies of data.
- **2** different storage media.
- **1** off-site copy (different region / cloud / provider).
- **1** offline / immutable copy (Object Lock, air-gapped, write-once).
- **0** errors after restore verification.

The final "0" is what separates hope from capability.

## Test the restore, not the backup

The only thing that matters is: **can we restore, and how long does it take?**

Every backup must have a paired **test job** that runs on a schedule:

1. Pick a recent backup.
2. Restore to a scratch environment.
3. Run a data-integrity check (row counts, checksums, application smoke test).
4. Measure duration.
5. Alert on failure or duration regression.
6. Report metrics: `backup_age`, `last_successful_restore_age`, `last_restore_duration_seconds`.

If you cannot restore on demand, you do not have backups.

### Restore test cadence

| System importance | Restore test cadence |
|------------------|---------------------|
| SEV-1 data (revenue, compliance, user data) | Weekly |
| SEV-2 data | Monthly |
| SEV-3 data (internal) | Quarterly |

Cadence decays with data criticality; never "once a year" for critical data — drift accumulates.

### Backup-age SLI / SLO

Treat backup freshness as an SLI. Example Prometheus alert:

```yaml
- alert: BackupAgeHigh
  expr: time() - backup_last_success_timestamp{service="postgres-prod"} > 6 * 3600
  for: 5m
  labels:
    severity: page
    team: platform
  annotations:
    summary: "Postgres backup age > 6h"
    runbook: https://runbooks/platform/postgres-backup-age
```

Similarly alert on `restore_last_success_age` — if the automated restore hasn't run successfully recently, the backup is untested again.

See [`observability`](../observability).

## DR drill — quarterly game-day

A plan on paper is a wish. Exercise it.

### Drill scope levels

1. **Tabletop** — walk through the runbook with the team; confirm access, escalation, ownership. Lightweight, no production impact. Run quarterly.
2. **Partial failover** — failover one dependency to its standby (read replica → primary promotion, one AZ down simulation).
3. **Full regional failover** — take the primary region offline, bring up DR region, run for hours. Intensive, annual.
4. **Red team / chaos** — unannounced failure injection. Only when the team is ready.

Each drill produces action items. File them like [`incident-response`](../incident-response) postmortems.

### Drill readiness checklist

Before a drill:

- [ ] Everyone on-call knows it is happening.
- [ ] Customer-facing comm plan (status page note "planned exercise").
- [ ] Abort criteria defined — when do we call it off?
- [ ] Time-bounded — if drill runs over N hours, declare "exercise failed to meet RTO" and restore normal ops.
- [ ] Observation-only stance first; record data, do not fix issues live unless the exercise depends on the fix.

### Post-drill

- Blameless postmortem — what went well, what went badly (see [`incident-response`](../incident-response)).
- Actions tracked in the issue tracker.
- Run the same drill shape again in 6 months to measure improvement.

## Chaos engineering — a specific subset

Chaos is continuous, fine-grained DR practice:

- [Litmus](https://litmuschaos.io/) — Kubernetes chaos.
- [Chaos Mesh](https://chaos-mesh.org/) — similar, CNCF.
- [AWS Fault Injection Service](https://aws.amazon.com/fis/) — AZ failure, EC2 kill, latency injection.
- [Gremlin](https://www.gremlin.com/) — commercial.

Rules:
- **Start in staging**. Only graduate to production when the team understands the blast radius.
- **Hypothesis first** — "If we kill 1 Kafka broker, consumer lag peaks at X but does not fail". Chaos without a hypothesis is vandalism.
- **Abort switch ready** — can you stop injecting in under 10 seconds?
- **Observability in place** — chaos that you cannot observe is not an experiment.

## DR for Kubernetes

The cluster's own state + workloads.

### Cluster state

- **etcd snapshot**: `etcdctl snapshot save`. Store encrypted and off-cluster. For managed K8s (EKS / GKE / AKS) this is handled by the provider, but you cannot restore selectively — be aware.
- **Velero** — back up namespaces / resources / PersistentVolume snapshots. Scheduled, to object storage. Supports cross-region restore. Test restores.

### Workload state

- **Stateless services**: no backup needed; re-deploy from git / container registry.
- **Stateful services**: the data is in a PV / external DB. Back up the data, not the pod.
- **ConfigMaps / Secrets**: in git (encrypted via SOPS / sealed-secrets) or external secret store.

### GitOps as DR

If every workload is reconciled from git (ArgoCD / Flux), then restoring from disaster is:

1. Stand up a fresh cluster.
2. Point ArgoCD / Flux at the git repo.
3. Wait for sync.
4. Restore data volumes / databases from their own backups.

Test this annually with a `destroy-and-rebuild` drill.

See [`kubectl-workflows`](../kubectl-workflows) and [`helm-workflows`](../helm-workflows).

## DR for AWS

### RDS / Aurora

- Automated backups on (retention 7-35 days).
- Manual snapshots before risky DDL.
- PITR to any second within retention.
- Cross-region automated backups (Aurora: `CopyTagsToSnapshot`, `KmsKeyId`).
- Read replicas across AZs (and regions for warm standby).
- Test: quarterly `RestoreDBInstanceFromDBSnapshot` into a scratch VPC, run schema diff + row-count parity.

### EBS

- Policies via [Amazon Data Lifecycle Manager](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lifecycle.html).
- Tag-based snapshot scheduling.
- Cross-region copy for DR.

### S3

- **Versioning**: always on for any bucket with mutable data.
- **Object Lock** in compliance or governance mode for regulatory data.
- **Cross-Region Replication** for redundancy.
- **Lifecycle rules** to Glacier / deep archive for old versions — cheap, still durable.
- **MFA Delete** for extra protection on critical buckets.

### DynamoDB

- Point-in-time recovery on, always.
- On-demand backup before destructive operations.
- Global Tables for multi-region active-active.

### IAM and KMS

- Customer-managed KMS keys with key rotation + cross-region replicas.
- IAM identity providers, policies, and roles: managed via Terraform / CloudFormation (see [`terraform-iac-expert`](../terraform-iac-expert)).
- Never store the only copy of a KMS key material in one region.

See [`awscli-workflows`](../awscli-workflows) for the safe-read-before-write rules around DR ops.

## DR for SaaS dependencies

Your DR is only as good as your weakest dependency.

- **Identity provider** (Okta / Azure AD / Google Workspace) outage → no logins. Plan the break-glass.
- **DNS** (Route53 / Cloudflare / Cloudflare for SaaS) → cache / TTL / multi-provider setup.
- **CDN** (CloudFront / Cloudflare / Fastly) → origin shields, failover patterns.
- **Email / SMS provider** → can't send password resets → DR-drill this.
- **Payment processor** → revenue impact; must have fallback or degraded mode.

For each critical SaaS:
1. What is their SLA?
2. What is our fallback if they are down for 4 hours?
3. Is the fallback tested?

## Ransomware-specific

Modern DR includes ransomware as a primary threat:

- **Immutable backups** (Object Lock, WORM, tapes) that even admins cannot delete.
- **Air-gapped or offline copies** of the most critical data.
- **Separate credentials** for backup systems — compromised prod credentials cannot also wipe backups.
- **Regular restore to a clean environment** — confirm backups themselves are not infected.
- **Detect before encrypt** — unusual file-modification rates as an alert signal.

## Documentation — the DR runbook

Every DR capability has a runbook. See [`runbook-authoring`](../runbook-authoring) for structure.

Minimum per critical system:

```markdown
# DR Runbook: <system>

- RTO target: <N minutes>
- RPO target: <N minutes>
- Owner: <team>
- Escalation: <channel>
- Last drill: <YYYY-MM-DD>, result: <pass/fail/partial>

## 1. Detect
  <alerts / dashboards that signal this failure>

## 2. Decide to fail over
  <criteria — usually "symptom persists > X minutes AND no recovery expected">

## 3. Fail over steps
  1. <exact command>
     Verify: <exact check>
  2. ...

## 4. Validate
  <smoke test, data integrity check, user-facing sample>

## 5. Communicate
  <customer + stakeholder updates>

## 6. Fail back (later)
  <separate runbook; do not attempt during the initial recovery>

## 7. Post-event
  <data-integrity reconciliation, postmortem scheduling>
```

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| "We have backups" with no recent restore test | Almost always broken in ways you will discover at the worst moment |
| RTO/RPO picked without business input | Over-engineered in the wrong place; under-engineered in the critical place |
| Single-region architecture with no DR plan | One AWS us-east-1 event and you are out for a day |
| Backups in the same account / same region as primary | Ransomware or account compromise takes both |
| Credentials for backup system shared with prod | One compromise = total loss |
| DR runbook lives only in Confluence | Paywalled by Confluence being up |
| Nobody owns the backup job | Silent failure; nobody notices until disaster |
| Full-stack failover but untested DNS TTL | Customers still resolve to the dead primary |
| Manual steps in DR runbook that require an engineer's local tool | That engineer may be on holiday |
| Assumed read replicas are DR | They are not, until you test promotion under load |
| Tabletop-only drills | Only catches documentation gaps, not runtime gaps |
| DR tested only in the good-case scenario | Real DR is during the incident, at 3am, with half the team unavailable |
| "We will restore from X and figure it out" plan | Plans written during incidents cost minutes; RTO misses |
| Config / infra as code not in git | Nothing to reconcile against during cluster rebuild |

## Interaction with other skills

- [`incident-response`](../incident-response) — a DR event IS an incident. Combine the two disciplines.
- [`observability`](../observability) — `backup_age`, `last_restore_duration` are SLIs. Burn-rate alerts on them.
- [`database-migrations`](../database-migrations) — PITR is the only true rollback for some migrations. Verify PITR retention before the migration.
- [`runbook-authoring`](../runbook-authoring) — every DR capability has a runbook.
- [`deploy-safety`](../deploy-safety) — DR is not rollback. Application rollback is a different scope.
- [`security-hardening`](../security-hardening) — backup access control, backup encryption, key management.
- [`terraform-iac-expert`](../terraform-iac-expert) — infra as code is itself a DR asset.
- [`kubectl-workflows`](../kubectl-workflows) / [`helm-workflows`](../helm-workflows) — cluster + workload restoration path.
- [`awscli-workflows`](../awscli-workflows) — safe-by-default for the commands that touch DR assets.
- [`architecture-decision-records`](../architecture-decision-records) — record RTO/RPO decisions; record the choice of pilot-light vs warm-standby.
- [`pass-cli-secrets`](../pass-cli-secrets) — credentials for backup / DR paths are themselves in scope.

## Verification checklist

**Design phase:**

- [ ] RTO and RPO defined per system, agreed with business owners.
- [ ] Backup strategy documented per data class (app DB, object storage, secrets, K8s state, metrics / logs).
- [ ] 3-2-1-1-0 rule applied: ≥3 copies, ≥2 media, ≥1 off-site, ≥1 immutable.
- [ ] Backup credentials distinct from production credentials.
- [ ] Cross-region copies configured for critical data.
- [ ] Runbook written per critical system.

**Operating:**

- [ ] Automated restore test running on schedule; success / duration metrics published.
- [ ] `backup_age` alert configured with SLO.
- [ ] `last_successful_restore_age` alert configured.
- [ ] Drill performed within the last 6 months (partial or full).
- [ ] Action items from the last drill closed or tracked.

**During a DR event:**

- [ ] Incident declared (see [`incident-response`](../incident-response)).
- [ ] Runbook followed; deviations documented.
- [ ] Evidence preserved for postmortem.
- [ ] Customer communication on cadence.
- [ ] Clear resolution criteria before declaring recovered.
