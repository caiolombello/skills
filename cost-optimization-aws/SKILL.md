---
name: cost-optimization-aws
description: 'Use when reducing AWS spend, explaining a bill spike, right-sizing, finding idle/orphaned resources, or reviewing cost before a new architecture ships. FinOps: visibility then optimize.'
---
# AWS Cost Optimization (FinOps)

Every AWS bill has waste. The question is how much and where. This skill is about finding it, cutting it safely, and keeping it from coming back.

**Order matters**: visibility → right-sizing → commitments → architecture. Committing to a three-year Savings Plan on an oversized fleet locks in waste for three years. Right-size first, commit second.

This skill pairs with [`awscli-workflows`](../awscli-workflows) for the command-safety side and with [`terraform-iac-expert`](../terraform-iac-expert) for the IaC side — tags that drive cost allocation live in the terraform, not in the console.

## The FinOps loop

```
1. INFORM     → cost visibility, tagging, unit-economics
2. OPTIMIZE   → right-size, reserved capacity, architecture
3. OPERATE    → budgets, alerts, governance, culture
```

Teams skip to step 2 and optimize the wrong thing. Step 1 is load-bearing.

## Step 1 — Inform

### Enable the Cost and Usage Report (CUR)

Cost Explorer is nice for humans; CUR is nice for queries. Enable:

- **CUR → S3 (with Athena integration)**. Hourly granularity, resource-level detail, tags.
- **Partitioning in Athena** by `year` and `month`.
- Retention: 13 months minimum for year-over-year comparison.

Once enabled, you can answer questions the console hides (e.g. "which `Project` tag spent how much on EC2 in us-east-1 last month").

### Tagging — the cost foundation

Cost allocation without tags is impossible. Canonical minimum tag set:

- `Environment` — `prod`, `staging`, `dev`, `sandbox`.
- `Project` — the product or workstream.
- `Owner` — team name or owner email.
- `CostCenter` — if you chargeback.
- `DataClassification` — public, internal, confidential. Drives encryption + backup decisions.

Enforce in Terraform (every resource inherits the module's tags). Enforce in SCPs (AWS Organizations Service Control Policies) for tagging on creation. Run an audit job that flags untagged resources.

See [`terraform-iac-expert`](../terraform-iac-expert) for module-level default tags.

### Define unit-economics

Cost in dollars is useless without a denominator. Pick a unit that scales with business value:

- Cost per active user.
- Cost per API request.
- Cost per order / transaction.
- Cost per tenant.

Publish a weekly dashboard of `cost / unit` — flat or falling is the goal. Absolute cost rising with traffic is expected; **unit cost rising** is waste.

## Step 2 — Optimize

### The 80/20 of AWS waste

Addressed in this order, these typically cover 80% of the savings on a typical bill:

1. **Oversized EC2 / RDS** — CPU < 20% p95, memory < 40%. Right-size or switch to burstable / Graviton.
2. **Idle resources** — unattached EBS volumes, old snapshots, Elastic IPs, empty load balancers, orphaned NAT Gateways.
3. **S3 storage class mismatch** — data that should be Intelligent-Tiering or IA / Glacier still in Standard.
4. **NAT Gateway and cross-AZ data transfer** — expensive and often accidental.
5. **EBS gp2 → gp3** — same performance, ~20% cheaper.
6. **CloudWatch Logs** — high retention on DEBUG logs; missing log-class filters.
7. **Unused Reserved Instances / Savings Plans coverage** — paying for unused commitments, or no commitment on stable baseline.
8. **Dev / staging accounts running 24/7** — schedule to off-hours.

### EC2 right-sizing

Signals (from CloudWatch + Trusted Advisor):

- CPU < 20% p95 for 14 days → downsize one tier.
- Memory < 40% (CloudWatch Agent required to measure) → downsize or switch family.
- Network < 10% → smaller instance / family.

Tactics:

- **Graviton (Arm)** — 20-40% cheaper for equivalent workloads. Needs Arm-compatible AMIs and container images (`linux/arm64`). See [`container-image-hardening`](../container-image-hardening) multi-arch section.
- **Burstable (T-family)** — for dev / staging / batch bursty load. Watch CPU credit balance; if it runs out, latency tanks.
- **Compute Optimizer** recommendations — AWS-generated right-size suggestions.
- **Graceful change** — change instance type during a rolling deploy; do not "stop + start" prod instances.

### Spot and Fargate Spot

- **Spot**: 60-90% discount, can be reclaimed with ~2-minute notice.
- Good for: batch jobs, stateless workers, K8s worker nodes (via Karpenter / Cluster Autoscaler).
- Bad for: single-instance services, long-running stateful workloads, anything that cannot tolerate termination.
- Use **Spot Placement Score** to pick instance family + AZ combinations with low interruption rates.

### Savings Plans vs Reserved Instances

| Option | Flexibility | Commitment | Savings |
|--------|------------|-----------|---------|
| **Compute Savings Plan** | Any region, any family, EC2/Fargate/Lambda | 1-3y, no-upfront / partial / all-upfront | Up to ~66% |
| **EC2 Instance Savings Plan** | One family + region | 1-3y | Up to ~72% |
| **Standard RI** | One instance family + region + OS | 1-3y | Up to ~72% |
| **Convertible RI** | Swappable family | 1-3y | Up to ~66% |

Modern advice: **Compute Savings Plans** for most stable baseline. Do not commit above ~70% of steady-state usage; leave room for the fleet to shrink.

Never commit for the first 3-6 months of a new workload. You do not yet know the baseline.

### RDS right-sizing

- `gp2` → `gp3` storage for all modern instances: ~20% cheaper, better baseline IOPS.
- Right-size: CPU / memory / storage IOPS + throughput metrics.
- Aurora Serverless v2 for spiky workloads.
- Multi-AZ: not cheap, not optional for prod (see [`disaster-recovery`](../disaster-recovery)).
- Old snapshots: delete after retention; they cost the same as live EBS snapshots.

### S3 optimization

- **Intelligent-Tiering** for anything accessed unpredictably — auto-moves between tiers based on access pattern.
- **Lifecycle rules** for predictable access patterns (move to IA at 30d, Glacier at 90d, deep archive at 1y).
- **Abort incomplete multipart uploads** — lifecycle rule; hidden bill item.
- **Requester Pays** for data-set buckets shared across orgs.
- **Delete old object versions** — versioned buckets accumulate silently.
- **Request costs matter**: PUT is ~10x GET. Consolidate small writes.

### Data transfer — the stealth cost

AWS data transfer pricing is ruthless and often hidden:

| Transfer | Typical cost |
|----------|--------------|
| **Same AZ, same VPC** (private IPs) | Free |
| **Cross-AZ, same VPC** | ~$0.01/GB each way |
| **Cross-region** | ~$0.02/GB |
| **To the internet** | $0.09/GB (first TB) |
| **Through NAT Gateway** | $0.045/GB + hourly |
| **VPC Endpoint (S3, DynamoDB)** | Free for same-region |

Common wins:
- **VPC endpoints for S3 / DynamoDB / ECR / Secrets Manager / etc.** Every private-subnet call to these services goes through NAT without a VPC endpoint. Adding endpoints routinely saves 4-5 figures / month.
- **Cross-AZ chatty services** (e.g. noisy sidecars replicating across nodes) — use topology-aware routing (K8s `topologyKey`).
- **CloudFront** for internet egress — cheaper and faster than serving directly.
- **Inter-region replication** only for truly regional requirements; prefer single-region with multi-AZ.

### NAT Gateway

One NAT Gateway = ~$32/month + $0.045/GB. For a busy VPC: $1000+/month on data charges.

Alternatives:
- **VPC endpoints** for AWS service calls (see above).
- **NAT instance** for dev / low-traffic: cheaper, less managed, HA is manual.
- **Private subnets without NAT** for workloads that genuinely do not need internet — fully private RDS, Lambda in VPC without egress.
- **Shared NAT Gateway** across accounts via Transit Gateway — consolidate.

### CloudWatch Logs

Fastest-growing forgotten cost.

- **Retention per log group** — default is "never expire". Set 7 / 30 / 90 days per importance.
- **Log Classes**: [CloudWatch Logs Infrequent Access](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatch_Logs_Log_Classes.html) for audit / compliance logs — 50% cheaper than Standard.
- **Sample** in the application: for a debug endpoint doing 10k req/s, log 1% not 100%.
- **Archive old logs to S3** + delete from CloudWatch.
- Avoid writing high-cardinality metrics via embedded metric format (EMF) — pricing multiplies.

### Kubernetes cost

On EKS:
- **Karpenter** for node autoscaling — consolidates pods, picks cheapest instance types, Spot-friendly.
- **Goldilocks** / **VPA recommendations** for per-pod right-sizing.
- **Cluster Autoscaler** with minimum nodes that match the workload's min requirement.
- **Fargate** for spiky or infrequent workloads — no node management but more expensive per-resource.
- **Spot** via Karpenter NodePools with interruption handling.

## Step 3 — Operate

### Budgets and alerts

- **AWS Budgets**: define per-account / per-project / per-service budgets with forecasted + actual alerts.
- **Anomaly Detection**: ML-based spike detection. Alert when a service deviates from its baseline.
- **Cost allocation reports**: monthly, per tag, per owner.
- **Slack / email integration**: alerts go to the owner of the over-spending tag.

Per [`observability`](../observability), treat bill-anomaly alerts like any other alert: actionable + linked to a runbook.

### Governance — prevent waste at creation

- **Service Control Policies (SCPs)** at the AWS Organization level:
  - Restrict large instance types in dev / sandbox accounts.
  - Require tags on resource creation (`aws:RequestTag/Environment`).
  - Block unused regions.
- **Terraform modules with defaults** that encode cost-aware choices (gp3, Graviton, lifecycle rules).
- **Account structure**: prod / staging / dev in separate accounts; easier to shut dev down, detect drift, and cap budgets.

### Run an orphan sweep monthly

Automate a scan for:

- Unattached EBS volumes → delete after snapshot.
- EBS snapshots older than the retention policy → delete.
- Unused Elastic IPs → release.
- Load balancers with zero healthy targets for N days → delete.
- NAT Gateways in subnets with zero traffic for N days → investigate.
- S3 buckets with no `LifecycleConfiguration` → flag.
- Stopped EC2 instances older than 30 days → delete.
- AMIs + snapshots not referenced by any launch template → delete.
- Orphaned security groups / IAM roles / CloudWatch log groups.

Tools: [`cloud-custodian`](https://cloudcustodian.io/) is the canonical tool — rules as YAML, AWS-native actions.

### Dev / sandbox account hygiene

Dev accounts run 24/7 by default; most workloads are idle 80+ hours / week.

- **Start / stop schedules** via EventBridge + Lambda or SSM.
- **Auto-shutdown after N hours idle** — cron Lambda that stops instances with no metrics.
- **Expiring resources** — tag with `ExpiresOn: YYYY-MM-DD` and a janitor job deletes past expiry.
- **Per-developer budgets** — $X/month/dev with hard alerts.

### Continuous unit-cost dashboard

A CUR-backed Athena query rendered in Grafana or QuickSight showing cost per business unit over time. Reviewed weekly by the team — the goal is to notice trends before the monthly invoice lands.

## Investigating a cost spike

Routine — bill alert fires, "why is AWS up $10k this week?"

Step-by-step:

1. **Cost Explorer → Group by Service → Daily**. Which service spiked?
2. **Group by Usage Type** inside that service. Was it `BoxUsage:m5.large`? `DataTransfer-Out-Bytes`? `Requests-Tier1`?
3. **Group by Resource ID** (if CUR is enabled) → which specific resource?
4. **Check tags** (`Project`, `Environment`) → which team owns it?
5. **Correlate with a deploy / traffic event**. Did a canary roll last Thursday? Did a DAG job start emitting 10x the metrics?
6. **Open a ticket** or fix on the spot. Document in the bill-anomaly postmortem.

A cost spike is an incident if it would blow the month's budget before month end. Run it like [`incident-response`](../incident-response) (detect → triage → stabilize) with a financial severity instead of a user-impact severity.

## Common wins by effort

### Quick (< 1 day each)

- `gp2` → `gp3` for all EBS volumes.
- Set CloudWatch Logs retention.
- Delete unattached volumes + old snapshots.
- Enable S3 Intelligent-Tiering on eligible buckets.
- Release unused Elastic IPs.
- Delete empty load balancers.
- Set up Cost Anomaly Detection.

### Medium (days)

- Add VPC endpoints for S3, DynamoDB, ECR, Secrets Manager.
- Right-size top 10 oversized EC2 / RDS instances.
- Migrate burstable workloads to T-family.
- Set up Budgets per project / environment.
- Add canonical tags to every resource via Terraform default tags.

### Large (weeks)

- Migrate to Graviton (ARM) base instances.
- Adopt Karpenter on EKS for node consolidation + Spot.
- Move long-term logs from CloudWatch to S3 + Infrequent Access.
- Purchase Compute Savings Plans at 60-70% coverage.
- Re-architect high-egress pipelines (CloudFront, cross-region dedup).

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| Buying a 3-year Savings Plan before right-sizing | Locks in waste for 3 years |
| Chasing $50 wins while ignoring a $10k NAT Gateway bill | Wrong order of operations |
| "Cost is not my problem, the finance team owns that" | Finance team cannot right-size your RDS |
| Over-provisioning "for safety" without measurement | Pay 3x for unused capacity |
| Deleting EBS volumes without a snapshot | "Cheap cleanup" → data loss |
| Turning off backups to save money | [`disaster-recovery`](../disaster-recovery) violation |
| Running prod in a single AZ to save on cross-AZ traffic | One AZ event and you are out |
| Using Spot for a critical single-instance service | Termination-surprise outage |
| Removing logs / metrics for cost without replacing them | Lose visibility; future incidents cost more |
| Dev accounts with full prod-like instance sizes | Dev is not prod; scale down |
| No tags, chasing costs manually in Cost Explorer | Cannot allocate, cannot optimize |
| Ignoring data-transfer charges because "compute looks cheap" | Data transfer is 20-40% of many bills |
| Manual cleanup once per year, no governance | Waste grows back between audits |
| Cost spikes become "just the way it is" | Unit economics decouple from business value |

## Interaction with other skills

- [`awscli-workflows`](../awscli-workflows) — the safe-CLI discipline for commands that touch cost assets.
- [`terraform-iac-expert`](../terraform-iac-expert) — default tags, module defaults for cost-aware resource choices.
- [`disaster-recovery`](../disaster-recovery) — cost-cutting must not erode backup / restore capability.
- [`observability`](../observability) — cost alerts are a kind of SLO; bill anomalies are their own signal.
- [`incident-response`](../incident-response) — major cost spikes are incidents.
- [`architecture-decision-records`](../architecture-decision-records) — commitments (Savings Plans, Reserved Instances, migration to Graviton) warrant an ADR.
- [`kubectl-workflows`](../kubectl-workflows) / [`helm-workflows`](../helm-workflows) — cluster autoscaling, HPA, VPA, Karpenter policies.
- [`container-image-hardening`](../container-image-hardening) — multi-arch images unlock Graviton savings.
- [`project-rules-file`](../project-rules-file) — the team's rules file captures the tagging / naming / sizing conventions.

## Verification checklist

Monthly FinOps hygiene:

- [ ] CUR enabled; Athena + Grafana/QuickSight dashboard up to date.
- [ ] Canonical tags enforced via Terraform + SCP; untagged resources audited.
- [ ] Unit-cost metric (cost / active user / request / order) tracked; trend is flat or down.
- [ ] Cost Anomaly Detection active; alerts routed to owners.
- [ ] Monthly orphan sweep ran and closed out.
- [ ] Top 20 spenders reviewed for right-sizing opportunity.
- [ ] Savings Plan / RI coverage at 60-70% of steady-state compute.
- [ ] CloudWatch Logs retention set per log group.
- [ ] S3 lifecycle rules present on all buckets; multipart uploads aborted.
- [ ] VPC endpoints configured for S3, DynamoDB, ECR, Secrets Manager, CloudWatch Logs.
- [ ] Dev / staging accounts have schedules + budgets + auto-expire tags.
- [ ] Bill-anomaly runbook exists and has been rehearsed.
