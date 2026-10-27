# Isolated two-actor calibration example

Use only to learn/test this skill's procedure, never as proof about a real lock, runtime or personal project. The [Claim model](../evals/fixtures/Claim.tla) and [reference reducer](../evals/fixtures/claim.py) describe exactly two actors, finite sets `owners`/`ready`, and check/take/release actions. Each reducer call is treated as atomic in this example; no OS scheduling, real threads, persistence, timeouts or liveness claim is represented.

The invariant is at most one owner. Both actors may check readiness while no one owns the resource. The safe take action rechecks ownership atomically; a guard-removal variation takes from stale readiness and can create two owners. A model of a real implementation would need independent justification of these atomicity/coverage assumptions.

## Run in scratch

Use an already available, verified TLC jar and compatible Java; do not download/install them automatically. Copy the example files to a fresh scratch directory. The tool may write state/trace files, so keep those outside the skill source and active projects. Inspect live help/version first. Example invocation for the inspected TLC CLI, replacing placeholders with actual paths:

```sh
java -Xmx256m -cp /absolute/path/tla2tools.jar tlc2.TLC -workers 1 -config safe.cfg Claim
java -Xmx256m -cp /absolute/path/tla2tools.jar tlc2.TLC -workers 1 -config racy.cfg Claim
```

The 256 MiB heap is an example bound for this tiny fixture, not a project-wide recommendation. Keep separate output/log directories or the supported per-run metadata directory when rerunning; use an owned JVM temporary directory when isolation requires it. Bound wall time with the execution harness. Inspect completion and the actual property result, not just whether Java launched. The safe finite model should complete without a violation. The racy configuration should report a `SingleOwner` violation; syntax errors, tool errors or timeouts do not count as successful negative calibration. No result or state count is prefilled as evidence.

## Replay the causal sequence

In a disposable copy of `claim.py`, remove only the `or owners` part of the take guard. Keep the unmodified file and its hash. Starting from `(frozenset(), frozenset())`, call `step` in this order: actor 1 check, actor 2 check, actor 1 take, actor 2 take. The mutant can end with owners `{1, 2}`. The safe reducer refuses the last take (`None` means disabled), so it retains one owner. Compare this sequence with the actual TLC trace; actor order can be symmetric.

This exercises a concrete guard change and code replay. Manually changing a model to match a toy reducer does not prove correspondence for arbitrary production code. Preserve both model/config and code snapshots, mutation delta, checker logs, actual trace/replay and limits. Recheck the unchanged safe copy after calibration and report the two-actor safety claim only.
