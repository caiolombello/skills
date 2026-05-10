---
name: glab-cli-workflows
description: Canonical workflows for the GitLab CLI (`glab`) when multiple GitLab accounts or instances are configured on the same machine. Use WHENEVER (1) the user asks to create / list / merge MRs, issues, releases, snippets via `glab`; (2) a command must run against a specific GitLab instance or account and the repo has SSH remote aliases or multiple remotes; (3) the active `glab` account might not match the git remote host alias; (4) the user mentions multiple GitLab accounts, self-hosted GitLab plus gitlab.com, SSH aliases, `glab auth status`, unexpected `403` / `permission denied` on push or MR create.
---

# GitLab CLI (`glab`) Workflows

GitLab's `glab` CLI is the official equivalent of GitHub's `gh`. It supports creating MRs, listing issues, watching pipelines, managing releases — all from the terminal. Like `gh`, it has **one active auth context per host** at a time, which becomes a problem when a machine talks to multiple GitLab accounts or a mix of `gitlab.com` + self-hosted GitLab.

This skill is the GitLab companion of [`gh-cli-workflows`](../gh-cli-workflows). Most rules transfer; the vocabulary and commands differ.

## Golden rules

1. **Verify the auth host matches the remote host.** The classic failure: `glab mr create` against a self-hosted GitLab while authenticated only to `gitlab.com`, or vice versa.
2. **Use `--repo OWNER/REPO` (or `--host HOST`) for any command that could target the wrong project.** Do not trust the working-directory remote alone when you have multiple accounts.
3. **Authenticate once per host.** `glab auth login --hostname gitlab.example.com` gives you a distinct token per host.
4. **Short-lived tokens.** Prefer Personal Access Tokens with minimal scopes; rotate. Do not commit `GITLAB_TOKEN` to dotfiles.
5. **Use `glab auth status` at the start of any risky action.** Catches wrong-account drift before it causes a 403.

## Initial setup

### Install

```bash
# macOS
brew install glab
# Linux (various)
curl -sL https://gitlab.com/gitlab-org/cli/-/releases | ...
# Or from https://gitlab.com/gitlab-org/cli/-/releases
```

### Authenticate (one host at a time)

```bash
# Default: gitlab.com
glab auth login --hostname gitlab.com

# Self-hosted instance
glab auth login --hostname gitlab.internal.example.com

# Multiple accounts on the SAME host (e.g., two gitlab.com identities):
# glab does not support this as cleanly as gh does.
# Workaround: separate config files per account (see "Multi-account on same host" below).
```

List configured hosts:

```bash
glab auth status
# Hostname: gitlab.com
#   ✓ Logged in as caio (oauth_token)
#   ✓ Token: *******************
# Hostname: gitlab.internal.example.com
#   ✓ Logged in as c.lombello (personal_access_token)
```

## Pre-flight — always check first

Before any command that creates, updates, or destroys, run this sequence:

```bash
# 1. Where am I?
glab auth status

# 2. Where is the git remote pointing?
git remote -v
# origin  git@gitlab.com:caio/my-project.git (fetch)
# origin  git@gitlab.com:caio/my-project.git (push)

# 3. What's the current branch?
git branch --show-current
```

If `auth status` host and `remote -v` host disagree → stop. Fix auth before running `glab mr create`.

## Multi-remote / multi-host pattern

A repo with both a public mirror on gitlab.com and an internal GitLab:

```
$ git remote -v
origin    git@gitlab.com:public-org/my-project.git (fetch/push)
internal  git@gitlab.internal:private-group/my-project.git (fetch/push)
```

Every `glab` command becomes ambiguous. Be explicit:

```bash
# Against the internal remote's project:
glab mr create --source-branch feature/xyz \
  --target-branch main \
  --repo private-group/my-project \
  --host gitlab.internal.example.com

# Against origin (gitlab.com) — default host:
glab mr create --source-branch feature/xyz \
  --target-branch main \
  --repo public-org/my-project
```

### SSH config pattern

Mirror what works on GitHub: distinct SSH Host aliases for each account / instance.

```sshconfig
# ~/.ssh/config
Host gitlab.com
  HostName gitlab.com
  User git
  IdentityFile ~/.ssh/id_gitlab_public

Host gitlab-internal
  HostName gitlab.internal.example.com
  User git
  IdentityFile ~/.ssh/id_gitlab_internal
```

Then in a repo:

```bash
git remote set-url origin git@gitlab-internal:private-group/my-project.git
```

Now `git push` / `git fetch` always hit the correct identity. **However**, `glab` reads `--host` based on the **hostname in the URL**, not your SSH alias. So:

- If the remote URL is `git@gitlab-internal:...`, `glab` tries to talk to `gitlab-internal.example.com` (no such thing) → error.
- **Fix**: either pass `--host gitlab.internal.example.com` explicitly to every `glab` command, or keep the real hostname in the URL and rely on SSH key selection via `IdentityFile` + `IdentitiesOnly yes`.

Pragmatic advice: **use real hostnames in `git remote`**, use SSH key selection per-host. This makes `glab` work without `--host` in most cases.

## Multi-account on the same host

`glab` does not natively support multiple accounts on the **same** host. Two viable workarounds:

### Option A: environment variable override

```bash
# Default config
export GITLAB_TOKEN=""
# Repo-scoped shell: use a different token
GITLAB_TOKEN=glpat-xxxxxx glab mr list --repo other-org/other-repo
```

Combined with [`direnv`](https://direnv.net/) or a repo-local `.envrc`, this cleanly scopes per directory:

```bash
# .envrc
export GITLAB_TOKEN=glpat-xxxxxx
```

(Then `direnv allow` once, and the token is active only inside the repo.)

Never commit `.envrc` with secrets. See [`pass-cli-secrets`](../pass-cli-secrets) for secret sourcing.

### Option B: separate `GLAB_CONFIG_DIR`

```bash
alias glab-work='GLAB_CONFIG_DIR=$HOME/.config/glab-work glab'
alias glab-personal='GLAB_CONFIG_DIR=$HOME/.config/glab-personal glab'

glab-work auth login --hostname gitlab.com
glab-personal auth login --hostname gitlab.com
```

Two aliases; two distinct configs; never confused.

## Common commands

### MRs

```bash
# Create
glab mr create \
  --source-branch "$(git branch --show-current)" \
  --target-branch main \
  --title "feat(auth): add SSO support" \
  --description "$(cat /tmp/mr-body.md)" \
  --assignee @me \
  --label backend,security \
  --remove-source-branch \
  --squash

# List
glab mr list --assignee=@me --state=opened

# Status of the current branch's MR
glab mr status

# Check out an MR locally
glab mr checkout 1234

# Approve + merge (when rules allow)
glab mr approve 1234
glab mr merge 1234 --squash --remove-source-branch
```

Prefer `--draft` for work-in-progress MRs; flip to ready later with `glab mr update 1234 --ready`.

### Issues

```bash
glab issue create --title "Rate limit on /login" --label bug --assignee @me
glab issue list --state opened --label security
glab issue view 42 --web      # open in browser
```

### Pipelines

```bash
glab ci list                   # recent pipelines on the current branch
glab ci view                   # interactive UI for the latest pipeline
glab ci trace                  # stream logs of the current pipeline
glab ci run --branch main      # trigger a new run

# Retry a failed job without restarting the whole pipeline
glab ci retry <job-id>
```

### Releases

```bash
glab release create v2.1.0 \
  --name "v2.1.0" \
  --notes-file CHANGELOG-v2.1.0.md \
  --milestone "Q2-2025"
```

### Snippets

Rarely used; useful when you need to share a log excerpt without email:

```bash
glab snippet create --title "Failing trace 2024-11-12" \
  --visibility internal \
  --file trace.log
```

## Scripting with `glab`

```bash
# List the MRs assigned to me as JSON, pipe through jq
glab mr list --assignee=@me --output json \
  | jq '.[] | {id, title, web_url}'

# Check if a PR has been approved:
glab mr view 1234 --output json | jq '.user_notes_count, .upvotes'
```

Every `glab` subcommand supports `--output json` or similar. Prefer JSON output for any script — the default table output is not stable across `glab` versions.

## Error modes

| Error | Cause | Fix |
|-------|-------|-----|
| `authentication required` | No auth for this host, or token expired | `glab auth login --hostname <host>` |
| `403 Forbidden` on push or MR create | Token lacks `write_repository` or is from wrong account | Check `glab auth status`; re-login with correct scopes |
| `project not found` | Wrong `--repo`, or wrong `--host` | `glab auth status`; pass `--host` explicitly |
| `invalid token scope` | Token scope too narrow | Rotate token with `api`, `write_repository`, `read_user` as needed |
| Silent success on wrong project | Default host picked up the wrong repo | Always pass `--repo` and `--host` on machines with multi-host setup |
| `glab ci trace` hangs | Pipeline is waiting on approval or runner | `glab ci view` to inspect; may need `glab ci play` on manual jobs |

## Security hygiene

- **Scope tokens minimally.** `read_api` + `write_repository` covers most CLI workflows; do not hand out `api` (full) unless truly needed.
- **Short expiration.** Tokens that never expire are a time bomb.
- **Never log or print the token.** `glab` obscures it by default; never `echo $GITLAB_TOKEN`.
- **Revoke + rotate** on any machine loss or suspected leak.
- **Do not commit `.envrc`** or anything containing `glpat-*`.

See [`pass-cli-secrets`](../pass-cli-secrets) for the full secret-hygiene story.

## CI uses its own auth

GitLab CI pipelines authenticate to their own project automatically via `CI_JOB_TOKEN`. `glab` in CI should use the job token, not a personal token:

```yaml
# .gitlab-ci.yml
job:
  script:
    - export GITLAB_TOKEN=$CI_JOB_TOKEN
    - glab mr list --project $CI_PROJECT_ID
```

See [`gitlab-ci-workflows`](../gitlab-ci-workflows) for the pipeline-side discipline. Never use a developer's PAT in CI — rotate pain and audit trail loss.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|--------------|
| `glab` commands without checking `auth status` first | Drift: command succeeds against the wrong host / account |
| SSH alias in `git remote` URL (`git@gitlab-internal:...`) without `--host` | `glab` parses a hostname that does not resolve |
| Long-lived PAT without expiration | Leak detection is slower than rotation |
| Full `api` scope tokens | Unnecessary blast radius on leak |
| Wildcard `--host` flags across a script | Confusing; makes the script's target implicit |
| Using a developer PAT in CI jobs | Lost audit trail; rotation pain; violates separation of concerns |
| Chaining `glab` commands without `set -e` in scripts | Silent partial execution |
| `glab` + `gh` installed for the same repo mirror | Wrong tool picked up the wrong remote |

## Interaction with other skills

- [`gh-cli-workflows`](../gh-cli-workflows) — GitHub companion. Same pattern, different platform.
- [`gitlab-ci-workflows`](../gitlab-ci-workflows) — CI side. `glab` is the client CLI, `.gitlab-ci.yml` is the server side.
- [`git-hygiene`](../git-hygiene) — `git remote`, branches, pushes. `glab` extends this.
- [`pr-workflow`](../pr-workflow) — MR body structure, merge strategy, pre-flight. Host-agnostic; this skill is the tooling layer.
- [`pass-cli-secrets`](../pass-cli-secrets) — where `GITLAB_TOKEN` comes from and how to not leak it.

## Verification checklist

Before running `glab` that writes (create, approve, merge, close, delete):

- [ ] `glab auth status` shows the expected host and user.
- [ ] `git remote -v` shows a URL whose hostname matches that host.
- [ ] If the machine has multiple accounts / hosts, the command includes explicit `--host` and `--repo`.
- [ ] `GITLAB_TOKEN` (if set) corresponds to the intended identity.
- [ ] Token scope is minimum-needed; expiration is set.
- [ ] For CI, `CI_JOB_TOKEN` is used, not a developer PAT.
