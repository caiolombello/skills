# Validation, structured output, verification, and reports

Phases 3–6 of a full audit. The parent stays the only writer of shared files. "Fresh verifier" means a role with isolated context; when only sequential passes are possible, follow the fresh-notes procedure and disclosure rule in [full-audit-workflow.md](full-audit-workflow.md).

## Phase 3 — validate every candidate

After the final clean critic (or a recorded early stop), consolidate hunter candidates and carried prior records by fingerprint and root cause. Give each unique candidate to a fresh verifier that did not hunt it. Carried prior confirmations go through the same path.

The verifier gets its own `agents/<id>/scratch/` and receives only: the candidate, its linked ledger checks and artifact paths, the architecture facts needed to interpret it, the relevant domain validation block, the execution boundary block from [execution-safety.md](execution-safety.md), the `confirmed`, `needs_validation`, and `rejected` branches of `scripts/report-schema.json` verbatim, and prior records with the same fingerprint. Never another verifier's conclusion.

Verifier brief:

```text
You did not write this candidate. Try to refute it from repository source and
bounded local evidence, within the execution boundary below.

1. Re-read every cited trace and evidence location; check line, scope, and wording.
   The first entry must be a real lower-trust entrypoint, the last the claimed sink or
   boundary effect.
2. Reconstruct the strongest source-visible validation, identity, authorization,
   normalization, lifecycle, framework, and containment controls on the path. Use a
   comparable-software baseline only as calibration.
3. For proposed confirmed: independently reproduce the minimum result when possible;
   verify input shape, conditions, and the affected dummy principal or resource. Do
   not infer anything stronger than observed.
4. Check that likelihood, impact, confidence, and the proposed fix match only what the
   evidence shows.
5. For proposed needs_validation: is the blocker genuinely outside source and local
   observation? If source refutes the trace, reject. If the fact is still decisive,
   keep needs_validation and make the local and owner-observed plans exact and
   non-destructive.
6. Keep the fingerprint for the same root cause.

Return exactly one JSON object, no prose:
{"decision": "confirmed|needs_validation|rejected", "record": { ... }}
The record must match that verdict's schema branch exactly.
```

Transitions: promote to `confirmed` only with an independently established path and bounded observed result; demote to `needs_validation` when a specific deployment or runtime fact remains unknown; `rejected` when source, local behavior, a visible control, missing impact, or an impossible prerequisite refutes the claim.

The parent checks the fingerprint is unchanged unless a genuinely different root cause was found, merges corrections, records the decision in every linked unit, and keeps one record per fingerprint. A malformed or prose-wrapped result is discarded, not repaired; re-run with a fresh verifier if budget allows, otherwise the candidate stays unvalidated under the incomplete-run rule. Verifier checks are added to the unit's `local_checks` under the verifier's own `agent_id`; the unit keeps its assignment owner. For a carried prior record's seeded unit, the verifier becomes the owner and its re-check is the first check.

## Phase 4 — write and validate `findings.json`

Write all decided records to `<output-dir>/findings.json`, sorted by fingerprint. Read `scripts/report-schema.json` right before writing: it uses `additionalProperties: false`, so do not carry hunter wrapper fields such as `proposed_verdict`.

| Verdict | Must have | Must not have |
|---|---|---|
| `confirmed` | `root_cause`, `intended_behavior`, `trace`, `evidence`, `conditions`, `execution` (native interface: HTTP, CLI, library call, message, fixture, browser action, rendered policy, or harness; factual `observed_result`), `remediation`, `severity` (`likelihood`, `impact`, `overall_severity`), `confidence` | `claimed_root_cause`, `blockers`, `validation_plan`, `reason` |
| `needs_validation` | `claimed_root_cause`, `trace`, `evidence`, nonempty `blockers`, `validation_plan` with `local` and/or `deployment` (both only when they resolve different facts) | severity, execution, remediation, reason, `root_cause` |
| `rejected` | `claimed_root_cause`, `trace`, `evidence`, `reason` | severity, execution, remediation, blockers, validation plan, `root_cause` |

Every record has `verdict`, a stable `fingerprint`, `title`, `description`, and repository-relative paths. Overall severity never exceeds demonstrated impact.

```sh
node <skill-dir>/scripts/validate-findings.cjs <output-dir>/findings.json
node <skill-dir>/scripts/validate-coverage-ledger.cjs <output-dir>/coverage-ledger.json
```

Fix every error. The findings validator rejects input over 5 MiB, 1,000 records, or 64 nesting levels and caps output at 100 errors. Passing proves format and consistency, not truth.

## Phase 5 — verify final records with fresh eyes

One fresh verifier per final `confirmed` and `needs_validation` record, checking the structured record (not the hunter write-up) within the execution boundary. In `quick`, Phases 3 and 5 merge into one fresh verifier per candidate; every other profile keeps them separate. No profile skips independent review of a `confirmed` record.

For `confirmed`, check: every path, line, scope, and operation; the real entry interface and exact input; each condition, parser or policy step, and preventing layer; the observed result; affected principal and demonstrated impact; likelihood versus impact with overall not above impact; and whether the remediation enforces the invariant instead of moving trust.

For `needs_validation`, check: the source path supports only the stated `claimed_root_cause`; each blocker is decisive and not answerable locally; the record names a boundary and a possible concrete result, not a generic worry; the plan is exact (`local` uses a bounded fixture, `deployment` asks an owner to observe a configuration, identity, route, policy, or runtime fact — never audit traffic); the fingerprint matches prior and current records.

Return exactly `{"decision":"verified","fingerprint":"..."}` or `{"decision":"replace","reason":"...","record":{...}}`. Malformed results are discarded and re-run as in Phase 3.

A **material** replacement — any promotion to a stronger verdict, or a change to root cause, trace, execution input, observed result, impact, or severity — is not applied until a further fresh verifier (one that did not hunt, validate, or propose it) re-checks source, reproduces any decisive local result, and returns `verified`. Repeat if it proposes another material change. If budget or independence runs out, remove the disputed record from `findings.json`, keep its unit as an unresolved candidate, and set `run_status: "incomplete"` with the exact reason. Wording or line corrections that do not change meaning may be applied directly.

After every applied replacement, rerun both validators and update linked ledger decisions. A newly identified separate root cause gets a new fingerprint and goes through Phase 3 first. Set `run_status: "complete"` only when every ledger candidate has a final disposition and every retained record passed Phase 5.

## Phase 6 — reports derived from records

Write prose only after Phase 5, from the final records, the ledger, and retained hardening notes. Prose never changes a verdict, severity, blocker, or impact. No live-probe instructions anywhere.

**`REPORT.md`**

1. Run facts: profile, scope, budget spent versus planned, source ref, the statement that execution was sandboxed source-and-local only (or that no target code ran), prior-run use including carried confirmations and changed-source revalidations, deferred and out-of-scope coverage, and how independence was achieved. `quick`, scoped, budget-limited, or incomplete runs say plainly they are partial; list unvalidated fingerprints and any critic that did not run, and make no clean-coverage claim.
2. A short security posture summary.
3. Confirmed findings table: severity, title, affected boundary, one-line observed result.
4. Per confirmed finding: source location, lower-trust principal, native bounded reproduction, conditions, actual result, impact, priority rationale, smallest source fix and regression test.
5. A separate **Needs validation** table: title, trace, exact blocker, bounded local next step, safe owner-observed check. No severity; not called vulnerabilities.
6. Hardening notes and positive patterns, separately.
7. Coverage summary from the ledger: covered, candidate, blocked, deferred counts; important exclusions; final critic result.

Rejected records are not findings; mention fingerprints only to explain a prior disagreement or coverage decision.

**`FINDINGS-DETAIL.md`** — for each confirmed `medium`, `high`, or `critical`: ordered trace and evidence, dummy actor and affected dummy resource, native input and exact bounded steps, observed output and the invariant it proves, conditions and containment, remediation and regression case.

**`NEEDS-VALIDATION.md`** — for each unresolved record: trace, verified evidence, exact blocker, affected boundary, and each applicable bounded local or owner-observed plan, as prioritized leads without severity.

HTTP is one native interface among many: a library finding uses a function call, a parser a fixture, a CLI a command, a desktop app an IPC or file action, infrastructure a rendered policy. A clean run may have zero confirmed findings — say so with the remaining limits instead of inventing low-severity items.
