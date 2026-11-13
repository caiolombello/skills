# Reconnaissance and coverage ledger

Phase 1 of a full audit. Reconnaissance reads the target and locally available build and configuration state only. It does not run target code and does not contact deployed endpoints, identity providers, registries, brokers, or cloud APIs.

Apply the budget gate in [full-audit-workflow.md](full-audit-workflow.md) first. If it fails, record the incomplete status and start nothing.

## Reconnaissance roles

Four mapping passes, in parallel when the host can delegate, sequentially otherwise. Each returns structured facts with repository-relative `file:line` references to the parent and writes no files.

**Product and local operation.** Product type, users, operators, and ordinary trust-sensitive actions. Languages, frameworks, build system, runtimes, and source-visible deployment models. Entry points and subsystem boundaries. Build and test commands that could run offline with local dependencies, where they write, and which target-controlled inputs they process — listed, not run. Comparable software or protocol, only when source-grounded. Missing toolchains that limit local checks.

**Principals and controls.** Every lower-trust principal and its by-design actions. Authentication or peer identity per entry surface. Per-resource authorization and tenant/owner scoping. Process, browser, workload, CI, plugin, model/tool, device, and local-IPC authority. Privilege changes, confirmation, revocation, recovery, and fallback paths. Which controls are source-visible and which depend on an unobserved deployment fact.

**Entry surfaces and sinks.** Every place external or lower-trust input enters: HTTP/browser, RPC/messages, files/archives/documents, CLI/env/config, plugins/dependencies/CI, cloud events and IAM selectors, model context and tool arguments, mobile deep links and webviews, local IPC. For each, major transformations, stored or derived copies, security-relevant sinks, source-visible limits, and parallel paths to the same effect. No inputs are sent.

**Local execution and deployment visibility.** Existing offline tests or fixtures that could check trust boundaries with dummy data in the sandbox. Processes that could run on isolated loopback. Commands that would fetch dependencies, publish, call paid or provider APIs, or touch shared state — marked prohibited. Deployed controls that source cannot establish (future `needs_validation` blockers). Whether the host can enforce each sandbox control and the scratch-promotion rules in [execution-safety.md](execution-safety.md); any missing control blocks target execution for the whole run.

Add focused mapping passes for materially distinct deployment modes or subsystems these four do not cover. If the budget cannot fund one, seed the unmapped area as a `deferred` unit (`budget_cannot_reserve_critics_and_validation`) and disclose the gap.

## Architecture summary

The parent writes `<output-dir>/architecture.md`, capped at about 1,000 words:

1. Product, principals, normal authority, protected resources.
2. Comparable-software baseline, when source-grounded: which trade-offs it accepts. Calibration only — never grounds to dismiss a demonstrated finding; a shared defect pattern that has mattered in practice strengthens a finding.
3. Stack, source-visible deployment paths, offline build/test limits.
4. Entry surfaces and the important source-to-sink or lifecycle paths.
5. Trust boundaries and the strongest source-visible control on each.
6. Repository-relative starting paths.
7. Prior-run gaps, revalidation targets, and same-source carried exclusions.
8. Selected domain references and the boundary that justifies each.

Per-unit block selections belong in the ledger, not here, so the cap holds on large runs.

Select a domain reference because reconnaissance found its boundary, not because a language or dependency name appears. Do not drop a visible boundary because a related class is covered elsewhere.

## Coverage ledger

The parent writes `<output-dir>/coverage-ledger.json`: a top-level JSON array with one unit per material combination of **entry surface × trust boundary × subsystem × attack class** (plus lifecycle mode in `deep` or where material). `quick` coarsens subsystem to the fixed value `profile/quick/all-in-scope-subsystems`. Scoped runs seed in-scope units for work and record discovered excluded surfaces as `out_of_scope`.

The ledger is the coverage claim. An architecture paragraph, an agent count, or "auth was reviewed" is not coverage evidence.

### Canonical references and IDs

Each dimension has a human label and a stable source-derived value under `canonical_refs`: a repository-relative entry path plus route or exported symbol, the source control that defines a boundary, a package path, and the exact attack-class block. Reuse the same reference for the same source object across runs even if its label changes. Do not lowercase or slug labels.

Block references are `<file relative to skill dir>#<exact bold class name or heading>`, for example `references/attack-classes.md#Access control` or `references/domain-web-and-client.md#Ordinary CSRF`. For domain discipline and validation blocks use their heading text, e.g. `references/domain-web-and-client.md#Web and identity discipline`.

`coverage_id` is lossless: each reference must be NFC Unicode with visible content and no control, format, separator, or default-ignorable characters and no surrounding whitespace; percent-encode its UTF-8 bytes leaving only `A-Z a-z 0-9 - . _ ~` unescaped (uppercase `%HH`); join encoded `surface`, `boundary`, `subsystem`, `attack_class` with `::`, appending `lifecycle` when present. The validator recomputes the ID and reports the expected value on mismatch; `canonicalCoverageId` is also exported by `scripts/validate-coverage-ledger.cjs`.

Never put wave, agent, verdict, severity, or line numbers in a reference or ID. Sort units by `coverage_id` before each assignment. Duplicate IDs fail; duplicate IDs with different semantic fields are an identity collision — never merge or overwrite.

### Unit shape

```json
{
  "coverage_id": "src%2Froutes.ts%23POST%20%2Finvoices%2F%3Aid::src%2Fauthz.ts%23requireTenantMember::packages%2Fbilling::references%2Fattack-classes.md%23Access%20control",
  "canonical_refs": {
    "surface": "src/routes.ts#POST /invoices/:id",
    "boundary": "src/authz.ts#requireTenantMember",
    "subsystem": "packages/billing",
    "attack_class": "references/attack-classes.md#Access control"
  },
  "surface": "Update invoice endpoint",
  "boundary": "Tenant membership check",
  "subsystem": "Billing API",
  "attack_class": "Access control",
  "starting_paths": ["src/routes.ts", "src/authz.ts"],
  "ordinary_attack_class_block": "references/attack-classes.md#Access control",
  "selected_companion_blocks": [
    "references/domain-data-messaging-availability.md#Data isolation discipline",
    "references/domain-data-messaging-availability.md#Missing tenant or owner enforcement",
    "references/domain-data-messaging-availability.md#Data isolation validation"
  ],
  "excluded_blocks": [{"block": "references/domain-web-and-client.md#Ordinary CSRF", "reason": "Route requires a bearer header, no ambient cookie."}],
  "prior_status": "none",
  "attempts": [],
  "wave": 1,
  "status": "planned",
  "agent_id": null,
  "reviewed_paths": [],
  "local_checks": [],
  "result_fingerprints": [],
  "unresolved": []
}
```

Add `canonical_refs.lifecycle` and a human `lifecycle` together, or neither. `ordinary_attack_class_block` is null only when no core class applies. Selected domain blocks include the domain's discipline block, each chosen class, and its validation block; `excluded_blocks` lists every considered but unselected block with the source fact that excludes it.

`prior_status` values: `none` (no compatible prior ledger), `new` (first seen though prior ledgers exist), `prior_confirmed_same_source`, `prior_confirmed_changed_source`, `prior_needs_validation`, `prior_deferred`, `prior_blocked`, `prior_out_of_scope`, `prior_covered_same_source`, `prior_covered_changed_source`, `prior_rejected_claim_changed`. The parent may add bookkeeping fields (for example retained `hardening` notes) but keeps these semantic fields stable.

### State table

| Status | `agent_id` | `reviewed_paths` / `local_checks` | `result_fingerprints` | `unresolved` |
|---|---|---|---|---|
| `planned` | null | empty | empty | empty |
| `not_applicable`, `out_of_scope`, `deferred` | null | empty | empty | nonempty reason |
| `in_progress` | owner | empty | empty | empty |
| `blocked` | owner | both nonempty (partial evidence) | empty | nonempty blocker |
| `covered` | owner | both nonempty | empty | empty |
| `candidate` | owner | both nonempty | nonempty | optional |

Every entry in `local_checks` has its own `agent_id` and nonempty `reviewed_paths`; the unit's `reviewed_paths` is exactly their union, so hunter and verifier checks coexist under one assignment owner. Source checks use `artifact: null`; local checks point to a promoted file under `agents/<check agent_id>/artifacts/`.

### Reassignment archive

`attempts` is append-only. When a critic reopens a `blocked`, `covered`, or `candidate` unit, append its exact `wave`, `status`, `agent_id`, `reviewed_paths`, `local_checks`, `result_fingerprints`, `unresolved`, plus the critic's source-backed `reassignment_reason`. Then increment `wave` and give the live unit a fresh owner with empty evidence. If profile or budget prevents another assignment, increment `wave` and set the live state to `deferred` with null owner, empty evidence, and the reason. Never copy archived checks or artifacts into the live attempt.

### Validate after every update

```sh
node <skill-dir>/scripts/validate-coverage-ledger.cjs <output-dir>/coverage-ledger.json
```

Run it after seeding, after every parent update, and before Phase 6. It rejects input over 5 MiB, 64 nesting levels, 10,000 units, or 1,000 items in a nested collection, and caps reported errors at 100. Fix every error before assigning work or claiming coverage.
