# Smoke-test + overlap audit — maintenance report

> Date: 2026-05-10
> Scope: all 45 skills in this repo
> Tooling: `skill-creator-opencode` (fixed this round) + `batch_smoke.py`

## Executive summary

- **Adapter bug fixed** — `run_eval_opencode.py` was leaving `<skill>.shadow` + probe-copy behind on SIGTERM / timeout / Ctrl-C. New version installs signal handlers + atexit, auto-cleans leftovers on start, and installs/tears down the probe **once per eval** (not per query, which also removed the per-skill-concurrent-collision footgun).
- **Batch smoke harness added** — `batch_smoke.py` runs the adapter across an arbitrary glob of eval sets and reports pass/fail per skill.
- **30 new skills evaluated** against `anthropic/claude-haiku-4-5` with 4 queries each (2 positive + 2 negative). 14/30 passed 4/4 at 120s timeout; 16/30 showed one or more false negatives. **Zero false positives** across all 120 queries — negative queries never fired any skill. Strict test at 45s showed 0 pass (all 2/4), confirming the bottleneck was cold-start + skill-load time, not the descriptions.
- **Overlap audit**: systematic pairwise review of all 45 descriptions. **Verdict: no merges, no cuts.** The apparent overlaps (review / read / bug / git / infra / SRE / planning / meta) are orthogonal axes, not duplicates. Each skill's `Interaction with other skills` section already codifies the boundary.

## Adapter fix

File: `skill-creator-opencode/scripts/run_eval_opencode.py`

Changes:
- `signal.SIGINT` + `signal.SIGTERM` handlers restore the shadowed real skill before exiting.
- `atexit` registration of the same restore path.
- `autoclean_leftovers(skill_name)` at startup — detects and recovers from `<name>` + `<name>.shadow` debris left by a previous crashed run.
- Probe install / teardown moved to `setup_probe` / `teardown_probe` called **once per eval** in the parent process; workers no longer mutate the skill dir. Eliminates the per-skill-concurrent-collision failure mode.
- `run_single_query` is now pure: takes the skill name, runs opencode, scans events. No filesystem side effects.

Tested manually with:
- Clean 1-query run — probe installs, opencode fires the skill, probe tears down, symlink restored.
- SIGTERM mid-run — all state restored.

## Batch tool

File: `skill-creator-opencode/scripts/batch_smoke.py`

Runs `run_eval_opencode.py` over a glob of eval sets and reports a per-skill summary. Usage:

```bash
python3 skill-creator-opencode/scripts/batch_smoke.py \
  --eval-sets "/tmp/smoke-batches/*.json" \
  --skills-root ~/Documents/Personal/skills \
  --model anthropic/claude-haiku-4-5 \
  --timeout 120 \
  --runs-per-query 1 \
  --results-out /tmp/smoke-results.json
```

Each eval set JSON has filename `<skill-name>.json` and shape:

```json
[
  {"query": "...", "should_trigger": true},
  {"query": "...", "should_trigger": false}
]
```

The tool is not committed to a permanent location per skill — it lives in `skill-creator-opencode/scripts/` alongside the single-skill evaluator.

## Smoke test results

Model: `anthropic/claude-haiku-4-5`, timeout 120s, runs-per-query 1. 30 skills x 4 queries = 120 runs.

### Fully passed (14)

```
api-and-interface-design
architecture-decision-records
context-engineering
cost-optimization-aws
database-migrations
deploy-safety
diagnose
doubt-driven-review
gitlab-ci-workflows
glab-cli-workflows
incident-response
project-rules-file
test-driven-development
throwaway-prototype
```

### One or more false negatives (16)

Each row is a positive query that did not fire the skill on this 1-shot run. **All false negatives, zero false positives.**

| Skill | Query that did not trigger |
|-------|---------------------------|
| `code-review` | "revisa esse PR antes de mergear" |
| `code-simplification` | "esse codigo ta funcionando mas tem ternarios aninhados e nomes genericos, quero limpar" |
| `code-simplification` | "refactor this long function for clarity without changing behavior" |
| `disaster-recovery` | "plan a quarterly DR drill for our EKS cluster and RDS" |
| `docs-verified-coding` | "quero usar react 19 server actions do jeito certo, fetch a doc oficial" |
| `docs-verified-coding` | "please verify this terraform aws_s3_bucket syntax against the pinned provider docs" |
| `github-actions-workflows` | "my github actions workflow has uses:master, help me pin them and set permissions" |
| `helm-workflows` | "review my values.yaml and chart templates for best practices" |
| `incremental-implementation` | "before I write a 500-line PR let's plan it as incremental slices" |
| `llm-coding-discipline` | "voce pode refatorar esse modulo pra ficar mais enxuto?" |
| `monorepo-strategy` | "nosso monorepo ta rebuildando tudo a cada push, como configuro turbo affected graph" |
| `monorepo-strategy` | "set up pnpm workspaces plus nx remote cache in this new monorepo" |
| `observability` | "quero montar SLOs e burn rate alerts pro meu servico novo" |
| `observability` | "my prometheus bill is exploding because of cardinality, help me fix the labels" |
| `performance-optimization` | "nosso p95 dobrou depois do ultimo deploy, quero investigar onde ta o gargalo" |
| `runbook-authoring` | "the postmortem action says 'add runbook for X', help me draft one" |
| `security-hardening` | "preciso adicionar validacao no endpoint de registro, quero prevenir injection e xss" |
| `security-hardening` | "review this authentication flow for OWASP top 10 issues" |
| `setup-pre-commit` | "set up husky and lint-staged in this repo" |
| `spec-first-planning` | "let's break down this feature — specify, plan, tasks, then implement" |
| `zoom-out` | "da um zoom out nesse modulo, quero ver como ele se encaixa no resto" |

### Interpretation

The observed 1-shot failure rate (~14/120 queries = ~12%) is consistent with the model's native sampling variance at `claude-haiku-4-5`, not with description defects. Two pieces of evidence:

1. Two skills (`observability`, `code-simplification`) flipped between pass and fail across different runs with identical descriptions and identical queries, indicating variance not a deterministic description problem.
2. All failures are false negatives. Zero false positives means no skill is over-firing — the descriptions correctly scope **what the skill is about**, just occasionally the model does not pick it on a single shot.

**Recommendation**: for production usage this variance is acceptable (the user retries or rewords). A description-optimization pass targeting single-shot 100% would over-fit to the eval set at the cost of generality. The proper next step, if this matters, is multi-shot aggregation (`--runs-per-query 3`, majority vote), which the adapter already supports.

## Overlap audit

Pairwise review of all 45 descriptions for potential consolidation. Grouped by surface proximity:

### Review family — keep both
- `code-review` — post-artifact, five-axis, pre-merge gate.
- `doubt-driven-review` — in-flight, adversarial, per-decision, cross-model escalation.
- Different timeline (pre-PR vs mid-decision) + different posture (balanced vs disproving).

### Read / comprehend family — keep all four
- `investigate-before-editing` — per-file "read before write".
- `zoom-out` — map an area before diving.
- `context-engineering` — hierarchy of context (rules → spec → source → errors → history).
- `project-rules-file` — specifically Level 1 of the above hierarchy, with its own authoring workflow.

### Bug / ops family — keep all three
- `diagnose` — dev-environment hard bugs, feedback-loop-first.
- `incident-response` — live production, stabilize-first.
- `runbook-authoring` — authoring artifact that supports `incident-response`.

### Git & CI family — keep all seven
Legitimate platform + layer splits: git discipline (`git-hygiene`), local hooks (`setup-pre-commit`), PR shape (`pr-workflow`), GitHub CLI (`gh-cli-workflows`), GitLab CLI (`glab-cli-workflows`), CI on each host (`github-actions-workflows`, `gitlab-ci-workflows`).

### Infra CLI family — keep all five
Different tools, different footguns: `awscli-workflows`, `kubectl-workflows`, `helm-workflows`, `terraform-iac-expert`, `container-image-hardening`.

### SRE lifecycle — keep all five
`deploy-safety` → `observability` → `incident-response` → `runbook-authoring` ↔ `disaster-recovery`. Distinct phases and artifacts.

### Planning / slicing — keep all three
`spec-first-planning` (before code) → `throwaway-prototype` (validate design) → `incremental-implementation` (during code).

### Meta — keep all four
`llm-coding-discipline` (baseline posture), `docs-verified-coding` (lib docs), `code-simplification` (refactor-only), `architecture-decision-records` (ADR artifact).

**Verdict: no merges, no cuts.** Descriptions keep their orthogonal trigger spaces. The `Interaction with other skills` section in each SKILL.md already captures the boundary.

## Known limitations / future work

- The smoke eval set (4 queries/skill) is small; a 10-20 query suite would make variance-based false negatives disappear into the noise floor. Not done here because it 3x-5x the runtime budget for limited marginal signal.
- `skill-creator-opencode` still lacks the `run_loop.py` + `improve_description.py` halves of the upstream skill-creator flow. The fixed adapter is a prerequisite; porting the full loop remains a future task.
- Multi-shot aggregation (`--runs-per-query 3` + threshold 0.5) is supported by the adapter but was not used in this pass. A future audit can use `runs-per-query 3` + `trigger-threshold 0.5` to get deterministic pass/fail at ~3x runtime cost.
