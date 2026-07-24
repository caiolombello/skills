# Cross-Account Security Automation

Use this reference when a platform or AI-assisted workflow reads or remediates
resources in customer, tenant, or business-unit AWS accounts.

## Contents

1. Recommended trust chain
2. Tenant isolation
3. Remediation catalog
4. Safe execution sequence
5. Trust-policy checks
6. Audit fields
7. Primary sources

## Recommended trust chain

```text
workload identity
  -> platform workload role
  -> broker/control-plane role
  -> tenant-specific discovery or remediation role
```

Keep discovery and remediation separate:

- The discovery role is read-only and broad enough to gather required evidence.
- The remediation role permits only approved actions and resources.
- A governance record authorizes a specific remediation; it is not itself an
  AWS permission.
- Jira or another tracker records execution work; it is not the source of risk
  acceptance or cloud authorization.

## Tenant isolation

- Give every customer or tenant a unique external identifier.
- Validate tenant authorization before selecting an account or role.
- Never accept an arbitrary role ARN, account ID, command, or policy supplied
  only by model output.
- Bind the selected role to the authenticated tenant and approved action.
- Use source identity and session tags where supported for attribution.
- Limit session duration and permissions.
- Record role assumption, selected action, parameters, approval, and result.

OIDC authenticates the platform workload to AWS. It does not by itself prove
which customer account the workload may enter. Cross-account trust still needs
tenant authorization and, for third-party access, an external identifier or an
equivalent confused-deputy defense.

## Remediation catalog

Do not allow an AI to generate and execute arbitrary privileged commands. Use a
versioned catalog:

```yaml
action: restrict-public-s3-access
version: 3
allowed_resource_types:
  - AWS::S3::Bucket
required_parameters:
  - account_id
  - region
  - bucket_name
preview: required
rollback: required
postcheck: required
approval_class: security-change
```

The AI may:

- Explain a finding.
- Select a catalog action.
- Derive and validate parameters from evidence.
- Produce a preview and risk summary.
- Recommend a rollback and postcheck.

The AI must not:

- Invent a new privileged action at execution time.
- Broaden role permissions to make a remediation succeed.
- Skip tenant authorization, approval, preview, or postcheck.
- Mark a finding resolved because an API call returned success.

## Safe execution sequence

1. Resolve tenant, account, Region, role, resource, and finding.
2. Confirm the current state using the discovery role.
3. Select a pre-approved action and validate parameters.
4. Produce a plan, policy diff, dry run, or CloudFormation change set.
5. Obtain the required human or policy approval.
6. Assume the narrow remediation role with attributable session metadata.
7. Execute one bounded change.
8. Verify the resource state and service control result.
9. Record evidence, rollback status, and residual risk.

Prefer CloudFormation change sets or Terraform plans when the resource is
managed as code. Prevent direct remediation from fighting GitOps or recreating
drift on the next deployment.

## Trust-policy checks

- Scope the trusted principal.
- Require the tenant external identifier where appropriate.
- Add supported source-account/source-resource conditions for AWS services.
- Avoid wildcard principals and uncontrolled principal tags.
- Confirm SCPs, RCPs, permissions boundaries, session policies, resource
  policies, and endpoint policies do not create an unexpected bypass or deny.
- Preserve a tested incident/break-glass path.

## Audit fields

Capture at minimum:

- Governance record and approval ID.
- Tenant, account, Region, resource ARN, and finding/control ID.
- Workload identity and all assumed-role session identifiers.
- Catalog action and version.
- Preview/change-set digest.
- Start/end UTC timestamps.
- API result, postcheck evidence, and rollback result.

## Primary sources

- [AWS IAM confused deputy guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html)
- [AWS STS ExternalId guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html)
- [AWS source identity](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_monitor.html)
- [CloudFormation change sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)
