---
name: pass-cli-secrets
description: Use when the user needs a password, token, or credential, or generated code/IaC/CI/env will hold a secret. Prefer pass-cli for local creds and AWS SM/SSM for workloads; never echo or commit secrets.
---
# pass-cli (Proton Pass CLI) — single source of secrets

Use Proton Pass for local credentials. For AWS workloads, use Secrets Manager or SSM SecureString so the workload can retrieve secrets through its own IAM identity.

Official docs: https://protonpass.github.io/pass-cli/ — repo: https://github.com/protonpass/pass-cli

Changing instructions or researching a command does not authorize executing secret/account operations. Prefer official documentation or installed source for schemas: a template/metadata command can still initialize the client and affect authentication state. If the session or local key provider fails, stop credential operations; do not force logout, switch key providers, repair credential files, or reauthenticate as a documentation check. Follow the runtime's private credential/authentication workflow when that work is actually requested.

## Non-negotiable rules

1. Never print, log, comment, or pass a retrieved secret as a command-line argument.
2. Never run a secret-returning command by itself through an agent tool; its stdout becomes agent context.
3. Use a documented consumer input channel: stdin, a protected temporary file, or `pass-cli run` environment injection. Confirm that the consumer actually supports that channel.
4. Disable shell tracing before handling secrets. Keep temporary files under a private directory, use `umask 077`, and remove them with a trap.
5. Never save secrets to project files. Offer to store a newly generated secret in Proton Pass.

## Retrieve and consume a secret

Use `item view` only as part of a pipeline or redirect its output to a protected temporary file. A standalone `item view --field password` prints the secret and is for a human's private terminal only, never an agent tool result.

For tools that accept a password on stdin, pipe it directly:

```bash
pass-cli item view --vault-name 'Work' --item-title 'Docker Registry' --field password |
  docker login --username '<user>' --password-stdin

pass-cli item view --vault-name 'Work' --item-title 'GitLab Token' --field password |
  glab auth login --stdin
```

Use `pass-cli run` for a command that consumes a credential from an environment variable. Proton Pass documents `pass://` references in environment variables and resolves them before starting the command:

```bash
GITLAB_TOKEN='pass://Work/GitLab/token' pass-cli run -- \
  glab mr list --repo 'https://<gitlab-host>/<group>/<project>'

PGPASSWORD='pass://Work/DBProd/password' pass-cli run -- \
  psql -h <db-host> -U <db-user> -d <database> -c '\dt'
```

`psql` reads `PGPASSWORD` through libpq; stdin to `psql` is SQL input, not a password channel. Environment variables can be visible to processes with sufficient local privileges, so prefer a consumer's supported stdin or secret-file interface when available. Do not put an environment variable value into the same command that expands it, for example `TOKEN=... command "$TOKEN"`; the expansion happens before the assignment.

For a shell variable that must be used in a later statement, assign it first, keep tracing disabled, and clear it on exit:

```bash
set +x
GITLAB_TOKEN="$(pass-cli item view --vault-name 'Work' --item-title 'GitLab Token' --field password)"
trap 'unset GITLAB_TOKEN' EXIT
printf '%s\n' "$GITLAB_TOKEN" | glab auth login --stdin
```

Use only consumer flags confirmed by that consumer's installed help or official documentation. Do not assume a CLI accepts stdin because another CLI does. Avoid `curl -u "user:$TOKEN"`, headers containing an expanded token, or any other secret-bearing argument: those expose the value in process arguments. Never use `kubectl create secret` as a supposedly agent-blind path; the Kubernetes API persists that value as a Secret object.

## Keep secrets out of output and history

- Do not use `set -x`, `bash -x`, `echo`, `printf` to terminal, `printenv`, verbose HTTP logging, or debug flags with credentials in scope.
- Do not put credentials in command arguments, container environment options, URLs, error-prone connection strings, CI command bodies, or shell history.
- Do not use `tee` or redirect a secret to a project file. A process substitution does not stop the receiving tool from storing a Kubernetes Secret or logging the value.
- Treat any command's stdout and stderr as agent-visible. Redirect only to a private temporary file when the tool's output contains a one-time secret and the next operation consumes that file safely.

## Local applications and CI

For an application with a documented environment variable, prefer `pass-cli run`:

```bash
OPENAI_API_KEY='pass://Work/OpenAI/api-key' pass-cli run -- python app.py
```

Mark secret-bearing Terraform variables and outputs sensitive, and avoid printing plans or state that may contain values. For Docker and CI secret creation, use the platform's secret-management interface or a documented file/stdin facility. Do not use `docker run -e`, `gh secret set --body`, or an equivalent command argument to transfer a secret.

## Creating or rotating secrets

Proton Pass documents `item create login --from-template <file>` and `--from-template -` for a JSON template on stdin in its [item reference](https://protonpass.github.io/pass-cli/commands/item/); environment injection is covered by the [run reference](https://protonpass.github.io/pass-cli/commands/contents/run/). The template schema has `title`, `username`, `email`, `password`, and `urls`. Prefer the file/stdin template route when importing an externally generated credential; never use `--password <secret>` or `item update --field password=<secret>` because those put the value in argv. Protect temporary plaintext with `umask 077`, keep it outside the project, remove it on exit, and capture the consumer's response privately if it can contain the supplied secret. If these limits are unacceptable, use an approved private UI/API transfer.

For an AWS IAM access-key rotation, see the capture-and-import procedure in [`awscli-workflows`](../awscli-workflows). It redirects the one-time AWS response away from tool output and passes a protected template file to Proton Pass. Do not delete or deactivate an old credential until the replacement is in use and verified.

When bootstrapping an existing Proton Pass value into AWS Secrets Manager, use a private temporary file and AWS CLI's documented `file://` input. Use an explicit profile and region and follow [`awscli-workflows`](../awscli-workflows) preflight rules:

```bash
set +x
set -eu
umask 077
tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT
pass-cli item view --vault-name 'Work' --item-title 'External API prod' --field password > "$tmpdir/secret"
AWS_PAGER='' aws --profile <profile> --region <region> secretsmanager create-secret \
  --name <secret-name> --secret-string "file://$tmpdir/secret"
```

The file is temporary plaintext and may remain recoverable on some storage. If policy prohibits it, use a human-operated secure transfer or a supported API/stream path; do not fall back to putting the value in argv or agent-visible output.

## AWS runtime preference

For Lambda, ECS, EKS, EC2, CodeBuild, App Runner, Glue, and other AWS workloads, the canonical runtime source is:

- AWS Secrets Manager for credentials with rotation, structured JSON, and DB/API secrets.
- SSM Parameter Store SecureString for simple secret configuration.

Use IAM roles, EKS Pod Identity or IRSA as supported so workloads read their own secret. Prefer Secrets Store CSI Driver when the EKS design calls for mounting external secrets. An explicitly approved Kubernetes Secret is a different persisted resource and needs the cluster's access/encryption controls; process substitution does not change that. For Terraform, reference Secrets Manager/SSM using data sources where appropriate and mark outputs/variables sensitive; sensitive display flags do not encrypt state, whose backend and access need protection.

## When pass-cli is unavailable

If `pass-cli` fails (for example, an expired session), stop and tell the user. Do not fall back to asking for the secret in chat. The user can re-authenticate locally with the documented `pass-cli login` workflow.

## Auto-check before responding

- [ ] Is a secret about to appear in stdout, stderr, argv, shell history, a project file, or a container/CI command body? Stop and use a supported input channel.
- [ ] Is a secret retrieval command being run alone through an agent tool? Do not run it.
- [ ] Is a consumer's stdin/environment/file interface documented? Verify before writing the example.
- [ ] Was a new secret generated? Offer to store it in Proton Pass.
