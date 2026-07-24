---
name: diagnose
description: Use when tests fail, builds break, behavior is wrong/flaky/slow, a regression appears, or a fix is about to land without a reproducible failure. Reproduce first, then hypothesise.
---
<!-- Inspired by mattpocock/skills engineering/diagnose (MIT) and addyosmani/agent-skills debugging-and-error-recovery (MIT). See ../CREDITS.md -->

# Diagnose

A disciplined loop for hard bugs. Skip phases only when explicitly justified, and never skip Phase 1.

Before exploring the code, read `CONTEXT.md` if the repository provides one and check nearby ADRs. Use them to learn the module vocabulary and constraints; do not invent a context file or decision record when none exists.

## Stop-the-line rule

The moment something unexpected happens:

1. **STOP** adding features or making changes.
2. **PRESERVE** the evidence: exact error message, stack trace, logs, the command that produced it, environment (OS, versions, branch, commit).
3. **DIAGNOSE** using the phases below.
4. **FIX** the root cause, not the symptom.
5. **GUARD** with a regression test if a correct seam exists.
6. **RESUME** other work only after verification passes.

Do not push past a red build or a failing test to "work on the next thing". Errors compound. A bug at step N makes every decision at step N+1 wrong.

## The phases

```
1. FEEDBACK LOOP   → a fast, deterministic pass/fail signal for the bug
2. REPRODUCE + MINIMIZE → run the loop, confirm it shows the user's bug, then shrink it
3. HYPOTHESISE     → 3-5 ranked, falsifiable hypotheses before any fix
4. INSTRUMENT      → one probe per hypothesis, one variable at a time
5. FIX + REGRESSION TEST → minimal fix, protected by a test if a seam exists
6. CLEANUP + POST-MORTEM → remove instrumentation, state the root cause
```

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. Given a fast, deterministic, agent-runnable pass/fail signal for the bug, you *will* find the cause — bisection, hypothesis-testing, and instrumentation all just consume that signal. Without it, no amount of reading source code will save you.

Spend disproportionate effort here. **Be aggressive. Refuse to give up.**

### Ways to construct a loop (try roughly in this order)

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **HTTP invocation** — `curl` or a one-off script against a dev server.
3. **CLI invocation** with a fixture input, diff stdout against a known-good snapshot.
4. **Headless browser** (Playwright / Puppeteer) — drives the UI, asserts on DOM / console / network.
5. **Replay a captured trace** — save a real request / payload / event log to disk; replay through the code path in isolation.
6. **Throwaway harness** — minimal subset of the system (one service, mocked deps) that exercises the bug path with a single function call.
7. **Property / fuzz loop** — if the bug is "sometimes wrong output", run 1000 random inputs and watch for the failure.
8. **Bisection harness** — if the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so `git bisect run` can drive it.
9. **Differential loop** — run the same input through old-version vs new-version (or two configs); diff outputs.
10. **HITL bash script** — last resort. If a human must click, drive them with a structured script and capture output that feeds back to the agent.

**Build the right feedback loop and the bug is 90% fixed.**

### Iterate on the loop itself

Treat the loop as a product. Once you have *a* loop, ask:

- **Faster?** Cache setup, skip unrelated init, narrow test scope.
- **Sharper signal?** Assert on the specific symptom, not "did not crash".
- **More deterministic?** Pin time, seed RNG, isolate filesystem, freeze network, disable retries.

A 30-second flaky loop is barely better than no loop. A 2-second deterministic loop is a debugging superpower.

### Non-deterministic bugs

The goal is not a clean repro but a **higher reproduction rate**. Loop the trigger 100×, parallelise, add stress, narrow timing windows, inject sleeps.

```
Cannot reproduce on demand:
├── Timing-dependent?
│   ├── Add timestamps to logs around the suspected area
│   ├── Add artificial sleeps to widen race windows
│   └── Run under load / concurrency to increase collision rate
├── Environment-dependent?
│   ├── Compare runtime versions, OS, env vars
│   ├── Check for data differences (empty vs populated DB)
│   └── Try reproducing in CI where the environment is clean
├── State-dependent?
│   ├── Check for leaked state between tests / requests
│   ├── Look for globals, singletons, shared caches
│   └── Run the failing scenario in isolation vs after other ops
└── Truly rare?
    ├── Add defensive logging at the suspected location
    ├── Set up an alert on the error signature
    └── Document observed conditions and revisit when it recurs
```

A 50%-flaky bug is debuggable; 1% is not — keep raising the rate until it is.

### When you genuinely cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for either:

- **Access** to an environment that reproduces it.
- **A captured artifact** — HAR file, log dump, core dump, screen recording with timestamps.
- **Permission to add temporary instrumentation** in the environment that exhibits the bug.

Do **not** proceed to hypothesise without a loop. A hypothesis without a loop is a guess, and guesses ship wrong fixes.

## Phase 2 — Reproduce + minimize

Run the loop. Watch the bug appear. Confirm:

- [ ] The loop produces the **exact failure the user described** — not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] The failure is reproducible across multiple runs (or at a high enough rate to debug against).
- [ ] You have captured the exact symptom (error message, wrong output, timing) so later phases can verify the fix.

Do not proceed until you reproduce the bug.

### Minimize the reproduction

Once the loop is red, remove inputs, callers, configuration, data, and steps one at a time. Keep only what is load-bearing for the failure, rerunning the loop after each reduction. The minimized case becomes the regression test and narrows the hypothesis space.

Do not proceed to Phase 3 until the failure is reproduced and minimized, unless a reduction would destroy the only evidence of an environment-dependent failure; record that exception explicitly.

## Phase 3 — Localize + hypothesise

First narrow where the failure lives:

```
Which layer?
├── UI / frontend        → browser console, DOM, network tab
├── API / backend        → server logs, request/response shape
├── Database             → query plan, schema, data integrity
├── Build tooling        → config, dependencies, environment
├── External service     → connectivity, upstream change, rate limit
└── The test itself      → false negative? wrong assertion?
```

Then generate **3-5 ranked hypotheses** before testing any of them. Single-hypothesis generation anchors on the first plausible idea.

Each hypothesis must be **falsifiable**:

> Format: "If `<X>` is the cause, then `<changing Y>` will make the bug disappear / `<changing Z>` will make it worse."

If you cannot state the prediction, the hypothesis is a vibe — discard or sharpen it.

**Show the ranked list to the user before testing.** They often have domain knowledge that re-ranks instantly ("we deployed a change to #3 yesterday") or know which hypotheses are already ruled out. Cheap checkpoint, big time saver. Proceed with your ranking if the user is AFK.

### Regression bugs: bisect

If the bug appeared between two known states, do not guess — bisect.

```bash
git bisect start
git bisect bad                    # current commit is broken
git bisect good <known-good-sha>  # this commit worked
git bisect run <your-feedback-loop>
```

The loop from Phase 1 is the oracle. If `git bisect run` can drive it, the bad commit falls out mechanically.

## Phase 4 — Instrument

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

Tool preference:
1. **Debugger / REPL inspection** if the environment supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundary that distinguishes hypotheses.
3. **Never** "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end is a single `grep` + delete. Untagged debug logs survive cleanup; tagged ones do not.

### Perf branch

For performance regressions, logs are usually wrong. Instead:

1. Establish a **baseline measurement** (timing harness, `performance.now()`, profiler, query plan).
2. Apply the suspected change in isolation.
3. Measure again. Report the delta with the same harness.
4. Bisect. Measure first, fix second.

## Phase 5 — Fix + regression test

Write the regression test **before the fix** — but only if there is a **correct seam** for it.

A correct seam exercises the **real bug pattern** at the call site where it manifests. If the only available seam is too shallow (unit test that cannot replicate the chain that caused the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The architecture is preventing the bug from being locked down. Flag for Phase 6.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the **original (un-minimised) scenario** to confirm the fix holds in the real context.

Fix the **root cause**, not the symptom. If the fix is a `try/catch` around the error without changing what threw, ask whether you understood the cause.

## Phase 6 — Cleanup + post-mortem

Required before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop).
- [ ] Regression test passes (or absence of a seam is documented).
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix).
- [ ] Throwaway harnesses / prototypes deleted or moved to a clearly-marked debug location.
- [ ] The hypothesis that turned out correct is stated in the commit / PR message — so the next debugger learns.
- [ ] Any secrets, tokens, or production data used in reproduction are scrubbed.

**Then ask: what would have prevented this bug?** If the answer involves architectural change (no good test seam, tangled callers, hidden coupling), surface it as a follow-up after the fix is in. You have more information now than when you started.

## Anti-patterns

| Anti-pattern | Why it fails | Do instead |
|--------------|--------------|-----------|
| Patch the symptom (wrap in try/catch, add a null check) without understanding why | Bug comes back in a different shape | Phase 1-3: reproduce, then hypothesise |
| "Log everything and grep" | Drowns in noise, hides the signal | Targeted probes, one per hypothesis |
| Single hypothesis | Anchors on first plausible idea | Force 3-5 ranked, falsifiable |
| Fix without reproducing | You do not know if it worked | Phase 2 is mandatory |
| Keep debug logs in the commit | Pollutes the codebase | Tag with `[DEBUG-...]`, grep-delete in Phase 6 |
| Claim it is a "flaky test" without investigating | Flakes hide real bugs | Raise reproduction rate until it is debuggable |
| Declare done because "it seems to work now" | Not the same as "I proved it works" | Re-run the original loop; regression test if a seam exists |

## Interaction with other skills

- `test-driven-development` — the regression test in Phase 5 *is* TDD's RED → GREEN for the bug.
- `investigate-before-editing` — before Phase 3 hypotheses, read the relevant code. Do not theorise about unread modules.
- `llm-coding-discipline` — "verify, don't assume" and "surgical changes" apply: do not "clean up" adjacent code mid-diagnosis.
- `code-review` — once the fix is in, review it with the same rigor as a feature.
- `git-hygiene` — the fix commit message states the root cause (not "fix bug").

## Verification checklist

Before declaring the bug fixed:

- [ ] A feedback loop exists and produces the exact symptom the user described.
- [ ] 3-5 ranked, falsifiable hypotheses were written down; the correct one is stated.
- [ ] The fix addresses the root cause, not a symptom.
- [ ] The original feedback loop now passes.
- [ ] A regression test exists at a correct seam, or the absence is documented.
- [ ] All `[DEBUG-...]` instrumentation is removed.
- [ ] Commit message names the root cause.
- [ ] If architectural change would have prevented the bug, it is surfaced as a follow-up.
