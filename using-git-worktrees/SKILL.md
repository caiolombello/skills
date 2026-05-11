---
name: using-git-worktrees
description: Use git worktrees to isolate parallel agent work safely. Use WHENEVER (1) starting a non-trivial implementation branch that should not dirty the current checkout; (2) running multiple agents or experiments in parallel; (3) the user asks for a worktree, parallel branch, sandbox, isolated checkout, or disposable branch; (4) switching tasks while current work is in progress; (5) a risky refactor/prototype should be isolated from the main working tree. Pairs with git-hygiene; requires git.
---

<!-- Inspired by obra/superpowers using-git-worktrees (MIT). See ../CREDITS.md -->

# Using Git Worktrees

Git worktrees let you check out multiple branches of the same repository at once. For agentic work, they are a safety tool: each branch gets an isolated directory, tests run without trampling another task, and experiments can be discarded cleanly.

Use this with `git-hygiene`. A worktree does not make unsafe git commands safe.

## When to use

- A task will take more than one small commit.
- Multiple agents or sessions will work in parallel.
- The current checkout has unrelated work in progress.
- You need to test a risky approach without dirtying the main checkout.
- You want a disposable implementation branch for a plan.

## When not to use

- One-line fixes.
- Repositories with tooling that cannot tolerate multiple checkouts unless you know how to configure it.
- When the current working tree has uncommitted changes you do not understand.

## Pre-flight

Before creating a worktree, verify state:

```bash
git status
git branch --show-current
git worktree list
git log -5 --oneline
```

If the current tree is dirty, stop and decide:

1. Commit the current work if the user asked for that.
2. Stash only with explicit approval.
3. Create the worktree from the intended base while leaving current work alone.

Never hide dirty state.

## Naming

Use predictable names:

```text
../<repo-name>-<short-task>
```

Branch names should follow the repo's convention. Default:

```text
feat/<short-task>
fix/<short-task>
chore/<short-task>
```

Examples:

```bash
git worktree add ../app-feat-login-rate-limit -b feat/login-rate-limit origin/main
git worktree add ../infra-fix-alb-timeout -b fix/alb-timeout origin/main
```

Use the actual base branch for the repo (`main`, `master`, `develop`, or release branch). Do not assume.

## Creation workflow

1. Fetch and inspect the base:

   ```bash
   git fetch origin
   git log --oneline -5 origin/main
   ```

2. Create the worktree:

   ```bash
   git worktree add ../<repo>-<task> -b <type>/<task> origin/main
   ```

3. Enter the new directory and verify:

   ```bash
   git status
   git branch --show-current
   ```

4. Run the project's setup or baseline test command if needed. Use commands from `AGENTS.md`, manifests, or CI — do not invent them.

## Dependency setup

Worktrees share git object storage, not build artifacts. Expect to install or link dependencies per worktree:

- JS/TS: package-manager install may be needed per checkout.
- Python: use a separate virtualenv per worktree.
- Go/Rust: caches are usually shared outside the repo.
- Terraform: never share `.terraform/` blindly across worktrees; run init per checkout when needed.

Do not copy secrets or `.env` files into a new worktree unless the user explicitly approves and the repo's secret policy allows it.

## Parallel-agent coordination

When assigning work to agents, give each agent:

- Worktree path.
- Branch name.
- Scope boundaries.
- Verification command.
- Expected output or commit policy.

Avoid two agents changing the same files unless the plan explicitly accounts for merge conflicts.

## Finishing and cleanup

When the branch is done, use `finishing-a-development-branch` for the final checks. Then remove the worktree only after the user chooses to merge, PR, keep, or discard.

Safe cleanup for a merged/discarded worktree:

```bash
git worktree remove ../<repo>-<task>
git worktree prune
```

If removal fails because the tree is dirty, stop. Do not force remove without explicit confirmation.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Creating worktrees from a guessed base | Replays work onto the wrong branch |
| Sharing one branch across multiple agents | Race conditions and overwritten work |
| Copying `.env` by habit | Secret sprawl |
| Leaving abandoned worktrees | Confuses future status and disk usage |
| Force-removing dirty worktrees | Data loss |

## Verification checklist

- [ ] Current repo state was inspected before creation.
- [ ] Base branch was explicit and fetched.
- [ ] Worktree path and branch name are task-specific.
- [ ] No secrets were copied by default.
- [ ] Each parallel agent has an isolated path and scope.
- [ ] Cleanup is deliberate and non-destructive.
