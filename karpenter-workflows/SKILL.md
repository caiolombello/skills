---
name: karpenter-workflows
description: Safely design, install, tune, and troubleshoot Karpenter for Kubernetes node provisioning. Use WHENEVER the user mentions Karpenter, NodePools, NodeClaims, NodeClasses, EC2NodeClass, consolidation, drift, disruption budgets, capacity types, spot/on-demand/reserved, pending pods caused by node supply, or replacing/upgrading cluster autoscaling on Kubernetes. Core guidance is provider-agnostic, with AWS-specific detail for EKS because that is the most common production setup.
---

# Karpenter Workflows

Karpenter is not “just autoscaling.” It is cluster capacity control: which nodes may exist, how quickly they appear, how aggressively they disappear, what workloads may land on them, and what cost / interruption / disruption tradeoffs the cluster accepts.

This skill covers safe **authoring**, **operations**, and **troubleshooting** for Karpenter. The mental model and triage flow are provider-agnostic. The concrete NodeClass examples below are AWS-first because `EC2NodeClass` on EKS is the dominant production use case. Use [`kubectl-workflows`](../kubectl-workflows) for baseline Kubernetes command safety, [`deploy-safety`](../deploy-safety) for progressive rollout discipline, [`observability`](../observability) for SLO-gated verification, and provider docs for the NodeClass resource.

## When to use

- The user is installing or upgrading Karpenter.
- The user is creating or editing `NodePool`, `NodeClaim`, or provider-specific `NodeClass` resources.
- Pods are pending because the cluster is not provisioning the right nodes.
- The user is tuning consolidation, drift, expiration, disruption budgets, limits, or weighted pools.
- The user is designing spot / on-demand / reserved capacity strategies.
- The user wants to replace or complement Cluster Autoscaler.

## When NOT to use

- The issue is pure Kubernetes scheduling with static node groups and no Karpenter resources.
- The problem is an HPA/VPA config unrelated to node supply.
- The task is generic `kubectl` hygiene — load [`kubectl-workflows`](../kubectl-workflows) directly.

## Docs-first rule

Do not invent Karpenter API fields from memory. Verify against the pinned Karpenter version and the provider version.

- Core Karpenter: `NodePool`, disruption, limits, weight, requirements, taints, startupTaints, `expireAfter`, `terminationGracePeriod`.
- Provider-specific NodeClass: `EC2NodeClass` on AWS, or the equivalent provider resource elsewhere.

For AWS, the main provider-specific concepts are:

- `EC2NodeClass`
- subnet / security group selector terms
- role / instance profile
- AMI family or alias
- capacity type (`spot`, `on-demand`, `reserved`)

## Core mental model

Think in layers:

1. **Pending pods define demand** — resource requests, selectors, affinities, tolerations, topology spread.
2. **NodePool defines allowed supply** — what kinds of nodes may be created, disruption rules, total limits, relative preference.
3. **NodeClass defines infrastructure details** — AMI, networking, IAM/role, block devices, metadata options, provider selectors.
4. **Karpenter reconciles the gap** — it creates `NodeClaim`s / nodes that satisfy both workload demand and pool/class constraints.

When something fails, debug from pod demand outward to pool/class supply.

## Golden rules

1. **Start from workload requirements, not instance types.** If you start with fixed instance lists too early, you recreate node groups with extra steps.
2. **Keep NodePools broad enough to give Karpenter choice.** Narrow pools increase pending pods and cost.
3. **Constrain only what matters.** Architecture, OS, capacity type, special hardware, isolation labels/taints, compliance requirements.
4. **Treat disruption settings as production policy.** Consolidation, drift, expiration, and budgets are rollout behavior, not just cost tuning.
5. **Prefer mutually exclusive NodePools.** Overlap only when you intentionally want preference/fallback behavior.
6. **Use weights intentionally.** Multiple overlapping NodePools with weights are a scheduling preference system.
7. **Verify pod selectors / tolerations first.** Many “Karpenter is broken” incidents are actually incompatible pod constraints.
8. **Do not let cost optimization override availability.** Spot is a workload decision, not a universal default.

## Safe workflow: install or upgrade Karpenter

Use [`kubectl-workflows`](../kubectl-workflows) and [`helm-workflows`](../helm-workflows) for command-level mechanics. Karpenter-specific checks are:

1. Verify the target Karpenter version and provider version from the chart / manifest / lockfile / IaC.
2. Verify CRD/API compatibility for:
   - `karpenter.sh/v1` `NodePool`
   - provider-specific `NodeClass` version (for AWS, `karpenter.k8s.aws/v1` `EC2NodeClass`)
3. Verify controller permissions, webhook health, and leader election after rollout.
4. Apply progressively in lower environments before prod.
5. After install/upgrade, verify:
   - controller pods healthy
   - CRDs registered
   - webhook / leader election healthy
   - a known pending workload can provision nodes

## Authoring NodePools

### What belongs in a NodePool

- high-level requirements (`arch`, `os`, capacity type, instance category/generation/family when truly needed)
- `nodeClassRef`
- taints and `startupTaints`
- lifecycle controls (`expireAfter`, `terminationGracePeriod`)
- disruption policy (`consolidationPolicy`, `consolidateAfter`, budgets)
- global resource limits for the pool
- `weight` when more than one pool can satisfy the same workload

### What does NOT belong there

- deep provider wiring (AMI details, subnets, SGs, block devices, metadata options)
- workload-specific selectors that should live on the pod instead
- arbitrary overfitting to current node inventory

### NodePool example shape

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general
spec:
  template:
    metadata:
      labels:
        workload-tier: general
    spec:
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: kubernetes.io/os
          operator: In
          values: ["linux"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand", "spot"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
      expireAfter: 720h
      terminationGracePeriod: 5m
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
    budgets:
      - nodes: "10%"
      - nodes: "0"
        reasons: ["Drifted", "Expired"]
        schedule: "0 10 * * mon-fri"
        duration: 8h
  limits:
    cpu: "1000"
    memory: 1000Gi
  weight: 10
```

### NodePool design rules

- Prefer category/generation/family constraints over hardcoding exact instance types.
- Use exact instance types only for truly special workloads.
- Prefer mutually exclusive NodePools as the default design. If two pools can satisfy the same pod, document why.
- Use `startupTaints` when another DaemonSet / bootstrap phase must run before scheduling normal pods.
- Use `limits` to prevent runaway capacity growth.
- Use disruption budgets to fence business-hour churn.
- Use `weight` only when overlap is intentional, for example a preferred pool plus an explicit fallback pool.

## Provider-specific NodeClasses

The NodeClass is where infrastructure reality lives. The resource name differs by provider; verify it first.

### AWS (`EC2NodeClass`) checklist

- IAM role / instance profile correct
- subnet selector terms correct and broad enough
- security group selector terms correct
- AMI family / alias appropriate for the cluster version
- root volume size / type / encryption correct
- IMDS locked down (`httpTokens: required`)
- tags align with org ownership / billing expectations

### AWS example shape

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  role: KarpenterNodeRole-my-cluster
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  amiSelectorTerms:
    - alias: al2023@v20240807
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeType: gp3
        volumeSize: 100Gi
        encrypted: true
        deleteOnTermination: true
  metadataOptions:
    httpTokens: required
    httpPutResponseHopLimit: 1
```

## Capacity strategy

### On-demand

Use when:

- interruption-sensitive workloads
- control-plane-adjacent workloads
- critical latency-sensitive paths

### Spot

Use when:

- workloads tolerate interruption
- retries / queue semantics exist
- PodDisruptionBudget, graceful shutdown, and multi-AZ spread are already correct

### Reserved / capacity reservations

Use when:

- guaranteed capacity matters
- procurement/cost planning has already reserved capacity

On AWS, `karpenter.sh/capacity-type=reserved` refers to EC2 capacity reservations / capacity blocks, **not** Reserved Instances. Do not treat RI purchases as a scheduling signal inside Karpenter.

### Weighted pools

Common pattern:

- higher-weight on preferred cheaper or more available pool
- lower-weight fallback pool for safety

Do not use weights as a substitute for invalid workload selectors.

## Disruption controls

Karpenter is continuously changing node supply. Treat disruption settings like a rollout policy.

### Consolidation

- `WhenEmptyOrUnderutilized` / equivalent: more aggressive cost optimization
- `WhenEmpty`: safer, less churn

Use aggressive consolidation only when workload disruption tolerance is proven.

### Drift

Drift replaces nodes when the desired template no longer matches what exists.

Examples:

- AMI change
- NodeClass change
- requirement/label/taint changes

This is a deploy event. Gate it with business-aware disruption budgets.

### Expiration

`expireAfter` is useful for hygiene, AMI freshness, and reducing node snowflakes. But it creates routine disruption. Pair it with:

- graceful termination
- correct PDBs
- disruption budgets
- realistic maintenance windows

## Triage: pending pods

Use this order:

1. Inspect the pending pod:
   - requests/limits
   - `nodeSelector`
   - node affinity
   - tolerations
   - topology spread
2. Check whether any NodePool could satisfy those constraints.
3. Check NodeClass readiness / provider readiness.
4. Check Karpenter controller logs / events.
5. Check whether pool limits or budgets are blocking new capacity.

Common causes:

- pod requires labels/taints no pool can provide
- instance constraints too narrow
- no subnet / SG / IAM match in NodeClass
- capacity type too strict (`spot` only during spot scarcity)
- pool limits exhausted
- DaemonSet overhead ignored in tiny instance shapes

## Triage: too many nodes / surprise cost

Check:

- pool limits too broad or absent
- consolidation disabled or too conservative
- workloads with inflated requests
- too many specialized pools preventing bin-packing
- spot fallback behavior forcing on-demand unexpectedly
- topology spread / anti-affinity causing fragmentation

Do not blame Karpenter before checking pod requests. Bad requests create bad nodes.

## Triage: excessive churn

Check:

- consolidation too aggressive
- `expireAfter` too short
- drift after recent NodeClass/AMI/template changes
- disruption budgets too permissive
- workload PDBs missing or too weak

If churn is hurting availability, prefer slowing consolidation before tightening workload constraints blindly.

## Verification checklist after changes

After changing a NodePool or NodeClass, verify:

- Karpenter controller healthy
- resource status conditions (`Ready`, provider-specific readiness)
- a representative pending pod can now schedule
- consolidation/drift behavior matches expectation
- no unexpected node churn during the observation window
- cost/availability tradeoff is explicitly stated

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Hardcoding exact instance types everywhere | Eliminates Karpenter flexibility |
| One NodePool per app by default | Causes fragmentation and operational sprawl |
| Spot for critical workloads without interruption handling | Availability regression disguised as savings |
| Aggressive consolidation in business hours with no budgets | User-visible churn |
| Using NodePool labels instead of fixing pod scheduling intent | Hides the real scheduling bug |
| Treating drift/expiration as harmless background noise | They are rollouts |

## Pair with other skills

- [`kubectl-workflows`](../kubectl-workflows) — safe cluster commands
- [`deploy-safety`](../deploy-safety) — rollout/rollback thinking for drift and node replacement
- [`observability`](../observability) — what to watch during pool changes
- [`awscli-workflows`](../awscli-workflows) — AWS-side verification when on EKS

## Verification checklist

- [ ] Karpenter and provider versions were verified from docs/manifests.
- [ ] NodePool vs NodeClass responsibilities are cleanly separated.
- [ ] Workload scheduling constraints were checked before blaming provisioning.
- [ ] Disruption settings were treated as production policy.
- [ ] Capacity strategy (spot/on-demand/reserved) matches workload tolerance.
- [ ] Verification covers both scheduling success and unintended churn/cost effects.
