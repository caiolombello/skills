---
name: frontend-development
description: "Use before implementing, changing, or fixing authorized production web UI code from approved requirements or designs in an existing frontend stack: components, routes, forms, interactions, state, or client data flow. For disposable UI experiments, use throwaway-prototype instead. Not unresolved product or visual direction, diagnosis-only work, or final PR review."
---

# Frontend Development

Implement production frontend behavior in the project’s existing stack without inventing framework APIs, visual conventions, or backend contracts. Treat accessibility, states, responsiveness, security, and verification as part of the feature.

## When to use

- Build or change a production page, route, component, form, interaction, or client-side data flow.
- Convert an approved design, wireframe, or acceptance criteria into frontend code.
- Repair frontend behavior when the requested outcome includes implementation.
- Add frontend tests for user-visible behavior.

## When not to use

- Decide the product flow, visual direction, information architecture, or design system; use [`frontend-design`](../frontend-design).
- Build disposable alternatives to answer an unresolved design question; use [`throwaway-prototype`](../throwaway-prototype).
- Diagnose a failure without authorization to implement the fix; use [`diagnose`](../diagnose).
- Perform a generic PR or completed-change review; use [`code-review`](../code-review).

## Non-negotiables

1. **Inspect before editing.** Learn the exact framework, version, routing, state, styling, test, and build conventions.
2. **Use the existing design system.** Compose established primitives and tokens before adding variants, abstractions, or dependencies.
3. **Implement complete behavior.** Loading, empty, error, partial, permission, disabled, and success states are not optional cleanup.
4. **Use semantic native controls first.** A styled `button` is safer than recreating button behavior on a `div`.
5. **Preserve user work.** Late async responses, refreshes, validation, and retries must not silently overwrite manual input.
6. **Do not invent contracts.** Read generated clients, schemas, API types, fixtures, and actual call sites.
7. **Verify with observable evidence.** Compilation alone does not prove interaction, layout, or accessibility.

## Workflow

### 1. Establish the project contract

Read the project rules file (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, or equivalent), then inspect:

- Package and lock files for exact framework and dependency versions.
- App structure, routing, rendering model, and server/client boundaries.
- Existing components, tokens, themes, icons, and styling conventions.
- State management, forms, validation, API clients, schemas, and error shapes.
- Nearby implementations of the same interaction.
- Project-defined lint, typecheck, test, build, story, and end-to-end commands.

Use [`investigate-before-editing`](../investigate-before-editing) for unfamiliar code. Use [`docs-verified-coding`](../docs-verified-coding) before relying on version-sensitive framework or library behavior.

### 2. Resolve the implementation input

Translate the design or request into:

- User-visible acceptance criteria.
- Component and route boundaries.
- State and data ownership.
- Data contract and failure behavior.
- Responsive and accessibility requirements.
- Test and visual-verification plan.

If product direction is unresolved, pause implementation and route the decision to [`frontend-design`](../frontend-design). If only minor unspecified detail remains, follow the existing product pattern and state the assumption.

### 3. Implement a thin vertical slice

Build the smallest complete path through real boundaries:

1. Render with realistic fixture or contract-compatible data.
2. Implement the primary user action.
3. Connect the existing data/client layer.
4. Cover the state and failure behavior.
5. Add the narrowest meaningful behavior test.
6. Verify in the actual application.

Expand after the slice works. Do not start by creating a generic component framework for hypothetical reuse.

### 4. Model state explicitly

Prefer states that make impossible combinations unrepresentable. For example:

```ts
type ViewState<T> =
  | { status: "loading" }
  | { status: "ready"; data: T; stale?: boolean }
  | { status: "empty" }
  | { status: "error"; message: string; retryable: boolean };
```

Adapt this shape to the project rather than introducing it mechanically. Define behavior for:

- Initial and background loading.
- Empty and filtered-empty results.
- Validation, network, permission, and unknown errors.
- Partial, stale, offline, optimistic, conflicting, and successful updates.
- Disabled, read-only, rate-limited, and destructive actions.

For asynchronous work:

- Ignore or cancel stale requests where appropriate.
- Prevent duplicate submissions and unsafe races.
- Keep editable prefills distinct from authoritative user edits.
- Preserve valid form values when requests fail.
- Make retry and undo behavior explicit.

### 5. Build semantics and accessibility into the component

- Use native elements, landmarks, headings, labels, and form relationships.
- Keep keyboard behavior and focus order aligned with visual and reading order.
- Move and restore focus deliberately for dialogs, route changes, errors, and removed content.
- Expose names, descriptions, validation, status, and error messages to assistive technology.
- Do not communicate state with color, position, hover, or animation alone.
- Support zoom, text enlargement, reduced motion, and content reflow.
- Follow the relevant WAI-ARIA Authoring Practices pattern only for a necessary custom widget.

Target the project’s accessibility policy. If none exists, use WCAG 2.2 Level AA as the design and test baseline without claiming conformance from automated tools alone.

### 6. Preserve security and privacy boundaries

- Treat frontend validation as usability; enforce authorization and invariants on the trusted backend.
- Never expose secrets, privileged data, internal error details, or unsafe debug state to the client.
- Encode or sanitize untrusted content according to its rendering context.
- Make destructive, payment, privacy, consent, and permission actions explicit and reviewable.
- Avoid unsafe URL, redirect, file-upload, and rich-content behavior.

Use [`security-hardening`](../security-hardening) when the change handles authentication, authorization, sessions, PII, uploads, redirects, dynamic content, or other untrusted input.

### 7. Make layout resilient

- Use content-driven responsive behavior and existing breakpoints.
- Test long labels, localization expansion, empty values, large collections, and validation text.
- Prevent accidental layout shift by reserving stable space where practical.
- Size and load media intentionally; avoid shipping unnecessary assets or JavaScript.
- Preserve useful reading width on large screens and usable interaction on narrow screens.

Measure before making performance claims. Route profiling and budgets to [`performance-optimization`](../performance-optimization).

### 8. Test behavior at the right layers

Prefer user-observable assertions:

- Query by role, accessible name, label, or visible content.
- Test state transitions, keyboard paths, validation, failures, retries, and permission behavior.
- Use component tests for local behavior, integration tests for boundaries, and end-to-end tests for critical journeys.
- Mock at stable boundaries, not internal implementation details.
- Avoid snapshot-only coverage for interactive behavior.

Automated accessibility checks are useful regression guards, not proof of complete accessibility. Use [references/verification-matrix.md](references/verification-matrix.md) to select proportional checks.

### 9. Verify in the real application

Run project-defined commands and record exact outcomes:

- Targeted behavior tests.
- Typecheck and lint.
- Production build when the build path changed.
- Relevant integration or end-to-end tests.
- Visual checks at representative widths and states.
- Keyboard, focus, zoom, and automated accessibility checks.
- Slow, failed, stale, and duplicate-request behavior where relevant.
- Console and network inspection for unexpected errors or sensitive data.

Do not say “responsive,” “accessible,” or “all tests pass” unless the evidence supports that exact scope.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Inventing a component API from memory | Version and project conventions differ |
| Adding a new UI library for one component | Expands bundle, maintenance, and visual inconsistency |
| Testing implementation details | Refactors break tests without changing behavior |
| Happy-path-only UI | Failure and permission states reach users anyway |
| Hiding unauthorized actions as the only control | The client is not a trust boundary |
| Replacing user input with a late response | Destroys user work and creates race-dependent behavior |
| Declaring accessibility from one scanner | Automated tools detect only part of the problem |
| Large generic abstraction before one working path | Encodes guesses and makes review harder |

## Interaction with other skills

- [`frontend-design`](../frontend-design) — owns product flow, hierarchy, design-system decisions, and implementation-ready UX specifications.
- [`throwaway-prototype`](../throwaway-prototype) — explores disposable variants; never promote prototype code directly.
- [`investigate-before-editing`](../investigate-before-editing) — establishes repository conventions before production edits.
- [`docs-verified-coding`](../docs-verified-coding) — verifies framework and library APIs against the exact installed version.
- [`incremental-implementation`](../incremental-implementation) — expands the feature in verified vertical slices.
- [`test-driven-development`](../test-driven-development) — owns red-green-refactor discipline when behavior is testable first.
- [`security-hardening`](../security-hardening) — owns application-layer threat controls.
- [`performance-optimization`](../performance-optimization) — owns measurement-led performance work.
- [`code-review`](../code-review) — reviews the finished change across correctness, architecture, security, and maintainability.

## Verification checklist

- [ ] The exact stack, versions, project rules, and nearby patterns were inspected.
- [ ] Existing components, tokens, contracts, and commands were reused.
- [ ] Acceptance criteria and state ownership are explicit.
- [ ] Relevant loading, empty, error, partial, permission, disabled, and success states work.
- [ ] Async behavior preserves user edits and handles stale or duplicate work.
- [ ] Semantic structure, keyboard behavior, focus, names, errors, zoom, reflow, and motion were checked.
- [ ] Responsive behavior was observed with realistic and adversarial content.
- [ ] Security and privacy are enforced at trusted boundaries, not only in UI visibility.
- [ ] Targeted tests, typecheck, lint, build, and runtime checks were run as applicable.
- [ ] Verification evidence and untested gaps are reported precisely.
