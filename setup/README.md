# Provider setup

Reviewed against official documentation on 2026-10-02. Install only the skills
you need. This setup copies skills or exposes the optional frontend plugin;
it does not install providers, run hooks, configure models, change permissions,
or grant connector access. Python 3.9+ and Git are the only prerequisites for
the local copy workflow.

## Clone and install selectively

```sh
git clone https://github.com/caiolombello/skills.git
cd skills
python3 setup/install.py --provider codex --manifest install-manifests/frontend.txt
python3 setup/install.py --provider codex --manifest install-manifests/frontend.txt --apply
```

The first run is a dry-run. Repeat `--provider` for multiple local tools or
`--skill` for individual skills. Use `install-manifests/codex-keep.txt` for the
existing keep-set. Private manifests remain opt-in; no skill collection is
installed by default. Missing manifest entries fail before copying any skill.

| Provider / local surface | `--provider` | Native destination | Official reference |
|---|---|---|---|
| Codex CLI/IDE/desktop local | `codex` | `~/.agents/skills` | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code local | `claude` | `~/.claude/skills` | [Skills](https://code.claude.com/docs/en/skills) |
| OpenCode | `opencode` | `~/.config/opencode/skills` | [Agent skills](https://opencode.ai/docs/skills/) |
| Gemini CLI | `gemini` | `~/.gemini/skills` | [Agent skills](https://geminicli.com/docs/cli/skills/) |
| Kiro IDE/CLI local | `kiro` | `~/.kiro/skills` | [Agent skills](https://kiro.dev/docs/skills/) |
| Cursor local | `cursor` | `~/.cursor/skills` | [Skills](https://cursor.com/docs/skills) |
| Antigravity IDE/2.0 | `antigravity` | `~/.gemini/config/skills` | [Skills by surface](https://antigravity.google/docs/skills/) |
| Antigravity CLI | `antigravity-cli` | `~/.gemini/antigravity-cli/skills` | [CLI locations](https://antigravity.google/docs/skills/) |

OpenCode's current global path is plural `skills`, not the older singular
`skill` shown in past versions of this README. The installer does not delete
legacy directories. Codex/Gemini/OpenCode/Cursor also discover the shared
`.agents` location: avoid installing duplicate copies into several discovered
roots for the same runtime. Claude and Kiro use their own native roots.

Copies are portable; source checkout symlinks already pointing to this library
are recognized and left unchanged. An existing provider-root alias within the
chosen home (such as `.claude/skills -> .agents/skills`) is respected and
deduplicated. Aliases outside that home are refused. Unmanaged directories,
foreign links, broken links, and edits to managed copies are never overwritten.
This is file installation; provider discovery and activation must be confirmed
in a new/reloaded session. No catalog-budget or cross-version guarantee is made.

## Updates, backup and rollback

```sh
git pull --ff-only
python3 setup/install.py --provider codex --manifest install-manifests/frontend.txt
python3 setup/install.py --provider codex --manifest install-manifests/frontend.txt --apply
```

Updates compare complete source trees with managed installed snapshots. No-op
reruns produce no new transaction. A changed copy is backed up before replacing
it. State, backups and transaction journals are in
`~/.local/state/caiolombello-skills/`; do not remove this directory until you no
longer need rollback. Source-checkout symlinks update with the checkout, outside
the copy installer's transaction history.

Use the transaction ID printed by an applied install:

```sh
python3 setup/install.py --rollback TRANSACTION_ID
python3 setup/install.py --rollback TRANSACTION_ID --apply
```

Preview precedes restoration. Rollback verifies current content and backups,
refuses to overwrite edits, and restores only that transaction's destinations.
Undo later transactions first. Empty provider directories and backup history
remain. If a process was killed, inspect journals with `status: prepared` and
use that journal's filename ID for recovery; restore only destinations still
matching the recorded before/after snapshot, or absent during a recorded
publishing phase with an intact verified backup. Recovery reconciles ownership
metadata as well as file content. State aliases and invalid journals are refused. A stale `lock` directory requires
manual inspection of whether another installer is running before removing it.
Restoration copies into a journal-owned sibling staging directory on the same
filesystem, verifies its content, then retires the live directory and publishes
staging using renames. Each rename is atomic; the two-renames sequence has a
recoverable absent interval, not a single atomic directory exchange. Interrupted
staging may be retried only if its existing content matches backup content or a
partial byte prefix; edited scratch or live content is refused. Backups remain
intact. After journal completion, an interruption during scratch cleanup may
leave `.caio-rollback-*` siblings for manual inspection; installed content and
ownership are already complete. Filesystems must support ordinary same-directory
rename. Power loss durability/fsync and adversarial concurrent path replacement
are not certified by the process-interruption tests.
Do not use rollback as a generic uninstall of skills installed by other tools.

## Native link / command workflows

These commands are alternatives to local copies. Running native add/install or
choosing Import/Install in a provider is an explicit user action: inspect the
package and accept the provider's trust/install prompts. A repository URL alone
does not activate a plugin. Claude/Codex marketplace add registers a source;
plugin install/add separately installs the selected package. Cursor requires the
user to select/install the package; Kiro requires the user to confirm the skill
or Power import. Gemini keeps its native skill-install confirmation. Existing
sessions may require restart/reload and the user should verify discovery there.

Choose one mechanism per skill; do not combine copies and plugins merely to get the same capability twice.

Gemini CLI can fetch one root skill from this repository:

```sh
gemini skills install https://github.com/caiolombello/skills.git --path frontend-design --scope user
gemini skills list --all
```

Repeat with another skill path as needed. Keep Gemini's normal confirmation;
the setup does not pass `--consent`. Kiro's skill importer accepts a GitHub
subdirectory URL, for example
`https://github.com/caiolombello/skills/tree/main/frontend-design`, under
Agent Steering & Skills → Import a skill → GitHub. A repository root is not
a single-skill import URL. Native commands are documented, not executed against
the user's account by the tests here.

## Optional frontend plugin / power

`plugins/caio-frontend` contains the three frontend skills and their references.
It has a root Agent Plugins manifest, plus separate compatibility manifests for
Codex, Claude, and Cursor. Repo marketplaces also have distinct formats:

- Codex: `.agents/plugins/marketplace.json`; [package documentation](https://developers.openai.com/plugins/build/plugins).
- Claude: `.claude-plugin/marketplace.json`; [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference).
- Cursor: `.cursor-plugin/marketplace.json`; [plugin reference](https://cursor.com/docs/reference/plugins).
- Kiro Power: root `plugin.json` inside the package; [create powers](https://kiro.dev/docs/powers/create/) and [install powers](https://kiro.dev/docs/powers/installation/).

For a local checkout, inspect the payload before using the provider:

```sh
claude plugin validate ./plugins/caio-frontend
claude --plugin-dir ./plugins/caio-frontend
```

For repository distribution, after these setup artifacts are published:

```sh
claude plugin marketplace add caiolombello/skills
claude plugin install caio-frontend@caio-skills
```

Invoke `/caio-frontend:frontend-design` in Claude. Update with the provider's
marketplace/update mechanism rather than the copy installer's rollback.

Codex CLI 0.159.0 advertises these native commands (availability differs across
surfaces/versions):

```sh
codex plugin marketplace add caiolombello/skills
codex plugin add caio-frontend@caio-skills
```

For local authoring, the marketplace add source can instead be `.` from this
checkout. Do not add the user's personal marketplace automatically. A desktop
local marketplace can be browsed from the plugin directory after restart.
Public universal-directory submission is a separate action and has not occurred.

Cursor: Customize → From GitHub Repository →
`https://github.com/caiolombello/skills`, then choose `caio-frontend`. This uses
the committed Cursor marketplace, not a fabricated public directory listing.
No marketplace listing or cloud sync is enabled automatically.

Kiro: Powers → Add Custom Power → Import power from a folder →
`plugins/caio-frontend`. The native manifest makes this a skills-only power;
there is no MCP companion. Public GitHub power import is supported by Kiro,
but multi-directory selection has not been exercised here. Prefer the verified
single-skill GitHub URLs or local package until that UI path is tested.

OpenCode and Antigravity receive native skill directories through the selective
copy workflow. Their executable/plugin systems are different and no runtime
plugin or extension for them is claimed by this package. Gemini receives native
skills directly; a separate Gemini extension is not required for this workflow.

## Validation and release boundaries

```sh
python3 -m unittest discover -s setup/tests -v
python3 setup/build_frontend.py
claude plugin validate ./plugins/caio-frontend --strict
claude plugin validate . --strict
```

Tests use temporary homes and synthetic skill trees, without launching models
or installing providers. The builder checks versioned payloads against the
original root skills; `--apply` regenerates only those payloads and bundled
license files. Bundle regeneration is a sequential authoring operation, not
the installer transaction system; if interrupted, rerun the builder and checks. It does not change account settings. Keep generated copies
and sources in the same commit; bump every plugin manifest together for releases.

Claude manifest validation is executable locally. Codex's plugin-creator helpers
are not available in this executor; the compatible shape was checked against
official documentation and coordinator-provided skill guidance. Portable
manifest/schema fields and local paths are inspected, but Codex/Cursor/Kiro
runtime activation has not been certified. Codex's native catalog query returned
no available entries, so it did not confirm discovery. Claude 2.1.284 passed
strict package and marketplace validation and completed native marketplace
add/install/list in an isolated `CLAUDE_CONFIG_DIR`; version 0.1.0 was enabled
and its cached skill payload matched the reviewed bundle. No model was launched
and no real provider account configuration was changed.
Linux filesystem behavior was tested; Windows, remote/cloud and device UI were
not exercised. Local paths do not propagate to cloud sessions automatically.

The AI skill retains its own restricted LICENSE. Do not describe the whole
bundle as MIT or remove existing attributions. Adjacent skills linked from the
three workflows remain optional and are not silently bundled.
