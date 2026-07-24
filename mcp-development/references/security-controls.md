# MCP security controls

Read this reference for every MCP design, implementation, package evaluation,
or review. It translates the NSA security design considerations and the
official MCP security guidance into controls with testable evidence.

## Contents

1. Security model
2. Threat-to-control matrix
3. Human approval policy
4. Authentication and authorization details
5. URL and egress safety
6. Tool and content provenance
7. Sandboxing and execution
8. Logging without leaking data
9. High-assurance additions
10. Third-party MCP package review
11. Primary sources

## Security model

MCP links a model to data and actions. The model can be manipulated by user
input, server metadata, resources, tool results, sampled content, and outputs
from other agents. Therefore:

- the host or broker is the policy enforcement point;
- the server is responsible for handler-level authorization and safe execution;
- protocol content and model decisions are not trusted authorization sources;
- a trusted server can still return compromised or adversarial data;
- each hop in a multi-server chain is a new trust boundary;
- transport protection does not replace authorization, schema validation, or
  execution isolation.

## Threat-to-control matrix

| Threat | Required controls | Evidence |
|---|---|---|
| Missing or confused identity | Authenticate remote callers; identify effective user, client, server, and downstream principal; authorize every invocation | positive and negative identity tests; audit event with effective principal |
| Confused deputy | Per-client consent; exact redirect URI; short-lived single-use state; scope and target-resource binding | OAuth integration tests for client, redirect, state, and resource |
| Token passthrough | Accept only tokens intended for this MCP server; validate audience/resource; acquire a separate downstream token | wrong-audience rejection test; test proving inbound token is never forwarded |
| Session hijacking or event injection | Never use session ID as authentication; authenticate every request; secure random IDs; bind session state to server-side principal; rotate/expire | replay, stolen-session, cross-user queue, and expired-session tests |
| OAuth metadata SSRF | HTTPS except explicit loopback development; safe URL parser; block private/reserved/metadata destinations; validate redirect hops; egress proxy; DNS rebinding defense | malicious metadata/redirect corpus; network policy or proxy test |
| Local server compromise | Display exact executable and arguments before install/run; fixed executable without shell; sandbox; least-privilege filesystem and network | config review; process policy; denied filesystem/network tests |
| Tool parameter injection | Strict schema plus semantic validation; no ambiguous forwarding; typed library calls; fixed subprocess argument arrays; path and query containment | injection and traversal corpus; source review showing no shell interpolation |
| Tool poisoning or indirect prompt injection | Treat descriptions, annotations, resources, prompts, and results as untrusted; bind to verified origin; content cannot modify policy | poisoned metadata/result tests; explicit host policy decision |
| Tool-name collision or path confusion | Namespace by server identity; exact tool ID resolution; reject ambiguous names; never let content dynamically choose a privileged server | duplicate-name and lookalike tests |
| Capability rug pull | Inventory and hash/snapshot approved metadata; monitor `listChanged`; compute risk delta; re-approve new scopes/effects | changed-schema/description/tool tests; approval event |
| Cross-server toxic flow | Preserve provenance and data classification; validate outputs before the next input; broker enforces destination and field policy | taint/data-flow tests; blocked exfiltration scenario |
| Untrusted output or serialization | Validate `structuredContent` against `outputSchema`; cap content types and sizes; encode for the display/execution sink | malformed-output, MIME, oversized, and rendering tests |
| Arbitrary code execution | No generic shell/dynamic imports; sandbox generated code; no direct network; brokered typed calls; no credentials in sandbox | isolation tests and denied syscall/network evidence |
| Replay or duplicate effects | Idempotency keys/deduplication; expiry; maximum retry window; transactional or compensating behavior | duplicate request and partial-failure tests |
| Denial of service or prompt storm | Request/output limits; timeout and maximum timeout; cancellation; rate/concurrency/cost/recursion limits | load, timeout, cancellation, and recursive-call tests |
| Excess privilege | Progressive scopes; per-tool/action authz; least-privileged runtime and downstream identity; deny-by-default egress and filesystem | permissions diff; denied scope and denied destination tests |
| Weak forensics | Structured redacted audit trail; stable request/correlation IDs; integrity-protected centralized storage; alerts for anomalous invocation flows | log schema test; SIEM query or alert exercise |
| Vulnerable or abandoned package | Maintainer/release review; exact version pin; advisories/CVEs; dependency and source scan; inventory and patch owner | lockfile, SBOM, scan report, owner and update policy |

## Human approval policy

Require an approval that names the exact action, target, identity, and likely
impact before:

- creating, updating, deleting, sending, publishing, deploying, purchasing, or
  changing permissions;
- executing model-generated code or commands;
- accessing credentials, regulated data, private messages, broad repositories,
  or data outside the task's stated scope;
- connecting a new server or accepting changed tools/scopes with greater risk;
- moving data between servers or trust zones when that flow was not already
  approved.

Do not use a blanket "approve this MCP server forever" prompt. An approval can
be scoped to one action or one run, but the broker still evaluates each call
against that grant. Display canonical targets after resolution, not only the
user-controlled text that referred to them.

Read-only discovery can run without per-call approval only when identity,
scope, data classification, target boundaries, and logging are already
enforced. Discovery must not expose secrets or broaden later authority.

## Authentication and authorization details

### Remote HTTP

- Treat the MCP server as an OAuth resource server.
- For protected servers, include authorization on every HTTP request.
- For intentionally public servers, use an explicit anonymous principal and
  expose only public, low-risk data and effects; do not silently fall back from
  failed authentication to anonymous access.
- Validate issuer, signature, expiry/not-before, audience/resource, scopes, and
  principal before processing.
- Distinguish `401` invalid/missing authentication from `403` insufficient
  authorization.
- Use the canonical MCP server URI as the resource indicator.
- Use progressive scopes and accept down-scoped tokens.
- Keep MCP-server and downstream-API tokens separate.
- Store refresh tokens only in an appropriate client secret store and rotate or
  revoke them according to the authorization server's policy.

### stdio

The MCP HTTP authorization specification does not apply to stdio. Retrieve
credentials through the controlled environment or a host secret broker. Pass
only explicitly required variables to the child. Avoid inheriting the entire
parent environment, especially cloud credentials and tokens unrelated to that
server.

## URL and egress safety

For authorization discovery, resource links, web fetch tools, callbacks, and
any server-provided URL:

1. parse with a maintained URL/IP library;
2. allow only required schemes; production authorization endpoints use HTTPS;
3. reject userinfo, fragments, encoded parser ambiguities, and dangerous
   schemes where not explicitly needed;
4. resolve and block loopback, link-local, private, multicast, reserved, and
   cloud metadata destinations unless an exact approved use requires them;
5. validate every redirect target;
6. prevent DNS rebinding and time-of-check/time-of-use gaps;
7. enforce the same policy at an egress proxy or network layer;
8. open browser URLs through a platform API, never through a shell.

An application that legitimately accesses internal endpoints should use an
explicit allowlist for those destinations, not disable SSRF protection.

## Tool and content provenance

Maintain an internal identity such as:

```text
<verified-server-id>/<tool-name>@<approved-manifest-digest>
```

The display name can be friendly, but policy and routing use the verified
identity. Store the approved:

- package/artifact identity and version;
- server endpoint or executable plus arguments;
- tool names, schemas, annotations, and descriptions;
- requested scopes, filesystem roots, and network destinations;
- data classifications and side-effect classes.

On `notifications/tools/list_changed` or a package/config update, compare the
new inventory. Added tools, wider schemas, changed descriptions, broader
scopes, new egress, or changed side effects require review before exposure.

Do not use description text as a routing policy. Do not let a resource or tool
result provide the name of a tool, server, credential, or authorization scope
that the host then trusts without independent policy.

## Sandboxing and execution

For a local server or model-generated program:

- run as a dedicated non-root identity;
- use a fresh working directory;
- mount only approved roots, read-only by default;
- deny network by default; broker required calls through typed stubs;
- deny access to SSH agents, cloud metadata, Docker/container sockets, host
  IPC, credential stores, browser profiles, and unrelated environment
  variables;
- set CPU, memory, process, file, output, and wall-clock limits;
- apply seccomp/AppArmor/SELinux/AppContainer or equivalent;
- separate tenants and security domains at process/container boundaries;
- destroy ephemeral state after the run unless retention is required.

Approving generated code is not enough. Every brokered tool call remains
subject to authorization and the run's narrow grant.

## Logging without leaking data

The NSA guide emphasizes detailed logging for incident response. Preserve
forensic value without copying credentials or sensitive payloads into another
high-value data store.

Log structured fields such as:

- timestamp, request/correlation ID, protocol version;
- verified server/client identity and effective principal;
- tool/capability identifier and risk class;
- scopes and policy decision;
- approval identifier and grant boundaries;
- canonical target class or redacted target ID;
- outcome, error class, duration, retry/idempotency status;
- input/output byte counts and optional cryptographic hashes when policy
  requires integrity evidence;
- package and approved-manifest version.

Use field allowlists and deterministic redaction. Never log access/refresh
tokens, authorization headers, cookies, secret values, full credentials,
private keys, or raw sensitive prompts/results by default. For sensitive tool
arguments, log names, classifications, lengths, stable redacted IDs, or hashes
instead of values. Test redaction.

Protect audit logs from modification, define retention and access policy, and
integrate them with SIEM/detection for:

- unexpected tools or principals;
- denied or out-of-scope calls;
- new capability manifests;
- unusual cross-server flows;
- repeated authorization failures;
- recursion, rate, timeout, or output-size anomalies.

## High-assurance additions

The NSA guide recommends message integrity, expiry, and replay controls for
sensitive environments. The MCP core specification does not define a universal
interoperable message-signing format. Add application-level signatures only
inside a controlled architecture with an explicit extension contract, key
management, canonicalization rules, expiry, nonce/replay store, rotation, and
compatibility tests. Do not advertise a private signing envelope as standard
MCP behavior.

TLS, token validation, session binding, idempotency, and broker authorization
remain required even when signatures are added.

## Third-party MCP package review

Before installing or connecting a third-party server:

1. verify the repository, package namespace, publisher, license, maintenance,
   release cadence, security policy, and advisory history;
2. inspect the exact install command, executable, arguments, hooks, and
   transitive dependencies;
3. review tools, schemas, side effects, requested roots, environment, scopes,
   egress, update behavior, and telemetry;
4. pin an exact version and verify signatures/checksums when available;
5. scan source/dependencies and generate an SBOM when practical;
6. run it first in an isolated environment with synthetic data and no
   production credentials;
7. exercise malicious inputs and capability changes;
8. register owner, version, approved manifest, patch SLA, and kill switch.

Never run an unknown package with access to the user's home directory, source
repositories, cloud credentials, browser data, or production network merely to
"see what it does."

## Primary sources

Reviewed 2026-07-23. Re-check current versions before implementation.

- NSA, *Model Context Protocol (MCP): Security Design Considerations for
  AI-Driven Automation*, May 2026:
  https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF
- MCP Security Best Practices:
  https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- MCP Authorization specification:
  https://modelcontextprotocol.io/specification/latest/basic/authorization
- MCP Transports specification:
  https://modelcontextprotocol.io/specification/latest/basic/transports
- MCP Tools specification:
  https://modelcontextprotocol.io/specification/latest/server/tools
