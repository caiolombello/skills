---
name: aws-security-posture
description: Triage and govern AWS Security Hub CSPM findings and compliance controls. Use for FSBP, CIS, PCI DSS, NIST mappings, evidence, exceptions, risk acceptance, remediation plans, and post-remediation validation; not active compromises.
---

<!-- Inspired by aws/agent-toolkit-for-aws audit/remediation workflows (Apache-2.0) and AWS Security Hub CSPM guidance. See ../CREDITS.md -->

# AWS Security Posture

Convert AWS Security Hub CSPM findings into evidence-backed decisions and
verified remediation. Security Hub is a control signal, not a compliance
certificate or the authoritative record of business risk.

## Scope boundaries

Use this skill for:

- Security Hub CSPM organization, standards, controls, and findings.
- AWS Foundational Security Best Practices (FSBP).
- Relevant CIS, PCI DSS, NIST, and other supported standard mappings.
- AWS Config coverage that affects control evaluation.
- Finding triage, ownership, exceptions, risk acceptance, remediation, and
  revalidation.
- Security-posture reports and prioritized backlogs.

Do not use it as the primary workflow for:

- Active or suspected compromise — use
  [`aws-security-incident-response`](../aws-security-incident-response).
- Preventive architecture design — use
  [`aws-security-architecture`](../aws-security-architecture).
- Application vulnerabilities — use [`security-hardening`](../security-hardening)
  or a dedicated code-security scan.

## Non-negotiables

1. Treat standards and controls as dynamic. Discover the enabled/current
   versions and read the current control definition; do not rely on a hardcoded
   inventory.
2. Separate `observed`, `derived`, `assumed`, and `policy decision`.
3. Never equate a Security Hub score or all-passed view with compliance.
4. Never mark a real finding `RESOLVED` or `SUPPRESSED` merely to reduce noise.
5. A risk acceptance needs an owner, rationale, scope, expiry/review date,
   compensating controls, and approval outside the finding status alone.
6. Verify the resource and the control after remediation. API success is not
   proof of a fixed control.
7. Work read-only by default. Finding-status changes and infrastructure changes
   are writes.

If using AWS CLI, load [`awscli-workflows`](../awscli-workflows), identify the
caller, and pass explicit `--profile` and `--region`.

## Workflow

### 1. Define scope and authority

Record:

- Organization/account/OU, Region, environment, and resource owner.
- Aggregation/home Region and linked Regions.
- Delegated administrator and whether the account is centrally or locally
  managed.
- Enabled standards, policy requirements, and report period.
- Whether the request is read-only triage, workflow-status maintenance, or
  authorized remediation.

If the finding implies active malicious behavior, stop posture processing and
route it to AWS security incident response.

### 2. Confirm the data plane

Start with read-only discovery:

```bash
aws --profile <profile> sts get-caller-identity --output json
aws --profile <profile> --region <region> securityhub describe-hub
aws --profile <profile> --region <region> securityhub describe-standards
aws --profile <profile> --region <region> securityhub get-enabled-standards
```

Confirm AWS Config records every resource type required by the selected
controls. Missing recording, unsupported Regions, newly enabled controls, and
evaluation delay can produce a control status of `No data` or finding states
such as `WARNING` and `NOT_AVAILABLE`; none is interchangeable with pass or
fail.

### 3. Retrieve the exact finding and control

Capture:

- Finding ID, product ARN, generator/control ID, standard, account, Region, and
  resource ARN.
- `RecordState`, `Workflow.Status`, `Compliance.Status`, severity, first/last
  observed timestamps, and update history.
- Current control definition, parameters, evaluation method, Region
  availability, and remediation guidance.
- Actual resource configuration from the owning service.

Do not evaluate only a screenshot or email summary when the ASFF finding and
resource state are available.

### 4. Validate before prioritizing

Determine whether the finding is:

- A confirmed control failure.
- Stale or already corrected but waiting for reevaluation.
- A coverage/configuration problem.
- Not applicable to the scoped workload.
- A duplicate signal for one underlying issue.
- A potential false positive requiring evidence.
- A security event requiring incident response.

Read
[references/security-hub-governance.md](references/security-hub-governance.md)
for status semantics and disposition rules.

### 5. Prioritize contextual risk

Do not sort only by vendor severity. Evaluate:

```text
exposure × exploitability × privilege × data sensitivity × blast radius
× business criticality × detection/recovery weakness
```

Raise priority for public exposure, privileged identities, production data,
cross-account paths, security-tool tampering, missing logs, or easy
exploitation. Lower priority only with documented evidence and compensating
controls.

### 6. Choose a governed disposition

| Disposition | Use when | Required evidence |
|---|---|---|
| Remediate | Control objective applies and change is proportionate | Current state, approved target state, owner, plan, rollback, postcheck |
| Risk accept | Residual risk is knowingly accepted | Business owner, rationale, scope, expiry, compensating controls |
| Exception | Policy allows a time-bound deviation | Policy authority, scope, expiry, remediation or review date |
| False positive | Finding is factually incorrect | Resource/control evidence and provider follow-up |
| Not applicable | Control objective does not apply | Workload/data/scope reason and reviewer |
| Suppress signal | No action is needed for this finding class | Narrow rule, owner, review date, and proof that critical signals remain |

Risk accepted is not the same as remediated. Suppressed is not the same as
passed.

### 7. Plan remediation

For each action, include:

- Control objective and expected resource state.
- Resource owner and change owner.
- IaC source of truth and drift implications.
- Exact account, Region, resource, and permissions.
- Preview/dry run/change set.
- Blast radius, dependencies, downtime, lockout risk, and rollback.
- Direct resource postcheck and Security Hub re-evaluation check.

For AI-assisted remediation, use only a pre-approved, versioned action catalog;
never execute arbitrary model-generated privileged commands. Follow
[aws-security-architecture/references/cross-account-automation.md](../aws-security-architecture/references/cross-account-automation.md)
for delegated execution.

### 8. Execute only with authority

Prefer an IaC change and normal deployment path. If an emergency direct change
is approved:

1. Read current state and back up replace-all policies/configuration.
2. Show the exact target and command/change.
3. Obtain the required approval.
4. Apply the smallest bounded change.
5. Re-read the resource and test the intended behavior.
6. Reconcile the source of truth to prevent drift.

Do not loosen a guardrail, broaden IAM, or disable a control simply to make a
finding disappear.

### 9. Revalidate and close correctly

- Verify the service configuration directly.
- Account for the control's evaluation schedule.
- Confirm the finding updates to the expected compliance state.
- Change workflow status only after the investigation/remediation state is
  truthful.
- Preserve remediation evidence, approval, timestamps, and residual risk.
- If a control fails again, reopen the investigation; do not rely on the prior
  status.

## Required output

Lead with:

1. `Posture snapshot` — scope, coverage, and high-risk findings.
2. `Blockers/data quality` — missing Regions, Config coverage, permissions, or
   stale evaluations.
3. `Prioritized decisions` — finding, contextual risk, disposition, owner.
4. `Remediation plan` — preview, rollback, verification, and due date.
5. `Exceptions/accepted risk` — approval, compensating controls, and expiry.
6. `Evidence gaps` — what prevents a definitive conclusion.

## Interaction with other skills

- [`aws-security-architecture`](../aws-security-architecture) — defines the
  target preventive architecture.
- [`aws-security-incident-response`](../aws-security-incident-response) —
  handles active threats and suspected compromise.
- [`awscli-workflows`](../awscli-workflows) — governs every AWS CLI read/write.
- [`terraform-iac-expert`](../terraform-iac-expert) — implements approved IaC
  remediation.
- [`incident-response`](../incident-response) — provides incident command and
  communications when a posture finding becomes a live incident.

## Verification checklist

- [ ] Account, Region, aggregation, standard, control, finding, and resource are exact.
- [ ] Current control definition and resource state were inspected.
- [ ] AWS Config coverage and evaluation timing were considered.
- [ ] Contextual risk is distinct from vendor severity.
- [ ] Disposition has evidence, owner, and approval/expiry where required.
- [ ] No status update is being used to hide an unresolved issue.
- [ ] Remediation has preview, rollback, direct postcheck, and CSPM revalidation.
- [ ] Compliance claims are limited to the evidence actually collected.
