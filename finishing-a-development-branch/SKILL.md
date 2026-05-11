---
name: finishing-a-development-branch
description: Finish a development branch safely before merge, PR, handoff, or discard. Use WHENEVER (1) implementation tasks are complete; (2) the user asks to wrap up, finish the branch, prepare PR/MR, merge, or clean up; (3) a worktree branch needs final verification; (4) deciding whether to merge, open a PR, keep the branch, or discard it; (5) before declaring a multi-commit coding task done. Runs final checks, summarizes evidence, and presents safe next actions.
---

<!-- Inspired by obra/superpowers finishing-a-development-branch (MIT). See ../CREDITS.md -->

# Finishing a Development Branch

The end of a branch is where agents often overclaim. This skill forces a final, evidence-based checkpoint before merge, PR, handoff, or cleanup.

Pair with `verification-before-completion`, `git-hygiene`, `pr-workflow`, and `using-git-worktrees`.

## When to use

- All planned implementation tasks are complete.
- The user asks to wrap up or prepare a PR/MR.
- You are about to say "done" for a non-trivial branch.
- A worktree should be merged, kept, or removed.
- A branch needs final status for handoff.

## Final verification sequence

1. Inspect working tree:

   ```bash
   git status
   git diff --stat
   git diff
   ```

2. Run agreed verification:

   - Targeted tests for changed behavior.
   - Full test suite or CI-equivalent command when feasible.
   - Build/typecheck/lint as required by the repo.

3. Check for risky files:

   - `.env`, credentials, tokens, private keys.
   - generated artifacts not meant for commit.
   - local config or editor files.

4. Review scope:

   - Every changed file maps to the plan or user request.
   - No drive-by refactors.
   - No unresolved TODO/FIXME introduced by this branch unless intentionally tracked.

## Completion summary

Report with evidence:

```markdown
Branch finish check

Completed:
- <task/result>

Changed files:
- <path>: <why>

Verified:
- `<command>`: pass
- `<command>`: pass

Not verified:
- <command/check>: <why not>

Risks / follow-ups:
- <item or "None known">
```

If a check fails, do not present merge/PR as ready. Either fix, diagnose, or ask for direction.

## Present next actions

Offer explicit safe options:

1. Open PR/MR — use `pr-workflow`.
2. Commit remaining changes — only if the user asked for commits.
3. Keep branch/worktree for later.
4. Merge locally — only if requested and safe.
5. Discard/remove worktree — destructive; requires explicit confirmation.

Do not push, merge, delete, or clean up just because the branch is finished.

## Worktree cleanup

If using a worktree, remove it only after the user chooses the outcome.

Safe path after merge/PR/discard decision:

```bash
git worktree list
git worktree remove <path>
git worktree prune
```

If the worktree is dirty, stop. Do not use `--force` without explicit confirmation.

## PR/MR readiness checklist

Before opening a PR/MR:

- [ ] Branch is up to date enough for review or conflicts are disclosed.
- [ ] Tests/build/lint status is known.
- [ ] PR title uses the repo's convention.
- [ ] Body explains why, verification, and risks.
- [ ] Screenshots/logs are included if useful.
- [ ] Secrets and generated artifacts are not included.

Use `pr-workflow` for the actual PR/MR body.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| "Done" without final test evidence | False confidence |
| Auto-pushing after coding | Surprises user and can leak mistakes |
| Cleaning worktree before user decision | Data loss |
| Hiding skipped checks | Reviewers discover gaps later |
| Merging with known failing tests | Moves risk to mainline |

## Verification checklist

- [ ] Working tree and diff were inspected.
- [ ] Required verification commands were run or explicitly marked not run.
- [ ] Risky files were checked.
- [ ] Scope matches the plan/request.
- [ ] Next actions are presented, not assumed.
- [ ] No destructive cleanup without explicit confirmation.
