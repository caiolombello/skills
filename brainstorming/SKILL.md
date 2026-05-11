---
name: brainstorming
description: Refine a rough product or engineering idea before planning or coding. Use WHENEVER (1) the user starts with a vague feature request, product idea, architecture change, or "what if we..." prompt; (2) requirements are underspecified and need Socratic clarification; (3) multiple approaches exist and tradeoffs matter; (4) the next step would otherwise be writing a spec from guesses; (5) the user asks to brainstorm, ideate, shape, explore, or talk through an idea. Produces a concise validated direction, not code.
---

<!-- Inspired by obra/superpowers brainstorming (MIT). See ../CREDITS.md -->

# Brainstorming

Turn a rough idea into a clear direction before writing a spec, plan, or code. The purpose is not to win an argument or generate a giant option list. The purpose is to surface the real goal, constraints, tradeoffs, and decision points while changes are still cheap.

## When to use

- The user gives an idea, not a requirement.
- The implementation path is not obvious.
- Several reasonable solutions exist.
- Missing product, UX, operational, security, or rollout requirements would change the design.
- The user asks to brainstorm, ideate, shape, explore, scope, or sanity-check an approach.

## When not to use

- The user has already provided an approved spec and is asking for execution.
- The task is a small, mechanical fix.
- A production incident is active — stabilize first with `incident-response`.
- The user explicitly says not to ask questions and the risk is low.

## The loop

```
UNDERSTAND -> EXPLORE -> SYNTHESIZE -> VALIDATE -> HAND OFF
```

Do not jump straight to implementation. A few targeted questions prevent a plan full of invented requirements.

## 1. Understand the actual goal

Start with the why, not the feature shape.

Ask only questions that can change the answer. Good questions identify constraints or tradeoffs:

- Who is the user or operator?
- What problem are they trying to solve today?
- What does success look like in observable terms?
- What is explicitly out of scope?
- What failure would make this approach unacceptable?

Avoid interview spam. If you need more than 3-5 questions at once, group them and explain why they matter.

## 2. Explore options with tradeoffs

Present 2-4 viable options. Include the boring option. Most good engineering decisions are choosing the least surprising path.

Use this format:

```markdown
## Option A: <name>
- Shape: <1-2 sentences>
- Best when: <condition>
- Tradeoffs: <costs / risks>
- Verification: <how we would know it works>
```

Do not hide uncertainty. If a key fact needs code or documentation research, say that and propose a quick investigation before deciding.

## 3. Synthesize a recommended direction

After exploring, recommend one path unless the user asked for options only.

The recommendation should include:

- The chosen approach.
- Why it best fits the stated goal.
- What it intentionally does not solve.
- The biggest remaining risk.
- The next artifact to create: spec, ADR, prototype, or implementation plan.

## 4. Validate with the user

Before handing off to planning, ask for a checkpoint:

```markdown
Recommended direction: <short version>

I will proceed to a spec/plan with these assumptions:
1. <assumption>
2. <assumption>
3. <assumption>

Reply "approved" or correct the assumptions.
```

If the user corrects the direction, update the synthesis. Do not defend the first answer just because you wrote it.

## 5. Hand off cleanly

When the direction is approved, hand off to the right next skill:

- `spec-first-planning` for a feature or larger change.
- `architecture-decision-records` when the decision has long-term consequences.
- `throwaway-prototype` when the main uncertainty is empirical.
- `api-and-interface-design` when the result is a public contract.
- `security-hardening` when external input, auth, or sensitive data is involved.

## Anti-patterns

| Anti-pattern | Why it fails | Better |
|---|---|---|
| Asking 20 questions up front | User cannot tell which matter | Ask 3-5 decision-changing questions |
| Presenting only one option | Hides tradeoffs | Show the obvious alternatives |
| Premature implementation | Converts uncertainty into code debt | Validate direction first |
| Over-polished design | Wastes time before alignment | Keep brainstorming lightweight |
| Silent assumptions | Produces a fake spec | List assumptions explicitly |

## Output template

```markdown
## Goal I heard
<1-3 bullets>

## Clarifying questions
1. <question>
2. <question>
3. <question>

## Options
### Option A: <name>
...

## Recommendation
<short recommendation + why>

## Assumptions to validate
- <assumption>
- <assumption>

## Suggested next step
<spec / ADR / prototype / implementation plan>
```

## Verification checklist

- [ ] The user's real goal is stated in their terms.
- [ ] Decision-changing questions were asked before planning.
- [ ] At least two viable options were considered when tradeoffs exist.
- [ ] The recommendation states what it does not solve.
- [ ] Assumptions are explicit and validated before execution.
- [ ] The next step is clear and uses the appropriate downstream skill.
