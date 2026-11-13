# Full audit workflow

Use only in full audit mode: an explicit audit or pen-test request, a full/comprehensive/end-to-end review, or a request for report artifacts. Phase details live in the companion references:

1. Reconnaissance → [reconnaissance-and-coverage.md](reconnaissance-and-coverage.md)
2. Coverage ledger and hunting waves with critics → [reconnaissance-and-coverage.md](reconnaissance-and-coverage.md), [hunting-and-critics.md](hunting-and-critics.md)
3. Independent candidate validation → [validation-and-reporting.md](validation-and-reporting.md)
4. `findings.json` and validators → [validation-and-reporting.md](validation-and-reporting.md)
5. Independent record verification → [validation-and-reporting.md](validation-and-reporting.md)
6. Reports derived from records → [validation-and-reporting.md](validation-and-reporting.md)

Execution rules are in [execution-safety.md](execution-safety.md) and apply to every phase.

## Setup

Resolve before reconnaissance:

- **Skill directory** — absolute path of this skill; validators live in `<skill-dir>/scripts/`.
- **Target** — absolute repository root under review.
- **Repo name** — stable identifier from the directory or local Git remote.
- **Source ref** — reviewed commit plus whether the worktree is dirty. Unreviewed generated or modified files are not another revision.
- **Output directory** — a new writable directory **outside the target**, default `~/security-audit/<repo-name>/run-<N>` with the next unused `N`. Use a path inside the target only when the user explicitly chooses it and version control ignores the whole directory; otherwise stop and ask for an external path.
- **Profile, scope, budget** — from the request, or proposed from target size and stakes (see below).
- **Delegation capability** — whether the host offers context-isolated delegation, context-inheriting delegation, or none. This decides how independence is achieved and what the report must disclose.

## Write isolation

The parent (coordinating agent) creates and is the **only writer** of the shared files: `run-metadata.json`, `architecture.md`, `coverage-ledger.json`, `findings.json`, `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md`.

Each hunter or verifier gets `<output-dir>/agents/<agent-id>/scratch/` and a parent-owned `artifacts/`. Agent IDs are lowercase and match `^[a-z0-9][a-z0-9_-]{0,63}$`, excluding Windows device names (`con`, `prn`, `aux`, `nul`, `com1`–`com9`, `lpt1`–`lpt9`); the ledger validator enforces this. Agents write only to their own `scratch/`, and return results to the parent instead of editing shared files, target source, or another agent's directory. Never use `/tmp` or the host home as a fallback write location.

When roles run sequentially in one session, keep the same separation: per-role directories, and the parent step is the only one that edits shared files.

## Run metadata

Before any delegated or sequential role starts, write `run-metadata.json` with at least: `run_id`, `repo`, `target`, `source_ref`, `profile`, `scope_paths`, `budget` (null if unset), `execution_policy: "sandboxed-source-and-local-only"`, selected domain references, prior-run paths, shared-file owner, `independence` (`isolated_agents`, `inherited_context_agents`, or `sequential_fresh_notes`), and `run_status: "in_progress"`. Update it only when those facts change; candidate state belongs in the ledger and `findings.json`.

## Profiles and scope

| Profile | Use | Shape |
|---|---|---|
| `quick` | Small targets, re-runs, a fast first look | Units coarsened to surface × boundary × attack class, with subsystem fixed to `profile/quick/all-in-scope-subsystems`. One hunter wave, then one final critic; critic discoveries become `deferred`. One fresh verifier per candidate covers both validation and record verification. |
| `standard` | Default | The workflow as written. |
| `deep` | High stakes or large targets | Units split by subsystem and lifecycle mode; critic waves until a clean pass; candidate validation and record verification by separate fresh verifiers; a second independent pass on same-source previously covered units. |

A **scoped run** covers named paths, one subsystem, one domain, or the diff between two refs. Seed units only for in-scope surfaces and record other discovered surfaces as `out_of_scope`, never `covered`. Scoped and `quick` runs present themselves as partial coverage.

Profiles never relax the candidate gate, the execution boundary, `needs_validation` discipline, schema validation, or independent verification of `confirmed` records.

## Prior runs

If earlier runs exist for the same repo, read their `coverage-ledger.json` and `findings.json` before planning. A prior source ref alone does not prove a path is unchanged; compare the relevant current source.

- **Prior `confirmed`, source unchanged:** carry it into the current candidate set with the same fingerprint, link it to a current `planned` unit (`prior_status: "prior_confirmed_same_source"`), and exclude only that root cause from hunters. It still goes through current verification; the verifier that re-checks it becomes that unit's owner.
- **Prior `confirmed`, source changed:** create a `prior_confirmed_changed_source` revalidation unit and do not exclude it from hunting. It stays confirmed only if current independent validation re-establishes it.
- **Prior `needs_validation`, `deferred`, `blocked`, `out_of_scope`, or changed-source units:** current work. A still-blocked `needs_validation` record may be carried by fingerprint after its current trace is re-checked; it keeps its blocker. These states never suppress a unit.
- **Prior `rejected`:** suppresses only that exact unchanged claim, not coverage of its unit. Changed evidence makes it current work.
- **Prior `quick` or scoped runs** contribute only their recorded evidence and gaps, never an implied "the rest is fine".
- Missing or incompatible prior ledgers are recorded as such, not treated as empty coverage. If there are none, say so in the coverage statement.

Never imply that one run exhausts the target.

## Budget

When the user sets a budget, or the parent proposes one for a large target, record it as a maximum number of agent invocations (or sequential role passes) across all phases. One ledger unit is roughly one hunter assignment; one surviving candidate is one or two verifier passes by profile.

1. **Gate before reconnaissance.** Reserve the baseline reconnaissance passes, the mandatory critics (`quick`: one final critic; `standard`/`deep`: one post-wave critic plus one distinct final-clean critic), and at least one verifier. If the budget cannot fund that, start nothing: ask for more budget, narrower scope, or another profile. If the request stands, record `run_status: "incomplete"`, `incomplete_reason: "budget_cannot_fund_reconnaissance_and_reserves"`, and report that no audit pass ran.
2. **Reserve before every wave.** Before each hunter wave, reserve its post-wave critic, the final-clean critic, and a validation reserve (about one or two verifiers per expected candidate; when unsure, 30% of what remains after critics). Never spend those reserves on hunters.
3. **Spend in priority order** (see hunting reference). Units the budget cannot reach become `deferred` with reason `budget_cannot_reserve_critics_and_validation`. A wave whose reserves do not fit launches no hunters.
4. **Validation overflow.** If candidates exceed what remains, stop hunting, validate in fingerprint order while budget lasts, and set `run_status: "incomplete"` with `incomplete_reason: "validation_budget_exhausted"`. Unvalidated candidates stay in the ledger as `candidate` units with that reason; they never enter `findings.json` and are never relabeled `needs_validation`.
5. If the final-critic reserve is consumed, launch no more hunters, defer remaining planned work, and record `critic_budget_exhausted`.

Before wave 1, restate the estimate with seeded units, hunter count, critic calls, and validation reserve. If it clearly does not fit, propose a tighter scope or coarser profile instead of quietly thinning evidence. Never exceed a user-set strict budget silently.

## Independence without delegation

Roles that must be independent: the coverage critic (from hunters), the candidate verifier (from the hunter of that candidate), and the record verifier (from the candidate verifier, in `standard` and `deep`).

- **Context-isolated delegation available:** give each role only its brief inputs.
- **Only context-inheriting delegation, or none:** run roles sequentially. Before each role, write a fresh notes file with just its inputs, re-read cited source from disk, and work from that file with the explicit goal of refuting. Do not consult earlier reasoning for that candidate.

Sequential fresh-notes passes are weaker than isolated agents because one model and session can carry anchoring forward. Record `independence: "sequential_fresh_notes"` (or `inherited_context_agents`) in metadata and state plainly in `REPORT.md` that verification was sequential self-review. Do not call it independent review.

## Terminal states

A full audit ends in exactly one of:

- **complete** — all Phase 6 reports written, `findings.json` and `coverage-ledger.json` both pass their validators, every ledger candidate has a final disposition, and every retained record passed Phase 5;
- **incomplete** — `run_status: "incomplete"` with an exact `incomplete_reason`, and the gap disclosed at the top of `REPORT.md`.

Never stop mid-phase without recording one of these.
