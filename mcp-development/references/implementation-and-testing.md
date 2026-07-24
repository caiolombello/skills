# MCP implementation and testing

Read this reference when writing or testing an MCP client, host, server, or
package.

## Contents

1. Resolve versions before coding
2. MCP architecture and primitive choice
3. Tool contract pattern
4. Server implementation sequence
5. Client and host implementation sequence
6. Transport checklist
7. Test matrix
8. Using MCP Inspector safely
9. Deployment gate
10. Primary sources

## Resolve versions before coding

MCP and its SDKs evolve quickly. At the start of each task:

1. open `https://modelcontextprotocol.io/specification/latest`;
2. record the stable protocol revision to be supported;
3. inspect the project's lockfile and the selected SDK's official repository,
   release notes, and versioned documentation;
4. choose a supported stable SDK line unless the user explicitly asks to
   evaluate a prerelease;
5. pin the dependency and keep protocol/SDK compatibility tests in CI.

Snapshot on 2026-07-23:

- `/specification/latest` resolves to stable revision `2025-11-25`;
- the Python SDK `main` documents v2 as prerelease and v1.x as the production
  line;
- the TypeScript SDK `main` documents v2 as beta and v1.x as the production
  line.

Those SDK transitions were scheduled to change shortly after this snapshot.
Do not preserve this snapshot as an assumption: verify live before selecting
an API or dependency.

Prefer an official, maintained SDK. The official SDK catalog classifies SDKs by
feature completeness, protocol support, and maintenance commitment. A lower
tier is not automatically insecure, but it requires stronger compatibility,
maintenance, and security review.

## MCP architecture and primitive choice

The host owns the user experience, consent, model integration, connection
policy, and broker decisions. A client maintains one connection to one server.
A server exposes narrowly scoped capabilities and enforces authorization and
execution safety at its own boundary.

| Primitive | Primary control | Use it for | Do not use it for |
|---|---|---|---|
| Resource | application/host | addressable read-only context | hidden side effects or privileged instructions |
| Prompt | user | explicitly selected message template | policy, authorization, or automatic privileged execution |
| Tool | model, subject to host/user control | computation, lookup, or explicit side effect | generic unrestricted shell/filesystem/network access |
| Sampling | server request mediated by client | approved model inference | bypassing the host's model/data policy |
| Elicitation | server request mediated by client/user | collecting required additional input | collecting secrets through an untrusted form or URL |

Declare only supported capabilities, use them only after initialization, and
honor version/capability negotiation. Experimental extensions need explicit
namespacing, compatibility tests, and a downgrade/failure policy.

## Tool contract pattern

Prefer a narrow descriptor:

```json
{
  "name": "tickets.get",
  "description": "Read one ticket by its canonical ID. No side effects.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ticketId": {
        "type": "string",
        "pattern": "^TKT-[0-9]{1,10}$",
        "maxLength": 14
      }
    },
    "required": ["ticketId"],
    "additionalProperties": false
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "status": {
        "type": "string",
        "enum": ["open", "closed"]
      }
    },
    "required": ["id", "status"],
    "additionalProperties": false
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": true,
    "openWorldHint": false
  }
}
```

The schema is necessary but not sufficient. The handler must still:

1. authenticate the request;
2. authorize the principal for the resolved ticket;
3. canonicalize and validate the ID;
4. query through a parameterized API;
5. filter fields by data policy;
6. return structured content matching `outputSchema`;
7. emit a redacted audit event.

Annotations help clients render and plan; they do not prove behavior or grant
permission.

## Server implementation sequence

1. Initialize the official SDK using the project's established runtime.
2. Implement lifecycle and capability negotiation.
3. Add one read-only capability with strict input/output schemas.
4. Put authentication and authorization middleware before dispatch, then
   enforce object/action authorization again in the handler.
5. Add timeouts, cancellation, rate/concurrency limits, bounded pagination, and
   structured errors.
6. Add redacted audit events with request/correlation IDs.
7. Add mutation only after the read path and denial paths pass.
8. For mutation, add exact approval context, idempotency/deduplication, partial
   effect reporting, and compensating behavior where needed.
9. Add deployment isolation and a kill switch.

Keep business logic independent of protocol adapters so it can be unit tested
without a transport and reused without duplicating policy.

## Client and host implementation sequence

1. Maintain explicit server identities and configuration; display the exact
   local executable/arguments or remote origin before consent.
2. Negotiate protocol version and capabilities before operation.
3. Namespace tools by verified server identity and reject ambiguous routing.
4. Validate discovered schemas and cap catalog size.
5. Treat descriptions, annotations, prompts, resources, and results as
   untrusted.
6. Apply per-call authorization and human-approval policy in the host broker.
7. Hold credentials in the host; never expose them to the model or generated
   code.
8. Validate `structuredContent` against `outputSchema`.
9. Re-evaluate `listChanged` and server/package updates before exposing changed
   capabilities.
10. Bound retries, concurrent calls, result size, model recursion, and cost.

For progressive discovery, apply authorization filtering before a tool enters
the model context. Search results must not reveal tools the current principal
cannot use. For programmatic tool calling, run code in a no-network sandbox and
route typed calls through the same broker and approval rules as direct calls.

## Transport checklist

### stdio

- fixed executable and argument array; no `shell: true` or command string;
- minimal explicit environment;
- no non-MCP output on `stdout`; logs use `stderr` or a structured sink;
- process, filesystem, network, CPU, memory, output, and time limits;
- clean shutdown: close input, wait, terminate, then force only after a bound;
- synthetic/test credentials for development tools.

### Streamable HTTP

- production TLS and controlled origin;
- validate `Origin`; local servers bind to loopback, not all interfaces;
- authorization on every request;
- `MCP-Protocol-Version` on subsequent requests where required by the
  negotiated specification;
- bounded request bodies, streams, resumability buffers, sessions, and event
  queues;
- safe CORS, reverse-proxy, timeout, rate-limit, and error configuration;
- SSRF-safe OAuth discovery and redirects;
- session IDs random, expiring, principal-bound, and never authentication.

Prefer current standard transports. Add a custom transport only when the
requirement cannot be met otherwise and document its authentication,
confidentiality, integrity, framing, replay, lifecycle, and interoperability
contract.

## Test matrix

### Protocol and contracts

- initialize is first; incompatible versions fail closed;
- only negotiated capabilities are used;
- pagination, cancellation, timeout, progress, errors, and shutdown behave as
  specified;
- valid tool calls and results conform to input/output schemas;
- missing fields, unknown fields, wrong types, invalid formats, extreme
  values, oversized arrays/objects, deep nesting, and malformed JSON-RPC fail
  safely;
- `stdout` remains protocol-clean for stdio.

### Identity and authorization

- missing, invalid, expired, wrong-issuer, and wrong-audience tokens fail;
- insufficient scope returns denial without data;
- object/tenant ownership is checked after canonicalization;
- authorization runs on every request in a session;
- inbound bearer token never appears in a downstream request;
- reduced scopes work and privileged scopes elevate incrementally;
- stolen/guessed session IDs and cross-user queued events fail.

### Injection and boundary abuse

- shell metacharacters remain literal arguments or are rejected;
- path traversal, symlink escape, encoded separators, and alternate path forms
  cannot leave allowed roots;
- SQL/query/filter input stays parameterized and bounded;
- authorization URLs reject unsafe schemes and shell opening;
- OAuth metadata and redirects cannot reach loopback, private, link-local,
  reserved, or cloud metadata endpoints;
- DNS rebinding and redirect-hop policy are exercised;
- environment injection and dynamic module/executable selection fail.

### Agentic and supply-chain abuse

- poisoned tool descriptions cannot change policy or trigger privileged calls;
- tool results containing instructions cannot grant scopes or choose
  destinations;
- duplicate/lookalike tool names route deterministically or fail;
- new/changed tools, schemas, descriptions, scopes, or annotations remain
  unavailable until reviewed;
- cross-server data exfiltration is blocked by broker data-flow policy;
- generated code has no direct network or credential access;
- unmaintained, vulnerable, unsigned, or unexpected package versions fail the
  deployment gate.

### Reliability and forensics

- retries do not duplicate mutations;
- partial effects are reported and recoverable;
- concurrency, rate, output, memory, recursion, cost, and maximum timeout limits
  hold;
- cancellation releases work;
- logs contain identity, action, policy, approval, outcome, and correlation
  fields;
- tokens, authorization headers, cookies, secrets, and sensitive payloads are
  absent from logs and model-visible errors.

## Using MCP Inspector safely

MCP Inspector is useful for connectivity, negotiation, capability inspection,
invalid inputs, missing arguments, concurrency, and error behavior. It is not a
substitute for automated adversarial tests.

- pin an exact Inspector version;
- run it in an isolated development environment;
- inspect only code/packages already reviewed;
- use synthetic data and test credentials;
- do not expose its local interface to untrusted networks;
- do not use an unpinned `npx -y` invocation as a repeatable security check;
- preserve automated tests for every regression found manually.

The NSA report cites a historical MCP Inspector RCE as evidence that the
testing toolchain itself needs patching and isolation. Do not turn the cited
fixed version into a permanent minimum; check current advisories and releases.

## Deployment gate

- [ ] Stable protocol and SDK versions recorded and pinned.
- [ ] Trust/capability matrix reviewed.
- [ ] Authentication, per-call authorization, and approval policy tested.
- [ ] No token passthrough or session-as-authentication.
- [ ] Input and output schemas plus semantic validation tested.
- [ ] Sandbox, filesystem, network, secret, and runtime identity boundaries
      verified.
- [ ] Time, rate, concurrency, output, recursion, and cost bounds verified.
- [ ] Adversarial and cross-server data-flow tests pass.
- [ ] Dependency/source/secret scans pass; SBOM retained when supported.
- [ ] Redacted audit telemetry reaches monitoring.
- [ ] Inventory, owner, patch process, kill switch, and incident path exist.
- [ ] Residual risk and unverified controls are explicit.

## Primary sources

Reviewed 2026-07-23. Resolve the latest stable revision and SDK documentation
again before implementation.

- MCP latest specification: https://modelcontextprotocol.io/specification/latest
- MCP versioning:
  https://modelcontextprotocol.io/docs/learn/versioning
- MCP lifecycle:
  https://modelcontextprotocol.io/specification/latest/basic/lifecycle
- MCP tools:
  https://modelcontextprotocol.io/specification/latest/server/tools
- MCP resources:
  https://modelcontextprotocol.io/specification/latest/server/resources
- MCP prompts:
  https://modelcontextprotocol.io/specification/latest/server/prompts
- MCP transports:
  https://modelcontextprotocol.io/specification/latest/basic/transports
- MCP authorization:
  https://modelcontextprotocol.io/specification/latest/basic/authorization
- MCP official SDK catalog: https://modelcontextprotocol.io/docs/sdk
- MCP client best practices:
  https://modelcontextprotocol.io/docs/develop/clients/client-best-practices
- MCP Inspector: https://modelcontextprotocol.io/docs/tools/inspector
- Official Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Official TypeScript SDK:
  https://github.com/modelcontextprotocol/typescript-sdk
