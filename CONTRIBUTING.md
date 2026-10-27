# Contributing

Thanks for wanting to help. Skills are small, focused, and opinionated — the bar is **"would a senior engineer at a different company recognize this as useful discipline?"**, not "does it work for my stack". Contributions are welcome whether you are adding a skill, editing an existing one, flagging a gap, or proposing a cut.

## What kind of contribution fits here

| Good | Not a fit |
|------|-----------|
| A new skill covering a common failure mode across tools / stacks | A skill tied to a single proprietary tool or codebase |
| A fix to an existing skill (unclear trigger, broken example, stale info) | A rewrite that drops all references and links to other skills |
| A gap report ("I keep asking my agent X and no skill covers it") | A rename-only cosmetic PR |
| A curation proposal (merge two overlapping skills, split one bloated skill) | "Add 10 skills I found elsewhere" drive-by imports |
| Skill-creator / eval-tooling improvements (adapter, harness, audits) | Personal dotfile integrations |
| Description rewrites that preserve distinct branches and shrink catalog budget | Synonym bags and `WHENEVER (1)(2)(3)…(8)` trigger spam |

## Skill layout

Every skill lives in its own folder at the repo root:

```
<skill-name>/
├── SKILL.md              # required: YAML frontmatter + instructions
├── references/           # optional: longer docs loaded on demand
│   └── <topic>.md
└── scripts/              # optional: portable Python / shell helpers
    └── <tool>.py
```

Naming: `kebab-case`, noun-verb or noun-noun. Prefer specific names (`kubectl-workflows`) over generic ones (`kubernetes`).

## SKILL.md structure

```markdown
---
name: <skill-name>
description: <YAML-safe string. See "Writing the description" below.>
---

<!-- Inspired by <upstream-if-any> (MIT). See ../CREDITS.md -->

# <Skill Name>

<One-sentence what & why>

## When to use

- Concrete trigger 1
- Concrete trigger 2

## When NOT to use

- Adjacent scope handled by another skill, linked by name

## The process / rules / checklist

<The actual content: short, scannable, imperative.>

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|

## Interaction with other skills

- [`other-skill`](../other-skill) — what's the boundary

## Verification checklist

- [ ] ...
```

### Writing the description

Clients commonly expose name, description, and path before loading the skill body. Keep discovery cheap and discriminating. Aggregate limits, truncation, and invocation behavior depend on the client/version; do not assert a universal 2% or 8000-character budget without current evidence.

**Good descriptions:**

1. Lead with **when to use** (observable condition), not a marketing summary of the workflow.
2. Encode **distinct branches** only — one real decision surface per clause. Do **not** list synonym bags (`deploy/ship/roll out/promote…`).
3. Disambiguate neighbors in one short phrase when overlap is real (`Not for LIVE incidents — use incident-response`).
4. Keep YAML valid: quote the string if it contains `: ` or other plain-scalar breakers. No angle brackets (`<`/`>`).
5. Respect the target validator's supported fields/limits (the bundled validator caps descriptions at 1024 characters). Prefer a short description that captures distinct intents, not a quota or a guarantee that a particular keep-set fits every client.
6. **Never** pad with `Keywords:` suffixes or restate the skill body.

**Bad (do not merge):**

```yaml
description: Ship changes... Use WHENEVER the user is about to (1) release, deploy, ship, roll out, or promote... (2) ... (5) mention "canary", "blue/green", "rolling deploy", "rollback"...
```

**Good:**

```yaml
description: Use when shipping or promoting to production, designing canary/blue-green/rolling rollout, or production Deployment/ECS/Cloud Run rollout safety. Not routine app code.
```

Validate:

```bash
# frontmatter / Agent Skills shape
SKILL=incident-triage   # example; set to the skill dir name
python3 skill-creator/scripts/quick_validate.py ./"$SKILL"

# For trigger/behavior evaluation, use an authorized model and the installed
# client's currently supported interface. Do not infer provider access from
# an example model ID or mutate a live skill root to install a probe.
```

Include positive cases, near misses, clean counterexamples, and meaningful edge cases. Evaluate important description/workflow changes with realistic tasks and inspect failures, not just average scores. Small wording edits do not require a new evaluation platform. Label a description-only routing check as such; it does not certify native discovery or runtime behavior in another client. The legacy OpenCode adapter must be checked against the installed version and isolated before use; do not select a fallback provider/model without authorization.

See [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md) for methodology. Catalog budget / install tiers: [`install-manifests/`](./install-manifests/) and README.

### Writing the body

- **Provider-agnostic.** Do not assume Claude subagents / personas / `agents/` directories. Prefer the plural vocabulary: "the project rules file (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/`)". If a tool is mandatory, say so upfront in the description ("tooling-specific: requires X").
- **Short, scannable, imperative.** Bullets and tables beat paragraphs. The reader is a busy on-call.
- **Link, don't duplicate.** If another skill covers something, link it from `Interaction with other skills`. Do not restate.
- **Concrete examples** over abstract explanations. A good SKILL.md has at least one real command or YAML / code snippet.
- **English.** The repo language is English. Inline code comments can be in another language if the upstream project is; prose should be English.
- Keep the entrypoint as short as the task permits. Put substantial conditional detail in linked references; do not add or remove useful constraints merely to meet a line quota.
- Include `<!-- Inspired by <upstream>/<project> (MIT). See ../CREDITS.md -->` just below the frontmatter if the skill is adapted from an upstream library. Update [`CREDITS.md`](./CREDITS.md) in the same PR.

## Install manifests (do not reintroduce bulk install)

- [`install-manifests/codex-keep.txt`](./install-manifests/codex-keep.txt) — **public always-on** subset.
- [`install-manifests/codex-on-demand.txt`](./install-manifests/codex-on-demand.txt) — situational skills, install only when the domain is active.
- `install-manifests/codex-keep.local.txt` — **gitignored** private/company skills (example: branded client docs). Never put generic skills only there.

**Codex / Gemini shared path:** install into `~/.agents/skills/<name>` → this repo.  
**Do not** also install user skills into `~/.codex/skills` (leave `.system` alone). Duplicates waste catalog budget.

**Never** document "install everything" as the default. Bulk install is an anti-pattern for Codex-class budgets.

Writing scopes: `natural-writing` is the general keep-set workflow for voice,
register, and copy-ready prose. Keep article research and publication structure
in the on-demand `blog-posting` skill. `write-like-me` is an optional external
source of personal samples, not a required dependency to vendor or duplicate.
Skill availability does not guarantee invocation on every response.

## Proposing a new skill

Open a PR or issue with:

1. **Trigger evidence** — 3-5 real user queries (or agent tasks) that the skill should fire on, in your own words.
2. **Negative evidence** — 2-3 queries where it should **not** fire, demonstrating where the boundary lives.
3. **Draft description** (branch-preserving, budget-aware).
4. **Draft SKILL.md** (can be short at proposal time; full body after the scope is agreed).
5. **Install tier** — always-on (`codex-keep.txt`) vs on-demand (`codex-on-demand.txt`) vs repo-only.
6. **Link** to any upstream library / spec / internal runbook the skill draws from.

## Proposing a cut or merge

Overlap is inevitable as the library grows. If two skills drift too close:

1. Identify both skills by name.
2. State whether they should be **merged** (same scope, duplicated), **narrowed** (one scope swallowed by the other), or **split** (one description covers two unrelated things).
3. Draft the unified description or the revised descriptions.
4. Update the cross-links in `Interaction with other skills` sections of all affected skills.
5. Update install manifests if the keep/on-demand set changes.

## Commits and PRs

- **Conventional Commits** in English: `feat(<skill>): <imperative summary>` / `fix(<skill>): ...` / `docs(<skill>): ...` / `refactor(<skill>): ...`.
- One logical change per PR.
- PR body includes: the problem being solved, the scope of the change, any skill-creator eval results if you ran them, and a link to related skills you touched.
- Description-standard or install-path changes must update **README + CONTRIBUTING + manifests** in the same PR so the next contributor does not recreate the old bulk-install / long-description pattern.

## After merging

For a meaningful skill change, validate metadata/references and exercise relevant behavior/selection cases with an authorized client. Record which checks ran, the version/snapshot they cover, and what was not verified. Keep known-bug and clean cases so reviewer changes do not reward false positives. Prefer deterministic tests/lint for reproducible failures and concise examples/instructions for judgment gaps; compare like tasks before attributing outcomes to a model.

Reusable cases for this review-policy update are in `code-review/evals/scenarios.json`
and `pr-followup/evals/scenarios.json`. They are behavioral fixtures, not inputs
for the legacy flat-schema trigger adapter. Change one important rule at a time
when practical and measure task outcomes, unnecessary work, time/cost, and review
rounds proportionally to the change. No history-wide personal-data audit is
implied. Keep vendored `skill-creator` and client/plugin caches unchanged.

If your PR adds a skill that replaces or overlaps an existing one, update both SKILL.md `Interaction with other skills` sections in the same commit.

## Code of conduct

Treat everyone well. Disagree about skills, not people. Sarcasm in SKILL.md content is fine (the writing style here is pointed); sarcasm at contributors is not.

## Provider setup changes

Keep discovery paths and native commands grounded in current official provider
documentation; record the reviewed date in `setup/README.md`. Do not use one
provider's plugin schema for another. Keep the existing keep/on-demand manifests
selective; provider support does not justify bulk-installing all skills.

Run `python3 -m unittest discover -s setup/tests -v` for installer changes. Tests
must use isolated temporary homes, including paths with spaces, foreign installs,
managed edits, idempotent update and rollback. Never activate a provider account
or execute third-party hooks to make a test pass.

The frontend package's skill payload is generated from root sources. Run
`python3 setup/build_frontend.py --apply` after changing those sources, include
the generated payload and required license/credit files in the same commit, and
verify synchronization without `--apply`. Bump all native manifest versions
together when releasing the package. README, CONTRIBUTING and relevant manifests
should reflect installation changes in the same review. Record which native
validators ran and which provider runtime checks remain unavailable.
