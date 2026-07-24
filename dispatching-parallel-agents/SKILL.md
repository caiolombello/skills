---
name: dispatching-parallel-agents
description: "Coordinate parallel subagents or separate agent sessions safely. Use WHENEVER (1) a task can be split across independent research or implementation tracks; (2) the user asks to use multiple agents, subagents, parallel work, or delegate; (3) codebase exploration, review, docs verification, security audit, or test investigation can run concurrently; (4) you need fresh-context reviewers or specialists; (5) worktrees or branch isolation are needed to avoid collisions. Provider-agnostic: use subagent tools if available, otherwise give copy-pasteable session briefs."
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
```

If the provider has no subagent tool, paste this into separate sessions and collect the results manually.

## Worktree isolation for write tasks

For parallel implementation, use `using-git-worktrees` unless the tasks are read-only.

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

For generated code, use two review passes:

1. **Spec compliance** — does it satisfy the requested task and acceptance criteria?
2. **Code quality** — correctness, readability, architecture, security, performance.

Critical spec failures block integration. Quality findings are triaged by severity.

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
