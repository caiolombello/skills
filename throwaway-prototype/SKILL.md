---
name: throwaway-prototype
description: Build a disposable prototype to answer ONE design question before committing to it. Two branches — a runnable terminal/script for state-machine and business-logic questions, OR several radically different UI variations toggleable from a single route. Use WHENEVER the user wants to (1) prototype, mock up, or sanity-check an approach; (2) try several options before choosing one; (3) validate a data model, state machine, or API shape on paper does not survive contact with reality; (4) says "prototype this", "let me play with it", "try a few designs", "just hack something to see it"; (5) the real implementation would cost more than playing with a throwaway. The prototype is throwaway from day one. It is not tested, not polished, not persisted. It dies after answering the question.
---

<!-- Inspired by mattpocock/skills engineering/prototype (MIT). Expanded. See ../CREDITS.md -->

# Throwaway Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape. The prototype dies after it answers.

If you find yourself building tests, error handling, or abstractions — you are no longer prototyping. Stop, either promote the experiment to real work (with a real spec — see [`spec-first-planning`](../spec-first-planning)) or throw it away and restart smaller.

## Pick a branch

Figure out which question the user is answering:

- **"Does this logic / state model feel right?"** → **LOGIC branch**. Build a tiny runnable script / terminal app that pushes the state machine through cases that are hard to reason about on paper.
- **"What should this look like?"** → **UI branch**. Generate several radically different UI variations on one route, switchable from a floating control.

The two branches produce very different artifacts. Getting the branch wrong wastes the whole prototype.

If the question is genuinely ambiguous and the user is not reachable, default by surroundings — backend module → LOGIC; page or component → UI — and state the assumption at the top of the prototype.

## Rules that apply to both branches

1. **Throwaway from day one, clearly marked.** Locate the prototype next to the module or page it explores so context is obvious, but **name it so a casual reader sees it is a prototype**, not production. Examples: `__proto__/`, `prototype/`, `route: /playground/<name>`, file name `*.proto.ts`. Respect the project's existing routing / directory conventions — do not invent a new top-level.

2. **One command to run.** Whatever the project's task runner supports — `pnpm <name>`, `python <path>`, `bun <path>`, `cargo run --example <name>`, `go run ./proto/<name>`. The user must be able to start it without thinking.

3. **No persistence by default.** State lives in memory. Persistence is the thing you are **checking** with the prototype, not something it should depend on. If the question involves a database, use a local SQLite file or a scratch schema, with a name that screams throwaway: `tmp_proto_<date>.db`, `schema prototype_wipe_me`.

4. **Skip the polish.** No tests. No error handling beyond what makes the prototype **runnable**. No abstractions for reuse. The point is to learn fast and delete.

5. **Surface the state.** After every action (LOGIC) or variant switch (UI), print or render the **full relevant state** so the user can see what changed. The prototype is useless if you cannot observe it.

6. **Delete or absorb when done.** When the prototype has answered the question, either:
   - **Delete it** and fold the validated decision into the real code, or
   - **Absorb it** — rewrite it as production code via `spec-first-planning` + `incremental-implementation`.
   - If the experiment is valuable evidence that should remain inspectable, preserve it on a throwaway branch or worktree, record the branch/path and verdict in the issue or handoff, and keep it out of the production branch.
   - Never leave prototypes rotting in the repo.

## LOGIC branch — runnable terminal / script

For state models, business logic, data transformations, algorithm choice.

### Shape

A single file (or a few) you can run with one command. It:

- Declares the state shape as a plain data structure.
- Exposes a small set of actions (functions) that transform state.
- Has a loop: either scripted test cases or an interactive prompt.
- Prints the full relevant state after each action.

### Example (TypeScript / Node)

```ts
// proto/subscription-lifecycle.proto.ts
// Run: bun run proto/subscription-lifecycle.proto.ts
// Delete when answer is captured.

type State = { status: 'trial' | 'active' | 'past_due' | 'canceled'; periodEnd: Date };
type Action = { type: 'pay' | 'fail-charge' | 'cancel' | 'renew' };

const transition = (s: State, a: Action, now: Date): State => {
  // ... state machine under scrutiny ...
};

const script: Action[] = [{type: 'pay'}, {type: 'fail-charge'}, {type: 'pay'}, ...];
let s: State = {status: 'trial', periodEnd: addDays(new Date(), 14)};
for (const a of script) {
  s = transition(s, a, new Date());
  console.log(a.type, '→', s);
}
```

Keys:
- State after every action goes to stdout.
- Scripted actions beat an interactive prompt unless you need to explore.
- No database, no HTTP, no UI.

### When it has answered the question

Capture the answer: which state transitions are right, which are wrong, which invariant was unexpectedly violated. Write it in a commit message, an ADR (`docs/adr/NNNN-*.md`), or a `NOTES.md` next to the prototype. Then delete the prototype.

## UI branch — several variants on one route

For design exploration, information density questions, layout tradeoffs.

### Shape

One route (`/playground/<name>` or similar) that:

- Renders the **real content** (not lorem ipsum — use fixture data that resembles production).
- Offers **3-5 radically different variants** — not minor tweaks.
- Switches variants via a URL search param (`?v=compact`, `?v=dense`, `?v=kanban`).
- Exposes the switcher as a floating bottom bar or corner dropdown — always reachable.

### Example (React / Next.js)

```tsx
// app/(proto)/playground/task-list.proto/page.tsx
// Route: /playground/task-list.proto?v=compact

const variants = { compact: <Compact />, dense: <Dense />, kanban: <Kanban /> };

export default function Proto({ searchParams }: { searchParams: { v?: string } }) {
  const v = searchParams.v ?? 'compact';
  return (
    <>
      {variants[v] ?? variants.compact}
      <VariantSwitcher current={v} options={Object.keys(variants)} />
    </>
  );
}
```

Keys:
- Radically different, not A/B nits. If the variants would produce the same pixels after 5 CSS tweaks, they are not radical.
- Use fixture data that looks real (edge cases: long strings, empty list, 1 item, 100 items).
- No persistence, no auth, no tests.

### When it has answered the question

The user picks a variant (or a combination). Capture the decision — screenshot or commit note — and then either delete the playground route or keep it **only** if the team wants it as a living design reference.

## What NOT to do

| Anti-pattern | Why |
|--------------|-----|
| Adding tests | Prototypes are throwaway; tested code is not throwaway |
| Adding real auth / persistence | You are no longer answering the design question |
| Building a "reusable component" | Prototypes are one-shot |
| 3 variants that look identical | You are not exploring, you are polishing one variant |
| Hiding the prototype in a feature flag and forgetting it | Dead code in prod |
| Promoting the prototype directly to production code | Skips spec/plan/test — bugs inevitable |
| Persisting prototype state to the real DB | Corrupts real data when you forget about it |
| Landing the prototype PR with no "delete by" plan | It rots |

## When prototyping is the wrong tool

- The question has a known answer — you do not need a prototype, you need to write the code.
- The question needs real data at scale to answer — you need a spike / benchmark, not a prototype.
- The answer will change real user behavior — you need an A/B test in production, not a playground.

## Interaction with other skills

- [`spec-first-planning`](../spec-first-planning) — a prototype is what you build when you **do not yet have** the confidence to write a spec. After the prototype, you write the spec.
- [`incremental-implementation`](../incremental-implementation) — the follow-up to a successful prototype. Plan → slices → ship.
- [`llm-coding-discipline`](../llm-coding-discipline) — "minimum code that solves the problem" applies: a prototype that grows to 1000 lines is not a prototype any more.
- [`no-docs-unless-asked`](../no-docs-unless-asked) — prototypes do not need READMEs. A top-of-file comment is fine.
- [`code-simplification`](../code-simplification) — does NOT apply to prototypes. Do not spend effort refactoring throwaway code.

## Verification checklist

Before calling the prototype done:

- [ ] The original question is written at the top of the prototype file / route.
- [ ] The answer to the question is captured somewhere durable (commit, ADR, `NOTES.md`, issue).
- [ ] The prototype is deletable — no production code depends on it.
- [ ] No real data / production DB / real auth is reached by the prototype.
- [ ] The prototype is named / located so a first-time reader can tell it is throwaway.
- [ ] A plan exists to delete or absorb the prototype, with a rough date.
