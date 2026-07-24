# Security Hub CSPM Governance

Use this reference for finding semantics, triage, exceptions, suppression, and
evidence records. Verify current AWS documentation because standards, controls,
parameters, and regional coverage evolve.

## Contents

1. What Security Hub proves
2. Coverage checks
3. Finding states
4. Triage record
5. Exception and risk acceptance
6. Suppression safety
7. Remediation and revalidation
8. Primary sources

## 1. What Security Hub proves

Security Hub CSPM continuously evaluates supported technical controls when its
prerequisites and resource recording are present. It can provide evidence that:

- A specific supported check ran against a specific resource.
- The check produced a compliance status at a point in time.
- A finding moved through an investigation workflow.
- An enabled standard's applicable controls contribute to a security score.

It does not by itself prove:

- Full compliance with a law, contract, policy, or audit framework.
- That unsupported/manual controls are effective.
- That every account, Region, resource type, or data flow is in scope.
- That a passed configuration cannot be exploited.
- That an accepted risk was approved by the right business authority.

Keep the governance/risk record outside the finding when it needs richer
approval, expiry, ownership, or contractual meaning.

## 2. Coverage checks

Before interpreting results, verify:

- Security Hub is enabled in intended accounts and Regions.
- The delegated administrator and central configuration are correct.
- Home/aggregation and linked Regions match the organization policy.
- Standards and controls are enabled through the intended configuration policy.
- AWS Config records every required resource type in each Region.
- Global-resource recording follows the home-Region design.
- New accounts/OUs inherit the intended policy.
- Consolidated control findings and integrations are understood.
- Evaluation delay and unsupported Region behavior are accounted for.

The AWS-recommended central policy enables FSBP and all current/new FSBP
controls, but the organization must still configure AWS Config recording.
Choose additional standards based on actual business scope, not because more
standards automatically mean better security.

Discover the current standards with the API. Examples can include FSBP, CIS,
PCI DSS, NIST, and service-managed standards, but availability and versions can
change.

## 3. Finding states

Keep these fields distinct:

- `Compliance.Status` describes the result of a control check, such as
  `PASSED`, `FAILED`, `WARNING`, or `NOT_AVAILABLE`.
- `Workflow.Status` describes investigation progress, such as `NEW`,
  `NOTIFIED`, `RESOLVED`, or `SUPPRESSED`.
- `RecordState` describes whether the provider considers the finding active or
  archived.

Important consequences:

- A workflow status does not change the resource configuration.
- Suppressing or resolving one finding does not guarantee that a future check
  will not create or reopen a finding.
- A failed compliance state can reset a previously notified/resolved workflow
  to new.
- Suppressed findings are omitted from some control-status calculations and
  default views, so broad suppression can make posture look better without
  making it safer.
- A passed finding can resolve automatically; still retain the external change
  evidence when governance requires it.

## 4. Triage record

Record one row per decision:

| Field | Required content |
|---|---|
| Finding | Finding ID, product ARN, control/generator ID |
| Scope | Account, Region, environment, resource ARN |
| Time | First/last observed and triage UTC timestamps |
| State | Record, workflow, compliance, severity |
| Control | Current definition, parameters, evaluation method |
| Observation | Actual resource/service configuration |
| Context | Exposure, privilege, data, owner, criticality |
| Decision | Remediate, accept, exception, false positive, not applicable, suppress |
| Authority | Approver and governing policy |
| Action | Owner, target date, implementation path |
| Validation | Direct postcheck and future CSPM check |
| Residual risk | Remaining impact and compensating controls |

## 5. Exception and risk acceptance

A valid exception/risk record includes:

- The exact control objective and resources in scope.
- Evidence that normal compliance is not currently appropriate or feasible.
- Business and security owners.
- Approver with delegated authority.
- Start date, expiry/review date, and renewal criteria.
- Threats and business impact being accepted.
- Compensating controls and monitoring.
- Planned remediation, if temporary.
- Link back to each affected finding.

Do not turn a permanent exception into an unreviewed suppression rule. Do not
represent a temporary operational workaround as a policy exemption.

## 6. Suppression safety

Suppress only when no action is required for the narrowly defined signal. Before
creating an automation rule:

1. Enumerate every finding the rule would match.
2. Test on historical/sample findings.
3. Prove the filter cannot capture critical production signals.
4. Scope account, Region, product, control, resource, and environment as tightly
   as possible.
5. Record owner, rationale, review/expiry date, and rollback.
6. Monitor rule match volume and periodically sample suppressed findings.

If a control is truly irrelevant organization-wide, evaluate disabling it
through configuration policy rather than suppressing every resulting finding.
That is a policy decision requiring authority, not a noise-tuning shortcut.

Preserve credible GuardDuty and other threat-detection findings even when
removing duplicate email or notification routes. Deduplicate delivery, not the
security signal.

## 7. Remediation and revalidation

Use this evidence chain:

```text
finding -> resource observation -> approved desired state -> preview
-> change -> direct resource postcheck -> CSPM reevaluation -> governance record
```

If CSPM has not reevaluated yet, report `resource fixed; control pending
reevaluation` rather than claiming the finding is closed.

For GitOps/IaC-managed resources:

- Change the source of truth.
- Review the plan/change set.
- Deploy through the normal promotion path.
- Verify drift did not recreate the finding.

For direct emergency remediation:

- Capture current state and any replace-all policy first.
- Reconcile the IaC source immediately after stabilization.
- Record who authorized the bypass and why.

## 8. Primary sources

- [Security Hub CSPM standards reference](https://docs.aws.amazon.com/securityhub/latest/userguide/standards-reference.html)
- [FSBP standard](https://docs.aws.amazon.com/securityhub/latest/userguide/fsbp-standard.html)
- [Central configuration policies](https://docs.aws.amazon.com/securityhub/latest/userguide/configuration-policies-overview.html)
- [Finding workflow status](https://docs.aws.amazon.com/securityhub/latest/userguide/findings-workflow-status.html)
- [Compliance and control status](https://docs.aws.amazon.com/securityhub/latest/userguide/controls-overall-status.html)
- [Control finding generation and suppression](https://docs.aws.amazon.com/securityhub/latest/userguide/controls-findings-create-update.html)
- [Security Hub CSPM prescriptive guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/vulnerability-management/aws-security-hub.html)
