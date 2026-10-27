# Select a method and interpret its evidence

Use this when the question does not already have an established project verifier. Verify current official documentation and the actual tool version before writing version-sensitive commands. These are choices, not dependencies installed by this skill.

| Question | Potential method | What the result does not automatically establish |
| --- | --- | --- |
| Can interleaved actions reach a bad state? | Small explicit state model, such as TLA+/TLC | Concrete implementation follows the abstraction, or arbitrary larger instances are safe |
| Does this C/C++ code violate an assertion, pointer or arithmetic check? | Suitable code-level verifier, such as CBMC | Loops, environment, libraries and numeric behavior outside the actual harness/options |
| Does a property hold for every size/input in a mathematical domain? | A suitable proof assistant/verifier with explicit obligations | The executable, compiler/runtime and all external assumptions implement the proved definitions |
| Can sampled/generated inputs expose a bug quickly? | Existing tests, fuzzing, property-based testing | Exhaustive exploration or universal proof from a finite sample |

Use the lowest-cost method that answers the actual question. Tool unavailability is an environment fact: provide a useful static model/plan or bounded fallback when authorized, label it accurately, and do not fabricate a verifier invocation or change approval settings. A general SMT solver result only answers the formula actually encoded. Interpret satisfiable/unsatisfiable/unknown against that encoding; neither sat nor unsat is a universal success label.

## TLA+/TLC

Specify initial states and possible next actions, safety invariants and any separate temporal properties. Make the finite constants/domains, state/action constraints, fairness, symmetry/view reductions and stuttering/termination choices explicit. Explain how each affects the claim. A model that excludes the failing execution through a constraint has not established safety outside that constraint.

Liveness needs its own progress/fairness assumptions and appropriate tool run; a finite safety pass alone does not prove eventual completion. Deadlock checking can classify a valid terminal state as stuck if termination was modeled incorrectly. Model legitimate termination deliberately rather than globally disabling a useful check to conceal a real deadlock.

Inspect the actual run's completion, errors, warnings, states/properties and limits. Random simulation is not exhaustive model checking. Do not turn a state cap or missing liveness analysis into a proof. Different states merged for presentation can hide a distinction relevant to an invariant; a diagram is an explanation, not additional evidence.

## Code-level verification and proofs

Record the code/harness revision, entry point, preconditions, language/machine semantics, external-call models and enabled checks. For a bounded checker, name loop/recursion/input bounds and whether coverage/unwinding obligations were discharged; successful checks under a partial unwind do not cover larger executions. For a proof assistant, inspect remaining assumptions, admitted obligations, axioms or incomplete steps before reporting a theorem as checked.

Check reachability and satisfiability of relevant preconditions. A disabled action, contradictory assumptions or unreachable assertion can produce a vacuous success. Compare important abstractions with real source: one atomic storage operation in a model is not equivalent to several unlocked read/check/write operations in code.

## Calibrate and replay

A useful negative variation changes the guarded behavior, not syntax or the expected answer. Preserve the original artifact, use disposable copies, keep resource limits, and confirm the specific property fails. Return to the unmodified version and rerun affected checks. Failure to detect a realistic variation is a coverage/correspondence issue to investigate; do not modify the variation until the checker is happy.

Trace a counterexample through actual code states/inputs. Separate impossible model steps, plausible but unreplayed failures, and reproduced implementation defects. A test replay confirms that scenario; it does not replace broader formal coverage. A toy example or finite model in this library establishes nothing about a user's production system.

## Primary references

- [TLC model checker](https://docs.tlapl.us/using:tlc:start) and [official TLA+ tools](https://github.com/tlaplus/tlaplus).
- [CBMC documentation](https://diffblue.github.io/cbmc/cprover_documentation.html) and [command/reference options](https://diffblue.github.io/cbmc/man/cbmc.html).

Reviewed on 2026-10-27. Commands and support must be checked for the actual installed version; these links are not a promise that a tool is available or a license to download/run it in every task.
