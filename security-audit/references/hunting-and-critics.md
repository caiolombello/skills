# Hunting waves and coverage critics

Phase 2 of a full audit. The parent assigns `planned` ledger units to hunters, consolidates structured results into the ledger, and runs a coverage critic after every wave.

## Assignment

One hunter may own closely related units in one subsystem; do not bundle unrelated boundaries. No unit is silently skipped because of an agent limit — a unit the budget cannot reach is `deferred` with `budget_cannot_reserve_critics_and_validation`.

When budget or profile limits hunters, take units in this order and record the rationale in the ledger:

1. unauthenticated or lowest-trust surfaces before authenticated ones;
2. boundaries guarding the most valuable resources (credentials, cross-tenant data, code execution, release authority);
3. prior-run gaps, revalidation targets, and changed source before same-source re-passes;
4. classes that historically yield confirmed findings for this kind of target before speculative ones;
5. ties broken lexicographically by `coverage_id`.

Before launch, set each assigned unit to `in_progress` with a lowercase `agent_id`, and create that agent's `scratch/` and parent-owned `artifacts/`.

## Hunter brief

Give every hunter, in this order:

1. Role: find source-grounded security invariant failures in the assigned units and return exactly one JSON object matching the result contract below.
2. `architecture.md`, verbatim.
3. Assigned coverage IDs with subsystem, boundary, starting paths, and each unit's block map from the ledger.
4. The **text** of each selected block, copied — the core class from [attack-classes.md](attack-classes.md), and from each selected domain reference its discipline block, chosen classes, and validation block. Names alone are not enough.
5. Excluded blocks, each with its reason.
6. The hunting method from [../SKILL.md](../SKILL.md) (Hunting method), the candidate gate below, and the execution boundary block from [execution-safety.md](execution-safety.md).
7. Carried same-source prior confirmations to skip (fingerprint, title, root cause only) and peer-owned coverage IDs not to duplicate.
8. Its scratch path, agent ID, promotion allowlist with byte limits, the result contract below, and the `confirmed` and `needs_validation` branches of `scripts/report-schema.json` copied verbatim.

Scope is a coverage obligation, not permission to duplicate excluded work. A different boundary discovered along the way goes under `uncovered` so the parent can create a unit for it.

## Candidate gate for hunters

```text
1. A candidate needs a complete repository-relative source trace and evidence for the
   claimed root cause, including the strongest source-visible control on the path.
2. Proposing confirmed needs a bounded local observed result, impact across a stated
   boundary, complete conditions, and no visible preventing layer.
3. Do not upgrade a crash to code execution, ordinary work to shared outage, or a
   same-principal action to privilege gain.
4. A decisive fact outside source or local observation means needs_validation with the
   exact blocker. No severity, no speculative completion.
5. A missing best practice with no affected principal or resource is hardening, not a
   candidate. A claim source disproves is not needs_validation.
6. One root cause keeps one source-derived fingerprint in every state, matching
   ^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$ and containing no line, wave, agent, severity, or
   verdict.
7. If nothing survives, return an empty candidates array.
```

## Hunter result contract

Exactly one JSON object, no surrounding prose:

```json
{
  "units": [
    {
      "coverage_id": "one assigned ID",
      "disposition": "covered|candidate|blocked",
      "reviewed_paths": ["repo/relative/path"],
      "checks": [
        {
          "agent_id": "owner of this check",
          "reviewed_paths": ["repo/relative/path"],
          "invariant": "the specific control checked",
          "method": "source|local",
          "result": "what source or the bounded check established",
          "artifact": "agents/<agent-id>/artifacts/<file> for local, null for source"
        }
      ],
      "candidate_fingerprints": [],
      "unresolved": []
    }
  ],
  "candidates": [],
  "hardening": ["concrete non-finding note"],
  "uncovered": [
    {
      "surface": "...", "boundary": "...", "subsystem": "...", "attack_class": "...",
      "starting_paths": ["repo/relative/path"],
      "reason": "why this needs its own coverage unit"
    }
  ]
}
```

Rules:

- Every assigned ID appears exactly once in `units`. `covered` and `candidate` need nonempty paths and checks; only `candidate` carries fingerprints; `blocked` has paths, checks, and unresolved facts but no fingerprint; `covered` has no unresolved facts.
- Paths are repository-relative, never absolute or traversing. Unit `reviewed_paths` is the union of its checks' paths.
- Each candidate is shaped like a `report-schema.json` record but uses `proposed_verdict` instead of `verdict`:
  - `confirmed`: `fingerprint`, `title`, `description`, `root_cause`, `intended_behavior`, ordered `trace`, `evidence`, `conditions`, target-neutral `execution` (the bounded check already run, minimal `payloads`, actual `observed_result`), `remediation`, `severity`, `confidence`.
  - `needs_validation`: `fingerprint`, `title`, `description`, `claimed_root_cause`, ordered `trace`, `evidence`, nonempty `blockers`, and a `validation_plan` with at least one applicable `local` or `deployment` step. No severity, execution, remediation, or `root_cause`. A `deployment` step is something an owner observes, not a probe.
- A multi-entry trace starts at `entrypoint`, ends at `sink`, and uses `propagation` in between.

## Parent consolidation

Map each unit result to exactly one assigned ID and update only that unit. Reject duplicate or missing IDs, unsafe agent IDs, source checks with artifacts, and local artifacts the parent did not promote into the check owner's `artifacts/`. Copy paths, checks (into `local_checks`), fingerprints, and unresolved facts; keep `hardening` notes in a bookkeeping field for the report. A malformed or unsupported result leaves the unit `planned` for reassignment. Validate the ledger after each update; an invalid ledger cannot drive further assignment.

Consolidate candidates by fingerprint, then by root cause. One root cause reachable through several paths is one candidate with the strongest complete trace; independent missing controls get separate fingerprints. Record duplicates in the ledger and send each root cause to validation once.

## Coverage critics

Right after each wave, run one fresh critic that did not hunt. It gets `architecture.md`, the full ledger with block maps, current candidate fingerprints and states, and the prior-run gap summary. It reads source; it does not write or execute. It proposes coverage, not findings:

```json
{
  "missing_units": [
    {
      "surface": "...", "boundary": "...", "subsystem": "...", "attack_class": "...",
      "starting_paths": ["repo/relative/path"],
      "selected_companion_blocks": ["references/<file>.md#<block>"],
      "excluded_blocks": [{"block": "references/<file>.md#<block>", "reason": "..."}],
      "reason": "source-backed coverage gap"
    }
  ],
  "reassign_ids": ["existing ID that did not genuinely close"],
  "resolved_prior_leads": ["fingerprint"],
  "stop": false
}
```

The critic looks for unmapped entry points, unchecked parallel paths, missing lifecycle modes, selected domain classes without a unit, unjustified exclusions, units closed without real paths or checks, and prior `needs_validation` or changed-source gaps no unit addresses. `stop: true` only when it proposes nothing.

The parent rejects proposals outside scope or the execution boundary, derives IDs for accepted units, deduplicates, and fails rather than merging collisions. For each legitimate reassignment, archive the live attempt (see the reassignment archive in [reconnaissance-and-coverage.md](reconnaissance-and-coverage.md)) and assign a fresh owner. Mark resolved prior leads with the critic's reason.

Loop, by profile:

- **`standard` / `deep`:** when a post-wave critic accepts nothing and no `planned` units remain, run a separate **final-clean critic**. Coverage is complete only if it also finds nothing; otherwise queue its work and repeat wave → critic → final-clean.
- **`quick`:** one wave, one final critic. Accepted missing units are added as `deferred` (`quick_profile_final_critic`); reassignments archive the attempt and set the live unit `deferred` with the same reason. No second wave.
- **Scoped runs:** gaps outside scope are recorded `out_of_scope` with the critic's reason.
- **Budget or time stop:** mark untouched units `deferred` with the reason and disclose the gap. A silent wave cap is never evidence of complete coverage.

Critic-proposed units join the same priority queue and do not extend the budget.
