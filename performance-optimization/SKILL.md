---
name: performance-optimization
description: Measure before optimizing. Performance work without measurement is guessing. Use WHENEVER the user (1) reports something is slow — page load, API response, query, batch job, build, CI, anything; (2) has a performance budget or SLO (Core Web Vitals, p95 latency, throughput target); (3) suspects or was alerted to a regression; (4) mentions "slow", "latency", "throughput", "benchmark", "profile", "optimize", "p95/p99", "bundle size", "cold start", "query plan", "N+1", "memory leak", "CPU spike"; (5) is designing a feature that will clearly be performance-sensitive (large dataset, high traffic, real-time). The skill ENFORCES: measure → identify the actual bottleneck → fix → verify → guard. Prevents the most common failure mode — optimizing the wrong thing based on intuition. Does NOT apply to capacity / scaling decisions (see `observability` for USE / saturation) or deploy-time safety (see `deploy-safety`).
---

<!-- Inspired by addyosmani/agent-skills performance-optimization (MIT). See ../CREDITS.md -->

# Performance Optimization

**Measure before optimizing.** Every shortcut past measurement produces complexity that costs more than the performance it gains. The core discipline is the same across frontend, backend, database, and build:

```
MEASURE → IDENTIFY → FIX → VERIFY → GUARD
```

Intuition is wrong often enough that the only useful bias is "I do not know the bottleneck yet — I will measure". Applies at every scale, from a 10ms function to a 10-node service.

## When to use

- The user reports something is slow — page load, API, query, job, build.
- A performance budget or SLO is at risk.
- A regression is suspected (deploy caused latency to double).
- A feature is being designed that is clearly performance-sensitive.

### When NOT to use

- Code is not slow, there is no budget, and nobody is complaining. **Do not speculatively optimize.**
- Capacity / scaling limits → [`observability`](../observability) for saturation / USE, [`deploy-safety`](../deploy-safety) for replica counts.
- Correctness bug that happens to be slow → [`diagnose`](../diagnose) first; performance afterward.

## The workflow

### 1. Measure

Establish a **baseline** before touching anything. Two complementary approaches; use both when applicable.

- **Synthetic** — controlled, reproducible. Lighthouse, DevTools Performance, `wrk`, `k6`, `hyperfine`, benchmark harness. Good for CI regression detection and isolating a specific code path.
- **Real-user / production** — actual production load. RUM libraries (`web-vitals`), APM (Datadog, New Relic, Honeycomb), Prometheus histograms at the LB. Required to validate that a fix actually improved user experience.

Never optimize on synthetic numbers alone. Real user distributions are uglier — caches cold, networks bad, devices slow.

### 2. Identify the bottleneck

Use the symptom to pick a probe:

```
Slow first page load?        → Bundle size, critical-path rendering, LCP breakdown
Slow interaction?            → INP, main-thread blocking, hydration
Slow API?                    → Request span — DB query / external call / CPU?
Slow query?                  → Query plan, indexes, row counts, N+1 detection
Slow build / test?           → Bundler profile, test parallelism, cache invalidation
Slow cold start?             → Module resolution, init code, layer size
Memory growth over time?     → Heap snapshots, GC logs, retained size
```

Stop at the **first** bottleneck that accounts for a meaningful share of the time. Optimizing the second when the first dominates is wasted work.

### 3. Fix

One change at a time. Re-measure after each. Optimizations that compound are fine; optimizations that cannot be individually verified hide regressions.

### 4. Verify

Re-run the same measurement. The improvement must be:
- **Statistically significant** (run more than once; real deployments have noise).
- **In production-like conditions** (synthetic benchmarks mislead).
- **On the metric that matters** (p95 latency, not mean; LCP, not DOMContentLoaded).

If the number did not move, undo the change. "Felt faster" is not measurement.

### 5. Guard

Prevent regression:
- Add a benchmark to CI, fail on regression beyond a threshold.
- Add an SLO / burn-rate alert for the production signal.
- Add a test for the specific pathological input (N=100k, nested depth, etc.).

See [`observability`](../observability) for SLO + burn-rate patterns, [`test-driven-development`](../test-driven-development) for adding the guard test.

## Frontend — Core Web Vitals

| Metric | Good | Needs improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | ≤ 800ms | ≤ 1800ms | > 1800ms |

Measure at the 75th percentile of real users, not the mean.

### Tools

- **Chrome DevTools Performance panel** — flame graph of main thread, network waterfall.
- **Lighthouse** — synthetic score, audits, opportunities.
- **PageSpeed Insights** — Lighthouse + CrUX real-user data for the URL.
- **WebPageTest** — connection / device simulation, repeat visits.
- **[`web-vitals`](https://github.com/GoogleChrome/web-vitals) library** — RUM from the browser.
- **Bundle analyzer** — `vite-plugin-visualizer`, `webpack-bundle-analyzer`.

### Common wins

- **Code-split routes.** Ship what the user needs on this page, not the entire SPA.
- **Defer non-critical JS.** `<script defer>`, lazy-load below the fold.
- **Preload the LCP image.** `<link rel="preload" as="image" href="...">`.
- **Avoid layout thrash.** Batch DOM reads and writes. Use `IntersectionObserver` not scroll handlers.
- **Self-host critical fonts.** Third-party font CDNs are unpredictable.
- **Memoize expensive React renders** — but only ones measured to be expensive. Unnecessary `useMemo` is overhead.
- **Virtualize long lists.** React Window, TanStack Virtual.
- **Image format + `srcset`.** AVIF / WebP with fallback, explicit `width` / `height` to prevent CLS.

### What NOT to do

- Adding `React.memo` / `useMemo` / `useCallback` everywhere "just in case". It is overhead, not optimization.
- Rewriting from React → Preact → Solid before measuring the actual bottleneck.
- Obsessing about the Lighthouse score when RUM shows no real user impact.

## Backend — latency and throughput

### Signals to watch

- **Latency**: p50, p95, p99 from a histogram. Never just mean — tail latency drives user pain.
- **Throughput**: requests/sec a service sustains without regressing latency SLO.
- **Saturation**: resource utilization at which quality breaks (CPU, memory, connection pool, I/O wait).
- **Error rate**: 4xx, 5xx, timeouts. Errors under load are a perf problem.

See [`observability`](../observability) for the four golden signals + SLO/burn-rate framework.

### Profiling

- **CPU profiler**: `py-spy`, `perf`, Go `pprof`, Node `--prof`, `clinic`, Java JFR. Flame graph gives you the hot path.
- **Heap snapshot**: Chrome DevTools heap, `heapy`, Go `pprof` heap. Shows retained memory.
- **Request tracing**: distributed traces (OpenTelemetry → Jaeger / Tempo / Honeycomb). Shows where the time goes across services.
- **Continuous profiling**: [Pyroscope](https://pyroscope.io/), [Parca](https://www.parca.dev/), [Grafana Pyroscope](https://grafana.com/oss/pyroscope/) — always-on profiling in production.

### Common wins

- **Cache the hot read.** An hourly-consistent endpoint does not need per-request DB. Redis, Memcached, or an in-process LRU.
- **Batch upstream calls.** Hundreds of sequential calls → one batched call. Saves both latency and connection pool pressure.
- **Concurrent independent work.** `Promise.all`, `errgroup.Wait`, `asyncio.gather`. Sequential awaits on independent work is a common accidental serialization.
- **Connection pooling**. Do not create a DB connection per request.
- **Background async for non-critical work.** Write the response; enqueue the email / webhook / analytics.
- **Streaming / incremental response.** 1MB JSON response → stream as NDJSON or use HTTP streaming.
- **Compression** at the edge. Brotli > gzip for text.

### Language-specific cold starts

For serverless (Lambda, Cloud Run, Azure Functions):
- **Keep the package small.** Every dependency is startup cost.
- **Move init out of the handler.** Lazy-init what you do not always use; eager-init what you always use.
- **Provisioned concurrency / min-instances** for latency-sensitive endpoints.
- **Tune memory.** In Lambda, memory ~= CPU; more memory often means cheaper total cost.

## Database

The most common backend bottleneck. Measure, read query plans, index surgically.

### Tools

- `EXPLAIN (ANALYZE, BUFFERS)` in Postgres; `EXPLAIN ANALYZE` in MySQL; `explain()` in Mongo.
- Slow query logs. Every RDBMS has one — enable in prod.
- [`pg_stat_statements`](https://www.postgresql.org/docs/current/pgstatstatements.html) for Postgres — ranks queries by total time spent.
- [`pghero`](https://github.com/ankane/pghero), `pt-query-digest` for MySQL.

### Common wins

- **Missing index on `WHERE` / `JOIN` / `ORDER BY` column.** Usually the answer.
- **N+1 queries.** Load once, join or batch. ORM lazy loading is a classic trap.
- **`SELECT *` on wide tables.** Pick the columns you need.
- **Avoid `LIKE '%foo%'`** on non-trigram / non-FTS text. Use a search index.
- **Denormalize aggregates** (materialized views, count columns) when reads vastly outnumber writes.
- **Pagination** via keyset, not offset. `OFFSET 1_000_000` is expensive.
- **Connection pool size tuned** — too few and you queue; too many and you starve the DB.
- **Transactions around batch writes.** Ten inserts in one transaction can be 10x faster than ten separate ones.

### Indexes have costs

Every index slows writes and uses disk. Add indexes only for queries measured to need them. Audit and drop unused indexes (`pg_stat_user_indexes`).

## Build and CI

The forgotten bottleneck — developer productivity.

### Common wins

- **Incremental builds.** Vite, esbuild, Turbopack for JS. `tsc --incremental`. `mvn` incremental.
- **Persistent caches in CI.** See [`github-actions-workflows`](../github-actions-workflows) + [`gitlab-ci-workflows`](../gitlab-ci-workflows) for cache patterns.
- **Parallel test runs.** Most test runners support `--parallel` / `--shard`.
- **Split test suites.** Unit in parallel, integration serial, e2e on merge only.
- **Path filters in CI.** Do not re-run the full suite on a README change.
- **Profile the build.** `TIMING=1 turbo run build`, `esbuild --metafile`, `webpack --profile`.

## Cost as a perf signal

Slow systems are often expensive systems. When optimizing, watch for "this is fast enough but costs 10x what it should":
- Unused instances / replicas / read replicas.
- Over-provisioned memory when CPU is the bottleneck (or vice versa).
- Cardinality / log volume explosion — see [`observability`](../observability).
- Hot code path creating too many short-lived allocations.

## The measurement stack

Every project should have at least:

- A way to **profile** in development (DevTools, `py-spy`, `pprof`, `JFR`).
- A way to **measure in production** (APM, OpenTelemetry, `web-vitals`).
- A **benchmark harness** in CI for performance-sensitive code paths.
- An **SLO** for the user-facing path.
- A **regression alert** tied to the SLO burn rate.

Without these, performance work is storytelling.

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| "Let me add some caches" without measuring | New consistency bugs; the bottleneck was elsewhere |
| Micro-optimizing a 0.1% hot path | Zero impact, new complexity |
| Rewriting language / framework before measuring | Huge risk, often finds the bottleneck unchanged |
| Tuning based on mean, not p95/p99 | Tail users still suffer |
| Synthetic benchmark as the only signal | RUM disagrees; fix does not help real users |
| Optimizing one request in isolation, ignoring concurrency | Fix shifts the bottleneck to locks / connection pool |
| Adding indexes reflexively | Write throughput regresses; disk grows |
| `select *` + in-memory filter | Drags a lot more data than needed |
| "Scale horizontally" to mask a hot-path bug | Bill grows; bug still there |
| Not locking a regression test / benchmark into CI | Next PR re-regresses silently |

## Interaction with other skills

- [`observability`](../observability) — SLIs / SLOs / burn-rate alerts are how you know the perf work worked in production.
- [`diagnose`](../diagnose) — bug that happens to be slow; use diagnose first, then this skill for the bottleneck.
- [`test-driven-development`](../test-driven-development) — performance regression tests / benchmarks in CI.
- [`code-review`](../code-review) — the "performance" axis of review. Reviewers can check that perf changes include measurements.
- [`docs-verified-coding`](../docs-verified-coding) — verify framework perf APIs against docs; do not invent them.
- [`deploy-safety`](../deploy-safety) — perf fixes ship as any other change, with canary and rollback.
- [`github-actions-workflows`](../github-actions-workflows) / [`gitlab-ci-workflows`](../gitlab-ci-workflows) — where benchmarks and bundle-size checks live.

## Verification checklist

Before claiming a perf fix is done:

- [ ] I captured a baseline measurement before any change.
- [ ] I identified the specific bottleneck (not "the app is slow in general").
- [ ] I changed one thing at a time; re-measured after each.
- [ ] The improvement is on the metric that matters (p95 latency, LCP, throughput), not the mean.
- [ ] The improvement reproduces in production-like conditions, not just a synthetic benchmark.
- [ ] The improvement is statistically significant across multiple runs.
- [ ] A benchmark / SLO / burn-rate alert guards the fix from regressing.
- [ ] No code was added "just in case" — every change traces back to the measurement.
- [ ] Costs did not balloon elsewhere (memory, disk, cloud bill).
