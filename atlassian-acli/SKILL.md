---
name: atlassian-acli
description: Use when working Jira or Confluence via acli (issue keys, JQL, transitions, comments, pages). acli does NOT render Markdown; convert rich descriptions/comments to ADF with scripts/md2adf.py before sending.
---
# atlassian-acli — Jira and Confluence Cloud via `acli`

Prefer `acli` for Jira and for Confluence operations it currently supports. Do not assume it is installed or authenticated; check only when needed. For an unsupported Confluence operation, use the documented fallback below only when the user has authorized that operation and the environment's authentication and security rules permit it; otherwise use the UI or explain that the operation is unavailable. Do not treat this fallback as permission to bypass the `acli` preference for operations the CLI supports.

## Auth model

- Jira authentication is product-scoped. Use `acli jira auth login` to authenticate, `acli jira auth status` to show the active Jira account, and `acli jira auth switch` to move between Jira accounts.
- The session is global to the machine, not per-repo. Switching accounts affects future Jira invocations outside the current shell too.
- If a Jira command returns `unauthorized`, pause and tell the user to run `acli jira auth login`; do not try to work around it.
- Some versions expose top-level `acli auth ...` compatibility commands for global OAuth. Do not substitute them for the canonical `acli jira auth ...` workflow.

## Top-level shape

```
acli
├── jira
│   ├── auth       login/logout/status/switch
│   ├── workitem   view/search/create/edit/transition/comment/link/assign/...
│   ├── project    list/view/create/update/archive
│   ├── sprint     create/update/view/list-workitems
│   ├── board      (board management)
│   ├── dashboard
│   ├── field
│   └── filter
├── confluence
│   ├── auth       login/logout/status/switch
│   ├── page       view
│   ├── blog
│   └── space
└── rovodev        (skip; interactive AI agent)
```

Prefer `acli jira workitem ...` over any other path for issue work.

## Critical rule — acli does not render Markdown

Atlassian Cloud stores rich text in **Atlassian Document Format (ADF)**, a JSON tree. `acli` (verified on 1.3.39) accepts only two things in `-d/--description`, `--description-file`, `-b/--body` and `--body-file`:

- **ADF JSON** → stored as-is, renders as rich text.
- **Anything else** → wrapped as literal plain text. Markdown is **not** converted: `## Objetivo`, `**bold**`, `` `code` `` and `- item` show up in Jira exactly like that.

So any description or comment with headings, bold, lists, links, code or tables **must be converted to ADF first**. Use the bundled converter instead of hand-writing ADF JSON:

```bash
# Write the body as normal Markdown, then convert (stdlib only, Python 3.9+)
python3 <skill-dir>/scripts/md2adf.py card.md -o /tmp/card.adf.json

# Create / edit with the ADF file
acli jira workitem create --project ABC --type Task --summary "..." --description-file /tmp/card.adf.json
acli jira workitem edit --key ABC-123 --description-file /tmp/card.adf.json --yes

# Comments
acli jira workitem comment create --key ABC-123 --body-file /tmp/comment.adf.json
acli jira workitem comment update --key ABC-123 --id 10001 --body-adf /tmp/comment.adf.json   # update: --body-file is plain text only
```

`<skill-dir>` is the directory containing this `SKILL.md`. The converter supports headings, paragraphs, hard breaks, bullet/ordered/nested lists, task items (rendered as ☐/☑), fenced code blocks (with language), blockquotes, `---` rules, GFM pipe tables, inline code, bold, italic, strikethrough, links and bare URLs. It does not support images, HTML, footnotes or Jira mentions — keep those out or add them in the UI.

Rules:

- Plain `--description "..."` / `--body "..."` is only for **single-line, unformatted** text. Note that `"\n"` inside double quotes is a literal backslash-n in the shell, not a newline.
- Never paste Markdown into `-d`/`-b` expecting it to render, and never use Jira wiki markup (`h2.`, `*bold*`, `{code}`) — this API path does not render it either.
- Do not hand-write large ADF trees; generate them with `md2adf.py` and only tweak the JSON if strictly needed.
- `--from-json` requires `description` to be an ADF **object**, not a string. Embed the converted doc: `jq --slurpfile d /tmp/card.adf.json '.description = $d[0]' issue.json > issue.final.json`.
- After every write, re-read the item (`acli jira workitem view ABC-123 --fields description --json`) and confirm `description` contains `heading`/`bulletList`/etc. nodes, not a single paragraph with literal `##` or `**`.

## Work item operations (canonical patterns)

### View one or more items

```bash
# Concise default view
acli jira workitem view ABC-123

# Specific fields only (saves tokens when piping to an agent)
acli jira workitem view ABC-123 --fields key,summary,status,assignee,description

# All navigable fields minus comments
acli jira workitem view ABC-123 --fields '*navigable,-comment'

# Full payload for scripting
acli jira workitem view ABC-123 --json
```

### Search with JQL

```bash
# Human-readable
acli jira workitem search --jql 'project = ABC AND statusCategory != Done' --limit 20

# Pipe to jq for processing
acli jira workitem search --jql 'assignee = currentUser() AND sprint in openSprints()' --json \
  | jq '.[] | {key, summary, status: .status.name}'

# Count only (cheap when you just need a number)
acli jira workitem search --jql 'project = ABC AND created >= -7d' --count

# Via saved filter ID (avoid re-typing complex JQL)
acli jira workitem search --filter 10001 --json
```

JQL crib notes:
- `assignee = currentUser()`  — who the session belongs to
- `assignee = "user@example.com"` — explicit
- `sprint in openSprints()` / `sprint in closedSprints()`
- `statusCategory in ("In Progress", "To Do", "Done")` — more portable than `status = "In Progress"` (status names differ per project)
- `"Epic Link" = ABC-123` — stories in an epic (note the quoted field name)
- `text ~ "keyword"` — full-text search
- `updated >= -1d` / `created >= "2025-01-01"` — time filters
- Order: `... ORDER BY updated DESC`

### Create a work item

Quick form (body already converted with `md2adf.py`):
```bash
acli jira workitem create \
  --project ABC \
  --type Task \
  --summary "Add retries to downstream client" \
  --description-file /tmp/card.adf.json \
  --assignee @me \
  --label observability,reliability
```

Richer / multi-field form via JSON:
```bash
# 1. Generate the schema scaffold
acli jira workitem create --generate-json > /tmp/issue.json

# 2. Fill /tmp/issue.json with real data; description must be an ADF object:
python3 <skill-dir>/scripts/md2adf.py card.md -o /tmp/card.adf.json
jq --slurpfile d /tmp/card.adf.json '.description = $d[0]' /tmp/issue.json > /tmp/issue.final.json

# 3. Submit
acli jira workitem create --from-json /tmp/issue.final.json
```

`--from-file` reads summary + description as **plain text** (no Markdown rendering). Prefer `--summary` + `--description-file <adf.json>` for formatted bodies.

Parent linking (sub-task, story under epic):
```bash
acli jira workitem create --project ABC --type Sub-task \
  --parent ABC-100 \
  --summary "Implement retry logic" \
  --description-file /tmp/subtask.adf.json
```

### Edit

```bash
acli jira workitem edit --key ABC-123 --summary "New summary"

acli jira workitem edit --key ABC-123 --assignee user@example.com
acli jira workitem edit --key ABC-123 --assignee @me
acli jira workitem edit --key ABC-123 --remove-assignee

# Replace labels wholesale
acli jira workitem edit --key ABC-123 --labels "backend,reliability"

# Add (preserve existing) by editing labels is not supported directly — fetch current then set:
current=$(acli jira workitem view ABC-123 --json | jq -r '.fields.labels | join(",")')
acli jira workitem edit --key ABC-123 --labels "${current},newlabel"

# Update description: convert Markdown to ADF first
python3 <skill-dir>/scripts/md2adf.py new-desc.md -o /tmp/new-desc.adf.json
acli jira workitem edit --key ABC-123 --description-file /tmp/new-desc.adf.json
```

Bulk edit via JQL (use with care, always include `--yes` only when intentional):
```bash
acli jira workitem edit --jql 'project = ABC AND labels = "retro-2025-q1"' \
  --labels "retro-2025-q1,archived"
```

### Transition

Status names are **project-specific**. Use `view` on an existing item to confirm exact casing.

```bash
acli jira workitem transition --key ABC-123 --status "In Progress"
acli jira workitem transition --key ABC-123,ABC-124 --status "Done" --yes
```

If `--status "X"` errors with "transition not available", the workflow does not allow that jump from the current status. Either transition through an intermediate status or ask the user which path to take.

### Comment

```bash
# Single-line, unformatted
acli jira workitem comment create --key ABC-123 --body "Shipped in release 2.4.0"

# Formatted comment: Markdown -> ADF -> --body-file
python3 <skill-dir>/scripts/md2adf.py comment.md -o /tmp/comment.adf.json
acli jira workitem comment create --key ABC-123 --body-file /tmp/comment.adf.json

# Edit your last comment (same ADF file)
acli jira workitem comment create --key ABC-123 --body-file /tmp/comment.adf.json --edit-last

# Update a specific comment: ADF goes through --body-adf
acli jira workitem comment update --key ABC-123 --id 10001 --body-adf /tmp/comment.adf.json

acli jira workitem comment list --key ABC-123
```

### Links between issues

```bash
acli jira workitem link type                          # list link types
acli jira workitem link create --inward ABC-123 --outward DEF-456 --type "blocks"
acli jira workitem link list --key ABC-123
```

### Attachments, watchers, assignment

```bash
acli jira workitem attachment add --key ABC-123 --file ./diagram.png
acli jira workitem watcher add --key ABC-123 --user user@example.com
acli jira workitem assign --key ABC-123 --assignee @me
```

## Project

```bash
# List all projects visible to the user
acli jira project list --paginate

# List recently viewed projects (up to 20)
acli jira project list --recent

# List projects with JSON output
acli jira project list --limit 50 --json
```

## Board

Board commands manage Jira boards (Scrum / Kanban). Most board subcommands require a board ID (`--id`), so the first step is usually `search` to discover it.

### Discover boards

```bash
# List all boards (human-readable table)
acli jira board search

# JSON output for piping to jq (preferred in agent context)
acli jira board search --json

# Search boards by name (partial match, case-insensitive)
acli jira board search --name "Platform" --json

# Filter by project key
acli jira board search --project-key ABC --json

# Filter by board type
acli jira board search --type scrum --json
acli jira board search --type kanban --json
```

**Extracting the board ID from JSON:**
```bash
board_id=$(acli jira board search --name "Squad Platform" --json | jq -r '.values[0].id')
```

### Get board details

```bash
acli jira board get --id 123
acli jira board get --id 123 --json
```

Key fields in the JSON response:
- `id` — numeric board ID
- `name` — display name
- `type` — `"scrum"` or `"kanban"`
- `location` — project or filter context
- `self` — REST API URL

### List projects linked to a board

```bash
acli jira board list-projects --id 123 --json
```

**Pitfall:** This does **not** list all Jira projects globally. It returns only the project(s) associated with the given board ID. For a global project list, use `acli jira project list`.

### List sprints linked to a board

Only meaningful for **Scrum** boards. Kanban boards may return empty results.

```bash
# List sprints for a board
acli jira board list-sprints --id 123 --json

# Limit results
acli jira board list-sprints --id 123 --limit 10 --json

# Paginate through all sprints
acli jira board list-sprints --id 123 --paginate --json
```

### Board → Sprint → Workitem workflow

A common agent pattern is to traverse from a board to its active sprints and then to the workitems:

```bash
# 1. Find the board ID
board_id=$(acli jira board search --name "Squad Platform" --json | jq -r '.values[0].id')

# 2. List active / future sprints for that board
acli jira board list-sprints --id "$board_id" --json | jq -r '.values[] | select(.state != "closed") | {id, name, state}'

# 3. List workitems in a specific sprint (use the sprint ID from step 2)
acli jira workitem search --jql "sprint = 456" --json

# Alternative: list workitems directly for the board using JQL
acli jira workitem search --jql "project = ABC AND sprint in openSprints()" --json
```

### Board pitfalls

1. **Board IDs are numeric, not human-readable.** You almost always need `search` first.
2. **`list-sprints` only works for Scrum boards.** Kanban boards do not have sprints; the command may return an empty list or error.
3. **Board names are not unique.** Two projects can each have a board named "Backlog". Always verify the `projectKey` or `location` in the search result before picking an ID.
4. **`list-projects` scope is the board, not global.** If a board spans multiple projects (e.g., via a filter), all linked projects are returned; if the board is single-project, only that one is returned.
5. **Sprint state values:** `"future"`, `"active"`, `"closed"`. Use `select(.state == "active")` in jq to find the currently running sprint.
6. **Large boards with many sprints:** always use `--json` and pipe to `jq`. Human-readable tables truncate or wrap badly with long board names.

## Confluence

Use `acli` for supported Confluence page and blog operations. If the installed CLI does not support a requested create/update operation, an authenticated Atlassian REST API call is an approved fallback only when the user authorized the mutation and applicable credential, network, and tool policies allow it. Otherwise, use the UI or report the capability gap. Never infer authorization to mutate Confluence from mere tool availability.

```bash
acli confluence page view <page-id>
acli confluence space list
```

## Output formatting guidance

- Default human-readable tables are noisy in agent context. Prefer `--json` when piping to `jq`, or `--fields key,summary,status,assignee` when you want just a few columns.
- For agents, `--json | jq` is almost always the right move.
- `--csv` is good for spreadsheet export but bad for agents (no structure).

## Safety and destructive actions

Require explicit user confirmation **before** running any of these:

- `acli jira workitem delete`
- `acli jira workitem archive` (reversible via `unarchive`, but still disruptive)
- `acli jira workitem edit --jql ...` (bulk edit)
- `acli jira workitem transition --jql ...` (bulk transition)
- `acli jira workitem comment delete`
- `acli jira sprint delete`
- `acli jira project delete` / `archive`

For bulk operations, always run the same JQL through `search --count` first and show the number of items that will be affected.

## Pitfalls and agent-specific notes

1. **Status names vary per project.** "In Progress" in one project may be "Doing" in another. Always `view` an existing item in the same project to learn the vocabulary.
2. **Assignee is by email or account ID, not display name.** `--assignee "John Doe"` fails; `--assignee "john.doe@example.com"` works.
3. **`@me` resolves to the active Jira account**, not to the requestor if multiple accounts are logged in. Check `acli jira auth status`.
4. **Labels cannot contain spaces.** Hyphens or camelCase.
5. **`--json` is the stable contract.** Human-readable output can change between `acli` versions; JSON shape is stable.
6. **OAuth tokens can expire mid-session.** If a command that worked 10 minutes ago suddenly returns `unauthorized`, tell the user to run `acli jira auth login` rather than retrying.
7. **Account switching has side effects.** `acli jira auth switch` changes the active Jira account for future `acli` invocations on the machine, not just the current shell. If you switched accounts, switch back when done.
8. **Epic vs issue parent.** "Epic Link" is a custom field on older Jira projects; next-gen projects use the native `parent` field. If `--parent` fails, try setting the Epic Link via `edit --from-json` with the proper custom field.
9. **ADF on round-trip.** `view --fields description` returns rendered text. To change a description, rewrite it as Markdown, convert with `md2adf.py` and send the ADF file; never pipe the rendered text back into `--description`.
10. **Markdown is never rendered by acli.** If a card shows literal `##`, `**` or `- `, it was sent as plain text. Fix it by converting with `md2adf.py` and re-running `edit --description-file`.

## Pre-flight checklist

Before any write operation (create / edit / transition / comment / delete):

- [ ] `acli jira auth status` shows the correct active Jira account.
- [ ] The target key exists (`acli jira workitem view <key>` returns OK).
- [ ] For bulk ops, JQL was validated with `search --count` first.
- [ ] Formatted description / comment was converted with `md2adf.py` and is passed as an ADF file (`--description-file`, `--body-file`, or `--body-adf` for comment update).
- [ ] Destructive flags (`--yes`, `--ignore-errors`) are intentional.
- [ ] Status names match the project's workflow exactly (for `transition`).
- [ ] After the write, the item was re-read and the description renders as ADF nodes, not literal Markdown.
