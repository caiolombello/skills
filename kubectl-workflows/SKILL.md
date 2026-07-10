---
name: kubectl-workflows
description: Use whenever running kubectl against a cluster. Require explicit --context and --namespace, dry-run before apply, and safe delete/exec.
---
# kubectl-workflows

Baseline for using `kubectl` from an agent session. Most mistakes come from wrong context or wrong namespace; both are implicit by default. This skill makes them explicit and adds guardrails for destructive operations.

## Non-negotiables

1. **Always pass `--context` explicitly** when multiple contexts exist. Never rely on the current `kubectl config current-context`.
2. **Always pass `--namespace`** (or `-n`) for namespaced resources. Never rely on the default namespace.
3. **Read before write.** Before any `apply` / `patch` / `replace` / `delete` / `scale`, inspect the current state (`get`, `describe`, `diff`).
4. **Never apply YAML you have not read.** Open and inspect every manifest first.
5. **Never `kubectl delete` without confirmation** — see destructive list below.
6. **Never edit in-place with `kubectl edit`** in an agent context. It opens an interactive editor and stalls.
7. **Never exec into production pods without explicit user approval.** `kubectl exec` bypasses audit trails available in CI.
8. **Always prefer server-side dry-run** before `apply`.
9. **Never `port-forward` or `proxy` without telling the user the port is being exposed locally.**
10. **Never export / `get -o yaml` a Secret** unless the user asked to see decoded values. Even base64 output can land in the agent context.

## Pre-flight: context + namespace

Before any write:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl --context <ctx> --namespace <ns> get ns <ns>     # sanity: namespace exists
kubectl --context <ctx> --namespace <ns> auth can-i <verb> <resource>
```

Confirm:
- Context points to the right cluster (dev / stg / prod).
- Namespace exists and is the intended one.
- The active user has permission for the intended verb (RBAC).

For EKS specifically, `kubectl config current-context` usually encodes the profile; mismatched AWS profile → `could not refresh token: ...`. Run the `aws sts get-caller-identity --profile <p>` from the `awscli-workflows` skill to confirm.

## Standard invocation shape

```bash
kubectl --context <ctx> --namespace <ns> <verb> <resource> [flags]
```

Prefer:
- `-o json` / `-o yaml` for structured output the agent can parse (but beware of size).
- `-o name` when you only need resource names.
- `-o wide` for a quick human view.
- `--sort-by='.metadata.creationTimestamp'` for time-ordered lists.

## Discovery (safe defaults)

```bash
# Resources and short names
kubectl api-resources
kubectl api-resources --namespaced=true

# Schema for a resource (most useful single discovery command)
kubectl explain deployment.spec.strategy
kubectl explain pod.spec.containers.resources

# What can I do here?
kubectl --context <ctx> --namespace <ns> auth can-i --list
```

Use `kubectl explain` before writing any manifest the agent is less than 100% sure about. It is the authoritative schema source.

## Reading

```bash
# List
kubectl --context <ctx> --namespace <ns> get <kind> -o wide
kubectl --context <ctx> --namespace <ns> get <kind> -l app=<label>

# Detail
kubectl --context <ctx> --namespace <ns> describe <kind> <name>

# Sorted by recent events
kubectl --context <ctx> --namespace <ns> get events --sort-by='.lastTimestamp'

# Watch (time-box it)
kubectl --context <ctx> --namespace <ns> get pods -w     # Ctrl-C out; do not leave open
```

### Logs

```bash
# Single container
kubectl --context <ctx> --namespace <ns> logs <pod> -c <container> --tail=200

# All containers
kubectl --context <ctx> --namespace <ns> logs <pod> --all-containers --tail=200

# Previous (crash-looping pod)
kubectl --context <ctx> --namespace <ns> logs <pod> --previous --tail=500

# By label, most recent
kubectl --context <ctx> --namespace <ns> logs -l app=<label> --tail=50 --max-log-requests=5

# Follow (time-box it)
kubectl --context <ctx> --namespace <ns> logs <pod> --tail=100 --since=5m --follow
```

Follow-mode leaves the process attached. Use `--since=<duration>` plus a bounded `--tail` when triaging; avoid pure `--follow` without a time limit.

### Describe an issue quickly

Standard triage sequence:
```bash
kubectl --context <ctx> --namespace <ns> get pods -l app=<l> -o wide
kubectl --context <ctx> --namespace <ns> describe pod <pod>
kubectl --context <ctx> --namespace <ns> get events --field-selector involvedObject.name=<pod> --sort-by='.lastTimestamp'
kubectl --context <ctx> --namespace <ns> logs <pod> --previous --tail=200
```

## Writing (require reading first)

### Golden rule: dry-run then diff then apply

```bash
# 1. Server-side dry-run (uses cluster validation + admission + defaults)
kubectl --context <ctx> --namespace <ns> apply -f <file> --dry-run=server

# 2. Diff against the live resource
kubectl --context <ctx> --namespace <ns> diff -f <file>

# 3. Apply
kubectl --context <ctx> --namespace <ns> apply -f <file>
```

Prefer `--dry-run=server` over `--dry-run=client`. Server-side runs admission webhooks (OPA / Kyverno / Gatekeeper) that the client cannot simulate.

### Generate manifests, do not handcraft

For simple resources, use `--dry-run=client -o yaml` to get a starting template:

```bash
kubectl create deployment myapp --image=myrepo/myapp:1.0 --dry-run=client -o yaml > deploy.yaml
kubectl create configmap myconfig --from-literal=KEY=value --dry-run=client -o yaml > cm.yaml
kubectl create job oneoff --image=busybox --dry-run=client -o yaml -- echo hello > job.yaml
```

Edit the resulting YAML; apply with the dry-run / diff / apply sequence above.

### Patches

Prefer `apply` with a full manifest. Only use `patch` for small, targeted edits:

```bash
# Strategic merge (default, Kubernetes-aware)
kubectl --context <ctx> --namespace <ns> patch deployment <d> \
  -p '{"spec":{"replicas":3}}'

# JSON Patch (for fields strategic merge cannot express)
kubectl --context <ctx> --namespace <ns> patch deployment <d> --type json \
  -p='[{"op":"replace","path":"/spec/replicas","value":3}]'
```

Never `kubectl edit` in an agent session — interactive editor will stall.

### Scaling

```bash
kubectl --context <ctx> --namespace <ns> scale deployment <d> --replicas=3
kubectl --context <ctx> --namespace <ns> scale deployment <d> --current-replicas=3 --replicas=5
```

`--current-replicas` is a guard: the operation fails if the current count differs, preventing racing with HPA.

### Rollouts

```bash
kubectl --context <ctx> --namespace <ns> rollout status deployment/<d> --timeout=2m
kubectl --context <ctx> --namespace <ns> rollout history deployment/<d>
kubectl --context <ctx> --namespace <ns> rollout undo deployment/<d>
kubectl --context <ctx> --namespace <ns> rollout restart deployment/<d>
```

`rollout restart` triggers a pod refresh without code change — useful for rotating secrets that are mounted as env or volume.

## Destructive commands — require confirmation

Ask the user before any of these, naming context + namespace + resource:

- `kubectl delete <any>` (especially `ns`, `pv`, `pvc`, `deployment`, `statefulset`, `job`, `cronjob`, `crd`)
- `kubectl delete -f <dir>` or `delete -l <selector>` (bulk)
- `kubectl drain <node>` / `cordon <node>`
- `kubectl scale --replicas=0`
- `kubectl cp` **from** a production pod (exfiltrates data; check what is being copied)
- `kubectl exec` in production pods (write confirmation, even for `--rm` interactive debug)
- `kubectl port-forward` / `proxy` (exposes cluster-internal services locally)
- `kubectl rollout undo` / `restart` in production
- `kubectl apply` of a manifest that creates ClusterRole / ClusterRoleBinding / Namespace / CRD in production
- `kubectl delete --grace-period=0 --force` (force delete — can leave orphaned resources)

### Safer delete defaults

```bash
# Named delete with a dry-run first
kubectl --context <ctx> --namespace <ns> delete <kind> <name> --dry-run=server

# Wait for clean termination
kubectl --context <ctx> --namespace <ns> delete <kind> <name>     # default grace period
```

Avoid `--grace-period=0 --force` unless the resource is stuck and the user approves; it skips PreStop hooks and can orphan underlying resources (EBS volumes, LoadBalancers).

### Delete by label (bulk)

```bash
# Preview first
kubectl --context <ctx> --namespace <ns> get pods -l <label>=<v> -o name

# Then delete
kubectl --context <ctx> --namespace <ns> delete pods -l <label>=<v>
```

Never use `--all` on writes (`delete --all`, `apply --all`) without explicit user approval.

## Secrets handling

- `kubectl get secret <name> -o yaml` exposes base64 values to the agent context. Avoid unless needed.
- `kubectl get secret <name> -o jsonpath='{.data.<key>}' | base64 -d` decodes on purpose — handle as if it were plaintext from the start.
- Never `kubectl create secret --from-literal=KEY=<value>` with a real secret as argv. It lands in shell history and in the pod metadata as a managed field. Use:
  ```bash
  kubectl create secret generic <name> \
    --from-file=KEY=<(pass-cli item view --field password --item-title 'X') \
    --dry-run=client -o yaml | kubectl apply -f -
  ```
  (See the `pass-cli-secrets` skill.)
- Prefer External Secrets / Secrets Store CSI Driver / SOPS-sealed secrets over manually-created `Secret` objects.

## Debugging and exec

### Ephemeral debug container (preferred)

```bash
kubectl --context <ctx> --namespace <ns> debug <pod> \
  --image=nicolaka/netshoot \
  --target=<container> -it -- /bin/sh
```

`kubectl debug` adds an ephemeral container without mutating the pod spec. Does not require restart. Leaves a clean audit trail.

### `kubectl exec`

Only if `debug` is not an option:

```bash
kubectl --context <ctx> --namespace <ns> exec <pod> -c <container> -- <cmd>
kubectl --context <ctx> --namespace <ns> exec -it <pod> -c <container> -- /bin/sh     # ask before running in prod
```

Rules:
- Production pods: require user approval before exec.
- Never run `rm`, `kill`, or anything that modifies state inside a pod via exec unless explicitly asked.
- `-it` is fine when the user expects an interactive session; otherwise prefer non-interactive `-- <cmd>`.

## Port-forward / proxy

Both expose cluster-internal services to `localhost`. State this explicitly to the user:

```bash
# Tell the user: "This will expose <service>:port on localhost:<lport>."
kubectl --context <ctx> --namespace <ns> port-forward svc/<svc> 8080:80

# proxy (exposes the whole API server via localhost:8001)
kubectl --context <ctx> proxy
```

Both are long-running — do not leave them in the background without a plan to clean them up.

## Resources, probes, requests — when writing manifests

When generating Deployment / StatefulSet / Job / CronJob manifests, default to:

- `resources.requests` + `resources.limits` on every container (CPU + memory).
- Liveness, readiness, and startup probes appropriate to the workload.
- `securityContext.runAsNonRoot: true`, `readOnlyRootFilesystem: true` where feasible.
- `imagePullPolicy: IfNotPresent` (not `Always`, unless tag is `latest` — which itself should be flagged).
- Explicit `serviceAccountName` when the workload needs cluster access; never the default SA with cluster-wide perms.
- `terminationGracePeriodSeconds` tuned to the workload (default 30s is often too short for stateful apps).

Run `kubectl explain <kind>.spec` before inventing fields.

## Common pitfalls

1. **Wrong context.** `kubectl config use-context <ctx>` in one shell does not persist for an agent that spawns new shells — always pass `--context` on the command.
2. **kubeconfig merge.** `KUBECONFIG=<a>:<b>` merges; first wins for context names collisions. Unexpected if two kubeconfigs define the same name.
3. **`apply` vs `create`.** `apply` is idempotent; `create` errors if the resource exists. Prefer `apply` for manifests you expect to converge.
4. **`replace`.** `kubectl replace` removes managed fields the client does not set. Almost always wrong; use `apply` instead.
5. **Pager stalls.** `kubectl` does not pager by default, but some versions do for long output. Pass `--no-headers` + your own processing, or rely on `-o json`.
6. **Wide outputs truncate.** `-o wide` wraps in narrow terminals. Use `-o custom-columns` or `-o json | jq` for agent-safe output.
7. **EKS token refresh.** When `kubeconfig` shells out to `aws eks get-token`, it needs the matching AWS profile loaded. If `kubectl` fails with auth errors, check `aws sts get-caller-identity --profile <p>` first.
8. **CRD apply order.** Apply CRDs first, then resources that use them; otherwise `no matches for kind`. `kubectl apply -f dir/` sorts files alphabetically, which is not dependency-aware.
9. **Server-side apply** (`--server-side=true`) changes field ownership semantics; use when a controller is fighting you over a field, but understand it changes conflict behavior.

## Pre-flight checklist

Before any `kubectl` command that writes:

- [ ] `--context` set explicitly.
- [ ] `--namespace` set explicitly (namespaced resources).
- [ ] `kubectl config current-context` confirmed.
- [ ] Corresponding `get` / `describe` was run on the target.
- [ ] For `apply`: `--dry-run=server` passed and `diff` was reviewed.
- [ ] Destructive action? User confirmed with cluster + namespace + resource named.
- [ ] No interactive `edit`.
- [ ] No unintended `--all` / `-l` bulk selector.
- [ ] Secrets not being dumped to context.
- [ ] `port-forward` / `proxy` / `exec` in prod: user approved.
