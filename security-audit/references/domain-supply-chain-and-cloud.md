# Domain: supply chain, release, cloud, and deployment

Load the part whose boundary reconnaissance found:

- **Part A** — dependency resolution, untrusted contributions to builds, CI, release artifacts, signing and promotion, updaters, plugins and extensions.
- **Part B** — cloud identity and IAM, infrastructure as code, containers and Kubernetes, service mesh, serverless and edge, ingress, managed storage and events, environment configuration.

Source here often expresses intent, not live fact. Keep source-confirmed defects separate from facts an owner must observe. For AWS architecture, Security Hub findings, or live compromise, use the dedicated AWS skills instead; for Dockerfile and image work, `container-image-hardening`. Bold names and headings are ledger block identifiers.

## Part A — supply chain and release

### Supply-chain discipline

```text
- A mutable or known-vulnerable dependency is not a finding by itself. Show who can
  influence resolution, which build consumes it, and what execution or release
  boundary follows.
- Follow integrity across every handoff: source identity, resolved inputs, build
  worker, artifact identity, test result, signature or attestation, promotion, update
  consumer.
- CI configuration is authorization code: which event triggered the job, whose code
  runs, which secrets and tokens exist, what it can publish or mutate.
- A checksum fetched from the same untrusted place as the artifact proves nothing.
  Identify the trusted root and the failure behavior.
- Walk backward from a released digest or installed update to every input, credential,
  worker, cache, and decision. Compare untrusted and protected workflow events side by
  side; include revoked key, failed download, missing attestation, partial release,
  rollback, and registry-outage paths.
```

**Dependency source and namespace confusion** — resolver configuration can pick an unintended namespace, fallback registry, mirror, or source URL; check source priority, lockfile and checksum use, alternate build files, and first install versus update.

**Mutable and unbound build inputs** — builds consume branches, tags, unverified submodules, downloaded tools, remote includes, floating CI actions, or mutable image tags that a lower-trust writer can change.

**Generated-source and codegen provenance gaps** — schemas, vendored archives, generated clients, localization, or blobs ship executable content without the review and integrity gate that source gets.

**Build-context inclusion** — secrets, local config, repo metadata, or developer artifacts end up in a package or image because the build context exceeds intended inputs; confirm a real credential or private data is exposed.

**Untrusted code in a privileged workflow** — pull requests, comments, forks, dependency bots, or external events run contributor code with protected secrets, write tokens, deploy authority, or trusted runners. Compare trigger, checkout ref, approval gate, environment protection, and permissions; do not assume host defaults not in source.

**Workflow command and expression confusion** — branch names, commit messages, issue fields, artifact names, or matrix values reach shell, template expressions, paths, or privileged inputs unvalidated.

**Cache, artifact, and workspace trust mixing** — a lower-trust job populates a cache, artifact, or workspace that a higher-trust job restores and executes or releases; check key namespaces, producer identity, and digest binding.

**Automation identity overreach** — CI jobs hold more permission than needed and untrusted inputs select the affected resource. Least-privilege gaps without a reachable privileged action are hardening.

**Build-to-promotion substitution** — tests, review, signature, and publication refer to mutable names rather than one immutable digest across copies, repacks, and architecture merges.

**Release authorization and signing-policy gaps** — a release or signature is accepted from the wrong workflow, repository, branch, environment, key role, or threshold; consumers check that a signature is valid but not whose.

**Update metadata and rollback confusion** — an updater authenticates bytes but not version, product, platform, channel, target path, expiry, or rollback state, or mixes metadata and payload from different transactions; installation is not atomic.

**Plugin and extension trust expansion** — an extension gains host authority beyond its declared scope, a publisher replaces another's identity, or install hooks run before authenticity and capability checks. A user installing arbitrary plugins into their own environment is not a boundary.

### Supply-chain validation

1. Name the lower-trust actor, the controllable source, cache, artifact, or metadata, the trusted consumer, and the resulting unauthorized publication, code inclusion, secret disclosure, or privileged execution.
2. Prove artifact identity across the broken handoff: a different mutable name or unbound digest must reach a real consumer.
3. Verify package-manager, repository-host, registry, and signing defaults for the pinned version; branch protection, hosted runner, registry, and signing-service facts outside the repo make it `needs_validation`.
4. Validate with a harmless local fixture repository, dummy credential markers, local registry config, and a non-production namespace. Never publish, trigger real CI, or alter a release.

## Part B — cloud and deployment

### Cloud discipline

```text
- Do not infer live exposure from a manifest alone. Establish which environment
  consumes it, what defaults and overlays change it, and whether the path is active.
- Map each workload identity to specific operations and resources. Broad policy is a
  finding only when lower-trust input can reach an unauthorized action.
- Ingress, proxies, mesh, metadata services, and admission policy count only when
  their configuration and attachment are visible.
- A secret reference is not a disclosure. Require a lower-trust reader, output,
  artifact, log, or unsafe fallback.
- Render every maintained environment locally and tabulate exposed ports, workload
  identity, network peers, mounted secrets, and cloud resources. Diff deploy,
  migration, restore, failover, and emulator paths, and behavior when mesh, admission,
  identity, or secret services are unavailable.
```

**Workload identity overreach** — a workload, pod, function, or node identity can act on tenants, accounts, or resources beyond its role, and request or job input selects the target.

**Cross-account or cross-tenant role confusion** — role assumption, external IDs, token exchange, or federation accept claims not bound to the intended account, audience, repository, namespace, or workload.

**Application authorization delegated to cloud metadata** — the app trusts caller-supplied identity headers, tags, labels, or account IDs without verifying they came from the control plane or a trusted proxy.

**Unexpected service or management-plane reachability** — ingress, listeners, security groups, annotations, port mappings, or bind addresses expose admin, debug, metrics, or internal APIs to a lower-trust network. A repository-controlled public route to a sensitive handler can be confirmed; missing network controls alone are `needs_validation`.

**Trusted-proxy and mesh identity bypass** — a backend accepts forwarded identity or mTLS metadata from peers outside the intended ingress or sidecar, or an alternate port or health path skips the mesh; check fail-open when the proxy is absent.

**Metadata and internal-service reachability** — an untrusted URL or destination reaches instance metadata, control-plane sockets, or internal APIs carrying workload credentials.

**Host or control-plane capability exposure** — a lower-trust workload can select privileged mode, capabilities, host namespaces, host paths, devices, runtime sockets, or service-account tokens. Missing seccomp or read-only root alone is hardening.

**Admission and policy path inconsistency** — one deployment route enforces image, namespace, privilege, or secret policy while another controller, job, upgrade, or restore path does not.

**Namespace and label trust confusion** — network, admission, secret, or identity policy keys on labels, annotations, names, or namespaces that a less-trusted principal can set.

**Security-control precedence drift** — dev values, chart defaults, env vars, flags, feature gates, or per-region overlays disable authentication, TLS, tenant scoping, or audit in a deployed environment. Render the final config per environment.

**Secret exposure across workload boundaries** — secrets in logs, crash reports, process arguments, shared env, broad volumes, build outputs, or read APIs reachable by another workload or tenant.

**Credential renewal and outage fallback** — failed mount, refresh, rotation, or revocation leaves stale credentials active or drops to a less-trusted identity mode.

**Object and signed-URL policy confusion** — bucket policy, object keys, CDN origins, or signed URLs fail to bind principal, operation, namespace, audience, or expiry, including list, version, and write paths.

**Event-source identity confusion** — a function trusts event body fields as source identity instead of validating the provider-signed envelope, subscription, account, region, and replay state.

**Edge/runtime boundary mismatch** — an edge or serverless runtime assumes secrets, APIs, isolation, or tenant policy that differ from the origin runtime, and fallback changes authority or caching.

### Cloud validation

1. Establish the active source path and effective deployed object; otherwise `needs_validation`, naming the missing rendered manifest or owner-observed attachment.
2. Name the lower-trust caller or workload, the identity, the controllable selector, the affected resource, and the unauthorized operation or disclosure.
3. Verify provider and orchestrator defaults at the pinned version. Do not assume a public IP, reachable metadata service, permissive firewall, or missing admission attachment.
4. Local validation may render templates, evaluate policy, inspect a namespaced fixture, or run an emulator with dummy identities. No cloud CLI calls against real accounts, no live endpoints, no changes to shared resources.
