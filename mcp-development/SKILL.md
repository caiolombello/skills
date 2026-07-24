---
name: mcp-development
description: Use when designing, implementing, testing, evaluating, or reviewing an MCP client, server, tool, resource, prompt, transport, authorization flow, or package. Enforce the current stable MCP specification, least privilege, explicit approval, sandboxing, and adversarial security tests.
---

# Secure MCP Development

Build Model Context Protocol integrations in which content never grants
authority. Follow the current stable protocol and official SDK for the selected
language, then enforce security at the host, transport, handler, and execution
boundaries.

## Scope and neighboring skills

Use this skill for MCP-specific architecture, implementation, package
evaluation, protocol review, or testing. Keep security in the same workflow as
development; a separate optional MCP-security path would make the normal path
unsafe by omission.

Pair with:

- `docs-verified-coding` to resolve the current stable specification, SDK line,
  and exact APIs before coding.
- `api-and-interface-design` when a broader public API or compatibility policy
  is also changing.
- `security-hardening` for deeper application-layer controls around the MCP
  integration.
- `pass-cli-secrets` for local credentials and the project's workload secret
  store for deployed credentials.
- `incident-response` if there is evidence of an active compromise. This skill
  designs and hardens; it does not lead a live incident.

## Required references

- For every MCP design, implementation, package evaluation, or review, read
  [`references/security-controls.md`](references/security-controls.md).
- When writing or testing code, also read
  [`references/implementation-and-testing.md`](references/implementation-and-testing.md).

These references are part of the workflow, not optional background.

## Non-negotiable invariants

1. **Content cannot authorize.** Prompts, resources, tool descriptions,
   annotations, tool results, sampled output, and model-generated code are data;
   none can grant a scope, bypass approval, or select a privileged identity.
2. **Authorize every invocation.** Validate the authenticated principal,
   audience, scope, target object, and current policy inside the broker or
   handler on every call. A session ID is never authentication.
3. **Never pass inbound bearer tokens downstream.** Validate tokens issued for
   this MCP server and obtain a separate, audience-bound downstream credential.
4. **Constrain execution.** Do not interpolate model or user input into a shell,
   executable, path, URL, query, or import. Prefer typed APIs and fixed argument
   arrays. Sandbox code execution and deny unnecessary filesystem and network
   access.
5. **Require meaningful approval for risky effects.** Writes, deletes, sends,
   deployments, purchases, permission changes, arbitrary execution, and
   sensitive-data access need an approval showing the exact action, target, and
   impact. Approving a script or server does not approve every call it makes.
6. **Treat capability changes as security changes.** Re-evaluate
   `listChanged`, new tools, changed schemas/descriptions, new scopes, and
   server/package updates before exposing them to the model.
7. **Keep secrets out of protocol content and telemetry.** Credentials stay in
   the host or workload secret store, never in model context, tool arguments
   when avoidable, URLs, source, or logs.
8. **Bound all work.** Apply input/output size limits, timeouts, cancellation,
   concurrency limits, rate limits, recursion budgets, and resource quotas.

## Workflow

### 1. Investigate before choosing APIs

Read repository rules, lockfiles, runtime constraints, existing transports,
auth middleware, tests, and deployment manifests. Record:

- target host/client/server and data flow;
- current stable MCP protocol revision;
- official SDK, stable release line, and pinned project version;
- supported transports and negotiated capabilities;
- existing identity, authorization, approval, and secret mechanisms.

Do not copy examples from an SDK's prerelease branch into production code.
Never invent a method or schema from memory.

### 2. Draw the trust and capability map

Map the host, each client, each server, authorization server, downstream API,
tool runtime, model, user, queue/cache, and logging destination as separate
principals or trust zones. For each capability record:

| Field | Required decision |
|---|---|
| Primitive | tool, resource, prompt, sampling, elicitation, or other negotiated capability |
| Risk | read, write, destructive, execute, admin, or external communication |
| Data | public, internal, confidential, regulated, credential, or unknown |
| Identity | caller, effective principal, downstream principal |
| Boundary | filesystem roots, network destinations, tenant/account, object IDs |
| Approval | none, per action, scoped for one run, or prohibited |
| Limits | size, time, concurrency, calls, cost, recursion |
| Evidence | audit fields and tests proving the controls |

Reject designs that cannot identify the effective principal or bound the
affected data and side effects.

### 3. Minimize the MCP surface

Choose the smallest correct primitive:

- **Resource** for addressable read-only context selected by the application.
- **Prompt** for a user-selected template; never use it as a privileged policy.
- **Tool** for model-invoked computation or effects.

Do not expose a generic shell, arbitrary HTTP fetch, unrestricted filesystem,
raw SQL, dynamic import, or catch-all `action` tool when narrower capabilities
will work. Split read and mutation operations when they need different scopes,
approvals, or audit semantics.

### 4. Define strict contracts

For every tool:

- use a stable, server-namespaced name and one responsibility;
- define strict `inputSchema` and, when structured data is returned,
  `outputSchema`;
- reject unknown fields unless forward compatibility explicitly requires them;
- bound strings, arrays, objects, nesting, numeric ranges, formats, URIs,
  paths, and pagination;
- return `structuredContent` conforming to `outputSchema`; validate it at the
  client boundary;
- describe side effects, idempotency, required scopes, approval, data
  sensitivity, and failure behavior;
- treat annotations such as `readOnlyHint`, `destructiveHint`, and
  `idempotentHint` as untrusted hints, never enforcement.

Validate semantic context after schema validation: tenant ownership,
authorization, path containment, URL destination, state transition, and quota.
Block ambiguous parameter forwarding between tools or servers.

### 5. Secure identity, authorization, and transport

For `stdio`, use credentials supplied through a controlled environment or
secret broker; do not apply the HTTP OAuth flow. Launch a fixed executable with
a fixed argument array, without a shell. Reserve `stdout` exclusively for valid
MCP messages and send logs to `stderr` or a structured sink.

For Streamable HTTP:

- use TLS in production, validate `Origin`, and bind local-only servers to
  loopback;
- for protected servers, authenticate and authorize every HTTP request,
  including requests in an existing logical session; if a server is
  intentionally public, represent the caller as an anonymous principal and
  permit only explicitly public, low-risk capabilities;
- validate token issuer, signature, expiry, audience/resource, scopes, and
  principal;
- use exact redirect URI validation, PKCE/state protections, safe browser APIs,
  and progressive least-privilege scopes;
- harden OAuth metadata discovery and every redirect against SSRF, DNS
  rebinding, private/reserved addresses, and cloud metadata endpoints;
- never place tokens in query strings and never use session IDs as credentials.

Respect lifecycle ordering, protocol-version negotiation, and capability
negotiation. Disconnect on unsupported versions or required capabilities.

### 6. Enforce the execution boundary

Authorize inside every tool handler or host broker immediately before the
effect. Then:

- resolve canonical target IDs and re-check ownership;
- use allowlisted operations, paths, hosts, methods, and database statements;
- pass typed arguments directly to libraries or subprocess argument arrays;
- use least-privileged service identities and short-lived credentials;
- sandbox execution with no network by default, minimal filesystem roots,
  non-root identity, read-only filesystems, and OS/container controls;
- add idempotency keys or deduplication for retryable mutations;
- report partial side effects explicitly on error;
- keep a kill switch for high-risk capabilities.

### 7. Defend the model and tool chain

Bind every discovered capability to a verified server identity and namespace.
Snapshot or hash approved tool metadata when practical. On capability or
package changes, compute the risk delta and require re-approval before exposing
new privileges.

Treat every cross-server result as tainted. Validate its schema and provenance,
apply data-flow policy, and prevent it from selecting credentials, destinations,
tools, or scopes. Keyword filtering may add telemetry but is not a primary
control; rely on authorization, typed contracts, provenance, isolation, and
explicit policy.

### 8. Implement and test a thin slice

Start with one low-risk read capability and its client call. Prove
initialization, negotiation, schema validation, authorization denial, success,
timeouts, and clean shutdown before adding mutations or dynamic discovery.

Add tests while implementing. The minimum suite includes:

- contract and protocol lifecycle tests;
- per-tool positive and negative authorization tests;
- malformed, unknown, oversized, deeply nested, and concurrent requests;
- command/path/query injection, SSRF, token audience/passthrough, session
  replay, tool-name collision, poisoned descriptions/results, capability rug
  pull, recursive calls, and partial-side-effect cases;
- audit redaction tests proving tokens and sensitive payloads do not appear.

Use MCP Inspector only as an isolated development aid with an exact pinned
version and test credentials. It supplements automated tests; it is not a
security scanner or production control.

### 9. Review and ship

Before deployment:

- pin dependencies and verify maintained provenance;
- run unit, integration, protocol, adversarial, dependency, secret, and static
  security checks;
- generate an SBOM where the deployment process supports it;
- configure runtime identity, filesystem, network, resource, logging, and
  secret boundaries;
- inventory the server, tools, versions, owners, data classes, scopes, and
  emergency-disable path;
- connect structured, redacted audit events to monitoring and incident
  response;
- document residual risk and what was not verified.

## Output contract

For a design or review, return:

1. current protocol/SDK assumptions and evidence;
2. trust-boundary and capability matrix;
3. findings ordered by exploitability and blast radius;
4. implementation or remediation plan mapped to controls;
5. verification evidence, residual risk, and unverified items.

For code changes, implement the smallest safe slice, test it, and identify every
new permission, network destination, filesystem root, secret, and side effect.
