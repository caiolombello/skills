---
name: dispatching-parallel-agents
description: "Use when coordinating authorized subagents for independent parallel work, a genuinely separate review context, or execution isolation. Keep tightly coupled work in the main agent loop."
---

<!-- Inspired by obra/superpowers dispatching-parallel-agents and subagent-driven-development (MIT). See ../CREDITS.md -->

# Dispatching Parallel Agents

Parallel agents are useful when tasks are independent. They are dangerous when they edit the same files, duplicate decisions, or lose context. This skill provides the coordination layer: split work deliberately, give each agent a tight brief, collect results, and integrate only after review.

## When to use

- Independent research tracks can run at the same time.
- Separate code areas can be modified without file overlap.
- You need fresh-context review or adversarial analysis.
- A plan has tasks that are explicitly parallel-friendly.
- The user asks for subagents, parallel sessions, or delegation.

## When not to use

- Tasks share the same files or unresolved design decisions.
- The work is small enough for one focused pass.
- A single failing test needs tight diagnosis.
- The user needs one accountable implementation path, not broad exploration.

## Split by independence, not by layer

Before delegating, identify the benefit: independent parallel progress, an actually separate review context, useful execution/permission isolation, or measurable context overload. Weigh it against startup latency, duplicated reads, lossy summaries, coordination, and integration. If selective skill/source loading or parallel tool calls in the main loop suffice, use those. Do not create a router/planner/domain agent simply because a topic has a name.

Start with the smallest useful set, not a fixed number of specialists or models. Keep sequential tasks that share decisions/data in the same loop unless a real boundary can be defined. Respect the user's delegation and provider choices; this skill does not widen authorization.

On T3 Code, use [t3-workflows delegation](../t3-workflows/references/delegation.md) for the native/delegate distinction, app-owned checkout binding and asynchronous next steps. Do not transplant another client's Task/background/model syntax. For UI workers, establish actual tool/session access and one controller per surface; a shared checkout does not grant shared browser ownership.

Good splits:

- Agent A: investigate current auth flow; Agent B: verify library docs; Agent C: review security risks.
- Agent A: backend endpoint in worktree A; Agent B: frontend mock using approved API contract in worktree B.
- Agent A: code review; Agent B: test coverage review.

Bad splits:

- Agent A edits `UserService`; Agent B also edits `UserService`.
- Agent A designs the API while Agent B implements against a guessed API.
- Three agents all "look around" with no output contract.

## Dispatch brief template

Every agent needs a precise brief:

```markdown
TASK: <one sentence>

Context:
- Goal: <shared goal>
- Source of truth: <spec/plan path or summary>
- In scope: <files / areas>
- Out of scope: <explicit exclusions>

Rules:
- Do not edit files unless explicitly allowed.
- Do not commit unless explicitly asked.
- Treat secrets as sensitive; do not print values.
- Verify with: <command or read-only check>

Return:
- Findings / changes made
- Evidence
- Risks / open questions
- Exact files touched, if any
- Actual source/version references, observed results, and uncertainties needed to verify the handoff
```

If the provider has no subagent tool, paste this into separate sessions and collect the results manually.

## Worktree isolation for write tasks

For parallel implementation, use `using-git-worktrees` unless the tasks are read-only.

Use app-owned checkout/isolation tools when required by the runtime; a shell-created checkout does not necessarily bind a child to it. A nominal subagent may inherit parent history: configure a supported clean-context mode when independence is the goal. Do not assume freshness or permission separation from the word "subagent".

Each writing agent gets:

- Unique worktree path.
- Unique branch.
- Non-overlapping file ownership.
- Verification command.
- Merge/integration expectations.

Do not let multiple agents commit to the same branch concurrently.

## Research agents vs implementation agents

Prefer read-only agents by default.

Use implementation agents only when:

- The plan is approved.
- File ownership is clear.
- Test commands are known.
- Integration order is defined.

Research outputs should be short and structured. Ask for facts, not essays.

## Collecting results

When agents return, synthesize before acting:

1. Compare findings for conflicts.
2. Verify claims against code or docs when they drive decisions.
3. Surface unresolved disagreements.
4. Decide the integration order.
5. Run final verification in the main integration branch.

Do not blindly trust subagent output. Fresh context helps, but it can still be wrong.

## Two-stage review pattern

Check both concerns for generated code, proportionally to risk:

1. **Spec compliance** — does it satisfy the requested task and acceptance criteria?
2. **Code quality** — correctness, readability, architecture, security, performance.

Critical spec failures block integration. Quality findings are triaged by severity.

These concerns can be checked in one pass. Separate agents or rounds only when they add useful coverage or independence; there is no universal two-agent/two-round gate. Use the convergence rules in [`code-review`](../code-review/SKILL.md), not repeated full reviews until reviewers agree. A child should not recursively delegate unless its task and the runtime permit that.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Vague delegation | Returns unusable summaries |
| Parallel design decisions | Produces incompatible work |
| Shared branch writes | Race conditions and messy history |
| No output contract | Hard to integrate results |
| Trusting agents blindly | Multiplies hallucinations |

## Verification checklist

- [ ] Tasks are genuinely independent or isolated by worktree.
- [ ] Each agent has a precise brief and output contract.
- [ ] Write tasks have non-overlapping file ownership.
- [ ] Results are synthesized and conflicts surfaced.
- [ ] Claims that affect implementation are verified.
- [ ] Final integration is tested in one place.
