---
name: container-image-hardening
description: Canonical workflow for writing secure, fast, small container images. Use WHENEVER the agent is about to (1) write or edit a Dockerfile / Containerfile; (2) change CI that builds images; (3) discuss image size, build cache, multi-arch, SBOM, signing, provenance, or CVE patching; (4) run or suggest buildx/kaniko/nerdctl/podman build; (5) integrate trivy, grype, syft, cosign, copacetic, dive, or similar tooling. Covers Dockerfile structure, multi-stage, non-root, base image choice, cache mounts, multi-arch, SBOM, signing, CVE scan, and in-place patching.
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

# Copy only what the runtime needs
WORKDIR /app
COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src /app/src

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root (distroless:nonroot provides uid 65532)
USER nonroot

# Declare port for documentation; does not open it
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
- `ENV` set in the final stage only with runtime-needed vars; no secrets.
- `USER nonroot` (or explicit numeric uid) before `ENTRYPOINT`.
- `ENTRYPOINT` as JSON array (exec form), so signals propagate correctly.
- No `CMD` with shell form if `ENTRYPOINT` handles it.

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

## Pre-flight checklist

Before pushing / publishing an image:

- [ ] Base image pinned by digest.
- [ ] Multi-stage build; final stage has no compilers / build tools / test deps.
- [ ] Final `USER` is non-root (numeric uid or `nonroot`).
- [ ] No secrets visible in `docker history <image>` output.
- [ ] `.dockerignore` excludes `.git`, vendor dirs, build artifacts, `.env*`.
- [ ] BuildKit cache mounts used for package manager installs.
- [ ] Build is reproducible (`docker buildx build` runs cleanly in a fresh clone).
- [ ] Trivy (or Grype) scan passes the chosen threshold (HIGH/CRITICAL, fixed only).
- [ ] SBOM attached as OCI attestation (or exported artifact).
- [ ] Signature attached via cosign (keyless if in CI).
- [ ] Provenance (`--provenance=mode=max`) attached when using buildx.
- [ ] Image referenced by digest in downstream manifests, not by tag.
- [ ] For patching: `copa patch` considered before a full rebuild.
