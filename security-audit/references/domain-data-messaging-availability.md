# Domain: data isolation, messaging, and availability

Load the part whose boundary reconnaissance found:

- **Part A** — multi-tenant or access-controlled stores, derived copies (cache, search, analytics, previews), object links, export/import, migration, deletion, revocation, retention.
- **Part B** — gRPC, GraphQL transports, Protobuf/Thrift/Cap'n Proto, custom protocols, streaming RPC, webhooks, queues, brokers, pub/sub.
- **Part C** — untrusted work that can consume shared CPU, memory, disk, connections, workers, queues, quotas, or operator-owned spend.

Hunter briefs get the discipline block, chosen class entries, and validation block for each part used. Bold names and headings are ledger block identifiers.

## Part A — data isolation and lifecycle

### Data isolation discipline

```text
- A tenant or owner column is not isolation. Find the query, key, path, policy, or
  row-level control that enforces it on each read and write path.
- Follow derived copies: search, cache, analytics, export, previews, logs, replicas,
  and backups can have different ACLs and retention than the primary record.
- Deletion and revocation are lifecycle promises covering current, historical, cached,
  indexed, exported, restored, and queued copies within the product's stated boundary.
- A privacy preference is not automatically a vulnerability. Require an explicit
  access boundary or deletion/revocation guarantee and an unauthorized reader or later
  operation.
- Pick one protected record and draw write, query, cache, index, event, export, backup,
  deletion, and restore paths, marking principal and tenant on every edge. Start with
  bypass clients, background jobs, migrations, global uniqueness, and cache keys.
```

**Missing tenant or owner enforcement** — a read, update, delete, list, count, or bulk query selects an object without binding it to the authenticated tenant or owner, or trusts a body field for that identity. Compare direct, nested, background, admin, import, and legacy paths.

**Composite-key and namespace collision** — cache keys, object paths, unique constraints, search document IDs, temp files, or dedup keys omit tenant or environment, so two principals collide on one logical key.

**Policy and query disagreement** — row-level policy, ORM default scopes, and raw or service clients apply different predicates; check joins, aggregates, views, `unscoped` clients, and paths where request context is missing.

**Blob and signed-reference overreach** — attachment IDs, version IDs, share links, or signed URLs allow operations or namespaces beyond the issuer's access, or outlive an ACL change. Bind operation, exact object and version, audience, expiry, tenant.

**Search, cache, and index ACL drift** — an ACL or lifecycle change does not invalidate a searchable, cached, embedded, thumbnail, feed, preview, or index copy; retrieval-time filtering is missing.

**Analytics, logs, and diagnostics as alternate readers** — private content or credentials emitted to systems with broader access, longer retention, or tenant mixing. Confirm the data class and a realistic reader.

**Enumeration and aggregate oracles** — counts, filters, ordering, errors, uniqueness conflicts, timings, or notifications reveal a concrete confidential predicate.

**Export and backup scope expansion** — an export, snapshot, report, or backup includes other tenants, hidden fields, soft-deleted or secret data, or history above the requester's access; download of the final artifact is not authorized.

**Import and restore authority expansion** — import or restore bypasses ownership, schema, ACL, uniqueness, or validation, overwrites existing resources, or writes into a tenant the requester cannot write. Archive contents are untrusted.

**Migration default and ownership confusion** — old records lack tenant, ACL, or lifecycle fields, IDs collide, or old and new readers apply different defaults during rollout, backfill, dual-write, or rollback.

**Backup and replication boundary drift** — keys, storage accounts, replicas, restore environments, or support snapshots have broader scope than primary data. Only in-repo policy is source-confirmable.

**Soft-delete and tombstone bypass** — lookup, search, relations, links, background processors, or restore ignore the lifecycle predicate; deleted identifiers can be re-registered while references remain.

**Stale authorization and derived copy use** — membership removal, ACL change, consent withdrawal, secret revocation, or downgrade leaves sessions, caches, subscriptions, jobs, or materialized data still authorizing.

**Retention and queued-work overrun** — deletion completes in primary storage while queued work, retries, exports, analytics, or generated artifacts recreate or keep the data.

**Restore reintroduces invalid state** — undo, undelete, or replica recovery restores data, credentials, memberships, or permissions current policy no longer allows.

### Data isolation validation

1. Name the lower-trust principal, protected data or state, affected owner or tenant, the alternate copy or operation, and the unauthorized disclosure or mutation.
2. Cite the intended source-of-truth policy and the path that omits or contradicts it; confirm no other layer enforces the same condition.
3. Prove with two dummy tenants through the same local service methods, repeated after ACL change, deletion, account switch, or restore as relevant. Stop at the minimum record or operation.
4. External cache, object storage, replicas, analytics, backup, or retention policy that decides the outcome makes it `needs_validation` with the owner-observed check.

## Part B — protocols, RPC, and messaging

### Messaging discipline

```text
- "Internal" is not authentication. Name the peer identity at every hop and how it
  becomes the application principal used for authorization.
- Schema validation proves shape, not provenance, authority, ordering, or safe values.
  Follow decoded fields to policy and side effects.
- Broker and application guarantees differ. Write down retry, ordering, ack, dedup,
  and transaction behavior before judging state changes.
- Parser disagreement needs two concrete consumers, schema versions, or encodings and
  one security-relevant divergent value.
- Draw producer -> transport -> gateway -> consumer -> storage per message family.
  Compare normal, retry, dead-letter, replay, migration, reflection, stream, and
  gateway-transcoded routes.
```

**Message boundary and canonicalization disagreement** — components disagree on length, compression, duplicate or unknown fields, encoding, numeric width, or envelope/body precedence, and a different principal, resource, or operation results.

**Union, enum, and default confusion** — unknown variants, missing discriminators, zero values, or compatibility mappings reach code that assumes a validated case or grants a default privilege.

**Envelope and payload identity mismatch** — authorization uses envelope or routing metadata while the handler acts on a conflicting tenant, subject, or object in the body.

**Interceptor and method-path inconsistency** — auth interceptors cover unary calls but not streams, reflection, health, gateway-transcoded paths, compatibility services, or individual stream messages.

**Peer identity to application-principal confusion** — mTLS, workload identity, or broker credentials authenticate the channel while a caller field selects the user or tenant without binding.

**Per-item and streaming authorization gaps** — a stream, subscription, or batch is authorized once, then later items name other resources or continue after revocation.

**Callback and reply-correlation confusion** — predictable, reused, or cross-tenant correlation IDs let a response, webhook, cancel, or ack satisfy another caller's pending operation.

**Topic, routing-key, and subscription scope gaps** — a client selects another tenant's topic, wildcard, consumer group, partition, reply queue, or dead-letter route. Tenant text in a payload is not isolation.

**Dead-letter, retry, and diagnostic disclosure** — failure paths route secrets or cross-tenant payloads to consumers or operator views with lower trust.

**Untrusted producer treated as control plane** — a message declares itself an admin event, provider callback, replication record, or migration step without an authenticated producer and event type.

**Duplicate delivery and idempotency gaps** — redelivery repeats a non-idempotent side effect because dedup is missing, happens after mutation, or uses a colliding key.

**Out-of-order and stale message acceptance** — older state, revoked membership, or canceled work arrives late and overwrites newer state.

**Acknowledgment and commit ordering defects** — ack before durable commit loses security-relevant work, or commit before an unreliable ack duplicates a mutation.

**Partial multi-consumer transitions** — several consumers implement one authorization or business transition and partial failure leaves an invalid subset committed.

### Messaging validation

1. Name the realistic producer or peer, accepted message, authenticated channel identity, affected principal or resource, and unauthorized mutation or disclosure.
2. Disagreement claims cite both parsers or consumers and the divergent value; safe rejection on either side prevents confirmation.
3. Replay and ordering claims establish actual delivery guarantees and reproduce the failure with an in-memory or local transport, without generating load.
4. Broker ACLs, mesh identity, topic attachment, or compatibility behavior outside the repository make it `needs_validation`.

## Part C — resource exhaustion and availability

### Availability discipline

```text
- Require an input-to-cost path, a missing effective bound, and impact on another user,
  a shared service, a safety function, or operator-owned spend. Self-limited work in
  the requester's own process is not a service vulnerability.
- A missing rate limit is not enough: check body/message/file caps, concurrency,
  queues, deadlines, database constraints, upstream gateways, and tenant quotas first.
- Never stress or saturate anything. Use complexity analysis, small growth points,
  mocked paid calls, strict local limits, and deterministic cancellation tests.
- State attacker cost, service work, persistence, scope, and recovery. One small input
  with superlinear or persistent shared effect differs from sustained volume.
- Build an input-to-resource table: earliest size/cardinality gate, work before auth,
  fan-out, persistence, shared pool, limit and cleanup owner, recovery.
```

**Superlinear parsing, matching, or evaluation** — small accepted input drives catastrophic regex backtracking, nested parsing, recursive validation, graph traversal, template expansion, or adversarial hashing.

**Decompression and representation amplification** — compressed, sparse, nested, or aliased input expands far past the checked size; limits are not re-applied after each expansion stage.

**Database and downstream query amplification** — unbounded depth, cardinality, pagination, or expansion produces broad scans, fan-out, or many downstream calls beyond what authorization intends.

**Unbounded buffering and cardinality** — bodies, streams, uploads, sessions, cache keys, metric labels, subscriptions, or pending jobs accumulate without per-item and aggregate limits or cleanup on disconnect and cancel.

**Handle and temporary-resource leaks** — malformed or canceled work leaves sockets, files, cursors, timers, subprocesses, or temp files that drain a shared pool.

**Detached work after cancellation** — timeouts, disconnects, or failed authorization return while database, model, network, or worker work keeps running.

**Pre-authentication work imbalance** — expensive parsing, crypto, decompression, lookups, or outbound requests before authentication and the first size or rate gate.

**Quota-accounting scope and reset gaps** — accounting keyed on attacker-influenced IP, route, key prefix, or task ID, or broken by overflow, races, retries, or account switching.

**Worker, pool, and priority starvation** — attacker jobs hold shared locks, workers, connection pools, event-loop turns, or priority beyond their deadline or fairness limits.

**Reachable fatal error or deadlock** — untrusted input reaches panic, abort, unhandled exception, exit, lock cycle, or infinite loop in a shared process; establish supervisor scope.

**Retry storm and fail-open amplification** — failures trigger synchronized or unbounded retries without jitter, ceilings, circuit breaking, or dedup.

**Poison-record and head-of-line blocking** — one malformed record repeatedly fails at the head of a shared queue, partition, startup scan, or recovery loop.

**Unsafe recovery and capacity rollback** — restart, restore, or cleanup rebuilds unbounded state, ignores quotas, or replays the input that caused the failure.

### Availability validation

1. Name the untrusted input, requester work, amplification or retained resource, shared blast radius, and recovery. Missing limits without shared impact are hardening.
2. Confirm no source-visible upstream, parser, queue, tenant, or framework bound prevents it; unknown deployed limits, autoscaling, or quotas make it `needs_validation`.
3. Superlinear: show accepted complexity and a small local growth curve under strict limits. Leaks: show retention after cleanup should occur. Fatal paths: identify process and supervisor isolation.
4. Prioritize by low attacker effort, unauthenticated reach, cross-tenant scope, persistence, and poor recovery — never by causing an outage.
