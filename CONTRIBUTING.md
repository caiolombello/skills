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

The description is the **only thing** most agents inject for every skill on every turn (progressive disclosure: name + description + path). Codex-class agents also enforce an **aggregate catalog budget** (~2% of context, fallback **8000 characters** for the whole list). Long descriptions do not make triggers better — they blow the budget, get truncated, then skills are omitted.

**Good descriptions:**

1. Lead with **when to use** (observable condition), not a marketing summary of the workflow.
2. Encode **distinct branches** only — one real decision surface per clause. Do **not** list synonym bags (`deploy/ship/roll out/promote…`).
3. Disambiguate neighbors in one short phrase when overlap is real (`Not for LIVE incidents — use incident-response`).
4. Keep YAML valid: quote the string if it contains `: ` or other plain-scalar breakers. No angle brackets (`<`/`>`).
5. Spec max is 1024 chars per skill. Prefer **~120–220** for always-on skills so a keep-set of ~20 still fits under the aggregate budget with `.system` skills present.
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

# trigger eval (positive + near-miss). Prefer a real model the agent uses.
# Discover IDs with: opencode models
MODEL=$(opencode models 2>/dev/null | awk '/deepseek-v4-flash/{print; exit}')
MODEL=${MODEL:-opencode/deepseek-v4-flash}
python3 skill-creator-opencode/scripts/run_eval_opencode.py \
  --eval-set /tmp/"$SKILL".json \
  --skill-path ./"$SKILL" \
  --model "$MODEL" \
  --runs-per-query 3 --num-workers 1 --timeout 120 --verbose
```

Eval set: at least **2 should-trigger**, **2 near-miss** (adjacent skill), **1 edge**. Aim for stable pass rate before merging description changes.

See [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md) for methodology. Catalog budget / install tiers: [`install-manifests/`](./install-manifests/) and README.

### Writing the body

- **Provider-agnostic.** Do not assume Claude subagents / personas / `agents/` directories. Prefer the plural vocabulary: "the project rules file (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/`)". If a tool is mandatory, say so upfront in the description ("tooling-specific: requires X").
- **Short, scannable, imperative.** Bullets and tables beat paragraphs. The reader is a busy on-call.
- **Link, don't duplicate.** If another skill covers something, link it from `Interaction with other skills`. Do not restate.
- **Concrete examples** over abstract explanations. A good SKILL.md has at least one real command or YAML / code snippet.
- **English.** The repo language is English. Inline code comments can be in another language if the upstream project is; prose should be English.
- **Max ~250–500 lines** for the SKILL.md itself. Overflow goes into `references/` files linked from the main SKILL.md (progressive disclosure). Agents load those on demand only when the main skill content points to them.
- Include `<!-- Inspired by <upstream>/<project> (MIT). See ../CREDITS.md -->` just below the frontmatter if the skill is adapted from an upstream library. Update [`CREDITS.md`](./CREDITS.md) in the same PR.

## Install manifests (do not reintroduce bulk install)

- [`install-manifests/codex-keep.txt`](./install-manifests/codex-keep.txt) — **public always-on** subset.
- [`install-manifests/codex-on-demand.txt`](./install-manifests/codex-on-demand.txt) — situational skills, install only when the domain is active.
- `install-manifests/codex-keep.local.txt` — **gitignored** private/company skills (example: branded client docs). Never put generic skills only there.

**Codex / Gemini shared path:** install into `~/.agents/skills/<name>` → this repo.  
**Do not** also install user skills into `~/.codex/skills` (leave `.system` alone). Duplicates waste catalog budget.

**Never** document "install everything" as the default. Bulk install is an anti-pattern for Codex-class budgets.

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

If you change a skill body significantly, run the trigger eval to confirm you did not regress the description. If you change a description, definitely run the eval — description changes are where most regressions come from.

If your PR adds a skill that replaces or overlaps an existing one, update both SKILL.md `Interaction with other skills` sections in the same commit.

## Code of conduct

Treat everyone well. Disagree about skills, not people. Sarcasm in SKILL.md content is fine (the writing style here is pointed); sarcasm at contributors is not.
