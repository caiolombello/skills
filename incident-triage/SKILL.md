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
3. Start read-only. Gather evidence before proposing remediation.
4. Prefer concrete evidence from Grafana, Kubernetes, and AWS over generic advice.
5. If service or environment is ambiguous, inspect local config and state instead of asking immediately.

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

You may use both freely.

Prefer Kubernetes MCP for:

- structured resource discovery
- listing workloads and objects
- quick cross-resource navigation

Prefer `kubectl` for:

- current context and namespace checks
- `get`, `describe`, `logs`, `top`, and `events`
- fast inspection of pod restarts, rollout state, probes, HPA behavior, and recent failures

Useful starting points:

```bash
kubectl config current-context
kubectl get ns
kubectl get pods -A
kubectl get events -A --sort-by=.lastTimestamp
kubectl top pods -A
```

If the cluster or namespace is hinted in the alert, filter early.

#### AWS CLI

You may use AWS CLI directly. The machine already has profiles configured.

Rules:

- Inspect `~/.aws/config` when you need to discover available profiles
- Always use `--profile`
- Pass `--region` when relevant; do not assume if the environment suggests another region
- Start with read-only commands

Useful discovery commands:

```bash
sed -n '1,240p' ~/.aws/config
aws sts get-caller-identity --profile <profile>
aws ec2 describe-instances --profile <profile> --region <region>
aws ecs list-clusters --profile <profile> --region <region>
aws eks list-clusters --profile <profile> --region <region>
aws cloudwatch describe-alarms --profile <profile> --region <region>
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
