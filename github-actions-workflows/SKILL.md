---
name: github-actions-workflows
description: Design, audit, and maintain GitHub Actions workflows with a focus on security, speed, and maintainability. Use WHENEVER the user (1) writes, edits, or reviews a `.github/workflows/*.yml` file; (2) sets up CI/CD, automated tests, linting, security scanning, container builds, infra deploys, or release automation on GitHub; (3) mentions "GitHub Actions", "GHA", "workflow", "composite action", "reusable workflow", "OIDC to AWS/GCP/Azure", "workflow dispatch", "matrix build", "concurrency group"; (4) the workflow is slow, flaky, expensive, or insecure (pinned `@master`, leaked secrets, unrestricted permissions); (5) setting up branch-protection-required checks. Covers: OIDC federated auth (no long-lived cloud keys), SHA-pinned third-party actions, `permissions:` least-privilege, caching, matrix, reusable workflows vs composite actions, concurrency, path filters, secrets hygiene. Generic CI/CD concepts (stages, gates, artifact promotion) are mentioned briefly; for non-GitHub hosts see platform-specific skills.
---

# GitHub Actions Workflows

GitHub Actions is where most modern projects run CI/CD. Misconfigured it is a security hole and a cost center; well-configured it is a force multiplier.

This skill is GitHub-specific. General concepts (stages, gates, artifact promotion, deploy strategies) live in [`deploy-safety`](../deploy-safety) and [`incremental-implementation`](../incremental-implementation).

## Golden rules

1. **Pin third-party actions to a full commit SHA**, not a tag. Tags are mutable; SHAs are not.
2. **Default `permissions:` to read-only**, grant only what each job needs.
3. **Use OIDC for cloud auth** — never long-lived `AWS_ACCESS_KEY_ID` in secrets.
4. **Never run untrusted PR code with write tokens.** The `pull_request_target` event is the classic footgun.
5. **Cache aggressively.** Every second of CI is paid in developer time and actions minutes.
6. **One workflow file per concern.** Giant workflows with 20 jobs are unreadable; small workflows compose cleanly.
7. **Reusable workflows for cross-repo reuse**, composite actions for small DRY blocks. Different tools, different use cases.

## File layout

```
.github/
├── workflows/
│   ├── ci.yml                    # push + pull_request: lint, test, build
│   ├── deploy-prod.yml            # workflow_dispatch + push to main: gated deploy
│   ├── security.yml               # schedule + push: scanners, SBOM
│   ├── release.yml                # tag: changelog, release, publish
│   └── pr-labeler.yml             # pull_request: auto-label
├── actions/
│   └── setup-toolchain/           # composite action, reused across workflows
│       └── action.yml
├── CODEOWNERS
├── dependabot.yml
└── pull_request_template.md
```

## Minimum-viable CI workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

permissions:
  contents: read                  # least privilege at the top level

jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-node@1d0ff469b7ec7b3cb9d8673fde0c81c44821de2a  # v4.2.0
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint

  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    strategy:
      fail-fast: false
      matrix:
        node: ['20', '22']
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: actions/setup-node@1d0ff469b7ec7b3cb9d8673fde0c81c44821de2a
        with:
          node-version: ${{ matrix.node }}
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm test --reporter=junit --outputFile=reports/junit.xml
      - uses: actions/upload-artifact@65c4c4a1ddee5b72f698fdd19549f0f0fb45601b  # v4.6.0
        if: always()
        with:
          name: junit-${{ matrix.node }}
          path: reports/junit.xml
          retention-days: 14
```

What the snippet does right:
- SHA-pinned actions with a `# v4.2.2` comment so humans still see the version.
- Top-level `permissions: contents: read`; every job can tighten, none can loosen implicitly.
- `concurrency` cancels in-flight PR runs when the PR is updated, preserves main runs.
- `cache: pnpm` delegates lockfile-aware caching to the setup action.
- `fail-fast: false` on matrix so one matrix failure does not hide the others.
- Artifacts uploaded with explicit retention, limited to what is useful.

## Triggers and when to use them

| Event | When to use | Risk |
|-------|-------------|------|
| `push` (branches) | Main-branch CI, tag-based releases | Public for forks on `main` |
| `pull_request` | PR CI on code from the PR | Token is read-only for PRs from forks (safe default) |
| `pull_request_target` | **Dangerous.** Run workflow with the repo's token on PR code | Fork author can inject code that runs with your token |
| `workflow_dispatch` | Manual runs: deploy, scheduled one-offs | Require `permissions` that match the action |
| `schedule` (cron) | Nightly security scans, dep updates | Run only on `main`, not forks |
| `repository_dispatch` | External system triggers | Secure the PAT / webhook |
| `workflow_run` | Chain another workflow | Use `if: success()`; be careful with secrets |

### `pull_request_target` — only when you must

It exists for legitimate cases (labeling, auto-commenting) where you need repo write access on PR metadata. **Do not run PR source code** under this event. If you need to run code for a PR with secrets, use `pull_request` + a safer architecture (staged deployment from main, not from the PR).

## `permissions:` — least privilege

Default to read-only at the workflow level. Grant per-job only what is needed.

```yaml
permissions:
  contents: read            # default at workflow level

jobs:
  publish:
    permissions:
      contents: write       # only this job can tag releases
      packages: write       # only this job can publish to GHCR
      id-token: write       # only this job can mint OIDC tokens
    runs-on: ubuntu-latest
```

Reference: [GitHub docs — permissions for GITHUB_TOKEN](https://docs.github.com/actions/security-for-github-actions/security-guides/automatic-token-authentication#permissions-for-the-github_token).

Common patterns:
- Read-only CI: `contents: read`.
- Write to GHCR: add `packages: write`.
- Create a release: add `contents: write`.
- OIDC to cloud: add `id-token: write` (see OIDC section below).
- Post a PR comment: add `pull-requests: write`.

## SHA-pinning third-party actions

Action tags are mutable. A compromised maintainer or a typosquatted fork can replace `@v4` with malicious code. Pin to full commit SHAs. Keep the version in a comment for humans.

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

Automate the maintenance with Dependabot:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

Dependabot bumps pinned SHAs and updates the comment. Review each bump — `github/codeql-action` is trusted; a 3-contributor action is not.

## OIDC for cloud deploys — no long-lived keys

Storing `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in secrets is legacy. Use OIDC federation instead — GitHub mints a short-lived token the cloud IAM trusts.

### AWS

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502  # v4.0.2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy-prod
          aws-region: us-east-1
      - run: aws sts get-caller-identity
      - run: aws deploy create-deployment ...
```

Role trust policy pattern (conditioned on the repo + ref):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:owner/repo:ref:refs/heads/main" }
    }
  }]
}
```

Restrict `sub` to the exact repo, ref, or environment. Never `repo:*:*` — that trusts every repo on GitHub.

### GCP

Use [`google-github-actions/auth`](https://github.com/google-github-actions/auth) with a Workload Identity Pool + Provider bound to the repo.

### Azure

Use `azure/login` with OIDC. Configure a federated credential on the App Registration.

## Secrets hygiene

- Use `secrets.<NAME>` — never hardcode.
- **Use environments** for production secrets. `environment: production` + required reviewers gate deploys behind a human approval.
- Never `echo "${{ secrets.FOO }}"` or pass via command-line arg where it appears in `ps`. Pipe via stdin or set as env var.
- For structured secrets (kubeconfig, JSON), write to a file with `shell` mode and redact from logs: `echo "::add-mask::$VALUE"`.
- Rotate secrets on a schedule. Orphan secrets are landmines.

See [`pass-cli-secrets`](../pass-cli-secrets) for the broader secret hygiene story. GitHub Actions specifically: **prefer OIDC over long-lived secrets**. If you have a secret, you almost always have a better architecture without one.

## Concurrency — stop racing and wasting minutes

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

- Cancel in-flight PR runs when a new push updates the same PR. Saves minutes.
- **Do not** cancel `main` or deploy runs — that can strand half-applied deploys.

For deploy workflows:

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false    # never cancel a deploy mid-flight
```

## Path filters — do not run everything on every change

```yaml
on:
  pull_request:
    paths:
      - 'apps/web/**'
      - '.github/workflows/ci-web.yml'
      - 'pnpm-lock.yaml'
```

For monorepos, path filters are the difference between 5-minute CI and 45-minute CI. Combine with separate workflows per package, or use a matrix driven by changed-files detection.

## Caching — right tool for the job

- **`actions/cache`** — for generic caches (Rust target dir, pip wheels, Go modules). Keys should be lockfile-hashed.
- **Setup-action caches** — `actions/setup-node` with `cache: pnpm`, `actions/setup-go` with `cache: true`. Built-in; usually better than rolling your own.
- **Docker build cache** — use `buildx` with `cache-from`/`cache-to` against GHCR or registry cache.

```yaml
- uses: actions/cache@1bd1e32a3bdc45362d1e726936510720a7c30a57  # v4.2.0
  with:
    path: |
      ~/.cache/pip
      ~/.cache/pre-commit
    key: ${{ runner.os }}-py-${{ hashFiles('requirements.txt', '.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-py-
```

Rules:
- Cache keys include the lockfile hash so bumps invalidate.
- Restore keys allow partial hits during lockfile churn.
- Do not cache secrets or per-run artifacts.

## Matrix builds

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node: ['20', '22']
    exclude:
      - os: windows-latest
        node: '20'
```

- `fail-fast: false` when you want to see **all** failures, not just the first.
- Use `exclude` / `include` for sparse matrices — better than a second workflow.
- Matrix size × job time = bill. Audit.

## Composite actions vs reusable workflows

### Composite action (`.github/actions/<name>/action.yml`)

Use for: small reusable block of steps within the same repo. Fast, no extra job boundary.

```yaml
# .github/actions/setup-toolchain/action.yml
name: Setup toolchain
description: pnpm + node + install
runs:
  using: composite
  steps:
    - uses: actions/setup-node@1d0ff469b7ec7b3cb9d8673fde0c81c44821de2a
      with:
        node-version-file: .nvmrc
        cache: pnpm
    - run: pnpm install --frozen-lockfile
      shell: bash
```

Use from a workflow:

```yaml
- uses: ./.github/actions/setup-toolchain
```

### Reusable workflow (`.github/workflows/<name>.yml` with `on: workflow_call`)

Use for: cross-repo reuse, or when you want the reused block to have its own job, runner, permissions, secrets.

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'
    secrets:
      NPM_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: actions/setup-node@1d0ff469b7ec7b3cb9d8673fde0c81c44821de2a
        with:
          node-version: ${{ inputs.node-version }}
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

Consume:

```yaml
jobs:
  call-test:
    uses: your-org/ci-common/.github/workflows/reusable-test.yml@v1
    with:
      node-version: '22'
    secrets: inherit
```

Pin reusable workflows to a tag or SHA when cross-repo. Same rule as third-party actions.

## Environments and deploy approvals

Use **environments** to gate production deploys:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.example.com
```

In the repo settings → Environments → `production`:
- Required reviewers (humans who must approve each deploy).
- Deployment branches (only `main` can deploy to prod).
- Environment secrets scoped to the environment.
- Wait timer (optional: 5-minute cooling window).

Integrates with [`deploy-safety`](../deploy-safety) — the environment approval is one of the release gates.

## Security scanning as part of CI

Bake these into a scheduled workflow + push events:

- **CodeQL** — `github/codeql-action`. First-party, supports many languages.
- **Dependency review** — `actions/dependency-review-action`. Fails PRs introducing known-vulnerable deps.
- **Trivy / Grype** — container image and filesystem scanning. See [`container-image-hardening`](../container-image-hardening).
- **Gitleaks** — secret scanning in history and in PRs.

Example secret scan:

```yaml
- uses: gitleaks/gitleaks-action@ec0887dca66ef8e9a3c6c0b4d82a39b9b6c7f3e9  # v2.3.9
  env:
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}  # optional, for orgs
```

## Branch protection — wire CI to enforcement

CI is only valuable if merges are blocked on it. Repo settings → Branches → `main`:
- Require status checks: the exact job names from your CI workflow (`lint`, `test`, `build`).
- Require branches to be up to date.
- Require review approvals (2 for prod-critical repos).
- Block force pushes.
- Do not allow bypass for admins on prod repos.

## Performance — make CI fast

- Split long workflows: `lint` + `test` + `build` as parallel jobs, not one sequential script.
- Cache aggressively (see above).
- Skip paths that do not matter for the current change.
- Use `ubuntu-latest` for most jobs; reserve `macos-latest` / `windows-latest` for actual platform coverage (they cost 10x and 2x respectively in minutes).
- Avoid `ubuntu-latest` + `uses: actions/setup-*` when a prebuilt Docker image would serve — prebuilt beats rebuild.
- Use `continue-on-error: true` sparingly and only for non-blocking checks; otherwise failures hide.

## Cost control

- Use `workflow_dispatch` for expensive one-offs instead of nightly crons.
- Kill in-flight PR runs on re-push via `concurrency`.
- Prune old artifacts with short `retention-days`.
- Review monthly: Organization → Billing → Actions usage.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| `uses: some/action@master` | Mutable; maintainer compromise = your secrets |
| `permissions: write-all` or no `permissions:` at all | Default permissions are broader than you think |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` as secrets | Long-lived credentials rot and leak |
| `pull_request_target` running code from the PR | Fork can exfil your secrets |
| `${{ secrets.FOO }}` via command-line arg | Shows in `ps` and in logs on error |
| Single-file "monolithic" workflow with 20 jobs | Unreadable; hard to maintain |
| Scheduled workflows on forks | Non-maintainers keep running your org's budget |
| Cache key without a lockfile hash | Stale cache serves wrong deps |
| Matrix with `fail-fast: true` on a blocking check | First failure masks others; slower to fix |
| `continue-on-error: true` on the main test job | Turns real failures into green checks |
| Writing deploy logic in inline `run:` blocks | Untested; copy-pasted across workflows |
| No concurrency group | Racing runs on the same PR waste minutes |

## Interaction with other skills

- [`deploy-safety`](../deploy-safety) — defines what a safe deploy **is**; this skill implements it on GitHub.
- [`container-image-hardening`](../container-image-hardening) — image build / scan / sign steps land in workflows here.
- [`security-hardening`](../security-hardening) — dependency review, CodeQL, secret scanning.
- [`pass-cli-secrets`](../pass-cli-secrets) — broader story of where secrets live; this skill plugs into that.
- [`gh-cli-workflows`](../gh-cli-workflows) — `gh` CLI usage; complementary (CLI-side, not YAML).
- [`pr-workflow`](../pr-workflow) — PR workflow and branch protection interact directly.
- [`setup-pre-commit`](../setup-pre-commit) — same hooks can run locally and in GH Actions for parity.
- [`architecture-decision-records`](../architecture-decision-records) — decisions like "self-host runners" or "OIDC to AWS" warrant an ADR.

## Verification checklist

Every workflow should satisfy:

- [ ] All third-party actions pinned to a full commit SHA with a version comment.
- [ ] Top-level `permissions:` is set; per-job tightens as needed.
- [ ] No long-lived cloud keys — OIDC federated auth where cloud access is needed.
- [ ] No secrets are echoed, printed, or passed via command line.
- [ ] `pull_request_target` is not used, or is used without running PR code.
- [ ] `concurrency:` is set with a sensible group and `cancel-in-progress` policy matching the workflow.
- [ ] Path filters applied where they materially cut build time.
- [ ] Cache keys include the relevant lockfile hash.
- [ ] Matrix uses `fail-fast: false` if you want to see all failures.
- [ ] Production deploys go through an Environment with required reviewers.
- [ ] Branch protection requires the exact job names used here.
- [ ] Dependabot is enabled for `github-actions` updates.
- [ ] Scheduled workflows run only on the default branch, never on forks.
- [ ] Artifact retention is set; old large artifacts are pruned.
- [ ] Composite action vs reusable workflow chosen per use case (small DRY block vs cross-repo / per-job isolation).
