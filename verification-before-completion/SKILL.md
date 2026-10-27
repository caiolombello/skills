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

Choose the evidence that demonstrates this change's behavior; the list below is not a mandate to run every layer or rank a cosmetic screenshot below unrelated lint:

1. **Behavioral test** covering the requested behavior or bug.
2. **Integration/e2e test** proving components work together.
3. **Build/typecheck/lint** proving code shape is valid.
4. **Manual runtime check** with observed output.
5. **Static inspection** only for docs or mechanical changes.

For behavior changes, compilation alone is not enough.

Match evidence to consequences, uncertainty, and reversibility, not just diff size. Focused checks may suffice for a routine change; a one-line authorization change may need additional cases and independent review. A purely visual adjustment can be demonstrated with suitable before/after captures rather than a new test that repeats styling or markup.

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

Identify the relevant head/base SHA or working-tree snapshot and environment. For uncommitted work, record enough of the diff/file hashes or artifacts to distinguish the checked bytes. Do not assign a test result to a later materially changed version without rerunning affected checks.

Keep local checks, remote CI, automated review, required human approval, deployed version, and observed production behavior separate. Use explicit outcomes such as PASS, FAIL, NOT RUN, UNAVAILABLE, or NOT CONFIGURED. An absent check is not a passing check, and local tests do not prove deployment or production stability.

```markdown
Verified:
- `pnpm test -- auth.test.ts`: pass
- `pnpm typecheck`: pass

Not verified:
- `pnpm test`: not run; full suite takes ~45m and user asked for targeted check only
```

If a command fails, completion is blocked unless the failure is clearly unrelated and disclosed with evidence.

After a relevant change, invalidate and rerun affected evidence and reassess approvals according to the actual project/host policy. Do not assume any approval count, CI job, or branch protection exists. Agent review never substitutes for a required human approval. Stop at the requested endpoint: validated, committed, published, merged, or deployed are distinct states.

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

Diagnose whether the failure is in the change, an existing repository problem, or the environment/infrastructure. Run a bounded, supported substitute when it adds evidence, but do not call it equivalent to an unavailable required gate. Do not fix unrelated infrastructure or silently weaken acceptance criteria. Continue independent authorized work while a separate check is blocked, when safe.

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
