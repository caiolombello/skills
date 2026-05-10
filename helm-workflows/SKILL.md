---
name: helm-workflows
description: Write, audit, install, upgrade, and roll back Helm charts safely. Use WHENEVER the user (1) authors, edits, or reviews a Helm chart (`Chart.yaml`, `values.yaml`, `templates/**`, `helpers.tpl`); (2) installs, upgrades, or rolls back a release (`helm install`, `helm upgrade`, `helm rollback`, `helm uninstall`); (3) manages values hierarchies across environments (`values.yaml` + `values-prod.yaml` + Helmfile / helm-secrets / argo-cd `values:`); (4) debugs a broken release (stuck, immutable-field error, leftover resources); (5) packages, signs, or publishes charts to a registry (ChartMuseum, OCI registry, Harbor, GHCR); (6) mentions `helm template`, `helm lint`, `helm test`, `helm diff`, `helm secrets`, Helmfile, ArgoCD, Flux, chart dependency, subchart, umbrella chart. Pairs with `kubectl-workflows` (the underlying K8s discipline) and `deploy-safety` (progressive rollout shape).
---

# Helm Workflows

Helm is the most common way to package, ship, and upgrade Kubernetes workloads. It is also the most common source of production surprises — because a `values.yaml` bump looks innocuous and a `helm upgrade` can silently rewrite 30 resources.

This skill covers safe **authoring** and safe **operation** of Helm releases. Underlying K8s discipline lives in [`kubectl-workflows`](../kubectl-workflows); progressive-rollout design in [`deploy-safety`](../deploy-safety); image supply chain in [`container-image-hardening`](../container-image-hardening).

## Golden rules

1. **`helm template | kubectl diff` before every upgrade.** Read what changes *before* applying it, just like `terraform plan`.
2. **Pin chart versions.** Never `helm install foo bitnami/foo` without `--version`. Chart upstreams change API.
3. **Pin image tags by digest** inside values. Tags are mutable.
4. **Values are a tree, not a pile.** Environment-specific values overlay the base — do not fork.
5. **Never store secrets in `values.yaml`**. Use `helm-secrets`, External Secrets, SOPS-encrypted values, or a secret manager (see [`pass-cli-secrets`](../pass-cli-secrets)).
6. **`helm upgrade` is destructive by default.** Deletions in templates translate to deletions in prod.
7. **Charts are contracts.** A chart you publish has users; treat breaking changes with semver + deprecation notes.

## Chart anatomy

```
mychart/
├── Chart.yaml              # metadata: name, version, appVersion, dependencies
├── values.yaml             # documented defaults — the public API of the chart
├── values.schema.json      # (optional) JSON Schema for validation
├── templates/
│   ├── _helpers.tpl        # named templates, label helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   ├── configmap.yaml
│   ├── pdb.yaml
│   ├── networkpolicy.yaml
│   ├── tests/
│   │   └── test-connection.yaml
│   └── NOTES.txt
├── charts/                 # subchart dependencies (vendored via `helm dep update`)
└── README.md
```

## `Chart.yaml` — version discipline

```yaml
apiVersion: v2                         # always v2 (Helm 3+)
name: api
description: The api service.
type: application                       # or 'library'
version: 1.7.2                          # chart version — bump on every change to templates/values
appVersion: "2025.04.18"                # the app being packaged; free-form, prefer pinned
kubeVersion: ">=1.28.0"                 # minimum supported K8s
home: https://github.com/example/api
sources: [https://github.com/example/api]
maintainers:
  - name: Platform Team
    email: platform@example.com

dependencies:                           # subcharts
  - name: postgresql
    version: 14.3.1
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled

annotations:
  artifacthub.io/changes: |
    - kind: fixed
      description: probe endpoints now match container port
```

### Semver for charts

- **Major**: backwards-incompatible value changes (renamed keys, removed features). Users must read release notes.
- **Minor**: new features, backwards-compatible value additions.
- **Patch**: template fixes, doc changes, defaults tweaks without schema change.

Breaking a key means: any user's existing `values.yaml` stops working. Rename carefully, document migrations in the release notes.

## `values.yaml` — the public API of your chart

`values.yaml` is the chart's public API. Think of it as a schema.

### Structure

```yaml
# values.yaml — documented defaults

image:
  registry: registry.example.com
  repository: api
  # Use immutable image digest in environment overlays; keep a sensible tag here.
  tag: "2025.04.18"
  pullPolicy: IfNotPresent
  pullSecrets: []

replicaCount: 3

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts: []
  tls: []

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    memory: 512Mi               # no CPU limit by default; see rationale in README

podDisruptionBudget:
  enabled: true
  minAvailable: 1

autoscaling:
  enabled: false
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 75

networkPolicy:
  enabled: true
  allow:
    - namespaceSelector: { matchLabels: { role: ingress } }

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 10001
  fsGroup: 10001
  seccompProfile: { type: RuntimeDefault }
containerSecurityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: { drop: [ALL] }

probes:
  startup:
    httpGet: { path: /healthz/live, port: http }
    failureThreshold: 30
    periodSeconds: 5
  liveness:
    httpGet: { path: /healthz/live, port: http }
    periodSeconds: 10
    failureThreshold: 6
  readiness:
    httpGet: { path: /healthz/ready, port: http }
    periodSeconds: 5
    failureThreshold: 3

config:                          # app-level env-vars the user can override
  LOG_LEVEL: info
  OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector.observability.svc:4317

# Never defaults for secrets. Users provide via helm-secrets / External Secrets.
# secretRefs: []

# Subchart value overrides
postgresql:
  enabled: false
  auth:
    existingSecret: api-postgres-auth
```

### Rules

- **Every key is documented by a comment.** If a key has no doc, a user will misconfigure it.
- **Group related keys.** `image.*`, `resources.*`, `probes.*`.
- **Sensible defaults for dev; safe defaults for prod.** Secure by default: `runAsNonRoot: true`, `networkPolicy.enabled: true`.
- **No secrets in defaults.** Never.
- **`values.schema.json`** for type validation when the chart is published.

### `values.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["image"],
  "properties": {
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": { "type": "string", "minLength": 1 },
        "tag":        { "type": "string" },
        "pullPolicy": { "type": "string", "enum": ["Always", "IfNotPresent", "Never"] }
      }
    },
    "replicaCount": { "type": "integer", "minimum": 0 }
  }
}
```

`helm install` fails early on schema violation. Fast feedback beats a broken deploy.

## Templates — the discipline

### Standard labels + selectors

Use the [Helm standard label set](https://helm.sh/docs/chart_best_practices/labels/):

```yaml
# templates/_helpers.tpl
{{- define "api.labels" -}}
helm.sh/chart: {{ include "api.chart" . }}
{{ include "api.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ .Values.partOf | default "platform" }}
{{- end -}}

{{- define "api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

**Selector labels must be immutable across upgrades.** If you change `app.kubernetes.io/instance` across upgrades, Helm cannot match existing Pods and an upgrade rewrites everything. Pin `selectorLabels` and add more labels to `labels`.

### Deployment template essentials

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api.fullname" . }}
  labels: {{- include "api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  revisionHistoryLimit: 10
  selector:
    matchLabels: {{- include "api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels: {{- include "api.labels" . | nindent 8 }}
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
    spec:
      serviceAccountName: {{ include "api.serviceAccountName" . }}
      securityContext: {{- toYaml .Values.podSecurityContext | nindent 8 }}
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: "{{ .Values.image.registry }}/{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          securityContext: {{- toYaml .Values.containerSecurityContext | nindent 12 }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
          startupProbe: {{- toYaml .Values.probes.startup | nindent 12 }}
          livenessProbe: {{- toYaml .Values.probes.liveness | nindent 12 }}
          readinessProbe: {{- toYaml .Values.probes.readiness | nindent 12 }}
          resources: {{- toYaml .Values.resources | nindent 12 }}
          env:
            {{- range $k, $v := .Values.config }}
            - name: {{ $k }}
              value: {{ $v | quote }}
            {{- end }}
```

### The `checksum/config` trick

```
checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

Forces the Deployment to roll when the ConfigMap content changes. Without it, a `helm upgrade` that only changes config leaves pods running old config. Apply to every ConfigMap and Secret the Pod consumes.

### `helpers.tpl` hygiene

Name helpers with the chart name prefix (`api.name`, `api.fullname`). Prevents subchart collisions. Use `include` not `template` so Helm can pipe through `nindent`.

## Local validation — `lint`, `template`, `test`

```bash
# Syntax + best-practice checks.
helm lint ./mychart --values ./environments/prod/values.yaml

# Render locally. Pipe to kubeval / kubeconform for schema validation.
helm template api ./mychart --values ./environments/prod/values.yaml \
  | kubeconform -strict -summary

# Run chart tests on a live cluster (after install).
helm test api -n prod
```

Run `helm lint` + `helm template` in CI on every PR touching the chart.

## `helm-diff` — mandatory before upgrade

The [`helm-diff`](https://github.com/databus23/helm-diff) plugin shows what a `helm upgrade` would change. **Use it on every non-trivial release.**

```bash
# Install the plugin
helm plugin install https://github.com/databus23/helm-diff

# Diff current release vs the upgrade
helm diff upgrade api ./mychart \
  --namespace prod \
  --values ./environments/prod/values.yaml \
  --context 3 \
  --suppress-secrets
```

Read the diff. If any resource is being deleted and you did not expect that, stop and investigate.

## Upgrade discipline

```bash
# Safe upgrade shape
helm upgrade api ./mychart \
  --namespace prod \
  --values ./environments/prod/values.yaml \
  --version 1.7.2 \                    # pin chart version when pulling from repo
  --atomic \                           # rollback automatically on failure
  --wait --timeout 5m \                # wait for readiness
  --history-max 10                     # retain rollback history
```

Flags:
- `--atomic` — on failure, rollback to previous release automatically. **Always on for production.**
- `--wait` — wait for resources to become ready. Combined with readiness probes, this catches broken deploys at install time.
- `--timeout` — cap the wait. Match to the workload start time + margin.
- `--history-max` — retain previous releases so `helm rollback` can go back N steps. Default is 10.
- `--dry-run` — print what would be done. Useful but **inferior to `helm diff`** for upgrades.

### `--atomic` caveats

`--atomic` implies `--wait`. If the new release stalls on readiness, Helm rolls back the whole upgrade automatically — but deleted CRDs and orphaned resources may linger. The first rule of Helm ops: know the blast radius before you press enter.

### Rollback

```bash
helm history api -n prod
# REVISION  UPDATED    STATUS      CHART           APP VERSION  DESCRIPTION
# 12        ...        deployed    api-1.7.2       2025.04.18   Upgrade complete
# 11        ...        superseded  api-1.7.1       2025.04.10   Upgrade complete

helm rollback api 11 -n prod --wait
```

Rollback is a real release (it bumps the revision). Monitor after rollback just as you monitor after forward upgrade.

## Common `helm upgrade` failures

| Error | Cause | Fix |
|-------|-------|-----|
| `immutable field: spec.selector` | Selector labels changed | Never change `selectorLabels`. Revert selector change; add a new deployment if needed. |
| `release has no deployed releases` | Previous install failed | `helm rollback` to a healthy revision, or `helm uninstall` + reinstall if first-time. |
| `UPGRADE FAILED: another operation (install/upgrade/rollback) is in progress` | Previous release stuck in `pending-install` or `pending-upgrade` | `helm history` + `kubectl edit secret sh.helm.release.v1.api.v<N>` to inspect; roll back or delete stuck secret; restart upgrade. |
| `context deadline exceeded` | `--wait` timed out | Check readiness probes; check events; raise `--timeout` only if justified by workload size. |
| `Forbidden: patching objects without annotation` | Resource was created outside Helm | Add `meta.helm.sh/release-name` + `meta.helm.sh/release-namespace` annotations or delete+recreate. |

## Values hierarchy — one chart, many environments

Do not fork charts per environment. Overlay values.

### Pattern: repo layout

```
charts/
  api/
    Chart.yaml
    values.yaml                  # documented defaults — dev-safe
    templates/
    values.schema.json
environments/
  dev/
    values.yaml
  staging/
    values.yaml
  prod/
    values.yaml
  prod-eu/
    values.yaml
```

Install:

```bash
helm upgrade --install api charts/api \
  --namespace prod \
  --values environments/prod/values.yaml \
  --atomic --wait
```

Production override only the keys that differ. Keep env files short and scannable.

### Pattern: Helmfile (orchestration)

[Helmfile](https://github.com/helmfile/helmfile) wraps Helm for declarative multi-release management. Useful when you run many charts in one cluster.

```yaml
# helmfile.yaml
environments:
  prod:
    values:
      - environments/prod/globals.yaml

releases:
  - name: api
    chart: ./charts/api
    namespace: prod
    version: 1.7.2
    values:
      - environments/prod/api.yaml
    secrets:
      - environments/prod/api.secrets.yaml    # helm-secrets / SOPS

  - name: worker
    chart: ./charts/worker
    namespace: prod
    version: 0.5.1
    values:
      - environments/prod/worker.yaml
```

```bash
helmfile -e prod apply
```

### Pattern: ArgoCD / Flux (pull-based GitOps)

Commit values files to a git repo. ArgoCD/Flux watches, applies. The sync window + drift detection + rollback UI are the value. See [`deploy-safety`](../deploy-safety) for the progressive-rollout shape on top.

## Secrets — never in values.yaml

Options:

1. **External Secrets Operator** — references AWS Secrets Manager / SSM / Vault / etc. Best for most cloud envs.
2. **SOPS + helm-secrets plugin** — encrypt values files with age / KMS / PGP; `helm secrets upgrade ...` decrypts at apply time.
3. **SealedSecrets** — client-side encrypted Secrets committed to git; controller decrypts in-cluster.
4. **Vault Agent Injector** — sidecar injects secrets as files at pod start.

Whatever you pick, **reference a Secret by name from values.yaml** — never inline the secret.

See [`pass-cli-secrets`](../pass-cli-secrets) for the broader picture.

## Subcharts and dependencies

```yaml
# Chart.yaml
dependencies:
  - name: postgresql
    version: 14.3.1
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
    tags: [database]
    alias: pg                # optional rename
```

```bash
helm dependency update ./mychart          # fetches into ./charts/
helm dependency build ./mychart           # uses Chart.lock; reproducible
```

**Commit `Chart.lock`**. It pins dependency versions across machines / CI.

Override subchart values:

```yaml
# values.yaml (parent)
postgresql:
  enabled: true
  auth:
    existingSecret: api-pg-auth
  primary:
    persistence:
      size: 50Gi
```

### Use library charts for shared templating

If you have 20 internal services with near-identical `deployment.yaml`, extract a [library chart](https://helm.sh/docs/topics/library_charts/) (`type: library`). Reduces duplication; one fix rolls to every consumer.

## Publishing charts

Modern: OCI registries (GHCR, ECR, Harbor, Docker Hub).

```bash
helm package ./mychart --version 1.7.2
helm push mychart-1.7.2.tgz oci://ghcr.io/your-org/charts

# Sign with cosign
cosign sign --key cosign.key ghcr.io/your-org/charts/mychart:1.7.2

# Install from OCI
helm install api oci://ghcr.io/your-org/charts/mychart --version 1.7.2 \
  --namespace prod --atomic --wait
```

Rules:
- Pin versions. `latest` for charts is as unsafe as `latest` for images.
- Sign charts. Users verify signatures in CI or at install time.
- Include `README.md` with example values, upgrade notes, deprecation notices.

## ArgoCD Application example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/charts
    targetRevision: v1.7.2
    path: charts/api
    helm:
      valueFiles:
        - ../../environments/prod/values.yaml
      parameters:
        - name: image.tag
          value: "2025.04.18"
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=false
      - ServerSideApply=true
```

Rules:
- `selfHeal: true` undoes out-of-band changes. Good for drift but painful during a live incident — know how to pause sync (`argocd app set api-prod --sync-policy none`).
- `prune: true` deletes resources no longer in the chart. Combined with a template refactor, this can delete production workloads. Diff first.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| `helm install foo bitnami/foo` without `--version` | Next chart release silently upgrades your install |
| Renaming `app.kubernetes.io/instance` across upgrades | Immutable selector error; or worse, Helm rewrites everything |
| Secrets in `values.yaml` committed to git | Self-explanatory |
| Forking the chart per environment | Two charts drift; fixes applied to one never reach the other |
| Skipping `helm diff` on prod upgrade | The bug is in the diff you did not read |
| `--force` to push past an upgrade error | Usually amplifies the damage |
| `--set` for complex values in CI | Shell quoting issues; prefer values files |
| Manually editing Helm-managed resources | Next `helm upgrade` fights you |
| No `revisionHistoryLimit` on Deployment | Rollback impossible |
| No `PodDisruptionBudget` on critical workloads | Node drain takes the service down |
| No `checksum/config` annotation | Config changes do not roll pods |
| CRDs inside `templates/` | Not upgraded by Helm reliably — use `crds/` directory, deploy separately, or a dedicated CRD chart |
| Tight `livenessProbe` restarting on any blip | Restart storms |
| Subchart values not namespaced | Global collisions |
| `--wait` without a sensible `--timeout` | Hangs forever on broken Pods |

## Interaction with other skills

- [`kubectl-workflows`](../kubectl-workflows) — K8s safety; applies to every `kubectl` used to debug a Helm release.
- [`deploy-safety`](../deploy-safety) — Helm delivers pods, but the progressive-delivery / rollback-first shape lives in `deploy-safety`.
- [`container-image-hardening`](../container-image-hardening) — image pinning by digest, signing, SBOM. Helm references, does not replace.
- [`pass-cli-secrets`](../pass-cli-secrets) — where secrets live; Helm reads them by reference.
- [`terraform-iac-expert`](../terraform-iac-expert) — cluster and infra are Terraform, workloads are Helm. Keep the boundary clean.
- [`observability`](../observability) — chart should expose `ServiceMonitor`, dashboards, default alerts.
- [`github-actions-workflows`](../github-actions-workflows) / [`gitlab-ci-workflows`](../gitlab-ci-workflows) — CI that runs `helm lint`, `helm template | kubeconform`, `helm diff` on PRs, publishes charts on release.
- [`architecture-decision-records`](../architecture-decision-records) — decisions like "ArgoCD vs Flux vs Helmfile" warrant an ADR.

## Verification checklist

**Authoring a chart:**

- [ ] `Chart.yaml` has pinned `version`, `appVersion`, `kubeVersion`.
- [ ] `values.yaml` keys are all commented; secrets are not in defaults.
- [ ] `values.schema.json` exists (for published charts).
- [ ] Standard `app.kubernetes.io/*` labels applied via `_helpers.tpl`.
- [ ] `selectorLabels` are a pure subset of `labels` and are immutable across upgrades.
- [ ] Deployment uses `maxUnavailable: 0` + distinct readiness / liveness / startup probes.
- [ ] `revisionHistoryLimit` is set.
- [ ] `PodDisruptionBudget` defined for replicated workloads.
- [ ] `checksum/config` annotation references all ConfigMaps / Secrets the Pod reads.
- [ ] NetworkPolicy, PodSecurityContext, non-root by default.
- [ ] CRDs (if any) live in `crds/`, not `templates/`.
- [ ] `helm lint` passes; `helm template | kubeconform -strict` passes.
- [ ] Chart tests (`templates/tests/*.yaml`) cover the smoke path.

**Operating a release:**

- [ ] `helm diff upgrade` reviewed before every non-trivial upgrade.
- [ ] Upgrade uses `--atomic --wait --timeout <n>m` for production.
- [ ] Chart version pinned when installing from a repo.
- [ ] Image tag pinned (prefer digest) in environment values.
- [ ] Rollback command ready and tested (`helm rollback <rel> <rev>`).
- [ ] No secrets in the values files in git.
- [ ] `helm history` retained (≥ 10 revisions).
- [ ] ArgoCD / Flux sync events monitored during and after the release.
