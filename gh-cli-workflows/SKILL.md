---
name: gh-cli-workflows
description: Canonical workflows for the GitHub CLI (`gh`) when multiple accounts are configured on the same machine. Use WHENEVER (1) the user asks to create/list/merge PRs, issues, releases, or gists via `gh`; (2) a command must run against a specific GitHub account and the repo has SSH remote aliases (e.g. `git@github-<alias>:...`); (3) the active `gh` account might not match the git remote host alias; (4) the user mentions multiple GitHub accounts, SSH aliases, `gh auth switch`, or unexpected `403`/`permission denied` on push.
---

# gh CLI workflows

Encodes the patterns that keep `gh` commands pointed at the right GitHub account when the machine has multiple accounts and the repositories use SSH host aliases.

## The core problem

One machine, many GitHub identities. Two orthogonal things can be misaligned at any moment:

1. **Git remote URL.** The repo's `origin` may use `git@github-<alias>:org/repo.git`, where `<alias>` is defined in `~/.ssh/config`. Different aliases route to different SSH keys (different GitHub users).
2. **Active `gh` account.** `gh` stores one token per logged-in account but only one is "active" at a time. `gh` uses the active account's token for API calls, regardless of the SSH alias in the git remote.

When the two are mismatched:

- `gh pr create` succeeds with the wrong author context, or fails with `GraphQL: Resource not accessible by integration`.
- `git push` via SSH works (because keys are picked by alias), but `gh` commands that need API access (review requests, PR body edits, labels) silently target the wrong account.
- `git push` over HTTPS returns `403` because `git` reaches for the active `gh` account credentials while the user intended another.

## Golden rule

**Before any `gh` command on a repo, verify the active account matches the repo's intended owner.** One line, always:

```bash
gh auth status --active
```

If it does not match the org/owner in the remote, switch **before** running the command:

```bash
gh auth switch -u <username>
```

## Multi-account layout (typical)

The user usually has `~/.ssh/config` shaped like:

```
Host github-<orgA>
  HostName github.com
  User git
  IdentityFile ~/.ssh/<orgA>
  IdentitiesOnly yes

Host github-<orgB>
  HostName github.com
  User git
  IdentityFile ~/.ssh/<orgB>
  IdentitiesOnly yes

Host github.com                    # fallback for git@github.com:...
  HostName github.com
  User git
  IdentityFile ~/.ssh/<default>
  IdentitiesOnly yes
```

And three `gh` accounts logged in (`gh auth status`):

```
github.com
  ✓ account <personal>            (active)
  ✓ account <work-org-A>
  ✓ account <work-org-B>
```

## Mapping remote → required account

Given a remote URL, derive the required `gh` account:

| Remote form | How to pick the account |
|---|---|
| `git@github-<alias>:<owner>/<repo>.git` | account that owns (or has access to) `<owner>`. Typically the SSH alias name hints at which one. |
| `git@github.com:<owner>/<repo>.git` | fallback SSH host, still owner-driven. |
| `https://github.com/<owner>/<repo>.git` | same owner rule. Push goes through `gh` credential helper, so active account must match. |

If ambiguous, prefer reading `CODEOWNERS`, existing PRs, or asking the user once — do **not** guess.

## Standard flow

### 1. Inspect repo context
```bash
git -C <repo> remote -v
gh auth status --active
```
Compare: is the active account the right one for that remote's owner?

### 2. Switch if needed
```bash
gh auth switch -u <username>
gh auth status --active
```
Confirm the switch before proceeding.

### 3. Run the `gh` command
```bash
gh pr create --fill --draft
gh pr list --author @me
gh issue create --title "..." --body-file ISSUE.md
```

### 4. (Optional) Revert to default active account
Only if you started this session with a different account and want to leave things as you found them:
```bash
gh auth switch -u <original-user>
```

## Common operations

### Create a PR, correctly

```bash
# 1. Verify remote + active account match
git remote -v
gh auth status --active

# 2. Ensure branch is pushed
git push -u origin HEAD

# 3. Create with structured body
gh pr create \
  --base main \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<type>(<scope>): <short description>" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

Rules:
- PR title under 70 characters. Use the body for details.
- Never `--fill` when the commit message is weak; write the body explicitly.
- Use `--draft` when the work is not ready for review.
- Never pass `--admin` on merge without explicit user approval.

### Create an issue

```bash
gh issue create \
  --title "<clear imperative title>" \
  --body-file ISSUE.md \
  --label "bug,needs-triage" \
  --assignee "@me"
```

Branch off an issue:
```bash
gh issue develop <issue-number> --checkout
```

### Release

```bash
gh release create v1.2.0 \
  --title "v1.2.0" \
  --notes-file CHANGELOG.md \
  --target main
```
Never `--latest` on pre-releases. Never delete a release without confirmation.

### Manage repository secrets

Populated from a local secret store (see the `pass-cli-secrets` skill) rather than echoed in the shell:

```bash
gh secret set MY_TOKEN --body "$(pass-cli item view --item-title 'X' --field password)"
```

For environment-scoped secrets:
```bash
gh secret set MY_TOKEN --env production --body "$(...)"
```

### Cross-account cloning

When cloning a repo that belongs to a non-active account, use the SSH alias explicitly so the right key is used:

```bash
git clone git@github-<alias>:<owner>/<repo>.git
cd <repo>
gh auth switch -u <username>
```

## Destructive commands that need explicit confirmation

- `gh pr merge --admin`
- `gh pr merge --delete-branch` on shared branches
- `gh release delete`
- `gh repo delete`
- `gh secret delete` on production environments
- `gh run cancel` / `gh run rerun --failed` on mainline runs

Always state what the action will do and wait for user approval.

## Pitfalls

- **`gh pr create` in a fresh branch** fails silently if the branch is not pushed yet. Run `git push -u origin HEAD` first.
- **`gh repo set-default`** persists in git config. If the repo has multiple remotes (fork + upstream), set it once per clone.
- **`gh auth login --web`** only logs in the **current active scope**. Adding a new account requires `gh auth login` and then `gh auth switch`.
- **`gh` inherits `GH_TOKEN` / `GITHUB_TOKEN`** from env. If set, they override the stored account. Unset them for interactive work:
  ```bash
  unset GH_TOKEN GITHUB_TOKEN
  ```
- **`git push` over HTTPS** uses `gh`'s credential helper. Wrong active account = `403`. Fix by `gh auth switch -u <user>` or by switching the remote to the matching SSH alias.
- **`gh pr checkout`** may fail if the PR branch lives on a fork the active account cannot reach. Switch to an account that can, or clone the fork explicitly.

## Quick diagnostics

```bash
# Who am I right now, and where would a push go?
gh auth status --active
git remote -v
ssh -T git@github-<alias>     # confirms which GitHub user the alias resolves to

# Find all logged accounts
gh auth status

# Switch active account
gh auth switch -u <username>

# Reset credential helper (after changing active account on HTTPS remotes)
gh auth setup-git
```

## Pre-flight checklist

Before executing any `gh` command that writes (create/merge/delete/edit):

- [ ] `git remote -v` confirms the intended owner.
- [ ] `gh auth status --active` matches that owner (or a user with access).
- [ ] `GH_TOKEN` / `GITHUB_TOKEN` env vars are not overriding the stored account.
- [ ] The branch is pushed (for PR creation).
- [ ] Destructive flags (`--admin`, `--delete-branch`, `--force`) are intentional and confirmed.
