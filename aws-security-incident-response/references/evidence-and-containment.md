# AWS Evidence and Containment

Load this reference before a disruptive security response action.

## Contents

1. Decision gate
2. Clean access
3. Evidence record
4. Identity containment
5. Compute containment
6. Data containment
7. Organization containment
8. Verification and rollback
9. Primary sources

## 1. Decision gate

Before a write, state:

```text
Observed threat:
Exact target:
Action:
Expected security effect:
Expected business impact:
Evidence at risk:
Rollback:
Verification:
Authority:
```

Prefer containment that is:

- Reversible.
- Narrow to the confirmed/suspected path.
- Fast enough to reduce active harm.
- Compatible with evidence preservation.
- Unlikely to lock out responders.

Do not let "preserve everything" become a reason to leave an active attacker
uncontained. Record the trade-off and obtain the appropriate authority.

## 2. Clean access

- Use a pre-created incident role in a security account.
- Verify the caller identity, account, and Region.
- Do not assume a role through a principal that may be compromised.
- Use a clean workstation/session and out-of-band communication where needed.
- Protect incident credentials and do not paste them into tickets, chat, shell
  history, or agent context.
- Ensure SCPs, network quarantine, or trust changes will preserve the clean
  response path.

## 3. Evidence record

For every artifact, capture:

- Unique evidence ID.
- Source account, Region, service, resource, and log location.
- Collection UTC timestamp and relevant event time window.
- Collector identity and exact read-only command/tool.
- Original filename/object/key and immutable storage destination.
- Cryptographic digest where practical.
- Access/transfers after collection.
- Reason for collection and related incident/finding.

Preserve originals. Analyze copies. Apply legal-hold and retention requirements
defined by the organization.

Useful evidence categories:

- CloudTrail trail/Lake events and digest validation where configured.
- GuardDuty/Security Hub findings and update histories.
- AWS Config history.
- IAM credential reports, policies, trust, access-key metadata, last-used data,
  and identity-provider logs.
- VPC Flow Logs, Route 53 Resolver query logs, WAF/ALB/CloudFront/S3 access logs.
- EBS snapshots, memory/volatile artifacts when capability exists, AMI and
  instance metadata.
- Container image digest, task/pod spec, node/runtime logs, and control-plane
  audit logs.
- Object versions, access logs, bucket policy/configuration, and data-event
  logs.

## 4. Identity containment

Sequence for a suspected IAM credential:

1. Preserve key/principal/session metadata and related events.
2. Identify every workload and dependency using the credential.
3. Add a narrow deny/restriction or deactivate the key when authorized.
4. Revoke active sessions where the identity/session type supports it.
5. Create and distribute replacement credentials through the approved secret
   path.
6. Verify legitimate workloads with the replacement.
7. Remove unauthorized policy/trust/persistence.
8. Delete old credentials only after evidence and dependency validation.

For a compromised role, inspect both permission and trust paths. Blocking one
caller is insufficient if another principal can assume the same role.

For root-account suspicion, treat it as highest urgency: secure root email and
MFA, review account contacts and payment/security settings, invalidate exposed
credentials, and engage AWS Support through a known-clean path.

## 5. Compute containment

### EC2

- Record instance, AMI, volumes, security groups, IAM profile, network
  interfaces, user data, tags, and metadata settings.
- Capture required volatile evidence before a stop/reboot when feasible.
- Snapshot relevant volumes under the evidence process.
- Prefer reversible network isolation while keeping the instance intact.
- Check secondary ENIs, load balancers, SSM, IPv6, endpoints, and alternate
  egress; changing one security group may not isolate every path.
- Prevent automation/Auto Scaling from replacing or terminating the evidence
  instance unintentionally.

### ECS/EKS

- Capture task/pod spec, image digest, runtime identity, node, network, secrets
  references, logs, and deployment source.
- Quarantine the workload and credential path without destroying the only
  artifacts.
- Assume node/control-plane scope until evidence proves the compromise is
  workload-only.
- Block the compromised artifact from redeployment.

### Lambda

- Preserve configuration, code/package digest, layers, environment metadata,
  role, policy, event sources, versions, aliases, and recent updates.
- Disable or isolate the unsafe trigger/path when authorized; retain the
  relevant version for analysis.

## 6. Data containment

For S3 or another data store:

- Preserve policy, ACL, public-access state, endpoint policies, keys, logging,
  versioning, lifecycle, replication, and access history.
- Stop unauthorized access with the narrowest reversible control.
- Do not delete suspicious objects, versions, snapshots, or logs as a first
  response.
- Protect keys and backups from the same compromised administrator.
- Determine whether data was read, changed, encrypted, deleted, replicated, or
  exfiltrated.
- Validate application impact before denying a shared production path.

## 7. Organization containment

An account quarantine SCP can be effective but dangerous:

- Use a pre-tested policy, not an improvised deny-all.
- Preserve incident roles, logging delivery, evidence export, security tooling,
  and required AWS Support paths.
- Test policy inheritance and management-account limitations.
- Record exactly which OU/account attachment changes.
- Keep a rollback operator outside the quarantined path.

## 8. Verification and rollback

After every containment action:

- Re-read the exact resource/principal configuration.
- Test that the malicious path is blocked.
- Test that the responder/evidence path remains available.
- Check customer/service impact.
- Search for continued activity using related IoCs.
- Record UTC action, API result, direct postcheck, and monitoring result.

Rollback only after the security lead confirms that the threat path is removed
or another control replaces the containment.

## 9. Primary sources

- [AWS Security Incident Response containment](https://docs.aws.amazon.com/security-ir/latest/userguide/contain.html)
- [AWS Well-Architected incident response](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/incident-response.html)
- [AWS SRA cyber forensics](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture-cyber-forensics/forensics-ir.html)
- [CloudTrail log file integrity validation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html)
- [AWS compromised credentials guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)
