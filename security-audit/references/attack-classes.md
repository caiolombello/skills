# Core attack classes

Use these for every target type; add domain references only where their boundary exists (see the table in [../SKILL.md](../SKILL.md)). Pick the classes reconnaissance supports, add target-specific ones, and split large codebases per subsystem. Every class answers to the same candidate gate and execution boundary: source review plus bounded local fixtures, no payload chains, no live or shared testing.

Each bold name below is a stable block identifier for the coverage ledger, e.g. `references/attack-classes.md#Access control`. When briefing a hunter, copy the whole block, not just the name.

**Injection**
Trace untrusted input to the sink that interprets it. Sinks depend on the target: SQL/NoSQL queries, HTML and templates, shell commands, file paths, redirects, deserializers, LDAP/XPath, log lines (web and services); buffer operations, parsers, and format strings (libraries); command construction, path handling, and environment interpolation (CLIs). Browser-side sinks belong to the web and client domain. Go beyond the direct path: data stored safely and later used unsafely by other code; injection through field names, keys, headers, and metadata as well as values; injection into secondary systems such as logs, caches, search indexes, and analytics.

**Access control**
Prove a caller cannot act outside its authority — not just that a check exists, but that it checks the *right* permission on the *right* resource through the *right* mechanism. Look for a second route to the same state change with a weaker check; body fields that override what the permission system restricts; endpoints gated on authentication but not authorization; one resource with several access paths and inconsistent checks; bulk, batch, export, and import operations that skip per-item checks. For complex models, split authentication bypass from authorization logic.

**Resource and file handling**
Path traversal on read or write, including symlinks, encoded sequences, and null bytes. SSRF, including redirects, DNS rebinding, and URL-parser differentials. Unsafe deserialization, archive extraction outside the target directory, and temporary-file handling. Check-then-use races on files. Memory-safety issues go to the native domain when it applies.

**Cryptography and secrets**
Weak randomness for tokens, keys, or nonces. Secrets in source, logs, errors, URLs, or client-visible responses. Broken key derivation, missing MAC verification, nonce reuse, timing-dependent secret comparison, and misused primitives (ECB, unauthenticated encryption, static IVs). The failure path: when a crypto operation errors, does the code fall back to no protection?

**Business logic**
Hand-traced, scanner-invisible, often high impact. For each major workflow:
- State machine: skip steps, go backwards, reach invalid states, replay completed flows; on partial failure, is earlier work rolled back?
- Races with business effect: double spend, double approval, lost updates from non-atomic check-then-act.
- Quantities: negative, zero, overflow, precision loss, string/number coercion.
- Right check for the rule: can input to one operation bypass a restriction enforced on another with the same effect?
- Implicit trust in stored, configured, or component-supplied data that a different path could have written.
- Time: expiry, scheduling, rate windows, clock skew, exact-boundary and timezone behavior.
- Defaults and fallbacks: missing config, feature flag off, dependency down, mid-migration.

**Feature abuse and data leakage**
Legitimate features used against their intent:
- Export or backup that includes other users' data, higher-privilege fields, deleted or draft content, or history meant to be pruned.
- Import or restore that overwrites data, skips validation, or writes where the user has no write access.
- Search, filter, and sort as oracles for content, statuses, roles, or hidden field values.
- Enumeration through differing errors, timings, sizes, or status codes, including reset, invite, and registration flows.
- Preview, draft, and staging tokens that unlock more than one item, or private content reachable through feeds, sitemaps, listings, or cacheable responses.
- User-supplied notification, webhook, or callback URLs fetched by the server without internal-network and post-redirect checks.

**Chained vulnerabilities and trust boundaries**
Individually acceptable behavior becomes a vulnerability when a later component relies on a stronger guarantee:
- Multi-step: map what a low-privilege principal can read, write, invoke, and retain, then connect only concrete outputs to later trust decisions; confirm each prerequisite.
- Cross-component gaps: compare exactly what A guarantees with what B assumes — truncation, coercion, normalization, tenant scope, plugin access.
- Second-order use: a field name becomes a JSON path, a slug a file path, escaped text raw HTML, a stored string a URL, regex, template, or policy expression.
- Capability growth after delegation, refresh, caching, role change, or composition of tokens, keys, plugins, OAuth, MCP, or AI capabilities.
- Timing windows: setup, migration, soft delete, revocation and cache expiry, check/use, validate/consume.
- Rollback and recovery: undelete, restore, revision rollback, and cancel must reapply current ownership, validation, and authorization.

**Wildcard**
No category. Find what the other classes miss, under the same boundary and evidence rules. Starting points:
- The strangest code in the repository, and why it exists.
- Half-finished, experimental, compatibility, or bolted-on features.
- API calls the UI never makes; undocumented routes, parameters, headers, and flags found in route registration, middleware, and config.
- Features combined in ways nobody designed for (localization + preview + caching; import + plugins + webhooks; OAuth + impersonation + API keys).
- Git history: reverted security fixes, removed auth checks, secrets committed then deleted.
- Valid-account actions that affect other users, shared integrity, availability, or operator-owned cost.
- Irreversible or elevated operations: is approval bound to the final principal, action, and resource?
- Environment assumptions: local database, accurate clock, trustworthy DNS, case-sensitive filesystem.
- What the tests do not cover, compared with the edge cases they do.

Read until each anomaly is settled. Verify comments that explain why something is safe. Read anything named `temp`, `hack`, or `legacy` closely.

**Obvious exposures**
Literal and thorough, because everyone assumes someone else checked:
- Hardcoded passwords, keys, tokens, private keys, default credentials (search for `password`, `secret`, `apikey`, `token`, `Bearer`, `-----BEGIN`).
- Security-related `TODO`, `FIXME`, `HACK`, `XXX` comments.
- Debug or dev mode that can be enabled in production by env var, query parameter, or header.
- Test, example, or seed credentials that would work in production.
- Unprotected `/debug`, `/admin`, `/test`, `/status`, `/health`, `/metrics`, `/env`, `/.env`, `/config` routes.
- Committed `.env`, `credentials.json`, `*.pem`, `*.key`; `.gitignore` gaps for secrets, uploads, and local config. Report the path and type only — never print secret values.
- Unpinned dependencies or known-vulnerable versions in lockfiles (from local data only; no network lookups).
- `eval`, `exec`, `child_process`, `Function`, `vm`, dynamic `import()` fed by input.
- CORS reflecting arbitrary origins with credentials.
- Session cookies without `HttpOnly`, `Secure`, `SameSite`.
- Open redirects through `redirect`, `return`, `next`, `url`, `goto`, `continue` parameters.
- Plain-HTTP endpoints; stack traces, internal paths, or SQL errors in production responses.

A flag is not a finding. Trace each hit to impact before reporting: a cookie without `HttpOnly` matters only if it carries a credential that script should not read; an error string matters only if the field is ever populated with sensitive data. Unconfirmed hits are hardening notes.
