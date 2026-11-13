# Domain: web, identity, and browser

Load when source shows an HTTP parsing, caching, session, or identity boundary (web apps, APIs, proxies, gateways, custom HTTP servers, JWT, OAuth/OIDC, SAML, MFA, passkeys, recovery, API keys, mTLS), or trust decisions and untrusted rendering in a browser (SPAs, extensions, webviews, service workers, browser storage, cross-window messaging). Core access control asks whether a principal may act; this domain asks whether the HTTP, identity, or browser layer confuses *which* principal, request, origin, token, or assurance level an action belongs to.

Hunter briefs get the discipline block, the chosen class entries, and the validation block for each part used. Bold names and headings are ledger block identifiers.

## Part A — HTTP and identity

### Web and identity discipline

```text
- Framing and cache claims need two components that interpret the same request,
  response, or key differently. Name both and the normalized value on each side.
- For every credential, locate signature or secret verification and every binding its
  role needs: issuer, audience, origin, relying party, client, session, principal,
  resource, assurance, expiry, one-time state.
- Host, Forwarded, X-Forwarded-*, Origin, Referer, redirect targets, callback state, and
  request-derived URLs are trust decisions. Trace each to the identity or response it
  affects.
- A missing header, cookie flag, MFA prompt, or rate limit is not a finding alone.
  Require an accepted invalid request, cross-principal effect, assurance downgrade, or
  credential disclosure.
- Walk issue -> store -> transmit -> consume -> refresh -> revoke for each credential,
  across normal, error, retry, legacy, migration, and account-switch paths. The
  effective policy is the weakest door to the same identity or operation.
- Proxy chains, edge cache keys, IdP policy, certificate trust, and deployed auth modes
  are often outside the repository: needs_validation, not assumption.
```

### HTTP framing and caching

**Request framing and desynchronization** — front and back ends disagree on request length or header normalization (duplicate `Content-Length`, `Transfer-Encoding`, HTTP/2–3 downgrade, header-name folding, CR/LF handling). Show which bytes each side assigns to which request.

**Web cache poisoning through unkeyed input** — a request value changes cached content or security headers but is missing from the cache key (forwarded host or scheme, selected cookies, query normalization, language or device headers, auth state).

**Cache deception and private-response caching** — the cache treats a private dynamic path as static, or caches a response whose identity inputs are not in the key. Compare edge cacheability with application routing and cache directives.

**Host and forwarded-header trust** — client-suppliable host or proxy metadata drives absolute URLs, tenant routing, reset links, callbacks, cache keys, or the client address used for authorization. Check whether trusted ingress strips client copies.

**Response-header injection** — untrusted data reaches `Location`, `Set-Cookie`, CSP, or another header with control characters. Verify framework rejection first; require a security-relevant change.

### Browser sessions

**Ordinary CSRF** — a cookie-authenticated mutation accepts a cross-site request without an effective token, same-site binding, or strict Origin/Referer check. Inventory form, JSON-like, multipart, method-override, and legacy routes; SameSite protects only the cookie and contexts actually used.

**Session fixation and invalidation** — session identifiers not rotated on login, account switch, MFA completion, or impersonation, or still valid after logout, password change, revocation, or disable. Include refresh tokens, signed cookies, websocket state, and caches.

**Cookie scope and transport** — a sensitive cookie with over-broad `Domain`/`Path`, sent over insecure transport, or shadowed by a sibling cookie another component prefers. Missing flags alone are hardening unless a less-trusted origin or network position can gain or replace the credential.

### Federated identity

Establish role first: authorization-server controls (redirect allowlists, code issuance) do not belong to a relying party; verification defects belong to whoever consumes the artifact.

**JWT verification and claim binding** — signature verified with a server-pinned algorithm and key source, then `exp`, `nbf`, `aud`, `iss`. Treat `kid`, `jku`, `x5u` as untrusted selectors; find decode-without-verify paths. A valid token for another service is invalid here.

**OAuth/OIDC request and callback binding** — exact `redirect_uri` (when this is the authorization server), session-bound `state`, PKCE and code binding, ID-token issuer/audience/signature/nonce, selected-IdP binding in multi-provider flows; compare retry, mobile, and account-link callbacks.

**SAML signed-object and assertion binding** — the signed element must be the element used as identity. Check unsigned fallbacks, XML parser safety, canonicalization differences, validity window, audience/recipient, request correlation, and replay state.

### MFA, passkeys, and account transitions

**MFA enrollment and assurance downgrade** — enrolling, replacing, or disabling a factor, generating recovery codes, or trusting a device without the policy-required fresh assurance; stale factors that still authorize.

**Step-up binding and bypass** — a challenge upgrades the wrong session, account, tenant, or action, or an alternate route skips it. Bind to principal, session, target assurance, operation, expiry, and single use.

**WebAuthn and passkey verification** — registration binds challenge, RP ID, origin, credential, user handle, algorithm, and required user verification to the initiating session; authentication verifies challenge, RP/origin, credential membership, and signature. Watch user-handle and credential-to-account confusion.

**Account linking and identity collision** — linking an IdP, passkey, email, phone, or device requires a current session, verified ownership of the new identifier, required step-up, and callback state bound to the initiating account. Check unlink/relink and invite acceptance.

**Password reset and broader recovery** — token randomness, user and action binding, expiry, single use, rate accounting, trusted delivery URL, and invalidation of earlier tokens and sessions; support/admin recovery and contact-change flows. Revealing public account existence is not automatically a finding.

### Service credentials

**API-key scope and resource binding** — a key reaches tenants, resources, actions, or environments beyond its server-side record, or request parameters override those bindings. Check prefix versus full-secret verification, publishable/secret type confusion, rotation, and revocation caches.

**API-key exposure and unsafe transport** — keys in client bundles, URLs, redirects, logs, errors, build artifacts, or responses a lower-trust principal can read. A public identifier named "key" is not a secret.

**mTLS peer and application-identity confusion** — identity headers trusted from any peer, attacker-influenced subject text mapped to the wrong account, or certificates accepted for the wrong trust domain or usage. With a terminating proxy: only the proxy can connect, it strips incoming identity headers, and the backend binds the sanitized identity.

**Certificate lifecycle fallback** — expired, revoked, or missing certificates fall back to bearer-only or anonymous mode, or pooled connections outlive revocation. An in-repo fail-open branch is source-confirmable; deployment revocation data is not.

### Web and identity validation

1. Apply the source-visibility gate: proxy chains, edge keys, IdP policy, certificate trust, cookie behavior, secrets, and deployed auth modes outside the repo make the candidate `needs_validation`.
2. Framing and cache: name both components and the divergent parse or key; show cross-request, cross-user, or private-response impact with local fixtures fed to each component, not live traffic.
3. Tokens, MFA, passkeys, linking, recovery, API keys, mTLS: cite the verification line and the missing binding, and show the server accepts the invalid credential or transition.
4. CSRF: name the ambient credential, the state-changing route, the accepted cross-site request shape, the cookie policy, and the missing check. Read-only routes and non-ambient bearer tokens do not qualify.
5. Verify framework and library defaults for the pinned version; unknown version or configuration means `needs_validation`, not a downgraded confirmed finding.

## Part B — browser and client

### Browser discipline

```text
- A client-side candidate needs a controllable source and an executing or disclosing
  sink, with attacker data shown reaching the sink.
- Impact must reach a victim's session, another origin, or shared persistence.
  Self-injection and disclosure of the attacker's own data are not findings.
- Framework escaping, same-origin policy, CSP, COOP/CORP, service-worker scope, and
  default noopener are real controls; verify them before assigning impact.
- Browser storage and caches are per-origin and can outlive login. Identify who
  writes, who reads, and which account, tenant, or worker lifecycle clears each entry.
- Work backward from DOM, navigation, worker, message, and storage sinks. Test account
  switch, logout, worker update, offline fallback, and stale tabs with a local origin
  and dummy accounts only.
```

### DOM and object state

**DOM-based XSS** — `location`, `document.referrer`, `window.name`, message data, or storage reaching `innerHTML`, `outerHTML`, `document.write`, string-evaluating APIs, executable URLs, jQuery HTML APIs, or framework escape hatches. Escaped interpolation is not a finding.

**DOM clobbering** — injected `id`/`name` attributes shadow a global, form property, config object, or flag that code trusts. Needs both surviving markup and a security-relevant use.

**Prototype pollution and gadget chain** — an attacker key reaches a recursive write (deep merge, path assignment) and a reachable gadget consumes the polluted property to change authorization, execution, navigation, or rendering. Pollution without a gadget is not enough.

### Cross-origin messaging and network

**postMessage origin and source trust** — a handler acts on `event.data` without an exact origin allowlist (and `event.source` where frames share an origin), or sensitive data is posted to `*`. Substring, prefix, or unanchored-regex matching is not an origin check.

**Cross-site WebSocket use** — an upgrade accepts ambient cookies from any origin without an Origin check or channel token, and a handler reads or mutates victim data.

**Credentialed CORS trust** — reflected or weakly matched `Origin` with credentials allowed on a sensitive response. A bare wildcard with credentials is blocked by browsers; report the actual reflected path.

### Workers and storage

**Service-worker registration and scope takeover** — attacker-influenced content becomes the worker script, gains an over-broad `Service-Worker-Allowed` scope, or alters imported scripts without integrity. Verify script URL, MIME type, origin, scope, and import control.

**Service-worker cache and identity confusion** — personalized responses cached without account, tenant, or auth state in the policy and served after account switch or logout, including offline and error fallbacks.

**Browser-storage disclosure and stale authorization** — tokens, private responses, or authorization decisions left in web storage, IndexedDB, Cache Storage, or extension storage and readable by another account or a less-trusted same-origin component, or still used after logout or revocation. Storage alone is not a finding.

**Cross-context storage and broadcast confusion** — `storage` events, `BroadcastChannel`, shared workers, or origin-wide caches carry identity or commands between tabs without session binding.

### Leaks, framing, and navigation

**XS-Leaks and cross-origin state oracles** — an attacker page distinguishes protected state through load/error events, frame counts, redirects, timing, cache state, or size while victim credentials attach. Needs a concrete secret-bearing predicate.

**Window and opener state disclosure** — permitted cross-origin window metadata or a retained opener reveals protected state or steers a privileged navigation. Check COOP, frame protections, and `noopener`.

**Clickjacking** — a state-changing action completes inside a frame because `frame-ancestors`/`X-Frame-Options` or equivalent is missing. Missing headers on read-only pages are hardening.

**Client-side navigation confusion** — a client source controls navigation without scheme and destination policy (`javascript:`, `data:`). Reverse tabnabbing only where code keeps `window.opener` or a supported browser lacks implicit noopener.

### Browser validation

1. Cite source, sink, browser policy, affected origin or session, and the observable mutation or disclosure.
2. Prototype pollution: prove the recursive write and a security-relevant gadget. DOM clobbering: prove the markup survives and the shadowed value is used.
3. Workers and storage: prove an attacker-controlled write or cache entry reaches a different account, tenant, or later authorization state.
4. Messaging, CORS, WebSocket, XS-Leaks: show the exact origin/source validation and the exposed state or action, and that CSP, COOP/CORP, cookies, and SameSite do not already block it.
5. Deployed headers, extension permissions, browser version, or renderer behavior that cannot be observed locally make the candidate `needs_validation`.
