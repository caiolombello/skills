---
name: security-hardening
description: Use when building or changing app code that handles user input, authn/authz, sessions, PII, uploads, redirects, dynamic SQL, or rendering untrusted data. OWASP app-layer, not container/IaC secrets.
---
<!-- Inspired by addyosmani/agent-skills security-and-hardening (MIT). See ../CREDITS.md -->

# Security Hardening

Application-layer security. Every external input is hostile. Every secret is sacred. Every authorization check is mandatory. Security is a constraint on every line that touches user data, authentication, or external systems — not a phase at the end.

This skill covers the app layer. Adjacent skills:
- [`container-image-hardening`](../container-image-hardening) — image supply chain, non-root users, SBOM, signing.
- [`pass-cli-secrets`](../pass-cli-secrets) — where secrets live and how to pipe them without leaking.
- [`terraform-iac-expert`](../terraform-iac-expert) — IaC security posture.

## The three-tier rule

### Always do (no exceptions)

- **Validate every external input** at the system boundary — API routes, form handlers, message queues, webhooks.
- **Parameterize every database query.** Never concatenate user input into SQL or NoSQL queries.
- **Encode output for its sink** — HTML for browsers, URL for redirects, shell for subprocesses, SQL for queries. Use framework auto-escaping; do not bypass it.
- **Use HTTPS / TLS** for all external communication. Reject plain HTTP where practical.
- **Hash passwords** with `bcrypt`, `scrypt`, or `argon2`. Never store plaintext. Never roll your own.
- **Set security headers** — CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- **Use `httpOnly`, `secure`, `sameSite` cookies** for session tokens.
- **Check authorization on every request**, not just authentication. "Logged in" ≠ "allowed to access this record".
- **Scan dependencies** (`npm audit`, `pip-audit`, `cargo audit`, Trivy, Dependabot) before every release.
- **Keep audit logs** of sensitive actions — login attempts, privilege changes, data exports.

### Ask first (require human approval)

- Adding or changing authentication flows or auth providers.
- Storing a new category of sensitive data (PII, payment, biometric, health).
- Adding a new external service integration that handles user data.
- Changing CORS configuration, especially wildcards.
- Adding file upload handlers.
- Changing rate-limit, throttling, or quota policies.
- Granting elevated permissions or admin roles.
- Adding redirects driven by user input.
- Parsing file formats that support external entities (XML, Office, PDF).

### Never do

- **Never commit secrets** — API keys, passwords, tokens, private keys, connection strings.
- **Never log sensitive data** — passwords, tokens, full card numbers, full SSNs, access tokens.
- **Never trust client-side validation** as a security boundary. UI validation is for UX; server validation is for safety.
- **Never disable security headers** "for convenience".
- **Never use `eval()`**, `Function(...)`, `exec`, or `innerHTML` with user-provided data.
- **Never store session tokens in `localStorage`** or other client-JS-accessible storage (XSS takes them).
- **Never expose stack traces** or internal error details to the outside world.
- **Never disable SSL verification** in production.
- **Never compare secrets with `==`** — timing attacks. Use constant-time compare.

## OWASP Top 10 — concrete patterns

### A01: Broken access control (IDOR, privilege escalation)

Every resource fetch must check ownership, not just authentication.

```ts
// BAD: any logged-in user can read any task by ID
app.get('/tasks/:id', requireAuth, async (req, res) => {
  const task = await db.tasks.findById(req.params.id);
  res.json(task);
});

// GOOD: enforce ownership
app.get('/tasks/:id', requireAuth, async (req, res) => {
  const task = await db.tasks.findOne({
    id: req.params.id,
    ownerId: req.user.id,      // ← authorization check
  });
  if (!task) return res.sendStatus(404); // 404, not 403 — do not leak existence
  res.json(task);
});
```

Rules:
- Check ownership at the data layer, not just in middleware.
- Return 404 (not 403) for unauthorized access to hide existence.
- For multi-tenant apps, scope **every** query by tenant.

### A02: Cryptographic failures

```ts
// Password hashing
import bcrypt from 'bcrypt';
const SALT_ROUNDS = 12;
const hashed = await bcrypt.hash(plaintext, SALT_ROUNDS);
const ok = await bcrypt.compare(plaintext, hashed);

// Symmetric encryption: authenticated cipher only
// AES-GCM or XChaCha20-Poly1305. Never ECB. Never CBC without HMAC.

// Constant-time comparison of secrets
import crypto from 'node:crypto';
const match = crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
```

Rules:
- Passwords: bcrypt / scrypt / argon2 only.
- Encryption: AEAD ciphers (AES-GCM, XChaCha20-Poly1305).
- Random: `crypto.randomBytes`, `secrets` (Python), `crypto/rand` (Go). Never `Math.random()` for security purposes.
- Secrets comparison: constant-time (`crypto.timingSafeEqual`, `hmac.compare_digest`).

### A03: Injection

SQL, NoSQL, OS command, LDAP — same pattern, different syntax.

```ts
// BAD
const query = `SELECT * FROM users WHERE id = '${userId}'`;
const cmd = `grep ${userInput} logs.txt`;

// GOOD
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
const user = await prisma.user.findUnique({ where: { id: userId } });
const proc = spawn('grep', [userInput, 'logs.txt']); // argv array, not shell
```

Rules:
- Parameterized queries only. ORMs that parameterize by default are fine.
- Subprocess calls: argv array, never `shell: true` with user input.
- MongoDB: validate operator keys; reject `$` and `.` in client-supplied object keys to prevent operator injection.

### A04: Insecure design

Threat-model features that handle money, identity, or privileged data **before** writing code. Write down:
- Who is trusted?
- What happens if each role is malicious?
- What is the blast radius if this component is compromised?

If you cannot answer these, escalate — do not ship.

### A05: Security misconfiguration

- Disable debug / verbose error pages in production.
- Remove default accounts, sample apps, directory listings.
- Set CSP that at minimum disables inline scripts without nonces/hashes.
- `X-Frame-Options: DENY` or CSP `frame-ancestors 'none'` unless embedding is required.
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- CORS: explicit allow-list of origins, not `*` when credentials are sent.

### A06: Vulnerable and outdated components

- Run `npm audit` / `pip-audit` / `cargo audit` / `go list -m -u all` in CI.
- Subscribe to security advisories for the frameworks you use.
- Pin versions in lockfiles; bump with intent, not with `latest`.
- Before adding a dependency: check maintenance status, download counts, CVE history, and whether the functionality is small enough to write yourself.

### A07: Identification and authentication failures

```ts
// Session cookie
res.cookie('session', token, {
  httpOnly: true,          // not accessible to JS
  secure: true,            // HTTPS only
  sameSite: 'lax',         // CSRF defense
  maxAge: 24 * 60 * 60 * 1000,
  path: '/',
});
```

- Lock out after N failed attempts (with exponential backoff, not permanent lockout).
- Require re-auth before sensitive actions (change password, change email).
- Rotate sessions on privilege changes (`req.session.regenerate()`).
- Never implement custom TOTP / OTP unless you must — use a library.
- MFA: TOTP or WebAuthn. SMS is weak but better than password only.

### A08: Software and data integrity failures

- Verify signatures on anything you download at build or deploy time.
- Use SRI (Subresource Integrity) for third-party scripts/styles loaded from CDNs.
- Sign container images (cosign) — see [`container-image-hardening`](../container-image-hardening).
- Do not deserialize untrusted data into constructed objects (`pickle.loads`, Java `ObjectInputStream`, PHP `unserialize`, Ruby `Marshal.load`). Use data-only formats — JSON, Protobuf with strict schemas.

### A09: Security logging and monitoring failures

Log sensitive actions (login, logout, privilege change, data export) with enough context to investigate — but **never** log the secret itself.

```ts
// BAD
logger.info({ user: user.email, password: req.body.password });

// GOOD
logger.info({
  event: 'login',
  userId: user.id,
  ip: req.ip,
  userAgent: req.get('user-agent'),
  // no password, no token, no session id
});
```

Redact tokens, card numbers, full emails (if email is sensitive in your jurisdiction), IPs if required by policy. Centralize logs, alert on anomalies, retain per policy.

### A10: Server-Side Request Forgery (SSRF)

When the server fetches a URL supplied by the user (image proxy, webhook, link preview):

- Allow-list the set of permitted hosts.
- Block private IPv4 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`) **and IPv6 equivalents** (`::1`, `fc00::/7`, `fe80::/10`).
- Block cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`).
- Resolve DNS **once**, validate the resolved IP, then connect by IP to prevent DNS rebinding.
- Disable redirects, or re-validate the redirect target.

## Input validation patterns

Use a schema validator (Zod, Yup, Joi, Pydantic, go-playground/validator, JSON Schema) at every boundary.

```ts
// Zod example
import { z } from 'zod';
const CreateUser = z.object({
  email: z.string().email().max(254),
  password: z.string().min(12).max(256),
  age: z.number().int().min(13).max(120),
});

const parsed = CreateUser.safeParse(req.body);
if (!parsed.success) return res.status(422).json({ errors: parsed.error.errors });
```

Rules:
- Whitelist allowed characters / shapes, do not blacklist "bad" ones.
- Enforce max lengths on strings, arrays, and nested depth.
- Normalize before validating (trim, lowercase emails, canonical URL forms).
- Reject unknown fields (Zod `.strict()`, Pydantic `model_config = {"extra": "forbid"}`).

## File upload rules

- Validate file type by **magic bytes**, not just extension or MIME type.
- Enforce size limits at the proxy and at the application.
- Store uploads outside the web root, or on a separate bucket.
- Generate a server-side filename; do not trust the client's name.
- Scan for malware where possible (ClamAV, cloud provider scanners).
- Serve user uploads from a different origin or subdomain so XSS cannot piggyback on the app's cookies.

## CSP cheat sheet

Minimum defensible CSP for a modern web app:

```
default-src 'self';
script-src 'self' 'nonce-<server-generated>';
style-src 'self';
img-src 'self' data: https:;
connect-src 'self' https://api.example.com;
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
upgrade-insecure-requests;
```

- Avoid `'unsafe-inline'` and `'unsafe-eval'`.
- Use nonces or hashes for required inline scripts.
- Start with `Content-Security-Policy-Report-Only` to tune without breaking.

## Dependency hygiene

Before adding a dependency:
- Is it actively maintained? Last release within a year?
- Download counts on the registry?
- CVE history?
- Can I write it myself in <50 lines? Prefer that.
- Does it pull in a large transitive tree?

In CI: `npm audit --audit-level=high` (or equivalent) fails the build on high/critical.

## Anti-patterns

| Anti-pattern | Why it is wrong |
|--------------|-----------------|
| Validate only on the client | Attacker skips the client entirely |
| "We authenticate, therefore safe" | Authn ≠ authz. Check ownership per request. |
| Catch + swallow errors with `try {} catch {}` | Hides real failures, may leak internal state elsewhere |
| Return 403 for unauthorized access to a resource | Reveals existence. Use 404. |
| Log the full request body | Tokens and passwords end up in logs |
| Trust a JWT without verifying signature and `exp` | `alg: none` attack, replayed token |
| Compare API key with `==` | Timing side channel leaks the key |
| Use `Math.random()` for session IDs | Predictable. Use `crypto.randomBytes`. |
| "We'll add rate limiting later" | Brute force takes seconds |
| Accept `..` in a user-supplied path | Path traversal |
| CORS `*` with credentials | Any origin can steal authenticated responses |

## Interaction with other skills

- [`code-review`](../code-review) — security is one of the five review axes. Use this skill as the detailed checklist.
- [`pass-cli-secrets`](../pass-cli-secrets) — where secrets come from and how to pipe them without leaking into agent context.
- [`container-image-hardening`](../container-image-hardening) — image layer. Pair with this skill for full-stack hardening.
- [`docs-verified-coding`](../docs-verified-coding) — verify security APIs against official docs (OWASP cheat sheets, framework security docs).
- [`doubt-driven-review`](../doubt-driven-review) — escalate non-trivial auth / crypto decisions to fresh-context review.
- [`terraform-iac-expert`](../terraform-iac-expert) — IaC security (IAM, network, encryption at rest).

## Verification checklist

Before shipping any feature touching user data, auth, or external services:

- [ ] Every input is validated against a schema at the boundary.
- [ ] Every database query is parameterized.
- [ ] Every resource fetch checks ownership, not just authentication.
- [ ] Every response that reveals existence uses 404, not 403, for unauthorized access.
- [ ] Secrets are loaded from env vars / secret store — none are in the diff.
- [ ] Passwords are hashed with bcrypt/scrypt/argon2; compared with constant-time functions.
- [ ] Session cookies have `httpOnly`, `secure`, `sameSite`.
- [ ] CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy are set.
- [ ] Logs do not contain passwords, tokens, or other sensitive data.
- [ ] Dependency audit passes; no known high/critical CVEs.
- [ ] Security-sensitive changes have been through `doubt-driven-review`.
- [ ] External URL fetches (if any) enforce the SSRF rules above.
- [ ] File uploads are validated by magic bytes, size-capped, and served from an isolated origin.
