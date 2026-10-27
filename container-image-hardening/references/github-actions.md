# GitHub Actions image publishing and signing

This reference covers the workflow boundaries for building, scanning, publishing, and signing container images. It intentionally contains no copyable action references: a workflow with publish or OIDC signing authority must use reviewed full commit SHAs verified against each action's official repository and release. Never substitute a guessed SHA or a mutable tag/branch. For syntax and the repository-wide pinning standard, see [`github-actions-workflows`](../../github-actions-workflows).

## Job boundaries

1. Build the image and record its immutable digest. Use a trusted runner and explicit image platforms, metadata, SBOM, provenance, and registry cache policy appropriate to the project.
2. Scan the digest produced by the build, with a documented fail-gate policy. Pin the scanner action and scanner image/database behavior according to the project's update process.
3. Publish only from trusted refs. Scope `packages: write` to the publishing job; pull request validation should not receive registry write access.
4. Sign the published digest with keyless OIDC only from a trusted workflow identity. Scope `id-token: write` to the signing job, constrain the Sigstore identity policy to the repository/workflow/ref, and verify the signature and provenance at admission or deployment.

The build, scan, publish, and sign steps may share a job when the trust boundary is appropriate, but permission grants apply to the entire job. Split jobs when doing so reduces authority, and pass the immutable image digest through a required workflow output/artifact. Do not treat a mutable tag as the identity of the artifact.

Before enabling the workflow, verify each action's SHA and release from its official source, review permission scope and fork behavior, and confirm the exact artifact digest is scanned and signed. Keep SHA updates in the normal dependency review process.
