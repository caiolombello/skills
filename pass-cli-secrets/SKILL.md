---
name: pass-cli-secrets
description: Canonical source of secrets. Use pass-cli (Proton Pass CLI) for local user credentials; use AWS Secrets Manager / SSM Parameter Store for workloads and AWS IaC. Trigger this skill WHENEVER (1) the user asks for a password/token/credential, (2) generated code/script/config/IaC needs a secret, (3) a secret must be exposed as an environment variable, (4) the user mentions Proton Pass, vault, secret, credential, Secrets Manager, SSM, parameter store. NEVER write literal secrets into files, commits, commands or responses.
---

# pass-cli (Proton Pass CLI) — single source of secrets

The user has `pass-cli` installed and logged in. All secrets (passwords, tokens, API keys, SSH keys, certificates) **must** come from `pass-cli` instead of:

- Hardcoded in code, scripts, configs, IaC
- Requests directly to the user ("give me the password")
- Read from versioned `.env` / `.envrc` files
- Copied from browser password managers

Official docs: https://protonpass.github.io/pass-cli/ — repo: https://github.com/protonpass/pass-cli

## Non-negotiable rules

1. **Never** print, log, comment or write the value of a retrieved secret. Use it only in the final command.
2. **Never** suggest `echo $TOKEN` or similar to "verify" a secret. To validate, use the secret in the real command.
3. **Never** save secrets to project files (`.env`, `secrets.yaml`, etc.) without confirming with the user that the file is in `.gitignore`.
4. **Never** run `pass-cli` with `--output json` redirected to a file without explicit warning.
5. In scripts, prefer **passing the secret via stdin or ephemeral environment variable** to the process that needs it. Do not persist it to disk.
6. When creating a new secret (generating a token, API key, DB password), offer to **store it in Proton Pass** at the end.

## Standard flow to retrieve a secret

### 1. List to find the item
```bash
pass-cli item list --output json | jq '.[] | {title, item_id, share_id}'
```
Or list vaults first:
```bash
pass-cli vault list --output json
pass-cli item list "Personal" --output json
```

### 2. Retrieve ONE specific field (normal use)
Use `--field` to extract only what you need, without exposing the rest:
```bash
pass-cli item view --item-title "GitHub Token" --field password
pass-cli item view --vault-name "Work" --item-title "AWS prod" --field "access_key"
```

Or via Pass URI (preferred in scripts — does not depend on title match):
```bash
pass-cli item view "pass://SHARE_ID/ITEM_ID/password"
```

### 3. Use in commands without exposing them in shell history

**Ephemeral local variable (preferred):**
```bash
GITHUB_TOKEN="$(pass-cli item view --item-title 'GitHub Token' --field password)" \
  gh auth login --with-token <<< "$GITHUB_TOKEN"
unset GITHUB_TOKEN
```

**Direct pipe when the command accepts stdin:**
```bash
pass-cli item view --item-title 'DB Prod' --field password | \
  psql -h db.prod -U admin
```

**Without showing it in the terminal:**
```bash
read -rs DB_PASS < <(pass-cli item view --item-title 'DB Prod' --field password)
```

## AI-blind patterns (when an agent is running the command)

When you (the AI) execute `pass-cli` through a Bash tool, **everything that comes out on stdout/stderr is returned as tool result and becomes visible to you and to the context**. To use secrets without seeing them:

### Golden rule
**The secret must never appear in the final output of the command.** Use a direct pipe or an inline env var into the consumer, in a single Bash line.

### Safe patterns (secret invisible to the agent)

```bash
# Direct pipe into the consumer's stdin
pass-cli item view --field password --vault-name V --item-title T | \
  docker login -u user --password-stdin

pass-cli item view --field password --vault-name V --item-title T | \
  gh auth login --with-token

pass-cli item view --field password --vault-name V --item-title T | \
  psql -h db.host -U admin

# Inline env var, command that does not echo the value
PGPASSWORD="$(pass-cli item view --field password ... )" \
  psql -h db -U user -c '\dt'

# Process substitution for tools that want a file
kubectl create secret generic foo \
  --from-file=token=<(pass-cli item view --field password ... )

# Command that only returns an exit code
PASS="$(pass-cli item view --field password ... )" \
  curl -fsS -u "user:$PASS" https://api.example.com/healthz -o /dev/null && echo OK
```

### Anti-patterns (leak to the agent)

```bash
# Direct stdout: the secret becomes a tool result
pass-cli item view --field password ...

# Assign to a variable then "check" — echo/printf leaks
TOKEN="$(pass-cli item view --field password ... )"
echo "$TOKEN"          # bad
printenv TOKEN         # bad

# set -x / bash -x expands commands on stderr
set -x; CMD="$(pass-cli item view --field password ...)"  # bad: leaks in trace

# Passing as argv — visible in ps, history, program logs
mysql --password="$(pass-cli item view --field password ...)"  # bad
# Use --password-stdin or MYSQL_PWD env var instead
```

### Extra pitfalls

- **`curl -v` / `-vvv`** logs headers, including `Authorization`.
- **`docker run -e SECRET=$X`** shows up in `docker inspect`.
- **Error messages**: many tools echo the full connection string (with password) on failure — redirect with `2>&1 | grep -v -i password` or `2>/dev/null` when safe.
- **`tee`, `>>` into a file** that you will later read with `Read` or `cat`.
- **History**: commands with secrets in argv persist in `~/.zsh_history`. Use an env var or a pipe.

### When you really need to see the value (bootstrap a config, populate another store)

If the task **requires** you to manipulate the value (for example, initial bootstrap into Secrets Manager, generating `.env.local` for dev), warn the user before executing:

> "I'm going to retrieve secret X via pass-cli — the value will appear in my context. Confirm?"

After using it, suggest cleanup:
```bash
history -d $(history 1)   # remove the last command from history
```

### Real limit

Even with a direct pipe, the secret lives decrypted in memory on the shell you triggered. The sandbox runs as the user — so technically a malicious agent could read `/proc/<pid>/environ`. The guarantee here is "honest agent + no accidental context leak", not "agent without any possible access". For strong guarantees (secret never touches the agent's machine), use IRSA/OIDC for AWS workloads or require human approval on the final command.

## Patterns by context

### Terraform / IaC
NEVER put secrets in `.tfvars`. Instead, export before running:
```bash
export TF_VAR_db_password="$(pass-cli item view --item-title 'RDS prod' --field password)"
terraform apply
```
Mark the variable as `sensitive = true` in the `.tf`.

### Docker / docker-compose
Use `--env-file` pointing to a file generated on-the-fly and deleted afterwards, or:
```bash
docker run -e API_KEY="$(pass-cli item view --item-title 'X' --field password)" image
```
For compose, prefer `secrets:` pointing to a temporary file generated from pass-cli.

### CI/CD (GitHub Actions, GitLab CI)
Do NOT commit secrets. Recommend:
- GitHub Actions: `secrets.NAME` in the repository settings
- To populate those secrets from pass-cli locally:
  ```bash
  gh secret set MY_SECRET --body "$(pass-cli item view --item-title 'X' --field password)"
  ```

### Application code (Python, Node, Go)
Do NOT embed a secret in the code. Always via env var, and instruct the user to populate it through pass-cli in the shell before running:
```bash
export OPENAI_API_KEY="$(pass-cli item view --item-title 'OpenAI' --field password)"
python app.py
```

### SSH / private keys
Use the built-in ssh-agent from pass-cli instead of copying the key into `~/.ssh/`:
```bash
pass-cli ssh-agent start          # start the agent
pass-cli ssh-agent load --item-title "GitHub Deploy"
```

## Creating new secrets in Proton Pass

When you generate a new token/password/key (for example rotating an API key, creating a new IAM user, issuing a new deploy key), offer to save it:

```bash
# Generate and save a strong password directly into Pass
pass-cli item create login \
  --vault-name "Work" \
  --title "Service X - prod" \
  --username "svc-account" \
  --generate-password="32,uppercase,symbols" \
  --url "https://servicex.com"

# Save a secret that was already generated externally
pass-cli item create login \
  --vault-name "Work" \
  --title "AWS access key - userY" \
  --username "AKIA..." \
  --password "$(cat /tmp/secret)" && shred -u /tmp/secret
```

## Exception: AWS context — Secrets Manager / SSM Parameter Store take precedence

When the work involves **AWS runtime** (Lambda, ECS, EKS, EC2, CodeBuild, App Runner, Glue, etc.) or **AWS IaC** (Terraform, CDK, CloudFormation, SAM), the canonical source of secrets becomes:

- **AWS Secrets Manager** — credentials with rotation, structured JSON, DB/API secrets with versioning.
- **AWS Systems Manager Parameter Store (SecureString)** — config + simple secrets, cheaper, tightly integrated with SSM.

Reason: AWS workloads already have IAM/IRSA to access these services natively, without exposing secrets in env vars inside manifests, without depending on pass-cli at runtime, with CloudTrail audit logging and automatic rotation.

### How to decide between pass-cli vs AWS Secrets/SSM

| Scenario | Canonical source |
|----------|------------------|
| Secret consumed by a workload running **inside AWS** | Secrets Manager / SSM SecureString |
| **AWS infra** secret referenced in IaC (RDS password, provider API key) | Secrets Manager / SSM (data source in Terraform) |
| **Local user** credential on the workstation (gh token, kubeconfig token, npm token) | pass-cli |
| Credential to **access AWS itself** (AWS access keys, SSO refresh) | AWS CLI profiles / SSO — not both |
| Secret used in **CI** that deploys to AWS | GitHub Actions secrets (populated via pass-cli locally OR via OIDC into AWS) |
| Secret being **bootstrapped** into Secrets Manager for the first time | pass-cli locally → script that runs `aws secretsmanager create-secret` |

### AWS patterns

**Terraform — reference Secrets Manager:**
```hcl
data "aws_secretsmanager_secret_version" "db" {
  secret_id = "prod/rds/master"
}

resource "aws_db_instance" "this" {
  password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

**Terraform — reference SSM SecureString:**
```hcl
data "aws_ssm_parameter" "api_key" {
  name            = "/prod/external-api/key"
  with_decryption = true
}
# use data.aws_ssm_parameter.api_key.value (mark variable as sensitive)
```

**EKS — mount via Secrets Store CSI Driver (no value in manifest):**
Use `SecretProviderClass` pointing to Secrets Manager via IRSA. NEVER `kubectl create secret` with a literal value.

**Initial bootstrap (pass-cli → AWS):**
```bash
aws secretsmanager create-secret \
  --name prod/external-api/key \
  --secret-string "$(pass-cli item view --item-title 'External API prod' --field password)"
```

**Rotation — generate a new credential and store it in both places:**
```bash
NEW_PASS="$(openssl rand -base64 32)"
aws secretsmanager put-secret-value --secret-id prod/rds/master \
  --secret-string "{\"password\":\"$NEW_PASS\"}"
pass-cli item update --item-title "RDS prod backup" --field password --value "$NEW_PASS"
unset NEW_PASS
```

### AWS rules

1. **Never** put a literal secret in `*.tfvars`, k8s manifests, ECS task definitions, or Lambda env blocks.
2. In Terraform, always mark `sensitive = true` on outputs/variables that touch secrets.
3. For Lambda/ECS, prefer `secrets:` (direct reference to Secrets Manager) over `environment:` with the raw value.
4. For EKS, use IRSA + Secrets Store CSI Driver, not a Kubernetes `Secret` populated manually.
5. Mandatory tags (`Environment`, `Project`, `Owner`) also apply to secrets created in AWS.

## When pass-cli is not available

If `pass-cli` fails (expired session, no network), stop and warn the user:
- `pass-cli login` to re-authenticate
- Do NOT fall back to asking for the secret in plain text in chat without an explicit warning.

## Auto-check before responding

Before any response that touches a password/token/credential, ask yourself:
- [ ] Am I about to write a literal secret? → Stop. Use `pass-cli item view --field`.
- [ ] Am I going to ask the user for the secret? → Stop. Suggest `pass-cli item view ...`.
- [ ] Will the secret land in a versioned file? → Stop. Use an env var via pass-cli at execution time.
- [ ] Am I generating a new secret? → Offer to save it in Pass at the end.
