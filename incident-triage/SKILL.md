---
name: incident-triage
description: Use for first-response triage of PagerDuty, Alertmanager, or operational monitoring alerts with Grafana, kubectl, and AWS CLI. Not incident command or suspected AWS compromise.
---
# Incident Triage

Use this skill for first-response operational triage. Treat PagerDuty and Alertmanager as inputs, not as the whole workflow.

## Use This Skill When

- The user pastes a PagerDuty event, Alertmanager payload, or alert text
- The user asks "what should we do with this alert?"
- The user wants an initial incident investigation
- The user wants a ready-to-send status update for Slack, PagerDuty, or incident chat

Do not use this as the primary workflow for GuardDuty findings, exposed AWS
credentials, or suspected malicious activity. Use
[`aws-security-incident-response`](../aws-security-incident-response).

## Immediate Rules

1. Normalize the alert first. If the input is JSON, use `scripts/normalize_alert.py`.
2. Identify `service`, `environment`, `severity`, `alertname`, `cluster`, `namespace`, `workload`, and likely impact.
3. For Alertmanager groups, inspect every entry in the normalized `alerts` array. Treat top-level target/severity fields as group-wide only when they are shared; never scope a group from its first member.
4. Start read-only. Gather evidence before proposing remediation.
5. Prefer concrete evidence from Grafana, Kubernetes, and AWS over generic advice.
6. If an operational target, cluster context, namespace, AWS account/profile, or region is absent, ask the service owner or incident lead for it before querying. Do not infer authority or target from ambient local config.

## Investigation Workflow

### 1. Normalize

- If the alert is JSON, run `python3 scripts/normalize_alert.py <file>` or pipe JSON to stdin.
- If the alert is plain text, manually extract the same fields.
- Read [references/inputs.md](references/inputs.md) only if the payload shape is unclear.

### 2. Scope The Incident

Determine:

- Is this availability, latency, error-rate, saturation, deployment, or infra?
- What service and environment are affected?
- Is this customer-facing or internal-only?
- Is the alert grouped? If yes, identify whether the group is one root cause or many symptoms.

### 3. Choose Tools

#### Grafana MCP

Use Grafana MCP to:

- inspect alert context
- search dashboards
- get dashboard summaries instead of full JSON when possible
- query Prometheus or Loki for evidence
- inspect datasource or alert rule details when relevant

Prefer targeted queries and summaries over large dashboard payloads.

#### Kubernetes MCP And `kubectl`

Use the cluster and namespace named by the alert or confirmed by the incident owner. First compare the displayed local context with the expected cluster, then pass the explicit `--context` on every query. A current context is not itself authorization to inspect that cluster.

Prefer Kubernetes MCP for:

- structured resource discovery scoped to the named cluster and namespace
- listing only the workloads and objects implicated by the alert
- quick cross-resource navigation within that scope

Prefer `kubectl` for:

- `get`, `describe`, `logs`, `top`, and `events`
- inspection of pod restarts, rollout state, probes, HPA behavior, and recent failures

Useful scoped starting points (replace placeholders with the alert's verified target):

```bash
kubectl config current-context
kubectl --context <cluster-context> get pods --namespace <namespace> -l app=<service>
kubectl --context <cluster-context> get events --namespace <namespace> --sort-by=.lastTimestamp
kubectl --context <cluster-context> top pods --namespace <namespace> -l app=<service>
```

Do not begin with `-A` or another broad listing. Expand to additional namespaces or all namespaces only when the incident scope and authority include them, and state why the narrower target did not answer the question.

#### AWS CLI

Use AWS only after the incident context or service owner identifies the target account, profile, and region. Do not infer the target from local AWS configuration.

Rules:

- Always pass the explicitly selected `--profile`.
- Pass the verified `--region` for regional services.
- Start with read-only commands and confirm the returned account identity matches the incident target before querying resources.

Useful scoped discovery commands:

```bash
aws --profile <profile> --region <region> sts get-caller-identity
aws --profile <profile> --region <region> ec2 describe-instances --filters 'Name=tag:Service,Values=<service>'
aws --profile <profile> --region <region> ecs list-clusters
aws --profile <profile> --region <region> eks list-clusters
aws --profile <profile> --region <region> cloudwatch describe-alarms --alarm-names <alarm-name>
```

### 4. Build A Hypothesis

Correlate at least two signals when possible:

- alert payload
- Grafana metrics or logs
- Kubernetes state
- AWS resource state
- recent deployment or rollout evidence

Do not present a root cause as certain unless the evidence is specific.

### 5. Propose Next Actions

Order actions by risk:

1. Safe observation
2. Low-risk mitigation
3. Human approval needed for writes or disruptive actions

If a write action may be needed, clearly separate:

- what is proven
- what is inferred
- what action is proposed
- what could go wrong

## Output Format

Respond in this structure:

- `Summary`: one short paragraph
- `Impact`: who or what is affected
- `Evidence`: concrete observations only
- `Hypothesis`: most likely cause and confidence level
- `Next steps`: ordered actions
- `Escalation`: whether another team or owner should be involved

Use the fuller wording pattern in [references/response-template.md](references/response-template.md) when the user wants a message to forward.

## Heuristics

- `CrashLoopBackOff`, `OOMKilled`, probe failures, restarts: inspect pods, events, resource pressure, recent rollout
- `5xx`, latency, saturation: inspect dashboard trends first, then logs, then workload scaling and dependencies
- node or infra alerts: inspect cluster health, AWS node group or underlying instances, networking, and quotas
- noisy repeated alerts: determine whether deduplication failed or whether one dependency is fanning out into many symptoms

## Stop Conditions

Stop and say so when:

- the alert cannot be mapped to a service or environment with reasonable confidence
- the environment is inaccessible
- remediation requires destructive action without approval
- the evidence does not support a specific hypothesis yet

## Bundled Resources

- [references/inputs.md](references/inputs.md): field mapping for PagerDuty and Alertmanager payloads
- [references/response-template.md](references/response-template.md): response format for updates and handoffs
- `scripts/normalize_alert.py`: normalize common alert payloads into a stable JSON shape
