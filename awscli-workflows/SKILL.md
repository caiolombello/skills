---
name: awscli-workflows
description: Use whenever running the AWS CLI. Require explicit --profile and --region, read-before-write, dry-run when available, and confirm before destructive calls.
---
# awscli-workflows

Baseline for using the AWS CLI from an agent session. The account and region an AWS CLI call targets are almost always **implicit**, which is where most mistakes come from. This skill makes them explicit.

## Non-negotiables

1. **Always pass `--profile` explicitly.** Never rely on `AWS_PROFILE` or `[default]` when multiple profiles exist.
2. **Always pass `--region` explicitly** for regional services. Never rely on `AWS_REGION` / `AWS_DEFAULT_REGION` for writes.
3. **Read before write.** Before any `create-*` / `put-*` / `update-*` / `delete-*`, inspect current state with the matching `describe-*` / `get-*` / `list-*`.
4. **Never write to a production account** without an explicit user statement naming the environment.
5. **Destructive calls require explicit user confirmation** — see list below.
6. **Never echo secrets or temporary credentials** to stdout. Use `--query` and `--output` to narrow.
7. **Never pipe `aws sts get-session-token` / `assume-role` output to a file** without discussing it; those credentials are bearer tokens.
8. **Pager off in agent context** — prepend `AWS_PAGER=""` or pass `--no-cli-pager` so output does not stall.

## Pre-flight: identity + target

Before any write, run:

```bash
aws --profile <profile> sts get-caller-identity --output json
aws --profile <profile> configure get region
```

Confirm:
- `Account` matches the intended account (dev vs stg vs prod).
- `Arn` is the expected principal (user, role, SSO session).
- Region is the expected one.

For SSO profiles, if the call returns `Unable to locate credentials`:
```bash
aws sso login --profile <profile>
```

## Standard invocation shape

```bash
AWS_PAGER="" aws \
  --profile <profile> \
  --region <region> \
  --output json \
  <service> <command> [flags]
```

Prefer:
- `--output json` for agents (structured, stable).
- `--output table` for user-facing summaries.
- `--output text` only when piping to `awk`/`cut`.
- `--query '<JMESPath>'` to narrow output before it reaches the context.

Avoid:
- `--output yaml-stream` unless specifically needed.
- `--debug` in agent sessions (prints full signed request, noisy).

## Reading (safe defaults)

### Identity and account
```bash
aws --profile <p> sts get-caller-identity
aws --profile <p> organizations describe-account --account-id <id>   # needs org access
```

### IAM
```bash
aws --profile <p> iam list-users --query 'Users[*].[UserName,CreateDate]' --output table
aws --profile <p> iam list-roles --query 'Roles[*].RoleName' --output text
aws --profile <p> iam get-role --role-name <name>
aws --profile <p> iam list-attached-role-policies --role-name <name>
aws --profile <p> iam simulate-principal-policy --policy-source-arn <arn> --action-names s3:GetObject --resource-arns <bucket-arn>
```

### S3
```bash
aws --profile <p> s3 ls s3://<bucket>/<prefix>/ --recursive --human-readable --summarize
aws --profile <p> s3api get-bucket-policy --bucket <bucket>
aws --profile <p> s3api get-bucket-encryption --bucket <bucket>
aws --profile <p> s3api get-bucket-versioning --bucket <bucket>
```

### EC2 / networking
```bash
aws --profile <p> --region <r> ec2 describe-instances --filters "Name=tag:Name,Values=<name>" \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PrivateIpAddress]' --output table
aws --profile <p> --region <r> ec2 describe-security-groups --group-ids <sg-id>
aws --profile <p> --region <r> ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock,Tags[?Key==`Name`].Value|[0]]' --output table
```

### Secrets Manager / SSM
```bash
aws --profile <p> --region <r> secretsmanager list-secrets --query 'SecretList[*].Name' --output text
aws --profile <p> --region <r> secretsmanager describe-secret --secret-id <name>
aws --profile <p> --region <r> ssm describe-parameters --max-results 50
```

Do not `get-secret-value` / `get-parameter --with-decryption` unless you actually need the value — they surface plaintext in output.

### CloudWatch Logs
```bash
aws --profile <p> --region <r> logs describe-log-groups --log-group-name-prefix /aws/lambda/
aws --profile <p> --region <r> logs tail /aws/lambda/<fn> --since 15m --follow
```

`logs tail --follow` stays attached; use a time-boxed `--since` value when triaging.

## Writing (require confirmation + reading first)

### Destructive commands — require explicit user confirmation

Ask the user before any of these, and show the exact target resource:

- `aws s3 rm`, `aws s3 rb --force`
- `aws s3api delete-bucket-policy`, `put-public-access-block` (loosening)
- `aws ec2 terminate-instances`, `delete-vpc`, `revoke-security-group-ingress`, `delete-snapshot`
- `aws rds delete-db-instance`, `delete-db-cluster`, `modify-db-instance --apply-immediately`
- `aws iam delete-*`, `detach-*`, `put-user-policy`, `attach-role-policy`, `update-assume-role-policy`
- `aws kms schedule-key-deletion`, `disable-key`
- `aws secretsmanager delete-secret`, `update-secret` in prod
- `aws cloudformation delete-stack`, `update-stack` with replacement
- `aws ecr batch-delete-image`, `delete-repository --force`
- `aws ecs update-service --desired-count 0`, `delete-service`
- `aws eks delete-cluster`, `delete-nodegroup`
- `aws lambda delete-function`, `update-function-code` in prod
- `aws route53 change-resource-record-sets` with `DELETE` / `UPSERT`

### Dry-run where available

Many services support `--dry-run`:
```bash
aws --profile <p> --region <r> ec2 run-instances --image-id ami-... --dry-run
aws --profile <p> --region <r> ec2 terminate-instances --instance-ids i-... --dry-run
```

For CloudFormation, generate a change set instead of applying directly:
```bash
aws --profile <p> --region <r> cloudformation create-change-set \
  --stack-name <s> --change-set-name <cs> --template-body file://template.yaml --capabilities CAPABILITY_NAMED_IAM
aws --profile <p> --region <r> cloudformation describe-change-set --stack-name <s> --change-set-name <cs>
# only then:
aws --profile <p> --region <r> cloudformation execute-change-set --stack-name <s> --change-set-name <cs>
```

For Route 53 zone edits, `change-resource-record-sets` accepts a JSON change batch. Write it to a file first, `diff` against current, then submit.

### IAM rotation pattern (access keys)

Classic footgun: create new → switch apps → deactivate old → test → delete old. Do **not** delete the old key before new is in use.

```bash
# 1. Inventory
aws --profile <p> iam list-access-keys --user-name <u>

# 2. Create new key (STDOUT contains the new secret — handle via pass-cli-secrets skill)
aws --profile <p> iam create-access-key --user-name <u>

# 3. Test new key works before touching the old one.

# 4. Deactivate old
aws --profile <p> iam update-access-key --user-name <u> --access-key-id <old-id> --status Inactive

# 5. Verify workloads still healthy over a reasonable window.

# 6. Delete old
aws --profile <p> iam delete-access-key --user-name <u> --access-key-id <old-id>
```

Follow the `pass-cli-secrets` skill for handling the new secret — never echo it.

## Assume-role chains

When the caller identity is not the target, chain via `assume-role`:

```bash
TMP=$(aws --profile <source-profile> sts assume-role \
  --role-arn arn:aws:iam::<acct>:role/<role> \
  --role-session-name cli-session --output json)

export AWS_ACCESS_KEY_ID=$(echo "$TMP" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$TMP" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$TMP" | jq -r '.Credentials.SessionToken')

aws sts get-caller-identity     # confirm new identity
# ... work ...

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
```

Better: configure a profile with `role_arn` + `source_profile` and just use `--profile <assumed>`.

For SSO workflows, prefer `aws sso login --profile <profile>` and `~/.aws/config` over manual assume-role.

## Secrets handling

Follow the `pass-cli-secrets` skill. Reminders specific to AWS:

- `aws secretsmanager get-secret-value --secret-id X --query SecretString --output text` leaks the value into the agent context. Only run when the value is actually needed; otherwise stick to `describe-secret`.
- `aws ssm get-parameter --name /x --with-decryption` also leaks. Use `--query Parameter.Name` to verify existence without decrypting.
- Bootstrap pattern (from `pass-cli` → Secrets Manager) is in the `pass-cli-secrets` skill.
- For Terraform / IaC, reference secrets via data sources, not via CLI-read-then-inject.

## Output control

Narrow before it hits context:

```bash
# Just instance IDs
aws --profile <p> --region <r> ec2 describe-instances \
  --query 'Reservations[].Instances[].InstanceId' --output text

# State + private IP per running instance
aws --profile <p> --region <r> ec2 describe-instances \
  --filters 'Name=instance-state-name,Values=running' \
  --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress,Tags[?Key==`Name`]|[0].Value]' \
  --output table
```

For very large outputs, use `--max-items` and `--starting-token` for pagination instead of dumping everything.

## Tags

Respect the user's mandatory tag policy when creating resources (commonly `Environment`, `Project`, `Owner`, `ManagedBy`, `CostCenter`). When a user workflow requires tags, include them on `create-*` / `run-instances` / `put-*` in a single call rather than tagging after creation.

## Common pitfalls

1. **Default region drift.** `~/.aws/config` has a default region that may differ from the profile's expected region. Always pass `--region`.
2. **`AWS_PROFILE` leaking from parent shell.** Unset it at the start of a session, or always pass `--profile`.
3. **SSO token expiry.** `aws sso login` has to be re-run when the session ends; the error is `Error loading SSO Token`.
4. **`--dry-run` only works where the service supports it.** Most EC2 mutations do; most IAM / RDS / S3 do not.
5. **`s3 cp` / `s3 sync` deletes.** `s3 sync --delete` removes destination objects not present in source. Always confirm before using `--delete`.
6. **Throttling.** When scripting many calls, expect `Throttling` / `RequestLimitExceeded`. Use `--cli-read-timeout` / backoff, or batch via `--max-items`.
7. **Eventual consistency.** `describe-*` right after `create-*` may not see the new resource. Re-query after a short wait if needed.
8. **JMESPath quirks.** `Tags[?Key==` uses backticks for literals: `Tags[?Key==\`Name\`].Value|[0]`. Wrong quoting returns empty.

## Pre-flight checklist

Before any `aws` command that writes:

- [ ] `--profile` set explicitly.
- [ ] `--region` set explicitly (regional services).
- [ ] `aws sts get-caller-identity` confirmed target account/principal.
- [ ] Corresponding `describe-*` / `list-*` / `get-*` was run first.
- [ ] Destructive action? User confirmed with account + resource named.
- [ ] `--dry-run` used where available.
- [ ] Secrets not being echoed; values narrowed via `--query`.
- [ ] `AWS_PAGER=""` or `--no-cli-pager` to prevent stall.
