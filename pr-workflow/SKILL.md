---
name: pr-workflow
description: "Use when opening or preparing a PR/MR: clear problem-first title/body, appropriate verification, and draft/ready state. Monitoring through later reviews belongs to pr-followup."
---
# pr-workflow

Opening a PR/MR is the handoff between the author and every reviewer, CI job, and future reader of the git log. This skill encodes what goes into a good handoff and what to verify before submitting.

Terminology: "PR" is used throughout for brevity; rules apply identically to GitLab merge requests, Bitbucket pull requests, and Azure DevOps pull requests unless explicitly noted.

## Non-negotiables

1. **Never open a PR against `main` / `master`** directly when the project uses a different default base (e.g., `develop`, `release/*`). Check the repo default before setting `--base`.
2. **Never push work-in-progress to a branch shared with another human** and open a non-draft PR on it.
3. **Never skip the body.** Every PR ships with a body explaining what and why.
4. **Never add new files that were not part of the stated change** — no stray edits, no accidental reformatting, no generated files committed because the tool ran.
5. **Respect actual readiness/review policy.** Do not describe pending, missing, or failed checks as green. If CI is not configured, say so instead of creating an impossible green-CI gate; never bypass a required check.
6. **Never force-push to a branch with open review comments** unless the user approves — it loses review anchors on many hosts.

## When to use draft vs ready

Open as **draft** when any of the following is true:

- Tests are not yet written or not yet passing.
- The design is explicitly up for discussion.
- Known implementation work remains; an unrelated existing TODO is not itself a reason to force draft.
- The PR depends on another unmerged PR.
- You want CI feedback before involving humans.

Open as **ready** only when:

- Relevant local checks meet the project's requirements, with any unrun scope disclosed.
- Required host policies permit the state; distinguish pending CI from checks passed on the current head.
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

Follow required project prefixes, including issue IDs when mandated. Otherwise link issues in the body footer.

## Body structure

Default body:

```markdown
## Summary

<The concrete problem/trigger, followed by the behavior after this change.>

## Changes

<Optional implementation details that help assess the result; omit a redundant inventory.>

## Testing

- <what was added/updated in tests>
- <manual verification steps, if any>
- <commands, actual outcomes, reviewed head/snapshot, and verification limits>

## Notes

<When relevant: impact/risk, concrete rollback or limits of reversibility, tradeoffs, dependencies>

<!-- Footer -->
Closes #<issue>
Relates to #<issue>
```

Adapt to the project's template if one exists (`.github/PULL_REQUEST_TEMPLATE.md`, `.gitlab/merge_request_templates/`). Do not fight the template.

Rules:
- Lead with the user's problem and resulting behavior, not an inventory of symbols or files. Scale detail to complexity; a small PR can need only a few sentences and validation.
- Use bullets when they improve scanning; omit empty template sections.
- The "why" is more valuable than the "what". The diff shows the what.
- For a visible change, include suitable captures when useful and authorized; do not upload or publish private artifacts merely to satisfy a template.
- If the PR changes a public API, include a before/after snippet.
- For meaningful operational/data risk, describe how to reverse or mitigate the change, with actual limitations. Do not invent a tested rollback or demand a production rollout plan for a wording fix.

## Problem-first examples

These are illustrative briefs, not verified claims about a repository:

- Weak: `fix(ui): synchronize pending form state`. Better when supported: `fix(ui): preserve unsaved settings when closing the dialog`.
- Weak body: "Extracted state helpers, updated handlers, and added flags." Better for that brief: "Closing the settings dialog discarded unsaved input. The dialog now retains it until the user saves or explicitly discards it."

Only use measurements such as "70% faster" if the actual change has evidence for that number. Read project history for naming conventions rather than copying an unrelated example.

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
git diff origin/<base>...HEAD --stat     # actual base, size + shape of the change
```

### 2. Up to date with base

```bash
git fetch origin
# Inspect divergence first. Rebase/merge only when needed and authorized.
git log --oneline HEAD..origin/<base>
```

Follow the repository's branch/update policy. After an authorized rebase/merge or relevant correction, rerun affected verification and reassess approval/check validity for the resulting head. Do not rewrite a shared branch by routine.

### 3. Local verification

Select the project's real commands (from package manifest / Makefile / CI) that exercise this change:

- Build
- Tests
- Lint / format check
- Type check

Do not present an unverified behavioral fix as ready or expect CI to excuse a known change-caused failure. Use [`verification-before-completion`](../verification-before-completion/SKILL.md) to distinguish local results, remote checks, approvals, and production. Run broader suites when required or justified, rather than for every small edit.

### 4. Push the branch

```bash
git push -u origin HEAD
```

First push needs `-u` to set upstream. Subsequent pushes are plain `git push`.

## Creating the PR

Check whether a PR for this branch already exists before creating another. Respect the user's requested endpoint and existing publication authority. When the runtime exposes `link_pull_request`, register each PR created, taken over, or pushed to using its full URL, immediately as required by that runtime, including every stack layer. Git/host operations do not register it with the app. Report linking failures honestly.

### GitHub (`gh`)

```bash
gh pr create \
  --base <default-branch> \
  --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<type>(<scope>): <summary>" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --draft    # remove when ready
```

Prepare the exact body in a temporary Markdown file and pass `--body-file`; preserve actual newlines and do not interpolate untrusted content into shell arguments.

**Do not** use `--fill` when the commit message is weak; it will produce a weak PR body. Write the body explicitly.

With multiple remotes, use an explicit repository argument/API target rather than changing persistent Git/CLI configuration unless requested.

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

- **Request reviewers** according to actual policy, risk, readiness, and authorization. Do not assume a CI service or human approval count exists, or send review requests merely because this skill was loaded.
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

Check whether configured CI started and show the PR URL and current head/status. If no CI exists or checks are inaccessible, report that explicitly. This initial check does not start indefinite follow-up.

```bash
gh pr checks                      # short status
gh pr view --web                  # open in browser

glab mr view
glab mr status
```

### Responding to review

- Use [`receiving-code-review`](../receiving-code-review/SKILL.md) to verify findings before any authorized correction/reply. Preserve the original objective and review anchors.
- When monitoring/follow-up is requested, continue with [`pr-followup`](../pr-followup/SKILL.md). Opening a PR alone does not authorize ongoing monitoring, new scope, external comments, closure, or merge.

### Merging

Only merge when:

- Merge is authorized and the actual required checks are passing for the current relevant head/merge result.
- Real human approvals satisfy the project's rule; an AI recommendation or bot approval cannot fill a required human slot.
- Base compatibility/merge-queue requirements and material review findings are satisfied according to the actual host policy.
- After new relevant commits, affected evidence/approvals were revalidated; an old green result is not automatically current.

Strategy per project convention:

- **Squash merge**: when individual commits are messy or the project prefers one commit per PR.
- **Rebase and merge**: when commits are clean and linear history matters.
- **Merge commit**: when the project wants explicit branch topology.

```bash
gh pr merge <n> --squash         # only with merge authorization
glab mr merge <n> --squash       # delete source branches only when separately authorized
```

**Never** pass `--admin` / force-merge without explicit user approval — it bypasses required checks.

## Pre-flight checklist

Before `gh pr create` / `glab mr create`:

- [ ] Working tree is clean (`git status`).
- [ ] Branch is based on current `origin/<base>`.
- [ ] Relevant local checks and actual host requirements are satisfied or honestly reported as pending/unavailable; no absent gate is called passed.
- [ ] Diff contains only the files the change requires (no stray edits).
- [ ] Title follows Conventional Commits, under 70 chars.
- [ ] Body leads with the problem and result, records meaningful verification, and follows any required project template.
- [ ] Draft vs ready is the correct state for where the work is.
- [ ] Base branch is the project's real default (not always `main`).
- [ ] Labels / reviewers match the project's convention.
- [ ] Issue linkage uses the right keyword (`Closes` / `Fixes`) or none at all.
- [ ] For GitHub: active `gh` account matches the repo's org (see `gh-cli-workflows`).
