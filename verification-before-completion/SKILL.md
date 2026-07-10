---
name: verification-before-completion
description: Use before claiming done, fixed, or passing, or before opening a PR. Require concrete verification evidence and list what was not checked.
---
<!-- Inspired by obra/superpowers verification-before-completion (MIT). See ../CREDITS.md -->

# Verification Before Completion

Completion is not a feeling. Completion is evidence that the requested behavior works, the relevant checks pass, and known gaps are disclosed.

Use this before saying "done" on any non-trivial task.

## When to use

- You are about to declare a task complete.
- A bug fix needs proof.
- A plan task or branch is finished.
- The user asks whether something is fixed.
- A previous check failed, timed out, or was skipped.

## The evidence ladder

Prefer the strongest evidence available:

1. **Behavioral test** covering the requested behavior or bug.
2. **Integration/e2e test** proving components work together.
3. **Build/typecheck/lint** proving code shape is valid.
4. **Manual runtime check** with observed output.
5. **Static inspection** only for docs or mechanical changes.

For behavior changes, compilation alone is not enough.

## Select checks deliberately

Use project-defined commands from `AGENTS.md`, manifests, Makefiles, CI, or the approved plan. Do not invent commands when the repo already defines them.

Match check to change:

| Change type | Minimum verification |
|---|---|
| Bug fix | Repro test fails before or is documented; test passes after |
| New behavior | Test for happy path and important edge/failure path |
| Refactor | Same tests pass before and after; no behavior change claimed |
| Build/config | Command that consumes the config succeeds |
| Docs-only | Link/path/format check when possible; otherwise read rendered diff |
| Infra/IaC | validate + plan/diff; no apply unless explicitly requested |

## Run and record

Record exact commands and outcomes:

```markdown
Verified:
- `pnpm test -- auth.test.ts`: pass
- `pnpm typecheck`: pass

Not verified:
- `pnpm test`: not run; full suite takes ~45m and user asked for targeted check only
```

If a command fails, completion is blocked unless the failure is clearly unrelated and disclosed with evidence.

## Handling flaky or unavailable checks

Do not pretend.

If a check is flaky:

- Rerun once if cheap.
- Capture both results.
- State that confidence is lower.

If a check cannot run:

- Explain why.
- Run the strongest available substitute.
- Tell the user what remains to be verified elsewhere.

## Manual verification

Manual checks should be observable, not vibes.

Good:

```markdown
Manual check: POST /api/tasks with missing title returns 422 and body contains `code: "validation_error"`.
```

Bad:

```markdown
Manual check: looks fine.
```

## Completion statement

Use this shape:

```markdown
Done, with verification:
- <evidence 1>
- <evidence 2>

Not verified:
- <gap or "None known">
```

Never say "all tests pass" unless you ran all tests.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| "Looks good" | No evidence |
| Running only lint for behavior change | Does not prove behavior |
| Ignoring failing checks | Ships unknown risk |
| Hiding skipped checks | Misleads user/reviewer |
| Using a different command than CI without saying so | False confidence |

## Verification checklist

- [ ] The verification command comes from repo rules, plan, manifest, or CI.
- [ ] Behavior changes have behavioral tests or a clear manual observation.
- [ ] Failed checks are resolved or explicitly disclosed.
- [ ] Skipped checks are listed with a reason.
- [ ] Completion language matches the evidence actually gathered.
