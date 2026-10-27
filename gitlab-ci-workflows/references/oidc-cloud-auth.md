# OIDC cloud authentication patterns

This reference contains the detailed recipe linked from [`SKILL.md`](../SKILL.md). Check project-specific versions, permissions, schemas, and targets before use.

## OIDC for cloud deploys — no long-lived keys

### AWS

```yaml
.aws-oidc: &aws-oidc
  id_tokens:
    AWS_ID_TOKEN:
      aud: https://gitlab.com
  before_script:
    - >
      STS=$(aws sts assume-role-with-web-identity
        --role-arn "$AWS_ROLE_ARN"
        --role-session-name "gitlab-$CI_PIPELINE_ID"
        --web-identity-token "$AWS_ID_TOKEN"
        --query "Credentials" --output json)
    - export AWS_ACCESS_KEY_ID=$(echo "$STS" | jq -r .AccessKeyId)
    - export AWS_SECRET_ACCESS_KEY=$(echo "$STS" | jq -r .SecretAccessKey)
    - export AWS_SESSION_TOKEN=$(echo "$STS" | jq -r .SessionToken)

deploy:prod:
  <<: *aws-oidc
  variables:
    AWS_ROLE_ARN: arn:aws:iam::123456789012:role/gitlab-deploy-prod
    AWS_DEFAULT_REGION: us-east-1
  script:
    - aws sts get-caller-identity
    - aws deploy create-deployment ...
  environment: production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

Trust policy (AWS side):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/gitlab.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "gitlab.com:aud": "https://gitlab.com" },
      "StringLike":   { "gitlab.com:sub": "project_path:group/repo:ref_type:branch:ref:main" }
    }
  }]
}
```

### GCP

Use a Workload Identity Pool with GitLab as the provider, bind `sub` to the exact repo + branch.

### Vault

```yaml
read-secret:
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  secrets:
    DATABASE_URL:
      vault: ops/data/db/prod@secret-store
      file: false
  script: ./deploy.sh
```
