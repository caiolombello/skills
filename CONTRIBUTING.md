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
description: <160-1024 chars. See "Writing the description" below.>
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

The description is the **only thing** the agent sees on every turn to decide whether to load the skill. It determines both recall (does it trigger when it should?) and precision (does it stay quiet when it shouldn't?).

**Good descriptions:**

1. State what the skill is in ~15 words.
2. Enumerate concrete triggers: "Use WHENEVER (1) the user asks to X; (2) the user mentions Y; (3) the agent is about to Z".
3. List explicit **negative** triggers too, linking the adjacent skill that covers the out-of-scope cases.
4. Include the vocabulary a user naturally uses ("rollback", "canary", "p99", "SLO", "expand/contract") so the model can match fuzzy phrasing.
5. End between 250-1024 characters. Too short = weak trigger. Too long = skill-creator heuristics degrade.

Validate with the tools in `skill-creator-opencode/scripts/`:

```bash
# single skill, 4 queries
python3 skill-creator-opencode/scripts/run_eval_opencode.py \
  --eval-set /tmp/<skill>.json \
  --skill-path ./<skill> \
  --model anthropic/claude-haiku-4-5 \
  --runs-per-query 3 --num-workers 1 --timeout 120 --verbose
```

Aim for 4/4 with `runs-per-query 3` at threshold 0.5 before merging a new or substantially-edited skill. See [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md) for the methodology.

### Writing the body

- **Provider-agnostic.** Do not assume Claude subagents / personas / `agents/` directories. Prefer the plural vocabulary: "the project rules file (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/`)". If a tool is mandatory, say so upfront in the description ("tooling-specific: requires X").
- **Short, scannable, imperative.** Bullets and tables beat paragraphs. The reader is a busy on-call.
- **Link, don't duplicate.** If another skill covers something, link it from `Interaction with other skills`. Do not restate.
- **Concrete examples** over abstract explanations. A good SKILL.md has at least one real command or YAML / code snippet.
- **English.** The repo language is English. Inline code comments can be in another language if the upstream project is; prose should be English.
- **Max ~250 lines** for the SKILL.md itself. Overflow goes into `references/` files linked from the main SKILL.md (progressive disclosure). Agents load those on demand only when the main skill content points to them.
- Include `<!-- Inspired by <upstream>/<project> (MIT). See ../CREDITS.md -->` just below the frontmatter if the skill is adapted from an upstream library. Update [`CREDITS.md`](./CREDITS.md) in the same PR.

## Proposing a new skill

Open a PR or issue with:

1. **Trigger evidence** — 3-5 real user queries (or agent tasks) that the skill should fire on, in your own words.
2. **Negative evidence** — 2-3 queries where it should **not** fire, demonstrating where the boundary lives.
3. **Draft description** (any length; will be iterated).
4. **Draft SKILL.md** (can be short at proposal time; full body after the scope is agreed).
5. **Link** to any upstream library / spec / internal runbook the skill draws from.

## Proposing a cut or merge

Overlap is inevitable as the library grows. If two skills drift too close:

1. Identify both skills by name.
2. State whether they should be **merged** (same scope, duplicated), **narrowed** (one scope swallowed by the other), or **split** (one description covers two unrelated things).
3. Draft the unified description or the revised descriptions.
4. Update the cross-links in `Interaction with other skills` sections of all affected skills.

The most recent overlap audit lived in [`skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md`](./skill-creator-opencode/SMOKE-AUDIT-2026-05-10.md). Future audits follow the same format.

## Commits and PRs

- **Conventional Commits** in English: `feat(<skill>): <imperative summary>` / `fix(<skill>): ...` / `docs(<skill>): ...` / `refactor(<skill>): ...`.
- One logical change per PR.
- PR body includes: the problem being solved, the scope of the change, any skill-creator eval results if you ran them, and a link to related skills you touched.
- Do not bundle a new skill with a README update that restructures the library into a new category — ship the skill first, restructure later.

## After merging

If you change a skill body significantly, run the trigger eval to confirm you did not regress the description. If you change a description, definitely run the eval — description changes are where most regressions come from.

If your PR adds a skill that replaces or overlaps an existing one, update both SKILL.md `Interaction with other skills` sections in the same commit.

## Code of conduct

Treat everyone well. Disagree about skills, not people. Sarcasm in SKILL.md content is fine (the writing style here is pointed); sarcasm at contributors is not.
