---
name: formal-verification
description: "Use to model-check consequential state/concurrency behavior, verify a stated invariant, or create/maintain project-local formal checks as covered code evolves. Ordinary test execution, simple CRUD and routine fixes do not need formal methods."
---

<!-- Inspired by pstack create/maintain-formal-verification-skill (MIT). See ../CREDITS.md. -->

# Formal Verification

Establish a precise property and the evidence that supports it within a stated scope. Creating a model, passing its checker, validating its correspondence to code, and proving a deployed implementation are different results. Never let the word "formal" replace those distinctions.

## Choose a useful target

Start with the user's named property/area. Otherwise identify a concrete consequential promise where concurrency, retries, state transitions, input bounds, arithmetic or memory safety makes ordinary examples weak. State the property and the harm of a violation in plain words. Prefer one meaningful property over a broad model of everything.

Scale the method to the question and cost. A routine regression belongs to [diagnose](../diagnose/SKILL.md) and [test-driven-development](../test-driven-development/SKILL.md); a reusable real-app procedure belongs to [project-verification](../project-verification/SKILL.md). Generated-input testing is useful but is not automatically a formal proof. Do not trigger a prover for every code edit or create proof infrastructure just to run existing tests.

Read applicable rules, the contract, actual covered implementation, relevant callers/state writers, tests and any existing model/harness. Establish the authorized endpoint and permitted execution. A proof-only or static-only request does not authorize editing product code, running arbitrary artifacts, installing tools or injecting failures into active systems. Reuse existing authorization for isolated verification work.

## Create or extend a check

1. **Frame the claim:** property, domain, initial states, environmental assumptions, safety versus liveness, and intended scope. Identify important excluded behavior. Check that assumptions do not make the property vacuous.
2. **Choose the tool:** use an existing suitable project verifier first. Read [methods and evidence](references/methods-and-evidence.md) when choosing a model checker, code verifier, proof assistant or fallback. Verify the installed/pinned tool and actual command; no automatic toolchain installation.
3. **Connect to code:** map states/actions or proof obligations to real symbols and the checked revision/hashes. Respect atomicity, interleavings, numeric domains, persistence, failures and other relevant boundaries. An indivisible model step must have a justified relation to the implementation. Missing state writers or runtime assumptions remain gaps.
4. **Run within limits:** use an isolated scratch/output directory, deliberate time/memory/state bounds and actual configuration. Preserve tool/version, inputs, command, exit/output and per-property status. A timeout, state cap, solver unknown, parse error or unvisited obligation is incomplete, not passing. A passing syntax check is not model checking.
5. **Challenge the check:** where useful and permitted, make a realistic failing variation in disposable code/model state and confirm the intended property fails for the intended reason. A mutation run that only hits a syntax error has not calibrated the property. If this cannot be done within scope, say so; do not widen authorization or discard a sound theorem solely because no mutation was run.
6. **Reconcile findings:** tell the counterexample in implementation terms and replay it against the actual code when authorized and feasible. If a step cannot occur, investigate abstraction/model error first; an unexecuted plausible trace remains a candidate. Do not weaken a property, remove an assumption's inconvenient case or shrink a bound merely to get green.

For a reusable project-local verification skill, put its actual command, relevant prerequisites, covered symbols, property/configuration, assumptions/bounds, known exclusions, artifact location, and last code-correspondence revision in the project's native location. Keep it small enough to rerun and maintain. A procedure that has not run is a draft. Use the [check record](references/check-record.md) when several claims or versions need traceable evidence; do not generate paperwork for a single existing check.

## Maintain a check

Use [maintenance and drift](references/maintenance.md) after covered code changes, merges/refactors skipped verification, or a review asks whether the model is still true to the code. An old green result is not transferable by filename or date. Keep creation and upkeep in this skill rather than separate always-loaded workflows.

Under maintenance-only authorization, edit verification artifacts and report product findings. Do not silently change production code or the promised behavior. A property change needs evidence of an intended contract change under current instructions, not merely a failing implementation.

## Report precisely

Give each property its actual result: verified within named model/bounds/assumptions; violation with replay status; stale correspondence; or incomplete/unavailable. Do not collapse checked and unvisited properties into one green badge. Separate tool result, code correspondence, calibration, code replay/tests, CI, required human approval and production evidence. A verified abstract model does not prove all inputs, real scheduling or implementation correctness.

State the checked source/configuration/tool versions, relevant bounds and assumptions, findings in plain language, evidence paths, what remains outside coverage and the reproducible next step. Update the correspondence marker only after actually checking that relation; record tool results separately. Do not create a PR, publish, deploy or auto-fix a discovered bug beyond the authorized endpoint.

An [isolated two-actor example](references/example.md) illustrates a bounded pass, guard-removal counterexample and code replay. [Decision cases](evals/scenarios.json) exercise scope and evidence; neither certifies any personal project or provider.
