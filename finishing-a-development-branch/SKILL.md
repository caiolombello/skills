---
name: finishing-a-development-branch
description: Use when implementation is complete and a branch or worktree needs final verification before PR, merge, handoff, or cleanup. Present integration choices; never offer discard unless the user asks.
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

Do not push, merge, delete, or clean up just because the branch is finished.
Do not offer discard as a routine completion choice. Discuss discard only when
the user explicitly asks to throw the work away.

## Explicit discard requests

Resolve and show every target before deleting anything:

```bash
git status
git log --oneline <base>..<branch>
git worktree list
```

Then ask for confirmation that names the branch, commits, and worktree path.
Only after confirmation may `git worktree remove` and branch deletion be
considered. Dirty worktrees, unpushed commits, and force deletion require a
separate warning; follow `git-hygiene`.

## Worktree cleanup

If using a worktree, remove it only after the user chooses the outcome.

Capture workspace provenance while still inside the worktree:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

Safe path after merge or a confirmed discard decision, run from outside the
worktree:

```bash
git worktree list
git worktree remove "$WORKTREE_PATH"
git worktree prune
```

If the worktree is dirty, stop. Do not use `--force` without explicit confirmation.
If the workspace was created and managed by the host rather than by this
workflow, leave cleanup to the host.

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
| Offering discard as a normal finish option | Normalizes irreversible cleanup |
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
