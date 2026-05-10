---
name: api-and-interface-design
description: Design stable APIs and module interfaces. Use WHENEVER the user (1) designs, reviews, or refactors a public API — REST, GraphQL, gRPC, webhook, RPC, event bus message, SDK; (2) defines or changes a module boundary / public interface / type contract between parts of a codebase; (3) versions, deprecates, or migrates an existing API; (4) mentions "breaking change", "backwards compatibility", "semver", "API versioning", "v2 endpoint", "deprecation policy", "contract", "interface design", "Consumer-Driven Contracts", "schema evolution"; (5) is about to name a new endpoint, method, or type that will be called by code you do not own. Pairs with `docs-verified-coding` (for consuming an API), `architecture-decision-records` (capture interface choices), and `security-hardening` (input validation at boundaries).
---

# API and Interface Design

An API is a **promise**. Once published, it is easier to keep than to break. Breaking an API breaks your users — either people you will never meet (public SDK) or teammates on a call next week (internal service-to-service). Either way, the cost of "just one change" compounds.

This skill covers interface design at three granularities: **network APIs** (REST, GraphQL, gRPC, webhooks, events), **language-level public interfaces** (module exports, SDK surface), and **internal module boundaries**. The discipline is the same; the syntax differs.

## The seven principles

1. **Design for the consumer**, not the implementer. What does the caller need? What would surprise them?
2. **Make the happy path obvious.** A consumer should discover correct usage by reading the types / docs, not by experimentation.
3. **Reject invalid states.** If an argument combination cannot be valid, make it unrepresentable (separate types, enum, discriminated union) rather than "validated at runtime".
4. **Be strict in what you accept, liberal in what you return** — the *reverse* of Postel's Law. Servers should reject malformed input; clients should not depend on extra fields. Postel's original law led to decades of ambiguous protocols; current guidance is the opposite for safety.
5. **Explicit over magical.** A consumer reading the signature should know what the function does. No hidden global state. No `null` with 5 meanings.
6. **Small surface area.** The fewer endpoints / methods / options, the less to maintain and the less to break. Add deliberately, remove carefully.
7. **Versioning is a contract with the future.** Plan for v2 before you ship v1.

## Before you design — four questions

Answer in 5 minutes; 20 minutes later you avoid a re-design.

1. **Who calls it?** Internal team, external partner, SDK consumer, AI agent, cron job. The audience changes everything.
2. **How do they discover it?** OpenAPI spec, gRPC proto, type definitions, docs site, internal handoff. Discovery shapes naming.
3. **What is the consistency contract?** Strongly consistent, eventually consistent, read-your-writes. Surface this explicitly.
4. **What is the stability commitment?** "Stable forever", "stable within v1", "experimental, may break". Users deserve to know.

Write the answers next to the design. They become the skeleton of the interface doc.

## Naming — the load-bearing boring work

- **Verbs for actions, nouns for things.** `GET /users` (things), `POST /users/{id}/activate` (action on a thing). `POST /activate-user` is awkward.
- **Consistent pluralization.** `/users` and `/orders`, not `/user` and `/orders`.
- **Stable ID shape.** Do not mix `number`, UUID, and slug in the same API. Pick one.
- **Names survive refactors.** A name that matches today's implementation is brittle; a name that matches the domain concept lasts. `sendConfirmationEmail` survives the SMTP → Mailgun switch; `callMailgunSendApi` does not.
- **Avoid implementation leakage.** `/db/query` exposes your backend; `/reports/run` does not.
- **Match the project's glossary.** See [`project-rules-file`](../project-rules-file). If the rules file calls it a "tenant", do not name the endpoint `/account`.

## REST APIs

### Resource modeling

- **Nouns, plural, hierarchical.** `GET /workspaces/{id}/projects/{pid}/tasks`.
- **Verb via method, not URL.** `DELETE /tasks/{id}`, not `POST /tasks/delete`.
- **Sub-resources for containment, not relationships.** Use `GET /tasks?project_id=X` rather than `GET /projects/{id}/tasks` if the same task can belong to multiple projects.
- **Actions that do not map to CRUD** — use a sub-resource: `POST /deployments/{id}/rollback`. Clearly named; not a GET with side effects.

### HTTP status codes — the minimum set

| Code | When |
|------|------|
| 200 | Success with body |
| 201 | Created; body contains the new resource; `Location:` header |
| 202 | Accepted; async work queued |
| 204 | Success, no body |
| 301 / 308 | Permanent redirect (308 preserves method) |
| 302 / 307 | Temporary redirect |
| 400 | Client error, malformed input |
| 401 | Missing / invalid authentication |
| 403 | Authenticated but not authorized |
| 404 | Resource does not exist (or you do not want to reveal it) |
| 409 | Conflict — concurrent update, unique violation |
| 410 | Gone — resource permanently removed |
| 412 | Precondition failed — `If-Match` etag mismatch |
| 422 | Validation error (more specific than 400) |
| 429 | Rate limited |
| 500 | Server error, unexpected |
| 502 / 503 / 504 | Upstream / unavailable / gateway timeout |

Prefer 422 over 400 for validation errors — more specific, clearer. Always include a machine-readable error body (see below).

### Error body shape — follow a standard

Use [RFC 9457 Problem Details](https://datatracker.ietf.org/doc/html/rfc9457) for JSON APIs. It is a stable standard and framework-supported.

```json
{
  "type": "https://example.com/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "The 'email' field is required.",
  "instance": "/users",
  "errors": [
    { "field": "email", "rule": "required" },
    { "field": "age", "rule": "min", "min": 18 }
  ]
}
```

- `type` is a stable URI the consumer can switch on. Treat as part of the contract.
- `errors` is a list so the client can surface multiple problems at once.
- Never leak stack traces or internal details in `detail`.

### Pagination

Always paginate list endpoints. Never return unbounded arrays.

| Style | Good for | Watch out for |
|-------|----------|---------------|
| Cursor-based | High-volume, append-heavy data (timelines, logs) | Can't random-access pages |
| Offset/limit | Static tables, admin UIs | Skipping / duplicates on concurrent writes |
| Keyset | Sorted stable data | Tight coupling to sort key |

Cursor shape:

```json
{
  "data": [...],
  "next": "eyJjcmVhdGVkX2F0IjoiMjAyNS0wNS0wMSIsImlkIjoxNDJ9",
  "prev": null
}
```

`next` is opaque to the client — base64 an internal shape. Never expose "page 3" arithmetic as part of the contract; you lose flexibility to change the sort.

### Idempotency

Mutations that can be retried must be idempotent, or clearly unsafe.

- **GET, HEAD, OPTIONS** — safe and idempotent by definition.
- **PUT, DELETE** — idempotent.
- **POST** — not idempotent by default. If retries are expected (payments, create-resource), accept an `Idempotency-Key: <uuid>` header and de-duplicate server-side. Document the replay window.

### Filtering, sorting, fields

- Query params: `?status=active&sort=-created_at&fields=id,name`.
- Document exactly which fields are filterable / sortable. Do not let users sort by arbitrary columns — that is a query-plan hazard.
- Avoid overly flexible filter DSLs unless that is actually required. GraphQL or a dedicated search endpoint is better.

### Authentication + authorization

- **Auth in headers.** `Authorization: Bearer <token>`. Not query string, not body.
- **One scheme per API.** Do not mix API keys and OAuth bearers in the same surface.
- **Authz per endpoint.** See [`security-hardening`](../security-hardening) A01 — "logged in" ≠ "allowed".
- **Rate limits** — return `429` with `Retry-After` and `RateLimit-*` headers.

## GraphQL

- **One schema, one source of truth.** No "internal" vs "external" schema drift.
- **Nullability is a contract.** Non-null fields force consumers to handle them. Do not flip a field from non-null to nullable as a "safe" change; it breaks clients.
- **Pagination via Relay Cursor Connections.** Standard, cross-tool.
- **Mutations return the modified object**, including fields the client might need to re-render. `input:` types are mutable; output types are the contract.
- **Persisted queries in production.** Client queries are registered; server rejects unknown ones. Cuts attack surface + allows query-plan optimization.

## gRPC / Protobuf

- **Field numbers are forever.** Never re-use. When you remove a field, keep the number reserved: `reserved 5, 6;`.
- **Default values have no wire representation.** Do not design semantics on "did the client send 0 vs omit it". Use wrappers (`google.protobuf.Int32Value`) or `optional` in proto3.
- **Oneof for mutually-exclusive states.** `oneof result { Success ok = 1; Error err = 2; }` beats "one of these fields will be set".
- **Service method names are imperative, not CRUD-y.** `CreateInvoice`, not `Create`.
- **Server streaming for long polls; bidirectional streaming for true conversations.** Do not overuse streaming for request/response — harder to load-balance.

## Webhooks

- **Signed payloads.** HMAC-SHA256 over the body with a shared secret; signature in a header. Consumers verify before trusting.
- **Idempotency keys** in the payload; retries are expected.
- **Timestamps** in the signature base to prevent replay attacks.
- **Retry policy** documented — consumers need to know to make the endpoint idempotent.
- **Event type in the envelope**, not the URL. Lets consumers dispatch by type.

## Event bus / messaging

- **Schemas are contracts.** Use Avro / Protobuf / JSON Schema with a schema registry.
- **Forward and backward compatibility.** Old consumers must tolerate new fields; new consumers must tolerate old events.
- **Event naming**: past tense, noun-verbed. `UserActivated`, `InvoicePaid`. Present tense is a command.
- **Idempotency key** in the envelope so consumers de-dup.
- **No personal or sensitive data in plaintext** unless the bus is explicitly encrypted. See [`security-hardening`](../security-hardening).

## Language-level interfaces (modules, SDKs)

### Small public surface

- Export what is needed. Keep implementation types internal.
- Prefer named exports to default exports — easier to refactor, easier to grep.
- Avoid boolean flag parameters; use options objects or two functions.

```ts
// Bad — what do the flags mean?
fetchUsers(true, false, true);

// Good
fetchUsers({ includeArchived: true, withPermissions: false, cache: true });

// Also good — two simple functions beat one with a flag
fetchActiveUsers();
fetchAllUsers();  // includes archived
```

### Sum types / discriminated unions for valid states

```ts
// Bad — 4 impossible state combinations
type Result = { loading: boolean; error: Error | null; data: T | null };

// Good — only valid states representable
type Result<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; error: Error }
  | { status: "success"; data: T };
```

Applies to Go (`type Result interface { … }` with implementations), Rust (`enum Result`), Python (`Union` / `Literal` types), Kotlin (`sealed class`).

### Options objects evolve

When a function may gain options later, accept an options object from day one:

```ts
// Day one
save(task: Task, opts: { force?: boolean } = {});
// Day ten
save(task: Task, opts: { force?: boolean; idempotencyKey?: string } = {});
```

Easier than breaking the positional argument order twice a year.

## Versioning

### Semver for language-level APIs

- `1.0.0` means stable; `0.x.y` means "may change". Use `0.x` when you mean "unstable".
- Bump **major** on any backwards-incompatible change. No exceptions.
- Bump **minor** for backwards-compatible additions.
- Bump **patch** for bug fixes with no API change.

### Network API versioning

Three options. Pick **one** and commit.

| Strategy | Shape | Pros | Cons |
|----------|-------|------|------|
| **URL** | `/v1/users`, `/v2/users` | Discoverable, easy to cache | Heavy migration; proliferation |
| **Header** | `Accept: application/vnd.company.v2+json` | Invisible in URLs; cleaner | Hard to demo; caches need to vary |
| **Field** | `POST /users` with `{"schema_version": 2, ...}` | One endpoint forever | Conditional logic explodes |

URL versioning is the default for public APIs — simplest operationally, even if aesthetically ugly. GraphQL and gRPC take a different approach — **evolve in place** with additive changes; versioning happens at the deployment/client level.

### Additive vs breaking — the table

| Change | Additive? | Notes |
|--------|-----------|-------|
| Add a field to the response | Yes | If clients ignore unknown fields (they should) |
| Add an optional request field | Yes | |
| Add a required request field | **No** | Break |
| Remove a field | **No** | Break |
| Rename a field | **No** | Add new, deprecate old |
| Narrow a type (string → enum) | **No** | Break |
| Widen a type (enum → string) | Yes, for output; **No** for input |
| Make a required field optional | Yes, for input; **No** for output |
| Change an enum value | **No** | Break; add new value, deprecate old |
| Remove an endpoint | **No** | Break (deprecate + sunset instead) |
| Change error codes | **No** | Break |
| Change pagination shape | **No** | Break |
| Change authentication scheme | **No** | Break (offer both during migration) |

## Deprecation

Breaking changes happen eventually. Do it with a plan, not by surprise.

### The four-stage deprecation

1. **Announce.** Mark deprecated in docs, OpenAPI `deprecated: true`, JSDoc `@deprecated`, proto `[deprecated=true]`. Add a header / log: `Deprecation: true`, `Sunset: Wed, 31 Dec 2025 00:00:00 GMT` (see [RFC 8594 / RFC 9745](https://datatracker.ietf.org/doc/html/rfc9745)).
2. **Measure use.** Instrument the endpoint. You cannot deprecate what you cannot see.
3. **Migrate users.** Reach out to the top N consumers. Provide migration docs with concrete before/after.
4. **Sunset.** Only when usage is zero (or the announced date has passed and you are prepared to break stragglers). Return 410 Gone, not 404.

Minimum deprecation windows:
- Internal-only API: 2 sprints or 1 release cycle.
- External partner API: 90 days.
- Public SDK / API: 6-12 months.

### Migration docs

Every deprecation comes with a migration guide. Before / after, step-by-step, one commit per consumer.

```markdown
## Migrating from /v1/users to /v2/users

v2 uses cursor pagination and flattened user-profile fields.

Before (v1):
  GET /v1/users?page=2&per_page=50
  → { users: [...], total: 412 }

After (v2):
  GET /v2/users?after=eyJ...&limit=50
  → { data: [...], next: "eyJ...", prev: null }

Field changes:
  - profile.first_name → first_name (flattened)
  - role_id → roles: [{id, name}]  (now multi-role)
```

## Contract testing

API tests that fake the consumer are not proof of a stable API.

- **Consumer-Driven Contract tests** (Pact, Spring Cloud Contract) — consumers publish their expectations; provider CI runs them. Catches breaking changes before they ship.
- **Schema snapshot tests** — `openapi.yaml` / `.proto` / `schema.graphql` committed; CI fails on unreviewed changes.
- **Golden file tests** — full request / response pairs stored as fixtures; changes require review.

Minimum: the schema file is in git, and CI blocks on unreviewed diffs.

## Documentation is part of the API

- **OpenAPI for REST** — generated or hand-written, published with the service.
- **GraphQL introspection + SDL** — schema is its own doc.
- **Proto files** — proto is the doc.
- **Examples beat prose.** Every endpoint / method / type has at least one example.
- **Stability table.** A top-level section lists each endpoint with its stability level.

See [`docs-verified-coding`](../docs-verified-coding) — this skill's discipline of "cite the docs" is the other side of this skill's "write docs worth citing".

## Anti-patterns

| Anti-pattern | Why it hurts |
|--------------|-------------|
| HTTP 200 with `{"error": "..."}` | Breaks every automated retry / alerting tool |
| Boolean flag parameters | Call sites become unreadable |
| Single endpoint with a `"action"` field dispatching 20 behaviors | Hidden surface area; hard to authorize, hard to rate-limit |
| `v2` endpoint that silently drops fields | v1 consumers upgrade and break |
| Deprecation without measurement | Cannot know when it is safe to remove |
| Removing a field in a minor release | Consumers broken without warning |
| `PATCH` where `PUT` was advertised | Semantics confusion; merge conflicts |
| Unversioned events on a shared bus | One producer upgrade breaks every consumer |
| Proto with re-used field numbers | Wire-incompatible silently |
| JSON fields with inconsistent casing | `userId` next to `user_name` — pick one |
| Error messages designed for developers shown to end users | Leak internals, confuse users |
| Timestamps in local time or without timezone | Always send ISO 8601 UTC with `Z` |
| Epoch-seconds in some fields, ISO strings in others | Consistency matters |

## Interaction with other skills

- [`docs-verified-coding`](../docs-verified-coding) — the consumer side. What this skill builds, that skill consumes correctly.
- [`architecture-decision-records`](../architecture-decision-records) — non-trivial interface choices (REST vs GraphQL, URL vs header versioning) warrant an ADR.
- [`security-hardening`](../security-hardening) — input validation at every boundary; strict accept, defensive reject.
- [`code-review`](../code-review) — interface diffs get extra scrutiny — the "architecture" and "correctness" axes spike on every API change.
- [`deploy-safety`](../deploy-safety) — breaking API changes often require the same expand/contract pattern as DB migrations: add new, migrate consumers, retire old.
- [`test-driven-development`](../test-driven-development) — contract tests belong in the test pyramid.
- [`project-rules-file`](../project-rules-file) — a good rules file includes the project's API conventions (URL shape, error format, pagination style).
- [`incremental-implementation`](../incremental-implementation) — v2 rollout is a multi-slice task, not a single merge.

## Verification checklist

Before publishing a new endpoint / method / type:

- [ ] Consumer identified; stability commitment documented.
- [ ] Name matches the domain glossary, not the implementation.
- [ ] Input validated at the boundary (schema library, protobuf validate, etc.).
- [ ] Error shape follows the project's error standard (RFC 9457 or equivalent).
- [ ] Pagination present on any list endpoint.
- [ ] Idempotency documented (or idempotency key supported) for any mutation that clients will retry.
- [ ] Authn + authz per endpoint (not just "logged in").
- [ ] OpenAPI / proto / SDL updated and committed.
- [ ] Examples exist for request + response + common errors.
- [ ] Test that the schema file in git matches the running server.

Before releasing a breaking change:

- [ ] Four-stage deprecation followed.
- [ ] Usage measured; top consumers contacted.
- [ ] Migration guide written, linked from the deprecation notice.
- [ ] Announced window elapsed.
- [ ] Sunset returns 410 Gone with the migration URL in the body.
