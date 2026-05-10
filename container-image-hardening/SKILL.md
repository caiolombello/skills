---
name: container-image-hardening
description: Canonical workflow for writing secure, fast, small container images. Use WHENEVER the agent is about to (1) write or edit a Dockerfile / Containerfile; (2) change CI that builds images; (3) discuss image size, build cache, multi-arch, SBOM, signing, provenance, OCI labels, HEALTHCHECK, STOPSIGNAL, PID-1/init, or CVE patching; (4) run or suggest buildx/kaniko/nerdctl/podman build; (5) integrate trivy, grype, syft, cosign, copacetic, hadolint, dive, or similar tooling. Covers Dockerfile structure, multi-stage, non-root, base image choice, cache mounts, multi-arch, OCI labels/annotations, init/signals, SBOM, signing, CVE scan, in-place patching, reproducibility, and runtime securityContext pairing.
---

# container-image-hardening

One skill for the four things that usually come together in container work: **correctness, security, build speed, image size**. Use as a checklist when producing or reviewing a Dockerfile and its build pipeline.

## Non-negotiables

1. **Never build `FROM` a floating tag in production** (`latest`, `alpine`, `22-bullseye`). Pin to a digest (`image@sha256:...`) or at minimum a fully-qualified tag (`python:3.12.5-slim-bookworm`).
2. **Never ship as root.** Final image runs as a non-root user with `USER <uid>`.
3. **Never embed secrets at build time** via `ARG`, `ENV`, or `COPY`. Use BuildKit secret mounts (`--mount=type=secret`).
4. **Never invalidate the cache for no reason.** Order layers from least-to-most-volatile (dependencies before source).
5. **Multi-stage builds are default**, not an optimization. Final stage contains only runtime artifacts.
6. **Never publish an unscanned image.** Trivy or Grype scan runs in CI, with a fail-gate policy for HIGH/CRITICAL.
7. **Never merge a Dockerfile change without a working `docker build`.** No "looks right to me" reviews on image work.
8. **SBOM and signatures ship together.** If the image goes to a registry, attach the SBOM attestation and cosign signature.
9. **When CVEs arrive after publish, patch in place with Copacetic** rather than rebuilding and re-deploying from scratch — unless a base image bump is also needed.

## Base image choice

Decide in this order:

1. **Distroless** (`gcr.io/distroless/*`) — no shell, no package manager, tiny attack surface. Use when the runtime does not need a shell (compiled binaries, JVM apps).
2. **Chainguard / Wolfi** (`cgr.dev/chainguard/*`) — minimal, glibc-compatible, frequent CVE patches, signed + SBOMs attached.
3. **`-slim` variants** (`python:3.12.5-slim-bookworm`, `node:22.6.0-bookworm-slim`) — small Debian, has a shell, has apt. Compromise between distroless and full.
4. **Full distro** (`debian:bookworm`, `ubuntu:24.04`, `fedora:40`) — only when you need package manager at runtime.
5. **Alpine** — only if your runtime is known to behave on musl. Python, Node, Ruby wheels/binaries often break; Go, Rust static binaries are fine.

Anti-patterns:
- `FROM ubuntu` with no tag.
- Building a 1.2 GB image when a distroless final stage would be 80 MB.
- Alpine with `glibc` shims layered on — the point of Alpine is musl; if you need glibc, switch base.

## Dockerfile structure (reference)

```dockerfile
# syntax=docker/dockerfile:1.7

# ---------- Stage 1: build ----------
FROM python:3.12.5-slim-bookworm@sha256:<digest> AS builder

WORKDIR /build

# System build deps only (not in final image)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
 && rm -rf /var/lib/apt/lists/*

# Dep manifest first — maximises cache reuse
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    pip install --no-cache-dir uv \
 && uv sync --frozen --no-dev

# Source after deps
COPY src/ ./src/

# ---------- Stage 2: runtime ----------
FROM gcr.io/distroless/python3-debian12:nonroot@sha256:<digest> AS runtime

# Build args for labels (passed from CI: --build-arg VERSION=... etc.)
ARG VERSION=dev
ARG REVISION=unknown
ARG BUILD_DATE

# OCI image labels — single source of truth for provenance
LABEL org.opencontainers.image.title="my-service" \
      org.opencontainers.image.description="What this service does in one line." \
      org.opencontainers.image.source="https://github.com/<org>/<repo>" \
      org.opencontainers.image.url="https://github.com/<org>/<repo>" \
      org.opencontainers.image.documentation="https://github.com/<org>/<repo>/blob/main/README.md" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.vendor="<org>" \
      org.opencontainers.image.licenses="Apache-2.0"

# Copy runtime artifacts with explicit ownership matching the nonroot user
WORKDIR /app
COPY --from=builder --chown=nonroot:nonroot /build/.venv /app/.venv
COPY --from=builder --chown=nonroot:nonroot /build/src /app/src

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root (distroless:nonroot provides uid 65532)
USER nonroot

# Graceful shutdown signal; default is SIGTERM, set explicitly when the app expects something else.
STOPSIGNAL SIGTERM

# Container-level liveness. Orchestrators (k8s, ECS) usually prefer their own probes,
# but the HEALTHCHECK directive is read by Docker Compose, Swarm, and some registries.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3).status==200 else sys.exit(1)"]

EXPOSE 8000

ENTRYPOINT ["python", "-m", "src.main"]
```

Rules embedded in that structure:

- `# syntax=docker/dockerfile:1.7` at top enables cache mounts, secret mounts, heredocs.
- `FROM ... @sha256:<digest>` pins exactly.
- `WORKDIR` explicit; never rely on `/` or CWD of base image.
- `RUN --mount=type=cache,...` keeps apt/pip/npm caches across builds without baking them into the layer.
- Deps copied **before** source (cache survives source edits).
- `&& rm -rf /var/lib/apt/lists/*` and `--no-install-recommends` keep layer small when apt is used.
- Multi-stage: build deps never reach runtime.
- `ARG VERSION/REVISION/BUILD_DATE` + `LABEL org.opencontainers.image.*` put provenance on the image, queryable via `docker inspect` and most registries.
- `COPY --chown=<user>:<group>` when switching `USER` later, so files are readable by the runtime user without `RUN chown` (which would add a layer and duplicate the copied bytes).
- `ENV` set in the final stage only with runtime-needed vars; no secrets.
- `USER nonroot` (or explicit numeric uid) before `ENTRYPOINT`.
- `STOPSIGNAL` explicit when the app's default signal is not `SIGTERM` (nginx wants `SIGQUIT`, some JVMs want `SIGINT`).
- `HEALTHCHECK` declared even when the orchestrator (k8s, ECS) overrides it — it documents intent and Docker Compose / Swarm consume it directly.
- `ENTRYPOINT` as JSON array (exec form), so signals propagate correctly.
- No `CMD` with shell form if `ENTRYPOINT` handles it.

## OCI labels and annotations

Two places metadata can live on an image:

- **Labels** (`LABEL` in Dockerfile) — stored in the image *config* blob. Travel with `docker pull` / `docker save`. Visible via `docker inspect`.
- **Annotations** — stored in the image *manifest* (or *index* for multi-arch). Registry-facing metadata (e.g., for UIs, policy engines). Set via `buildx` `--annotation`.

Both use the `org.opencontainers.image.*` namespace. Prefer labels for anything a running container or a pulled image should carry; prefer annotations for registry-facing metadata that does not need to roundtrip through `docker save`.

### Canonical label set

| Label | Meaning | Example |
|---|---|---|
| `org.opencontainers.image.title` | Short human-readable name | `api-gateway` |
| `org.opencontainers.image.description` | One-line purpose | `Edge HTTP gateway for the X platform` |
| `org.opencontainers.image.source` | Source repo URL | `https://github.com/org/repo` |
| `org.opencontainers.image.url` | Project homepage | `https://github.com/org/repo` |
| `org.opencontainers.image.documentation` | Docs URL | `https://.../README.md` |
| `org.opencontainers.image.version` | Version (semver / tag / sha) | `1.4.2` |
| `org.opencontainers.image.revision` | Commit SHA | `abc123...` |
| `org.opencontainers.image.created` | RFC 3339 build timestamp | `2024-05-09T22:30:00Z` |
| `org.opencontainers.image.vendor` | Organization | `my-org` |
| `org.opencontainers.image.licenses` | SPDX license expression | `Apache-2.0` or `Apache-2.0 OR MIT` |
| `org.opencontainers.image.authors` | Maintainers | `team@example.com` |
| `org.opencontainers.image.ref.name` | Tag / ref name | `main` |
| `org.opencontainers.image.base.name` | Base image tag used | `gcr.io/distroless/python3-debian12:nonroot` |
| `org.opencontainers.image.base.digest` | Base image digest used | `sha256:...` |

GitHub's `docker/metadata-action` emits most of these automatically when fed the right inputs:

```yaml
- id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=sha,format=long
      type=ref,event=branch
      type=semver,pattern={{version}}
    labels: |
      org.opencontainers.image.title=<service>
      org.opencontainers.image.description=<one-line>
      org.opencontainers.image.licenses=Apache-2.0
      org.opencontainers.image.vendor=<org>
```

Then pass `labels: ${{ steps.meta.outputs.labels }}` to `docker/build-push-action`.

### Organization-specific labels

Add your own under a namespace you own. Common pattern: `<domain>.<field>`. Examples:

```dockerfile
LABEL com.example.team="platform" \
      com.example.env="production" \
      com.example.cost-center="<value>" \
      com.example.pii="none"
```

Treat these the same way you'd treat Kubernetes labels — pick a small, stable set; avoid ad-hoc labels per image. Keep values short; `docker inspect` output bloats quickly.

### Annotations (buildx)

```bash
docker buildx build \
  --annotation "index:org.opencontainers.image.source=https://github.com/org/repo" \
  --annotation "manifest:org.opencontainers.image.title=api" \
  --tag <registry>/<repo>:<tag> \
  --push .
```

Prefixes: `manifest:`, `manifest-descriptor:`, `index:`, `index-descriptor:`. Use `manifest:` for per-arch manifests (most common case) and `index:` for the multi-arch index.

## Runtime init and signal handling

Containers run the entrypoint as PID 1. PID 1 has two special responsibilities: reaping zombie children and receiving kernel signals. Many application runtimes fail at one or both.

### When to use `tini` / `dumb-init`

Add a minimal init when:

- The entrypoint spawns child processes and zombies can accumulate (common with Node, Python multiprocessing, shell-based wrappers).
- The entrypoint is a shell script — shells swallow or proxy signals unpredictably.
- The app does not install its own `SIGTERM` handler and you see containers hanging for the full termination grace period.

### Option A — use the distro's init

Distroless publishes `gcr.io/distroless/base:nonroot` with `tini` built in as `/usr/bin/tini`. Wolfi has `tini`. Alpine: `RUN apk add --no-cache tini`.

```dockerfile
FROM cgr.dev/chainguard/python:latest AS runtime
# ... copy artifacts ...
ENTRYPOINT ["/usr/bin/tini", "--", "python", "-m", "src.main"]
```

### Option B — let Docker inject `tini`

`docker run --init ...` (and `containerd` with `--init` equivalent) wraps the container with `tini` without touching the image. Fine for local dev; not always available in production orchestrators.

### When **not** to use an init

- The app (Go, Rust, compiled binaries) already handles signals correctly and spawns no child processes. Extra process adds nothing.
- Using `s6-overlay` or any supervisor already — they do init duties.

## `HEALTHCHECK` directives

`HEALTHCHECK` is interpreted by Docker Engine, Compose, Swarm, Podman, and most registry UIs. Kubernetes ignores it and uses its own probes — but the directive still documents the app's health contract.

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1
```

Rules:

- `--start-period` covers slow app startup; during it, failures don't count against `--retries`.
- Use `CMD` (exec form preferred). Never shell out to heavy commands; probe should be cheap.
- For distroless images without `curl`, use a language-native probe:
  ```dockerfile
  HEALTHCHECK CMD ["/app/.venv/bin/python", "-c", "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3).status==200 else sys.exit(1)"]
  ```
- When the orchestrator is Kubernetes, define the probe in the Pod spec too — `HEALTHCHECK` is ignored there.

## Reproducible builds

Enable reproducibility when images need to be auditable or when SLSA requires bit-identical rebuilds:

- Pin **everything** by digest or lockfile: base image, OS packages (e.g., `apt-get install pkg=version`), language deps via lockfiles (`uv.lock`, `package-lock.json`, `Cargo.lock`, `go.sum`).
- Set `SOURCE_DATE_EPOCH` to a fixed value (usually the commit timestamp) so timestamps in layers are deterministic:
  ```bash
  export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
  docker buildx build --build-arg SOURCE_DATE_EPOCH ...
  ```
- Use BuildKit's `--output type=image,rewrite-timestamp=true` (available in recent buildx) to rewrite layer mtimes.
- Avoid `RUN` steps that embed entropy (random ids, temp filenames with `$$`).

Reproducibility is a spectrum. Bit-for-bit is hard; byte-equivalent content where it matters is achievable and usually enough.

## Security hardening — runtime side (k8s Pod spec)

The image is one half of the story. When deploying, pair with:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65532          # matches distroless:nonroot
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
volumes:
  - name: tmp
    emptyDir: {}
volumeMounts:
  - name: tmp
    mountPath: /tmp
```

`readOnlyRootFilesystem: true` combined with `tmpfs` mounts for `/tmp` and any app write paths catches a surprising amount of runtime drift and limits exploit blast radius. If the app cannot run on a read-only rootfs, that is itself a finding worth tracking.

## Linting — `hadolint`

Adds static checks specifically for Dockerfiles that Trivy's config scan doesn't cover.

```bash
hadolint Dockerfile
hadolint --ignore DL3008 Dockerfile     # ignore "pin apt versions" when base is Wolfi/chainguard
hadolint --failure-threshold error Dockerfile
```

Run it alongside `trivy config` in CI:

```yaml
- uses: hadolint/hadolint-action@v3
  with:
    dockerfile: Dockerfile
    failure-threshold: error
```

## Build acceleration

### BuildKit — always on

```bash
DOCKER_BUILDKIT=1 docker buildx build ...
# or with buildx driver
docker buildx create --use --name ci --driver docker-container
docker buildx build --platform linux/amd64,linux/arm64 ...
```

BuildKit enables:
- `--mount=type=cache,...` — per-layer persistent caches for package managers.
- `--mount=type=secret,id=X` — secrets available only during `RUN`, never in layers.
- `--mount=type=bind,...` — bind host files without copying into a layer.
- Parallel independent stages.
- Inline cache export (`--cache-to type=inline`).

### Cache patterns

**Package-manager caches** (no secret contamination risk):
```dockerfile
# apt
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y ...

# pip / uv
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# npm / pnpm / yarn
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# cargo
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --release

# go
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -ldflags="-s -w" -o /out/app ./cmd/app
```

### Registry cache for CI

```bash
docker buildx build \
  --cache-from type=registry,ref=<registry>/<repo>:buildcache \
  --cache-to   type=registry,ref=<registry>/<repo>:buildcache,mode=max \
  --tag <registry>/<repo>:<tag> \
  --push .
```

`mode=max` caches every layer of every stage; `mode=min` (default) caches only final-stage layers. For CI, prefer `max` — the slight registry cost pays for itself on repeated builds.

GitHub Actions native cache alternative:
```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Multi-arch

```bash
docker buildx create --use --name multiarch --driver docker-container
docker buildx inspect --bootstrap
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag <registry>/<repo>:<tag> \
  --push .
```

Cross-compile inside the Dockerfile when possible (`TARGETOS`, `TARGETARCH`, `BUILDPLATFORM`) — faster than QEMU emulation:
```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.22 AS builder
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/app ./cmd/app
```

### Other wins

- Put `.dockerignore` in the repo; exclude `.git`, `node_modules`, `dist`, `target`, `*.log`, `.env`. Shrinks build context dramatically.
- Use `COPY --link` when available (BuildKit): copies are addressable and cache-stable.
- Use heredocs for multi-line RUN (avoids `\\` soup):
  ```dockerfile
  RUN <<EOF
  set -euo pipefail
  apt-get update
  apt-get install -y --no-install-recommends ca-certificates
  rm -rf /var/lib/apt/lists/*
  EOF
  ```

## Image optimization

### Size levers (by impact)

1. **Pick a smaller base.** Distroless → Wolfi → slim → full. 800 MB → 80 MB is typical.
2. **Multi-stage.** Drop build tools, test deps, source maps.
3. **Install nothing you do not use.** `--no-install-recommends`, `--no-dev`, `--production`, `--omit=dev`.
4. **Clean in the same layer as install.** `rm -rf /var/lib/apt/lists/*` must be in the same `RUN` as `apt-get install`, else the data is already in a layer.
5. **Strip binaries** when language supports it. Go: `-ldflags="-s -w"`. Rust: `strip = true` in Cargo.toml.
6. **Consolidate `RUN`s only when they share state**, not for aesthetic reasons. Unrelated `RUN`s should stay split for cache granularity.
7. **No `ADD http://...`.** Use `RUN curl` + checksum verify, or `ADD --checksum=...` (BuildKit).

### Inspecting

- `docker image ls` — final size.
- `dive <image>` — layer-by-layer breakdown, highlights waste.
- `docker history <image> --no-trunc` — quick layer audit.
- `docker buildx build --progress=plain` — full build output, useful to see which steps take what.

## Supply chain security

### Scan — Trivy / Grype

**Trivy** (full-featured):
```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed <image>
trivy image --format sarif --output trivy.sarif <image>
trivy config .                        # scans Dockerfile for misconfig
trivy fs . --scanners vuln,secret,misconfig
```

Useful flags:
- `--ignore-unfixed` — only fail on CVEs with a fix available (actionable).
- `--exit-code 1` — fail the CI job.
- `--severity HIGH,CRITICAL` — start here; add MEDIUM once pipeline is clean.
- `--ignorefile .trivyignore` — suppress known-accepted CVEs (with justification in comments).

**Grype** (Anchore):
```bash
grype <image> --fail-on high --output sarif --file grype.sarif
```

Both scanners disagree sometimes; running both in CI catches more. Pick one as the blocker.

### SBOM — Syft / Trivy

```bash
# Syft
syft <image> -o spdx-json > sbom.spdx.json
syft <image> -o cyclonedx-json > sbom.cdx.json

# Trivy (equivalent)
trivy image --format cyclonedx --output sbom.cdx.json <image>
```

Store the SBOM alongside the image: either as a build artifact or as an OCI referrer (via `cosign attest` below).

### Signing — Cosign

Keyless signing (OIDC, best for CI):
```bash
# During CI, with Fulcio/Rekor
cosign sign <registry>/<repo>@sha256:<digest>
```

Attach the SBOM as an attestation:
```bash
cosign attest --predicate sbom.cdx.json \
  --type cyclonedx \
  <registry>/<repo>@sha256:<digest>
```

Verify (in deploy pipeline / admission controller):
```bash
cosign verify <registry>/<repo>@sha256:<digest> \
  --certificate-identity "https://github.com/<org>/<repo>/.github/workflows/<wf>.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"

cosign verify-attestation <registry>/<repo>@sha256:<digest> \
  --type cyclonedx \
  --certificate-identity ... --certificate-oidc-issuer ...
```

Always sign by **digest**, never by tag. Tags are mutable.

### Provenance (SLSA)

BuildKit emits SLSA provenance automatically when you enable it:
```bash
docker buildx build \
  --provenance=mode=max \
  --sbom=true \
  --tag <registry>/<repo>:<tag> \
  --push .
```

`mode=max` includes source, environment, materials. `--sbom=true` attaches an SBOM attestation. These become OCI referrers of the image manifest.

### In-place patching — Copacetic (`copa`)

When a new CVE drops and the fix is a package upgrade, avoid a full rebuild / redeploy by patching the existing image:

```bash
# 1. Generate a vulnerability report
trivy image --vuln-type os --ignore-unfixed \
  --format json --output report.json \
  <registry>/<repo>:<tag>

# 2. Patch
copa patch -r report.json -i <registry>/<repo>:<tag> -t <tag>-patched

# 3. Scan the patched image
trivy image <registry>/<repo>:<tag>-patched

# 4. Re-sign
cosign sign <registry>/<repo>@sha256:<patched-digest>
```

`copa` only patches OS-level packages (apt/apk/dnf). App-level deps (npm/pip/go modules) still need a rebuild.

### Admission controllers (deploy-side)

Common setups:
- **Kyverno** / **OPA Gatekeeper** — verify `cosign` signature before scheduling the pod.
- **Sigstore Policy Controller** — policies that check signatures + attestations.
- **ECR Enhanced Scanning** / registry-native policy — block pulls of unscanned / critical-CVE images.

Skill stays at the build side; deploy-side enforcement is a separate concern.

## Secrets during build

Never:
```dockerfile
ARG NPM_TOKEN
RUN npm install
```
(Token lands in the build history.)

Do:
```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```
And invoke:
```bash
docker buildx build --secret id=npmrc,src="$HOME/.npmrc" ...
```
The secret is visible during the `RUN` and is never written to a layer.

For SSH-backed deps:
```dockerfile
RUN --mount=type=ssh git clone git@github.com:org/private.git
```
```bash
docker buildx build --ssh default ...
```

See the `pass-cli-secrets` skill for handling the host-side secret before it reaches buildx.

## CI reference (GitHub Actions example)

```yaml
jobs:
  image:
    permissions:
      contents: read
      id-token: write       # required for cosign keyless
      packages: write       # ghcr.io push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,format=long
            type=ref,event=branch

      - id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          provenance: mode=max
          sbom: true
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
          severity: HIGH,CRITICAL
          ignore-unfixed: true
          exit-code: 1

      - uses: sigstore/cosign-installer@v3
      - run: |
          cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
```

Adapt to GitLab CI, CircleCI, Buildkite as needed — the structure (build → scan → sign → publish) is the same.

## Anti-patterns cheat sheet

- `FROM ubuntu` or `FROM image:latest` in production.
- `RUN apt-get install ...` without `--no-install-recommends`.
- `apt-get update` in a separate `RUN` from `apt-get install` (cache lies to you on later runs).
- `ADD` when `COPY` would do. `ADD` has implicit behaviors (url fetch, tar extract) that are easy to abuse.
- `ENV PATH=/something:$PATH` layered multiple times (each adds a layer and a merge cost).
- Running as root "for convenience" — then `USER` is forgotten.
- `docker build .` with a 500 MB context because `.git` and `node_modules` are not in `.dockerignore`.
- Copying the entire repo with `COPY . .` before installing deps — cache-killer.
- Hardcoded `chmod 777`.
- `EXPOSE 80` + binding inside the container to a port < 1024 (requires capabilities).
- Baking env-specific config (`ENV STAGE=prod`) into the image; pass at runtime.
- Using `latest` for the scanner image (`trivy:latest`) and skipping db updates — pin the scanner too.
- Omitting `HEALTHCHECK` in images destined for Compose / Swarm / Podman (K8s uses its own probes, but for everything else the directive is what orchestrators read).
- Dropping OCI labels and then wondering which commit a registry image came from — `org.opencontainers.image.revision` is free provenance.
- Shell-form `ENTRYPOINT` (`ENTRYPOINT python app.py`) — the app runs under `/bin/sh -c`, signals don't reach it, and you get stuck containers on shutdown.
- Running as non-root in the image but deploying with `runAsUser: 0` in the Pod — the image discipline is wasted.

## Pre-flight checklist

Before pushing / publishing an image:

- [ ] Base image pinned by digest.
- [ ] Multi-stage build; final stage has no compilers / build tools / test deps.
- [ ] Final `USER` is non-root (numeric uid or `nonroot`).
- [ ] `COPY --chown=<user>:<group>` used when files need to be owned by the runtime user.
- [ ] OCI labels present: at minimum `title`, `description`, `source`, `revision`, `version`, `created`, `licenses`.
- [ ] `HEALTHCHECK` declared (even if the orchestrator overrides it).
- [ ] `STOPSIGNAL` correct for the app when not `SIGTERM`.
- [ ] `ENTRYPOINT` in exec form; init (`tini` / `dumb-init`) present if the app needs PID-1 help.
- [ ] No secrets visible in `docker history <image>` output.
- [ ] `.dockerignore` excludes `.git`, vendor dirs, build artifacts, `.env*`.
- [ ] BuildKit cache mounts used for package manager installs.
- [ ] Build is reproducible (`docker buildx build` runs cleanly in a fresh clone).
- [ ] `hadolint` passes at `error` threshold.
- [ ] Trivy (or Grype) scan passes the chosen threshold (HIGH/CRITICAL, fixed only).
- [ ] `trivy config .` run against the Dockerfile for misconfigs.
- [ ] SBOM attached as OCI attestation (or exported artifact).
- [ ] Signature attached via cosign (keyless if in CI).
- [ ] Provenance (`--provenance=mode=max`) attached when using buildx.
- [ ] Image referenced by digest in downstream manifests, not by tag.
- [ ] Deploy manifests set `runAsNonRoot`, `readOnlyRootFilesystem`, `capabilities.drop: [ALL]`.
- [ ] For patching: `copa patch` considered before a full rebuild.
