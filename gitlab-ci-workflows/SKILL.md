---
name: gitlab-ci-workflows
description: 'Design, audit, and maintain GitLab CI/CD pipelines with a focus on security, speed, and maintainability. Use WHENEVER the user (1) writes, edits, or reviews `.gitlab-ci.yml` or any `include:`-d template; (2) sets up CI/CD, automated tests, linting, security scanning, container builds, or deploys on GitLab; (3) uses or configures GitLab Runners (shared SaaS, self-hosted, Kubernetes executor); (4) mentions "GitLab CI", "GitLab pipelines", "runner", "`include:`", "`extends:`", "`needs:`", "`rules:`", "merge request pipeline", "child pipeline", "DAG", "OIDC to AWS/GCP/Azure from GitLab", "stages", "artifacts", "cache"; (5) the pipeline is slow, flaky, expensive, or insecure; (6) required pipelines on the default branch are blocking merges. Covers: `rules:` vs `only/except`, `needs:` DAG, OIDC federated cloud auth, `include:` templates, parent-child pipelines, caching, DAST / SAST / SCA built-ins, protected variables, deploy environments.'
---

# GitLab CI/CD Workflows

GitLab CI is the other half of the "modern CI/CD on Git" universe — different vocabulary from GitHub Actions, same underlying concerns: security, speed, readability, determinism.

This skill is GitLab-specific. For GitHub, see [`github-actions-workflows`](../github-actions-workflows). For general CI/CD concepts (stages, gates, artifact promotion) see [`deploy-safety`](../deploy-safety).

## Golden rules

1. **Use `rules:` for everything, not `only/except`.** `only/except` is legacy.
2. **Use `needs:` to make the pipeline a DAG.** Default stage-based ordering is serial; `needs:` unlocks parallelism.
3. **`image:` pinned by digest.** Tags are mutable; digests are not. Applies to both `image:` and `services:`.
4. **OIDC for cloud auth.** Never long-lived cloud keys in CI variables. GitLab ID tokens federate to AWS / GCP / Azure / Vault.
5. **Protected variables on protected branches only.** `masked` + `protected` is the minimum; never mask a short secret (<8 chars).
6. **`include:` templates for reuse.** Copy-paste pipeline YAML is a bug.
7. **`dependencies:` / `needs:` is not artifacts.** Understand what is cache, what is artifact, what crosses job boundaries.
8. **Use merge-request pipelines for PR CI**, not branch pipelines (keeps feedback on the MR and avoids double-runs).

## File layout

```
.gitlab-ci.yml                      # entry point — usually thin; delegates via include
ci/
├── templates/
│   ├── build.yml                   # reusable job definitions
│   ├── test.yml
│   ├── security.yml
│   └── deploy.yml
├── rules/
│   └── common.yml                  # shared rule fragments
└── scripts/
    └── ensure-clean.sh
```

Entry point example:

```yaml
# .gitlab-ci.yml
include:
  - local: 'ci/templates/build.yml'
  - local: 'ci/templates/test.yml'
  - local: 'ci/templates/security.yml'
  - local: 'ci/templates/deploy.yml'

stages: [build, test, scan, deploy]

default:
  image: node:20.15.1-bookworm-slim@sha256:<digest>
  interruptible: true                # allow newer pipelines to cancel this one
  timeout: 30m
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
```

## Minimum viable pipeline

```yaml
# .gitlab-ci.yml
workflow:
  rules:
    # MR pipelines for MRs, branch pipelines only for the default branch + tags.
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
    - when: never

stages: [build, test, scan, deploy]

variables:
  FF_USE_FASTZIP: "true"
  FF_NETWORK_PER_BUILD: "true"
  GIT_STRATEGY: fetch
  GIT_DEPTH: "20"                    # deep-enough for diff, shallow for speed

.cache_node: &cache_node
  key:
    files: [pnpm-lock.yaml]
  paths:
    - node_modules/
    - .pnpm-store/
  policy: pull-push

install:
  stage: build
  image: node:20.15.1-bookworm-slim@sha256:<digest>
  cache:
    <<: *cache_node
    policy: pull-push
  script:
    - corepack enable
    - pnpm install --frozen-lockfile

lint:
  stage: test
  image: node:20.15.1-bookworm-slim@sha256:<digest>
  cache:
    <<: *cache_node
    policy: pull                     # read-only after install
  needs: [install]
  script:
    - corepack enable
    - pnpm lint

unit-test:
  stage: test
  image: node:20.15.1-bookworm-slim@sha256:<digest>
  cache:
    <<: *cache_node
    policy: pull
  needs: [install]
  script:
    - corepack enable
    - pnpm test --reporter=junit --outputFile=reports/junit.xml
  artifacts:
    when: always
    paths: [reports/]
    reports:
      junit: reports/junit.xml
    expire_in: 14 days
```

Highlights:
- `workflow.rules` controls when the whole pipeline runs. Prevents the classic "duplicate pipeline on branch + MR" problem.
- `needs:` makes `lint` and `unit-test` start as soon as `install` finishes — DAG, not serial.
- Images pinned with `@sha256:<digest>` (paste the real digest).
- `interruptible: true` lets a fresh push cancel an in-flight pipeline on the same MR.
- Cache key is file-hash-based; invalidates automatically when the lockfile changes.

## `rules:` — the new way

`only/except` is legacy. Use `rules:` everywhere.

```yaml
.deploy-prod-rules: &deploy-prod-rules
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual                   # human-approved deploy
    - when: never

deploy:prod:
  stage: deploy
  script: ./ci/scripts/deploy.sh prod
  environment:
    name: production
    url: https://api.example.com
  <<: *deploy-prod-rules
```

Common rule patterns:

```yaml
# Run only on MRs that touch backend files
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    changes:
      - backend/**/*
      - Dockerfile
      - .gitlab-ci.yml
  - when: never

# Run on default branch OR tag
rules:
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  - if: $CI_COMMIT_TAG

# Skip by commit message
rules:
  - if: $CI_COMMIT_MESSAGE =~ /\[skip ci\]/
    when: never
  - when: on_success
```

### Don't

```yaml
# Legacy — avoid
only:
  - main
except:
  - schedules
```

Mixing `rules:` and `only/except` in the same job fails. Pick rules.

## `needs:` — DAG pipelines

By default jobs within a stage run in parallel; stages run serially. `needs:` breaks out of stage ordering for a DAG — often halves pipeline duration.

```yaml
build:frontend:
  stage: build
  script: pnpm build:web

build:api:
  stage: build
  script: pnpm build:api

deploy:web:
  stage: deploy
  needs: [build:frontend]            # does NOT wait for build:api
  script: ./deploy-web.sh

deploy:api:
  stage: deploy
  needs: [build:api]
  script: ./deploy-api.sh
```

Rules:
- `needs:` can cross stages backwards only (towards earlier stages).
- Without `needs:`, the job waits for every prior-stage job.
- `needs: []` means "run immediately at pipeline start".

## Caching vs artifacts — know the difference

| Feature | `cache:` | `artifacts:` |
|---------|----------|---------------|
| Purpose | Speed up subsequent jobs / pipelines | Carry files from one job to the next, or publish |
| Lifetime | Per cache key, persisted by runner | Per pipeline, downloadable |
| Scope | Optimisation; can miss | Contract; must exist |
| Paths | Dependency caches, tool downloads | Build output, test reports, binaries |
| Invalidation | Cache key (lockfile hash) | N/A (artifact is per run) |

**Rule**: if the next job *requires* the file, it is an artifact. If the file *merely speeds things up* it is a cache.

### Cache keys

```yaml
cache:
  key:
    files:
      - pnpm-lock.yaml
      - .nvmrc
  paths:
    - node_modules/
    - .pnpm-store/
  policy: pull-push
```

- `files:` keys on the hash of these files. Lockfile change → cache invalidation.
- `policy: pull` for read-only consumers (test jobs); `pull-push` for the install job that builds the cache.
- Avoid `policy: push` on everything — causes concurrent overwrites.

### Artifacts with reports

Special artifact types integrate with GitLab UI:

```yaml
artifacts:
  when: always
  paths: [reports/]
  reports:
    junit: reports/junit.xml
    codequality: reports/gl-code-quality.json
    sast: reports/gl-sast.json
    dependency_scanning: reports/gl-dependency-scanning.json
    container_scanning: reports/gl-container-scanning.json
    coverage_report:
      coverage_format: cobertura
      path: reports/coverage.xml
```

GitLab MR UI highlights regressions automatically when the reports are uploaded.

## `include:` templates — DRY pipelines

```yaml
# ci/templates/test.yml
.test-template:
  image: node:20.15.1-bookworm-slim@sha256:<digest>
  cache:
    key:
      files: [pnpm-lock.yaml]
    paths: [node_modules/]
    policy: pull
  before_script:
    - corepack enable

unit-test:
  extends: .test-template
  stage: test
  needs: [install]
  script:
    - pnpm test

integration-test:
  extends: .test-template
  stage: test
  services:
    - name: postgres:16-alpine@sha256:<digest>
      alias: postgres
  variables:
    POSTGRES_PASSWORD: pgpass
  needs: [install]
  script:
    - pnpm test:integration
```

Use `extends:` for inheritance. Use `!reference [.template, key]` to pick up specific fragments. Use `include:` to pull templates from other repos (lock by Git ref, not `master`).

```yaml
include:
  - project: 'platform/ci-templates'
    ref: v2.14.0                     # never @master
    file: '/templates/node.yml'
```

Pin `ref:` to a tag or commit SHA — same rule as pinning third-party actions on GitHub.

## Parent-child pipelines for monorepos

For a monorepo where each service has its own pipeline:

```yaml
# Parent .gitlab-ci.yml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

stages: [trigger]

api:
  stage: trigger
  trigger:
    include: services/api/.gitlab-ci.yml
    strategy: depend                 # fails parent if child fails
  rules:
    - changes:
        - services/api/**/*
        - ci/templates/**/*

web:
  stage: trigger
  trigger:
    include: services/web/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes:
        - services/web/**/*
```

Child pipelines run in parallel; each service only builds when its files change.

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

## Protected variables and environments

- **CI/CD variables** — Settings → CI/CD → Variables.
- **Protected**: only available on protected branches / tags (default branch + tags by policy).
- **Masked**: value redacted from logs (keep <8 chars away; some chars fail masking).
- **Environment scope**: limit a variable to a specific environment (`production`).
- **File variables**: for multi-line secrets (certs, kubeconfig, etc.).

**Never** put long-lived cloud credentials in variables. Use OIDC (see above) or short-lived federated tokens.

### Environments and deploy approvals

```yaml
deploy:prod:
  stage: deploy
  environment:
    name: production
    url: https://api.example.com
    deployment_tier: production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual                   # human approval
```

Protected environments in the project settings:
- Required reviewers / groups.
- Allowed to deploy: specific maintainers.
- Approval rules (Ultimate tier).

## Security scanning — built-ins

GitLab ships templates for SAST, DAST, dependency scanning, container scanning, secret detection, IaC scanning.

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/IaC-Scanning.gitlab-ci.yml
```

Customize via variables:

```yaml
variables:
  SAST_EXCLUDED_PATHS: "spec, test, tests, tmp, node_modules"
  SECRET_DETECTION_EXCLUDED_PATHS: "fixtures, testdata"
  CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

Complement with [`container-image-hardening`](../container-image-hardening) and [`security-hardening`](../security-hardening).

## Runner discipline

- **SaaS shared runners** for OSS and simple cases — cheap, autoscaling, no ops.
- **Self-hosted Kubernetes executor** for enterprise and scale — private networks, cost control, custom images.
- **Never run privileged containers** unless required for Docker-in-Docker. Prefer Kaniko, Buildah, or BuildKit rootless.
- **Tag runners** and pin jobs to tags: `tags: [k8s, linux]`. Prevents accidental scheduling on a mismatched runner.
- **Resource limits** in runner config — per-job CPU / memory caps.

## Docker image builds — prefer Kaniko or BuildKit rootless

Avoid privileged Docker-in-Docker where possible.

```yaml
build:image:
  stage: build
  image: gcr.io/kaniko-project/executor:v1.23.2-debug@sha256:<digest>
  script:
    - /kaniko/executor
      --context=$CI_PROJECT_DIR
      --dockerfile=$CI_PROJECT_DIR/Dockerfile
      --destination=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
      --digestfile=image.digest
  artifacts:
    paths: [image.digest]
```

See [`container-image-hardening`](../container-image-hardening) for the broader image discipline — signing, SBOM, distroless base, etc.

## Performance

- **Use `needs:`** — parallelize aggressively.
- **Cache lockfile-hashed.**
- **`GIT_DEPTH` small** — shallow clone unless you need history.
- **`GIT_STRATEGY: fetch`** — reuse working dir.
- **Interruptible jobs** — cancel stale MR runs.
- **Child pipelines** for monorepo.
- **Self-hosted runners with warm caches** for tight feedback.
- **Profile** with `CI_PIPELINE_DURATION` in the pipeline detail page; find the long-tail jobs.

## Cost control

- Pin `timeout:` so a runaway job doesn't consume all minutes.
- Use `interruptible: true` + MR pipeline rules to prevent duplicate branch+MR pipelines.
- Review `Minutes usage` monthly: Group / Project Settings → Billing.
- Archive job logs older than N months; don't keep artifacts longer than needed.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| `only/except` everywhere | Legacy; inconsistent with `rules:` behavior |
| `image: node:latest` | Mutable; reproducibility gone |
| Secrets stored as plain CI variables | Long-lived cloud keys leak; logs leak |
| Single 300-line `.gitlab-ci.yml` | Hard to review; copy-paste across services |
| No `workflow.rules` | Double pipelines on branch + MR |
| Serial stages without `needs:` | Pipeline slower than necessary |
| `allow_failure: true` on a blocking check | Hides regressions |
| `retry:` on everything | Masks flaky tests; costs minutes |
| Cache without a lockfile hash key | Stale deps; mysterious failures |
| `dind` (Docker-in-Docker) with `privileged: true` | Security + cost; Kaniko / BuildKit rootless usually wins |
| `ref:` on imported templates is `master` | Mutable; upstream change breaks your pipeline silently |
| Protected variables exposed to all branches | Secrets leak via MR from a fork or branch |

## Interaction with other skills

- [`deploy-safety`](../deploy-safety) — canary / feature-flag / rollback discipline. GitLab is the plumbing; `deploy-safety` is the shape.
- [`container-image-hardening`](../container-image-hardening) — image supply chain; plug in at the `build:image` job.
- [`security-hardening`](../security-hardening) — app-layer security. Pair with GitLab's SAST / Secret Detection / Dep Scan templates.
- [`pass-cli-secrets`](../pass-cli-secrets) — broader secret hygiene; GitLab side is OIDC + Vault or AWS Secrets Manager via assume-role.
- [`kubectl-workflows`](../kubectl-workflows) + [`helm-workflows`](../helm-workflows) — where deploy jobs land on K8s.
- [`github-actions-workflows`](../github-actions-workflows) — companion skill, different host. Most concepts map.
- [`gh-cli-workflows`](../gh-cli-workflows) — not directly applicable; GitLab has `glab` CLI which follows similar multi-account patterns.
- [`observability`](../observability) — the SLO gates that a deploy stage reads.

## Verification checklist

Every pipeline should satisfy:

- [ ] `workflow.rules` avoids double pipelines on branch + MR.
- [ ] All `image:` / `services:` pinned by digest.
- [ ] `include:` templates pinned by Git ref / tag / SHA.
- [ ] `rules:` everywhere (no `only/except`).
- [ ] `needs:` used to parallelize where jobs are independent.
- [ ] Secrets protected + masked; sensitive variables scoped to protected branches / environments.
- [ ] OIDC federated auth for cloud deploys (no long-lived cloud keys).
- [ ] Production deploys gated by `environment:` + protected environment approval.
- [ ] Cache keys include the lockfile hash; `policy` matches the job's role (install vs consumer).
- [ ] Artifacts retention set; old artifacts pruned.
- [ ] Built-in security templates (SAST / Secret / Dependency / Container) included for the languages in use.
- [ ] No `privileged: true` / `dind` unless justified; prefer Kaniko or BuildKit rootless.
- [ ] `interruptible: true` on jobs where cancellation on a new push is OK.
- [ ] Timeouts set per job; `retry:` limited to runner-side flakes.
