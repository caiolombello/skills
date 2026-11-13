# Notice

This skill adapts concepts from [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill), snapshot `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, Copyright (c) 2025-2026 Cloudflare, Inc., MIT License. The upstream license text is in [LICENSE](LICENSE).

## Vendored files (unmodified)

Copied byte-for-byte from `skills/security-audit/` of that snapshot:

- `scripts/report-schema.json`
- `scripts/validate-findings.cjs`
- `scripts/validate-findings.test.cjs`
- `scripts/validate-coverage-ledger.cjs`
- `scripts/validate-coverage-ledger.test.cjs`

They are kept together in `scripts/` because `validate-findings.cjs` loads `report-schema.json` from its own directory and the tests load their validators by relative path. No path change was needed. Self-test with Node.js (pass files explicitly; a bare directory argument is not a test pattern on current Node):

```sh
node --test scripts/validate-findings.test.cjs scripts/validate-coverage-ledger.test.cjs
```

## Adapted prose

`SKILL.md`, `references/*.md`, and `evals/scenarios.json` are independently written for this repository. They keep the upstream concepts (operating modes, candidate gate, verdicts, severity anchors, execution boundary, coverage ledger, critic waves, independent verification, record-derived reports) but condense the workflow, merge the ten domain companions into five references, and make delegation optional for hosts without subagents. They are not a copy of the upstream text.
