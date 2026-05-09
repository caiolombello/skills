---
name: rtk-token-optimized-cli
description: Use RTK to reduce token usage from noisy shell command outputs such as git diff/status/log, tests, lint, kubectl logs, docker logs, AWS CLI, rg/grep/find, and package manager commands. Use when working through terminal output where compact summaries are enough; avoid when exact full output is required.
---

# RTK Token-Optimized CLI

RTK is expected to be installed on `$PATH` (commonly at `~/.local/bin/rtk`). Install instructions: https://github.com/sigoden/rtk

## When to use

Use RTK for shell commands that commonly produce large or noisy output:

- `rtk git status`
- `rtk git diff`
- `rtk git log -n 20`
- `rtk rg <pattern> <path>`
- `rtk read <file>`
- `rtk pytest`
- `rtk cargo test`
- `rtk npm test`
- `rtk kubectl logs <pod>`
- `rtk docker logs <container>`
- `rtk aws ...`

## When not to use

Use raw commands when exact output matters:

- full source file contents
- complete JSON/YAML payloads
- credentials or security-sensitive command handling
- binary/base64/encoded data
- command output that will be copied verbatim into a file or API call

## Diagnostics

- `rtk --version`
- `rtk gain`
- `rtk discover`
- `rtk proxy <cmd>` for raw passthrough with tracking
