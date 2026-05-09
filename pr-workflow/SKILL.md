---
name: pr-workflow
description: How to open a Pull Request / Merge Request that reviewers can actually review. Use WHENEVER the agent is about to run `gh pr create`, `glab mr create`, equivalent API call, or any command that opens a PR/MR. Covers title and body structure, draft vs ready, reviewer selection, required checks, commit scope, and the pre-flight that avoids "author forgot tests" style comments. Host-agnostic: works for GitHub, GitLab, Bitbucket and self-hosted variants.
---

# pr-workflow

Opening a PR/MR is the handoff between the author and every reviewer, CI job, and future reader of the git log. This skill encodes what goes into a good handoff and what to verify before submitting.

Terminology: "PR" is used throughout for brevity; rules apply identically to GitLab merge requests, Bitbucket pull requests, and Azure DevOps pull requests unless explicitly noted.

## Non-negotiables

1. **Never open a PR against `main` / `master`** directly when the project uses a different default base (e.g., `develop`, `release/*`). Check the repo default before setting `--base`.
2. **Never push work-in-progress to a branch shared with another human** and open a non-draft PR on it.
3. **Never skip the body.** Every PR ships with a body explaining what and why.
4. **Never add new files that were not part of the stated change** — no stray edits, no accidental reformatting, no generated files committed because the tool ran.
5. **Never request review** until CI is green, unless the PR is explicitly draft.
6. **Never force-push to a branch with open review comments** unless the user approves — it loses review anchors on many hosts.

## When to use draft vs ready

Open as **draft** when any of the following is true:

- Tests are not yet written or not yet passing.
- The design is explicitly up for discussion.
- Known TODOs remain inside the diff.
- The PR depends on another unmerged PR.
- You want CI feedback before involving humans.

Open as **ready** only when:

- Build + test + lint are green locally.
- CI is expected to pass (or has already passed on the pushed branch).
- The body answers "what", "why", and "how was this tested".

## Title

Format: `<type>(<scope>): <short imperative summary>`

- Types (Conventional Commits): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Scope is optional; use it when the repo uses a consistent scoping convention.
- Keep the first line under 70 characters. Use the body for details.
- Imperative mood: "Add retry logic to client", not "Added" / "Adds".
- No emoji by default.

Examples:
- `feat(auth): support refresh tokens with rotation`
- `fix(billing): round totals to 2 decimals before storing`
- `refactor(api): extract request validation into middleware`

Do not encode issue IDs in the title — put them in the body footer.

## Body structure

Default body:

```markdown
## Summary

<1–3 sentences: what this PR does and why.>

## Changes

- <key change 1>
- <key change 2>
- <key change 3>

## Testing

- <what was added/updated in tests>
- <manual verification steps, if any>
- <commands run locally>

## Notes

<optional: tradeoffs, follow-ups, blocked by, related PRs>

<!-- Footer -->
Closes #<issue>
Relates to #<issue>
```

Adapt to the project's template if one exists (`.github/PULL_REQUEST_TEMPLATE.md`, `.gitlab/merge_request_templates/`). Do not fight the template.

Rules:
- Prefer bullets over prose for changes.
- The "why" is more valuable than the "what". The diff shows the what.
- If the PR is a UX change, include screenshots or a short Loom/GIF.
- If the PR changes a public API, include a before/after snippet.
- If the PR touches infra or data, include rollback notes.

## Commit scope inside the PR

A PR should be one logical change. Signs the PR is too big:

- Touches more than one module unnecessarily.
- Mixes refactor + behavior change (split into two PRs).
- Mixes lint/format churn with real edits (do the churn in a separate commit or PR).
- Reviewers will need more than ~30 minutes to understand it.

If the change is too big, split it. Smaller PRs merge faster and regress less.

## Branch naming

- Lowercase, hyphens.
- Prefix by type when the project uses prefixes: `feat/`, `fix/`, `chore/`, `refactor/`.
- Include a short topic: `feat/add-retry-client`, `fix/500-on-empty-body`.
- Never push to a branch name another human is using.

## Pre-flight before opening the PR

### 1. Working tree + branch state

```bash
git status                # clean working tree
git log --oneline -n 5    # commits look right
git diff main...HEAD --stat     # size + shape of the change
```

### 2. Up to date with base

```bash
git fetch origin
git rebase origin/<base>    # or: git merge --ff-only origin/<base>
```

Resolve conflicts, run tests again.

### 3. Local verification

Run the project's real commands (from package manifest / Makefile / CI):

- Build
- Tests
- Lint / format check
- Type check

Never open a PR with local failures you planned to "fix in CI".

### 4. Push the branch

```bash
git push -u origin HEAD
```

First push needs `-u` to set upstream. Subsequent pushes are plain `git push`.

## Creating the PR

### GitHub (`gh`)

```bash
gh pr create \
  --base <default-branch> \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<type>(<scope>): <summary>" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --draft    # remove when ready
```

Or with an inline body:

```bash
gh pr create --base main --title "..." --body "$(cat <<'EOF'
## Summary
...
EOF
)"
```

**Do not** use `--fill` when the commit message is weak; it will produce a weak PR body. Write the body explicitly.

If the repo has multiple remotes (fork + upstream), set the default once:

```bash
gh repo set-default <owner>/<repo>
```

Multiple GitHub accounts? See the `gh-cli-workflows` skill — the active account must match the remote's owner or the API call fails.

### GitLab (`glab`)

```bash
glab mr create \
  --target-branch <default-branch> \
  --source-branch "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<type>(<scope>): <summary>" \
  --description-file .gitlab/merge_request_templates/Default.md \
  --draft \
  --squash-before-merge \
  --remove-source-branch
```

GitLab-specific niceties worth setting intentionally:
- `--squash-before-merge` when the project prefers linear history.
- `--remove-source-branch` when branches are not meant to stick around.
- `--assignee @me` if the reviewer != assignee convention applies.

### Bitbucket / Azure DevOps

No universally-used CLI; prefer API via host-specific tool (`az repos pr create`, Bitbucket API via `curl` or `bb`). Same structure for title and body.

## Reviewers, labels, milestones

- **Request reviewers only after CI is green.** Don't burn reviewer attention on a failing build.
- **Reviewer selection**: owners file (`CODEOWNERS`), recent authors of the touched files (`git log -n 10 -- <path>`), or team convention. Do not spam the whole team.
- **Labels**: use what the repo already uses. Do not invent new labels.
- **Milestones / iterations**: only set when the project actively uses them.

Apply labels in the create command:

```bash
gh pr create ... --label "area/auth,needs-review"
glab mr create ... --label "area::auth,review::ready"
```

## Linking issues

Use the host's autolink keywords in the body footer to auto-close issues on merge:

- GitHub: `Closes #<n>`, `Fixes #<n>`, `Resolves #<n>`.
- GitLab: `Closes #<n>`, `Closes group/project#<n>` for cross-project.

Never claim `Closes` unless the PR actually ships the fix.

## After opening

### Checks

Verify CI kicked off and show the user the PR URL.

```bash
gh pr checks                      # short status
gh pr view --web                  # open in browser

glab mr view
glab mr status
```

### Responding to review

- For small asks, push follow-up commits to the same branch. Do not rebase away review anchors while comments are active.
- For large asks, consider a new PR.
- When discussion resolves, mark the conversation resolved on the host; do not just reply "done".

### Merging

Only merge when:

- CI is green.
- At least one approval (or the project's rule).
- Branch is up to date with base (the host will often enforce this).

Strategy per project convention:

- **Squash merge**: when individual commits are messy or the project prefers one commit per PR.
- **Rebase and merge**: when commits are clean and linear history matters.
- **Merge commit**: when the project wants explicit branch topology.

```bash
gh pr merge <n> --squash --delete-branch         # or --rebase / --merge
glab mr merge <n> --squash --remove-source-branch
```

**Never** pass `--admin` / force-merge without explicit user approval — it bypasses required checks.

## Pre-flight checklist

Before `gh pr create` / `glab mr create`:

- [ ] Working tree is clean (`git status`).
- [ ] Branch is based on current `origin/<base>`.
- [ ] Local build / test / lint / typecheck all pass.
- [ ] Diff contains only the files the change requires (no stray edits).
- [ ] Title follows Conventional Commits, under 70 chars.
- [ ] Body has Summary / Changes / Testing (or matches the project template).
- [ ] Draft vs ready is the correct state for where the work is.
- [ ] Base branch is the project's real default (not always `main`).
- [ ] Labels / reviewers match the project's convention.
- [ ] Issue linkage uses the right keyword (`Closes` / `Fixes`) or none at all.
- [ ] For GitHub: active `gh` account matches the repo's org (see `gh-cli-workflows`).
