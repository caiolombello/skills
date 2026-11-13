# Domain: AI, LLM, and agents

Load when a language model takes part in a trust-sensitive decision: assistants, RAG, persistent agent memory, tool-calling loops, MCP servers and clients, prompt assembly from untrusted input, or code that acts on model output. The flow to follow is **untrusted content → model or memory → capability, authority, or sink**.

This adds a delegation layer on top of the core classes; transport, access control, query building, filesystem use, and rendering remain ordinary boundaries. Split large targets by retrieval, memory, tool dispatch, MCP, and output. Bold names and headings are ledger block identifiers.

### AI discipline

```text
- Prompt injection by itself is not a finding. Require a code-level boundary failure:
  content reaches another principal's context, invokes authority the requester lacks,
  discloses data they cannot read, or drives a sink they cannot reach directly.
- Model output, memory, tool descriptions, and MCP responses are untrusted input.
  Point to the code that grants authority, trusts output, writes durable state, or
  feeds a sink.
- A guardrail prompt is not a security control. Count only deterministic checks,
  resource-scoped authorization, isolation, binding, and constrained credentials.
- State attacker, affected principal, effective execution identity, resource, exact
  action, authority used, and observable result. A user deliberately asking the model
  to use the user's own authority is not a delegation defect.
- Authorization and action binding are separate controls: attacker content that
  triggers an action under a victim's valid authority, which the victim did not
  request or approve, is an action-binding failure.
- Draw four maps first: execution identities, capabilities, writable context and memory
  sources, output destinations. Then work backward from side-effecting tools and
  durable memory reads. The strongest gate must sit after arguments are final and
  before every side effect, on direct, queued, retry, resume, batch, and delegated paths.
```

### Context, retrieval, and memory

**Indirect injection through retrieved or ingested content** — an attacker writes a document, page, file, email, issue, tool response, or metadata that enters a *different* principal's context. Trace who can write each source, how retrieval scopes it, whose session consumes it, and what capability it enables there.

**Cross-session or cross-tenant context bleed** — history, embeddings, retrieval results, or prompt caches keyed too broadly. Tenant and ACL filters must be in the query and every cache key, including batch and alternate paths.

**Persistent memory poisoning** — attacker content or model summaries become durable memory that later shapes another user's or a privileged task. Review who creates, merges, and deletes memory, its provenance and tenant scope, and whether low-trust observations become instructions. A user's own saved memory used for that user's requests is not cross-boundary.

**Prompt role and provenance confusion** — prompt assembly lets untrusted text pose as system message, prior turn, tool result, policy, or memory (string concatenation, untyped history, caller-set role fields, lossy serialization). Show the forged provenance changes a deterministic decision or reaches a capability.

### Tools and actions

**Tool-argument injection into a downstream sink** — model-produced arguments reach SQL, shell, file, URL fetch, or privileged APIs without handler-side validation. A schema narrows shape; it does not establish authorization, safe paths, safe URLs, or query semantics.

**Excessive agency and confused-deputy authority** — the agent acts with a service or broad credential and the handler does not re-check the requester's permission on the named resource. Shared credentials with enforced per-user scope are not a defect.

**Action-confirmation and approval binding** — the user approves one action but execution uses changed arguments, resource, principal, or a later turn; or attacker content causes an unrequested side effect under the victim's authority. Approval must bind tool name, full normalized arguments, requester, target, amount, expiry, and batch membership, and must not cover retries or duplicates.

**Tool-schema and dispatcher disagreement** — the schema accepts aliases, extra or duplicate keys, coercions, free-form nested objects, or out-of-range values that the handler interprets differently. Re-validate where values become resource selectors.

**Unbounded delegated action loops** — one request can enqueue repeated spend, sends, mutations, or external calls without per-request budget, per-action authorization, cancellation, or idempotency. Validate with code-level accounting and a small bounded local loop, never by exhausting a service.

### MCP and sub-agents

**Sub-agent and MCP trust inheritance** — a delegated task receives the full session, credentials, memory, or capabilities instead of the minimum, or its results are trusted on return.

**MCP server and tool identity confusion** — calls or results routed by attacker-influenced server names, tool names, request IDs, resource URIs, or aliases instead of the authenticated connection and pending request; two servers claiming one tool; reconnect changing the binding.

**MCP metadata and schema as policy** — peer-supplied tool descriptions, resource metadata, prompts, or schemas treated as policy or authorization. They may guide the model but grant nothing; find the deterministic allowlist and handler authorization that win on conflict.

### Output and disclosure

**Insecure output rendering** — model output reaches HTML, Markdown, template, URL, or command sinks without the sink's encoding and policy. For browsers pair with the browser part of [domain-web-and-client.md](domain-web-and-client.md); renderer behavior outside the repo makes it `needs_validation`.

**Sensitive context extraction** — assembled context contains credentials, another user's data, private source, or access-granting policy values, and user-influenced output can reveal them. Generic system-prompt disclosure that crosses no data boundary is not a finding.

### AI validation

1. Name the crossed boundary and result: attacker, affected principal or shared resource, execution identity, target, and the unauthorized or unrequested action or disclosure.
2. Confused deputy: prove the tool lacks requester-and-resource authorization and the attacker cannot do the same action through the normal interface. Action binding: prove attacker content caused an action under the victim's authority that the victim did not request or approve; generic authorization does not establish intent.
3. Memory and retrieval: cite both the attacker-controlled write and the later cross-principal read or privileged decision.
4. Binding and schema: compare the approved or validated normalized object with the object the handler actually uses, and show a locally observable unrequested action, mutation, duplicate, or authority change — without carrying out a harmful action.
5. MCP identity: verify authenticated connection, request correlation, tool namespace, and effective credential; external server identity or routing makes it `needs_validation`.
6. Real model and provider behavior are not locally observable: use deterministic stubs for the model in local checks, and never spend paid quota.
