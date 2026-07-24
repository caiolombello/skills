# AWS Security Incident Scenarios

These are decision guides, not authorization to execute changes. Use the main
skill workflow and evidence gate first.

## Contents

1. Exposed IAM access key
2. Suspicious role assumption
3. Root-account compromise
4. Compromised EC2 or cryptomining
5. S3 exposure or exfiltration
6. ECS/EKS workload compromise
7. Security-control tampering

## 1. Exposed IAM access key

Investigate:

- Principal, key creation/last-used metadata, source IPs, Regions, user agents,
  and API events.
- New users, keys, policies, roles, trust, login profiles, MFA changes, and
  persistence.
- Data access, snapshot/image creation, compute launch, and cost spikes.
- Every legitimate dependency that still uses the key.

Contain:

- Preserve metadata/events.
- Deactivate or narrowly deny the key with approval.
- Revoke related sessions where applicable.
- Rotate every dependent secret through the approved secret channel.
- Hunt all accounts/Regions for the key and IoCs.

Recover:

- Remove persistence and unauthorized resources.
- Move the workload to temporary credentials/workload identity.
- Verify no legitimate dependency still uses the old key before deletion.

## 2. Suspicious role assumption

Investigate:

- Caller principal, session ARN/name, source identity, tags, external ID,
  source IP, user agent, and session duration.
- Trust policy and recent trust/permission changes.
- Upstream identities that can assume the role.
- `iam:PassRole` and resource-policy paths that extend privilege.

Contain:

- Restrict the trust path or principal, preserving known-good responders.
- Revoke sessions where supported.
- Apply a time-bound narrow deny when the exact path is still uncertain.

Recover:

- Correct trust and permission boundaries.
- Add source conditions/external ID/session attribution as appropriate.
- Revalidate every caller and cross-account tenant mapping.

## 3. Root-account compromise

Treat as critical.

Investigate:

- Root console/login events, credential changes, contacts, MFA, alternate
  contacts, support activity, payment settings, and organization changes.
- New keys, policies, roles, access paths, and security-tool tampering.

Contain:

- Use a known-clean channel to secure the root email and account.
- Invalidate exposed root credentials and restore MFA under the authorized
  process.
- Engage AWS Support/security response immediately.
- Preserve the response team's independent access.

Recover:

- Review the entire organization/account for persistence and impact.
- Re-establish root controls, contacts, alerts, and break-glass documentation.
- Rotate downstream secrets if root access could have exposed them.

## 4. Compromised EC2 or cryptomining

Investigate:

- Instance launch/update history, AMI, user data, IAM role, metadata settings,
  network connections, processes, files, cron/systemd, SSH keys, SSM sessions,
  volumes, snapshots, and Auto Scaling behavior.
- Cost and resource creation across all Regions.

Contain:

- Preserve volatile evidence and snapshot volumes as authorized.
- Isolate networking reversibly; prevent automated termination/replacement.
- Restrict the instance role if credential abuse is possible.

Recover:

- Rebuild from a verified image; do not return an untrusted host to service
  solely because malware was removed.
- Patch initial access and rotate reachable credentials.
- Block compromised images/artifacts and verify fleet-wide exposure.

## 5. S3 exposure or exfiltration

Investigate:

- Bucket/object policy, ACL, public access, access points, endpoint policies,
  presigned URLs, KMS key policy, versioning, lifecycle, replication, and
  CloudTrail data/access logs.
- Which objects and versions were listed, read, changed, deleted, or copied.
- Principal, source, time window, and destination.

Contain:

- Preserve policy/configuration and access evidence.
- Remove the narrow unauthorized path or apply public-access controls with
  impact approval.
- Restrict compromised identities and presigned URL sources.

Recover:

- Restore object versions where needed.
- Correct policy/IaC and key permissions.
- Complete data-impact, notification, and credential-rotation decisions.

## 6. ECS/EKS workload compromise

Investigate:

- Image digest/source, task/pod/service account, workload role, node, runtime
  events, secrets mounts/references, network connections, admission/deployment
  history, and control-plane audit logs.
- Whether the attacker reached node or cluster control-plane privileges.

Contain:

- Preserve workload and node evidence.
- Isolate the service/task/pod and credential path.
- Stop deployment of the compromised digest.
- Expand scope to the node/cluster until isolation is proven.

Recover:

- Rebuild from verified artifacts.
- Rotate reachable credentials.
- Patch admission, runtime, image, identity, and network controls.
- Verify other workloads did not share the same vulnerable artifact or role.

## 7. Security-control tampering

Signals include disabled trails/detectors, changed destinations, deleted logs,
weakened Config recording, altered KMS policies, or suppressed findings.

Investigate:

- Who changed the control, through which session/path, in every account/Region.
- Whether the change preceded other suspicious activity.
- Alternate logs that survived the tampering.

Contain:

- Restrict the tampering principal/path.
- Restore the control from a known-good, reviewable configuration.
- Protect the destination/key from the same administrator.

Recover:

- Identify visibility gaps and state what cannot be reconstructed.
- Add independent guardrails and alerts for future tampering.
- Review all activity during the blind window at elevated severity.
