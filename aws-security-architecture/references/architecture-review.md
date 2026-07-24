# AWS Security Architecture Review

Use this reference for a structured design review. Load only the sections that
match the workload.

## Contents

1. Security foundations
2. Identity and access
3. Network and edge
4. Data protection
5. Workload and delivery
6. Detection and evidence
7. Response and recovery
8. Review artifact
9. Primary sources

## 1. Security foundations

- Identify the organization management account and delegated administrators.
- Separate production, non-production, security, log archive, and shared
  services when their ownership or blast radius differs.
- Confirm how new accounts inherit baseline controls.
- Define preventive guardrails separately from detective checks.
- Protect break-glass access from accidental lockout while monitoring every use.
- Minimize the number of principals able to change Organizations, identity,
  logging, keys, or backups.
- Record mandatory tags, data residency, Region allowlists, and exception
  authority.

Evidence examples:

- Organization/OU/account map.
- SCP/RCP attachment and inheritance.
- Delegated administrator inventory.
- Root-user contact, MFA, and monitoring state.
- Landing-zone or account-vending templates.

## 2. Identity and access

- Centralize workforce identity and use short-lived sessions.
- Use workload identity instead of static keys.
- Separate deployment, runtime, read-only, incident, and break-glass roles.
- Scope trust policies as tightly as permission policies.
- Examine resource policies, permissions boundaries, session policies, SCPs,
  RCPs, and VPC endpoint policies together.
- Restrict `iam:PassRole`; treat broad pass-role plus compute creation as a
  privilege-escalation path.
- Protect service roles against confused deputy attacks with supported source
  conditions.
- Review public, external, and cross-account access continuously.
- Make session attribution visible through role-session names, source identity,
  session tags, and CloudTrail.

Evidence examples:

- Access Analyzer findings.
- IAM credential reports and last-used data.
- Role trust and permission policy review.
- Policy simulation, with the limitation that simulation is not proof of every
  resource-policy/SCP/session-policy path.

## 3. Network and edge

- Identify every public entry point and justify it.
- Separate ingress control, east-west segmentation, and egress control.
- Prefer private service access where it reduces exposure and operational
  complexity.
- Prevent administrative access paths from sharing the application data plane.
- Define DNS, TLS, certificate, WAF, DDoS, and origin-protection ownership.
- Inspect security groups, NACLs, route tables, transit paths, proxies, NAT,
  VPC endpoints, and hybrid links as one path.
- Log flows where the evidence value justifies cost and retention.
- Model exfiltration paths, including DNS, allowed SaaS endpoints, and
  cross-account resource sharing.

Evidence examples:

- Data-flow diagram with trust boundaries.
- Public IP/resource inventory.
- Reachability or network-access analysis.
- WAF/Shield configuration and response runbooks.

## 4. Data protection

- Classify data before selecting controls.
- Define ownership and administrative separation for KMS keys.
- Enforce encryption in transit and at rest where the control objective
  requires it.
- Scope decrypt permission separately from data read permission.
- Prevent destructive access to primary data, backups, and keys from sharing
  one role.
- Define versioning, immutability, retention, legal hold, and deletion policy.
- Test restore and integrity, not only backup creation.
- Keep secrets out of source, logs, plans, command output, and agent context.

Evidence examples:

- Data inventory and classification.
- Key policies/grants and rotation state.
- Bucket/database access policies.
- Backup restore-test results.
- Retention and deletion approvals.

## 5. Workload and delivery

- Reduce the runtime role to the APIs and resources the workload actually uses.
- Separate build identity from deploy identity and runtime identity.
- Pin and verify dependencies, actions, base images, and deployment artifacts.
- Require reviewable infrastructure changes and protected production promotion.
- Prevent untrusted pull requests from reaching privileged credentials.
- Harden metadata access and workload credential delivery.
- Define patching, image scanning, provenance, and rollback.
- Threat-model control-plane compromise in Kubernetes, serverless, and managed
  services rather than only host compromise.

Evidence examples:

- CI/CD trust and permission map.
- Deployment role and runtime role diff.
- Artifact/SBOM/signature records.
- Admission, policy-as-code, and drift checks.

## 6. Detection and evidence

- Centralize organization and multi-Region API activity with protected storage.
- Include data events selectively for high-value stores and functions.
- Confirm AWS Config records the resource types required by selected controls.
- Aggregate GuardDuty and Security Hub CSPM under delegated administrators.
- Protect logs from modification by workload and routine admin roles.
- Define alert ownership, severity, deduplication, and escalation.
- Preserve UTC timestamps and identity/session context.
- Prebuild queries for credential misuse, persistence, exfiltration, and
  detection tampering.

Evidence examples:

- Trail coverage and selectors.
- Log archive policy and integrity validation.
- GuardDuty/Security Hub/Config organization configuration.
- Alert route and runbook tests.

## 7. Response and recovery

- Pre-create clean incident roles and an evidence account.
- Test reversible isolation for IAM principals, EC2, S3, and workloads.
- Ensure containment cannot remove the responders' only access path.
- Define who can authorize disruptive containment.
- Document AWS Support and legal/regulatory escalation.
- Maintain known-good recovery artifacts and credential-rotation dependencies.
- Exercise scenario playbooks and record lessons.

Evidence examples:

- Incident role trust and permissions.
- Tabletop/game-day results.
- Evidence-store retention and access logs.
- Recovery verification reports.

## 8. Review artifact

Use one row per recommendation:

| Field | Meaning |
|---|---|
| Observation | Confirmed current state |
| Control objective | Outcome required by policy or threat |
| Threat/failure | What can go wrong |
| Recommendation | Smallest architecture change that meets the objective |
| Control type | Preventive, proactive, detective, or responsive |
| Owner | Team accountable for implementation and operation |
| Evidence | How deployment and effectiveness will be proved |
| Rollback/recovery | How to recover from implementation failure or lockout |
| Residual risk | Risk remaining after the control |

## 9. Primary sources

- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [AWS Security Reference Architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html)
- [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Organizations security best practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html)
- [AWS data protection guidance](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/data-protection.html)
- [AWS incident response guidance](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/incident-response.html)
