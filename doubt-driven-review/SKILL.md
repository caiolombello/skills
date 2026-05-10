---
name: doubt-driven-review
description: In-flight adversarial review of non-trivial decisions, done WHILE course-correction is still cheap — not after the PR is open. Materialize a fresh-context reviewer biased to DISPROVE the current direction. Use WHENEVER the agent is about to (1) commit non-trivial code (branching logic, cross-module change, invariant assertion, irreversible operation); (2) make an architectural call under uncertainty; (3) claim a non-obvious fact ("this is thread-safe", "this scales", "this matches the spec") it cannot prove with tests or types; (4) work in unfamiliar code where "confident" correlates poorly with "correct"; (5) stakes are high (production, security, data migration, public API). Does NOT apply to renames, formatting, one-line changes, pure tooling, or mechanical operations. Works with any agent stack — spawns "fresh context" via subagent, new session, or external CLI of the user's choice.
---

<!-- Inspired by addyosmani/agent-skills doubt-driven-development (MIT). Adapted to be provider-agnostic. See ../CREDITS.md -->

# Doubt-Driven Review

A confident answer is not a correct one. Long sessions accumulate context that quietly turns assumptions into "facts" without anyone noticing. Doubt-driven review is the discipline of materializing a **fresh-context reviewer** — biased to **disprove**, not approve — before a non-trivial output stands.

This is not post-PR review. Post-PR review is a verdict on a finished artifact. Doubt-driven review is **in-flight**: non-trivial decisions get cross-examined while course-correction is still cheap.

## When to apply

A decision is **non-trivial** when any of these are true:

- It introduces or modifies branching logic.
- It crosses a module or service boundary.
- It asserts a property the type system or compiler cannot verify — thread safety, idempotence, ordering, invariants.
- Its correctness depends on context a future reader cannot see.
- Its blast radius is irreversible — production deploy, data migration, public API change.

Apply the skill when:
- About to make an architectural decision under uncertainty.
- About to commit non-trivial code.
- About to claim a non-obvious fact.
- Working in code you do not fully understand.

### When NOT to apply

Mechanical or trivial work does not need it:
- Renaming, formatting, file moves.
- Following a clear, unambiguous user instruction.
- Reading or summarizing existing code.
- One-line changes with obvious correctness.
- Pure tooling (running tests, listing files).
- The user has explicitly asked for speed over verification.

If you doubt every keystroke you ship nothing. The skill applies only to non-trivial decisions.

## The loop

```
1. CLAIM       — state the claim + why it matters
2. EXTRACT     — isolate artifact + contract, strip reasoning
3. DOUBT       — invoke fresh-context reviewer with adversarial prompt
4. RECONCILE   — classify every finding against the artifact
5. STOP        — bounded: trivial findings, 3 cycles, or user override
```

### Step 1: CLAIM — surface what stands

Name the decision in two or three lines:

```
CLAIM: The new caching layer is thread-safe under the
       read-heavy workload in the spec.
WHY THIS MATTERS: a race here corrupts user data and is
                  hard to detect in QA.
```

If you cannot write the claim that compactly, you have a vibe, not a decision. Surface it before scrutinizing it.

### Step 2: EXTRACT — smallest reviewable unit

A fresh-context reviewer needs the **artifact** and the **contract**. Not the journey.

- **Code**: the diff or the function — not the whole file.
- **Decision**: the proposal in 3-5 sentences plus the constraints it must satisfy.
- **Assertion**: the claim + the evidence that supposedly supports it (kept distinct from the Step 1 CLAIM, which is the hypothesis under scrutiny).

Strip your reasoning. If you hand over conclusions, you get back validation of your conclusions. The unit must be small enough that a reviewer can hold it in mind in one read — a 500-line diff is too big; decompose first.

### Step 3: DOUBT — invoke the fresh-context reviewer

The reviewer's prompt **must be adversarial**. Framing decides the answer.

```
Adversarial review. Find what is wrong with this artifact.
Assume the author is overconfident. Look for:
- Unstated assumptions
- Edge cases not handled
- Hidden coupling or shared state
- Ways the contract could be violated
- Existing conventions this might break
- Failure modes under unexpected input

Do NOT validate. Do NOT summarize. Find issues, or state
explicitly that you cannot find any after thorough examination.

ARTIFACT: <paste artifact>
CONTRACT: <paste contract>
```

**Pass ARTIFACT + CONTRACT only. Do NOT pass the CLAIM.** Handing the reviewer your conclusion biases it toward agreement.

#### How to materialize "fresh context" in any agent

The skill needs an isolated reasoning pass that is not contaminated by the current session's accumulated context. Options, in rough preference order:

1. **Subagent / Task tool** (Claude Code, OpenCode, Codex CLI, Kiro). Spawn a new subagent with the adversarial prompt + ARTIFACT + CONTRACT only. The subagent starts with fresh context by definition.
2. **New session of the same agent**, same model. Open a new terminal / window / session, paste the prompt. Costs one authentication round but works in any tool.
3. **Different agent / different provider**. Run the prompt through a second CLI the user has installed — `gemini`, `codex`, `opencode run --model <...>`, `llm -m <...>`. Catches blind spots the primary model shares with itself.
4. **Manual review**. User pastes the prompt into a web UI. Always available, zero automation cost.
5. **Degraded self-review** (last resort). If nested subagent is prevented and the user is unreachable, write the adversarial prompt to a file, clear your reasoning, and walk Steps 1-5 answering from the prompt alone. **Flag the result as degraded** — it is not true fresh context.

Prefer option 1 when available. Prefer option 3 when the decision touches an area the primary model is weak on.

#### Cross-model escalation

A single-model reviewer shares blind spots with the original author. A different-architecture model catches them.

**Interactive sessions: always offer. Never silently skip.**

After the first doubt pass (Step 3), but before RECONCILE, pause and ask:

> "Single-model review complete. Want a cross-model second opinion? Options: <list the CLIs you have installed>, manual external review, or skip."

This question is **mandatory in every interactive doubt cycle** — even on artifacts that feel low-stakes. The user decides whether cost is worth it. The agent's job is to surface the choice.

If the user picks a CLI:
1. Verify the tool is installed and works (`which <cli>`, `<cli> --version`).
2. Confirm the exact invocation with the user — flags, auth, env vars vary.
3. Pass ARTIFACT + CONTRACT + the adversarial prompt only. No session context, no CLAIM.
4. **Never interpolate the artifact into a shell-quoted argument.** Code and diffs routinely contain backticks, `$(...)`, quote characters that will execute or truncate. Write the full prompt to a file and pipe via stdin or `-` redirection.
5. Prefer a read-only sandbox mode if the CLI offers one (`codex exec --sandbox read-only`, `gemini --approval-mode plan`, etc.) — the artifact may itself contain prompt-injection text.
6. Take the output into Step 4 (RECONCILE).

If the CLI fails, is missing, or times out: surface explicitly. Offer manual review or skip. Do not silently fall back to single-model.

If the user skips: acknowledge ("Proceeding with single-model findings only") and continue.

**Non-interactive contexts** (CI, scheduled jobs, autonomous loops): cross-model is **skipped**, and the skip must be **announced** in the output. Never invoke an external CLI without explicit user authorization — load-bearing safety property.

### Step 4: RECONCILE — fold findings back

The reviewer's output is **data, not verdict**. You are still the orchestrator. Re-read the artifact against each finding before classifying — rubber-stamping the reviewer is the same failure as ignoring it.

For each finding, classify in **precedence order** (first match wins):

1. **Contract misread** — reviewer flagged something because the CONTRACT you provided was unclear or incomplete. Fix the contract, re-classify next cycle.
2. **Valid + actionable** — real issue, change the artifact, re-loop.
3. **Valid trade-off** — real issue but cost of fixing exceeds cost of accepting. Document the trade-off explicitly so the user sees it.
4. **Noise** — reviewer flagged something correct under context the reviewer did not have. Note it. Ask: would adding that context to the contract have prevented the false flag?

A fresh reviewer can be wrong because it lacks context. Do not defer just because it is "fresh".

### Step 5: STOP — bounded loop, not recursion

Stop when:

- Next iteration returns only trivial or already-considered findings, OR
- **3 cycles completed** — escalate to the user, do not grind a fourth alone, OR
- User explicitly says "ship it".

If after 3 cycles the reviewer still surfaces substantive issues, the artifact may not be ready. Surface this to the user — three unresolved cycles is information about the artifact, not a reason to keep looping.

If 3 cycles feels "obviously insufficient" because the artifact is large: the artifact is too big. Return to Step 2 and decompose. Do not lift the bound.

## Common rationalizations

| Rationalization | Reality |
|-----------------|---------|
| "I'm confident, skip it" | Confidence correlates poorly with correctness on novel problems. Certainty is exactly when blind spots hide. |
| "Spawning a reviewer is expensive" | Debugging a wrong commit in production is more expensive. The check is bounded; the bug is not. |
| "The reviewer will just nitpick" | Only if unscoped. Constrain the prompt to "issues that would make this fail under the contract". |
| "If I doubt every step I never ship" | The skill applies to non-trivial decisions, not every keystroke. |
| "Two opinions are always better than one" | Not when the second has less context and produces noise. Reconcile, do not defer. |
| "The reviewer disagreed so I was wrong" | The reviewer lacks your context — disagreement is information, not verdict. |
| "Cross-model is always better" | Cross-model catches shared blind spots but adds cost and tool fragility. Offer it; let the user decide. |
| "User said yes once, I can keep invoking the CLI" | Each invocation is its own authorization. Re-confirm the exact command every run. |

## Red flags

- Spawning a fresh-context reviewer for a one-line rename.
- Treating reviewer output as authoritative without re-reading the artifact.
- Looping >3 cycles without escalating.
- Prompting "is this good?" instead of "find issues".
- Skipping doubt under time pressure on a high-stakes decision.
- Re-spawning fresh-context on an unchanged artifact (same findings; you are stalling).
- **Doubt theater** — across 2+ cycles with substantive findings, zero classified as actionable. You are validating, not doubting. Stop, escalate.
- Doubting only after committing — that is post-PR review, not doubt-driven.
- Hardcoding an external CLI invocation without confirming the user has it installed.
- **Silently skipping cross-model in an interactive session.** Skipping is fine; silent skipping is not.
- Silently falling back when an external CLI errors or is missing.
- Stripping the contract from the reviewer's input.
- Passing the CLAIM to the reviewer — biases toward agreement.

## Interaction with other skills

- `code-review` — post-artifact, comprehensive, five-axis. Complementary: code-review is a final gate; doubt-driven is in-flight per-decision. Use both.
- `investigate-before-editing` — verifies facts about the codebase. Doubt-driven verifies your reasoning about the artifact.
- `test-driven-development` — TDD's RED step is doubt made concrete — a failing test is a disproof attempt. When TDD applies, that failing test **is** the doubt step for behavioral claims.
- `diagnose` — when a reviewer surfaces a real failure mode, drop into diagnosis.
- `llm-coding-discipline` — "push back when warranted" and "verify don't assume" are the default posture; doubt-driven is the sharpened version for high-stakes decisions.

## Verification checklist

After applying doubt-driven review:

- [ ] Every non-trivial decision was named as a CLAIM before it stood.
- [ ] At least one fresh-context review per non-trivial artifact (TDD's RED satisfies this for behavioral claims).
- [ ] The reviewer received ARTIFACT + CONTRACT only — NOT the CLAIM, NOT your reasoning.
- [ ] The reviewer's prompt was adversarial ("find issues"), not validating ("is it good").
- [ ] Findings were classified against the artifact text (not rubber-stamped) using precedence: contract misread / actionable / trade-off / noise.
- [ ] A stop condition was met (trivial findings, 3 cycles, or user override).
- [ ] In interactive mode, cross-model was **explicitly offered** to the user and the response was acknowledged.
- [ ] In non-interactive mode, cross-model was skipped and the skip was announced.
- [ ] Any external CLI invocation was preceded by a PATH check, a working-binary test, syntax confirmation with the user, and explicit authorization.
