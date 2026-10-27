# Multi-environment values and release orchestration

This reference contains the detailed recipe linked from [`SKILL.md`](../SKILL.md). Check project-specific versions, permissions, schemas, and targets before use.

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

Commit values files to a git repo. ArgoCD/Flux watches, applies. The sync window + drift detection + rollback UI are the value. See [`deploy-safety`](../../deploy-safety) for the progressive-rollout shape on top.
