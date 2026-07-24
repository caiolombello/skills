---
name: aws-security-architecture
description: Design and review preventive AWS security architectures across accounts, identity, network, data, logging, and workloads. Use for landing zones, threat models, least privilege, cross-account access, or security architecture decisions; not live incidents or Security Hub finding triage.
---

<!-- Inspired by aws/agent-toolkit-for-aws rules and AWS service skills (Apache-2.0). See ../CREDITS.md -->

# AWS Security Architecture

Turn business and threat requirements into an AWS architecture with explicit
trust boundaries, control objectives, operational ownership, and verification.
Treat current AWS documentation and the organization's policies as authoritative
over remembered service behavior.

## Scope boundaries

Use this skill for preventive design or architecture review:

- Multi-account foundations, landing zones, Organizations, SCPs, and RCPs.
- Workforce, workload, service, and cross-account identity.
- Network segmentation, ingress/egress, private service access, and edge controls.
- Data classification, encryption, key ownership, backup, and retention.
- Logging, detection, auditability, resilience, and incident readiness.
- Threat models and security architecture decisions for AWS workloads.

Do not use it as the primary workflow for:

- Security Hub CSPM findings or control exceptions — use
  [`aws-security-posture`](../aws-security-posture).
- Suspected malicious activity or compromise — use
  [`aws-security-incident-response`](../aws-security-incident-response).
- Application-layer OWASP issues — use
  [`security-hardening`](../security-hardening).
- Terraform implementation details — use
  [`terraform-iac-expert`](../terraform-iac-expert) after the design is agreed.

## Operating mode

1. Work read-only unless the user explicitly asks for implementation.
2. Mark each input as `observed`, `required`, `assumed`, or `unknown`.
3. Verify service-specific behavior, quotas, IAM actions, and regional support
   against current official AWS documentation.
4. Prefer infrastructure as code and reviewable previews over direct changes.
5. Never claim that one control, service, or Security Hub score proves
   compliance.

If any AWS CLI command is needed, load
[`awscli-workflows`](../awscli-workflows) and use explicit `--profile` and
`--region`.

## Architecture workflow

### 1. Establish the security context

Collect only the facts that materially change the design:

- Workload purpose, environments, owners, and critical user journeys.
- Data classes, residency, retention, privacy, and key-custody requirements.
- Tenant model and external-party access.
- Applicable policy or regulatory obligations.
- Availability, RTO/RPO, recovery, and forensic-retention requirements.
- Existing account/OU structure, identity provider, network, and security tools.
- Threat actors, privileged paths, internet exposure, and acceptable residual
  risk.

Do not silently fill gaps. Record unknowns and state which decisions they block.

### 2. Draw trust and blast-radius boundaries

Map:

- AWS Organizations root, OUs, accounts, and delegated administrators.
- Human identities, workload identities, service principals, and third parties.
- Regions, VPCs, subnets, endpoints, egress paths, and public entry points.
- Data stores, keys, secrets, logs, backups, and evidence stores.
- CI/CD and administrative paths that can change production.

Separate environments and workloads with different ownership, data sensitivity,
or failure blast radius. An account is a stronger boundary than a VPC.

### 3. Threat-model privileged paths

For each critical asset, describe:

```text
asset -> entry point -> trust boundary -> privilege gained -> impact
```

Prioritize paths involving:

- Organization or account administration.
- `iam:PassRole`, role trust, resource policies, and confused-deputy risks.
- Public or cross-account data access.
- CI/CD credentials and infrastructure deployment roles.
- Log deletion, key disablement, backup deletion, and detection tampering.
- SSRF or workload compromise reaching instance/task metadata.

### 4. Select layered controls

For every material threat, choose controls in more than one category when
possible:

| Category | Purpose | Examples |
|---|---|---|
| Preventive | Block unsafe state | SCP/RCP guardrails, least privilege, private endpoints, encryption policy |
| Proactive | Reject drift before deploy | IaC policy checks, templates, CI validation |
| Detective | Expose unsafe behavior | CloudTrail, Config, GuardDuty, Security Hub CSPM, access analysis |
| Responsive | Limit impact and recover | Quarantine roles, reversible isolation, tested restore, incident playbooks |

Avoid service shopping. Start from the control objective, then choose the
smallest service set that satisfies it.

### 5. Design identity and delegation

- Prefer federation and temporary credentials over long-lived access keys.
- Separate human, workload, break-glass, discovery, and remediation roles.
- Scope `iam:PassRole` to explicit role resources and services.
- Protect service trust with source-account/source-resource conditions where
  the service supports them.
- Bound organization-wide administration with delegated admin accounts and
  guardrails that preserve emergency access.
- For customer or tenant accounts, use the cross-account pattern in
  [references/cross-account-automation.md](references/cross-account-automation.md).

### 6. Design evidence and operations

Ensure the architecture can answer:

- Who changed what, in which account and Region, using which session?
- Can an attacker disable or alter the logs that would investigate them?
- Where do findings aggregate, who owns them, and how are exceptions reviewed?
- Can the team isolate credentials, workloads, and data paths without destroying
  evidence?
- Are backup restore and security incident playbooks tested?

Read [references/architecture-review.md](references/architecture-review.md) for
the full review dimensions and expected output.

### 7. Validate the proposal

Review the design against:

- Explicit control objectives and threats.
- AWS shared-responsibility boundaries.
- Failure modes, lockout risk, and recovery access.
- Least privilege and cross-account trust.
- Regional and service availability.
- Operational ownership, cost, and complexity.
- Evidence that can prove each control is deployed and effective.

Use a change set, Terraform plan, policy simulation, or equivalent preview for
implementation. Keep architecture approval separate from execution approval.

## Required output

Lead with:

1. `Current state` — confirmed architecture and constraints.
2. `Unknowns/blockers` — facts that could change the recommendation.
3. `Threats and trust boundaries` — prioritized attack paths.
4. `Recommended controls` — control objective, service/pattern, owner, and
   evidence.
5. `Residual risks and decisions` — accepted, transferred, avoided, or pending.
6. `Implementation sequence` — reversible stages with validation and rollback.

For a review, classify recommendations as `critical`, `high`, `medium`, or
`advisory`, and explain business impact rather than relying on generic labels.

## Interaction with other skills

- [`aws-security-posture`](../aws-security-posture) — measures and governs
  deployed control state.
- [`aws-security-incident-response`](../aws-security-incident-response) —
  operates when preventive/detective controls signal a compromise.
- [`terraform-iac-expert`](../terraform-iac-expert) — implements the accepted
  design in Terraform/OpenTofu.
- [`security-hardening`](../security-hardening) — secures application code and
  user-facing trust boundaries.
- [`disaster-recovery`](../disaster-recovery) — designs and tests recovery
  capability.

## Verification checklist

- [ ] Requirements, observations, assumptions, and unknowns are separated.
- [ ] Account, identity, network, data, and administrative boundaries are shown.
- [ ] Critical assets have explicit attack paths and layered controls.
- [ ] Human, workload, discovery, remediation, and break-glass roles are distinct.
- [ ] Logging, evidence preservation, containment, and recovery are designed.
- [ ] Current AWS documentation backs version-sensitive claims.
- [ ] Every recommendation has an owner and verification evidence.
- [ ] No implementation or compliance claim exceeds the available evidence.
