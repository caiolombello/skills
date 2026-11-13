# Execution safety

Applies in both modes. Source reading is read-only. Anything the target controls — build scripts, tests, package hooks, fixtures, binaries, browsers, emulators, fuzzers — is untrusted code.

## Sandbox requirements

Run target-controlled code only when the host can **enforce at the OS level** every one of these. A promise in a prompt is not enforcement.

| Control | Requirement |
|---|---|
| Network | No external network. An isolated loopback namespace only when a local client/server fixture needs it. |
| Environment | Empty, then populated from an explicit allowlist of safe values. Scratch-local `HOME`, temp, and cache directories. No inherited variables, credentials, agent sockets, or tokens. |
| Filesystem | Target and toolchain read-only. The target-controlled process writes only inside its assigned `scratch/`. No host home, `/tmp`, other agents' directories, retained artifacts, or shared services exposed. |
| Resources | Explicit, low CPU, memory, process-count, file-size, disk, and wall-clock limits on every check, not only on checks expected to be expensive. |

When a build must write beside source, the agent (outside the sandbox) may first make a disposable copy of the source inside its `scratch/`.

If any control is missing, do not execute. Keep the source-grounded candidate as `needs_validation`, name the missing capability as the blocker ("no network isolation available", "cannot enforce read-only target mount"), and provide a validation plan an owner can run safely. A missing sandbox never erases a candidate and never justifies running "just this once".

## What local checks may do

Allowed inside the sandbox:

- offline builds with dependencies already present;
- existing unit and integration tests, or a minimal function harness;
- small malformed fixtures, sanitizers, bounded fuzz or regression cases;
- deterministic concurrency schedules;
- isolated-loopback services with dummy tenants and dummy secrets;
- local browser or emulator tests with dummy accounts;
- rendering manifests or templates and evaluating policy with dummy identities;
- mocked external and paid calls.

Never, sandbox or not:

- live, deployed, or shared traffic; requests to any service not started for this check;
- dependency installation or network fetches;
- real accounts, credentials, or production data;
- shared queues, cloud resources, CI runners, registries, signing or release services;
- publishing anything; stress, saturation, or cost generation;
- continuing past the minimum dummy-data boundary result.

## Recording a check

Record the command, the exact input or fixture, the sandbox limits, and only the allowlisted environment variable **names** plus safe non-secret values needed to reproduce. Launch from an empty environment instead of redacting one afterward. Never capture the ambient environment, authentication state, or unrelated host paths.

In guidance mode, do not retain target-produced files at all; summarize the observed result in the answer.

## Retaining scratch output as evidence (full audit)

Everything in `scratch/` is target-controlled once the sandbox has run. Only trusted coordinator-side code may copy a file from an agent's `scratch/` into that agent's retained `artifacts/`; neither the agent nor target code ever writes `artifacts/`. Promotion rules:

1. **Declare first.** Before execution, record an allowlist of expected scratch-relative file paths with per-file and cumulative byte limits. Open the scratch and artifacts roots as trusted directory handles and do not pass them to the agent or sandbox.
2. **Promote only after exit.** Start only after the sandbox and all its processes have terminated.
3. **Safe relative paths only.** Reject absolute paths, empty or `.`/`..` components, and any symlinked component.
4. **No link-following, anywhere.** Walk source and destination parents from the retained root handles with no-follow, directory-relative operations; never reopen by path. Create missing destination directories exclusively and re-verify them.
5. **Regular files only.** The source must be a regular file with link count exactly one. Reject symlinks, hard links, FIFOs, sockets, devices, directories, and archives meant for extraction.
6. **Bounded and stable.** Check size against the limits before and while reading; re-check identity, type, link count, and size after copying and reject any change.
7. **Exclusive destination.** Create the destination file exclusively without following links and verify it is a regular single-link file.
8. **One file at a time.** No recursive copy, globbing, or archive extraction into `artifacts/`.
9. **Fail closed.** If any rule cannot be enforced on this platform (use the equivalent race-safe APIs off POSIX) or any check fails, discard the scratch entry. If it was decisive evidence, keep the candidate `needs_validation` with the promotion failure as its blocker.

A ledger check with `method: "local"` must point to a file promoted this way under `agents/<check-owner>/artifacts/`. Scratch paths, output-root files, and another owner's artifacts are not evidence.

## Brief block for hunters and verifiers

Paste this block into every hunter and verifier brief so the rules travel with the work:

```text
Execution boundary: read source freely; never edit target source or shared run files.
Run target-controlled code only in the approved OS-enforced sandbox (no external
network, empty allowlisted env, read-only target and tools, writes only to your
scratch/, explicit CPU/memory/process/file-size/disk/time limits). If any control is
unavailable, do not execute: return needs_validation naming the missing control.
Dummy principals and secrets only. No deployed endpoints, shared services, installs,
publishing, or load. Stop at the minimum observed boundary result. Record command,
input, limits, and allowlisted env var names only. You never write artifacts/; the
coordinator promotes predeclared scratch files after the sandbox exits, regular
single-link bounded files only, no links, globs, or archives. A failed promotion of
decisive evidence means needs_validation with that blocker.
```
