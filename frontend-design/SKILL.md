---
name: frontend-design
description: "Use when designing or reviewing user-facing web interfaces, flows, visual hierarchy, responsive behavior, design systems, or accessibility. Produce implementation-ready UI decisions; not production frontend code or disposable prototypes."
---

# Frontend Design

Turn product intent into an implementation-ready interface specification. Design the complete user experience—content, hierarchy, states, interaction, responsiveness, and accessibility—not only an attractive happy-path screen.

## When to use

- Design or redesign a page, flow, component family, dashboard, form, or navigation model.
- Review an existing interface for usability, consistency, accessibility, or responsive behavior.
- Define or extend a design system, component vocabulary, token set, or interaction pattern.
- Convert rough requirements, screenshots, or product intent into a frontend-ready specification.

## When not to use

- Implement an already-decided interface in production code; use [`frontend-development`](../frontend-development).
- Design AI-native model states, tool activity, generated artifacts, trust, or approval flows with this skill alone; pair it with [`ai-interface-design`](../ai-interface-design).
- Explore several disposable UI directions before deciding; use [`throwaway-prototype`](../throwaway-prototype).
- Design an API, event, webhook, or SDK contract; use [`api-and-interface-design`](../api-and-interface-design).
- Perform a generic final code review; use [`code-review`](../code-review).

## Design principles

1. **Start with the user task.** Visual style serves comprehension and action.
2. **Design every state.** Loading, empty, error, partial, stale, permission-denied, disabled, and success states are part of the product.
3. **Prefer the existing system.** Reuse established components, tokens, language, and interaction patterns before creating new ones.
4. **Make hierarchy intentional.** Each view needs a clear purpose, primary action, reading order, and escape path.
5. **Make accessibility structural.** Semantics, keyboard behavior, focus, contrast, zoom, motion, and understandable errors are design inputs.
6. **Protect user agency.** Do not hide costs, preselect consent, manufacture urgency, obstruct cancellation, or trade clarity for conversion.
7. **Separate evidence from assumptions.** Never present guessed user needs, analytics, or research as facts.

## Workflow

### 1. Inspect the real context

Read the project rules file (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, or equivalent) and inspect:

- Current routes, adjacent screens, and navigation.
- Existing component library, tokens, typography, icons, and content style.
- Representative production-like data, including long, empty, malformed, and permission-limited cases.
- Product requirements, user research, analytics, support evidence, and constraints actually supplied.
- Supported viewports, input modes, languages, themes, browsers, and assistive-technology expectations.

Do not invent a new visual language because the task did not mention the existing one.

### 2. Frame the design problem

Record:

- Primary user and job to be done.
- Entry point and expected completion.
- Primary action, secondary actions, and safe exit.
- Product outcome and observable success signal.
- Constraints, risks, known facts, and explicit assumptions.

If a missing product decision would materially change the flow, ask for it. Otherwise choose the smallest reversible assumption and label it.

### 3. Map structure and flow

Define the information architecture before styling:

- Page purpose and content priority.
- Navigation path, back behavior, deep links, and recovery paths.
- Data grouping, progressive disclosure, and comparison needs.
- Form sequence, validation timing, destructive actions, and confirmation behavior.
- First-time, returning, and limited-permission experiences where they differ.

Keep one primary purpose per view. Split a flow only when it reduces cognitive load or risk; do not create wizard steps for decorative progress.

### 4. Build the state matrix

Create a concrete matrix for every important surface:

| State | Trigger | What the user sees | Available action | Recovery or next step |
|---|---|---|---|---|
| Loading | Initial request | Stable skeleton or progress message | Cancel when useful | Content replaces it without a layout jump |
| Empty | Valid response, no items | Explanation in context | Create, import, or change filters | New content appears in place |
| Error | Request failed | Specific, non-secret error | Retry or correct input | Preserve valid user work |
| Permission | Action is not allowed | Clear limitation | Request access or return | Never imply that hiding UI is authorization |
| Success | Goal completed | Confirmation and result | Continue or undo when safe | Focus and navigation remain predictable |

Add domain-specific states rather than treating this table as exhaustive.

### 5. Define the visual and interaction system

Specify decisions as reusable rules:

- Type scale, emphasis, line length, density, spacing, and alignment.
- Color roles and state meaning; never rely on color alone.
- Component variants, composition, and when each variant applies.
- Focus, hover, active, selected, disabled, validation, and drag states.
- Motion purpose, duration category, interruption behavior, and reduced-motion alternative.
- Content rules for labels, helper text, errors, confirmations, dates, numbers, and truncation.

Use tokens already present. Propose a new token or component only when an existing primitive cannot express a recurring need.

### 6. Design responsive and inclusive behavior

Let content pressure determine breakpoints. For each relevant width and input mode, specify:

- What reflows, wraps, stacks, scrolls, collapses, or remains fixed.
- Reading order and keyboard focus order.
- Navigation changes and how hidden content remains discoverable.
- Table, chart, dialog, tooltip, and overflow behavior.
- Zoom, text enlargement, localization expansion, touch, pointer, and keyboard behavior.

Target the project’s declared accessibility policy. When none exists, design toward WCAG 2.2 Level AA and document that automated checks alone cannot establish conformance. Prefer native platform semantics; use WAI-ARIA Authoring Practices only when a custom widget is truly necessary.

### 7. Choose the right fidelity

- Use a flow diagram or annotated wireframe for structure and state questions.
- Use a high-fidelity mockup only after hierarchy and behavior are stable.
- Use [`throwaway-prototype`](../throwaway-prototype) when competing directions need hands-on comparison.
- Use image-generation tools for supporting artwork or visual exploration, not as evidence that interaction, accessibility, or responsive behavior works.

Avoid building a polished screen around unresolved information architecture.

### 8. Produce the handoff

Deliver an implementation-ready specification containing:

1. Problem, user, outcome, constraints, and assumptions.
2. User flow and information hierarchy.
3. Component inventory and reuse/new-component decisions.
4. State matrix and interaction details.
5. Responsive behavior by content pressure or viewport class.
6. Accessibility requirements and keyboard/focus behavior.
7. Content and data examples with edge cases.
8. Acceptance criteria and unresolved decisions.

Use [references/design-review.md](references/design-review.md) for the full review and handoff template.

## Review an existing design

Review in this order:

1. Task completion and information architecture.
2. Complete states and recovery.
3. Accessibility and input-method behavior.
4. Responsive resilience and realistic data.
5. Visual hierarchy and design-system consistency.
6. Polish.

Report findings with location, user impact, evidence, and a concrete recommendation. Distinguish defects from preferences.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Designing only the ideal screenshot | Real products spend time loading, empty, failing, and constrained |
| Replacing the design system for novelty | Creates inconsistency and implementation cost |
| Mobile as a scaled-down desktop | Ignores content priority and input differences |
| Accessibility as a final audit | Structural problems become expensive to fix |
| Vague handoff such as “make it modern” | Leaves critical decisions to accidental implementation |
| Unfounded conversion claims | Confuses opinion with evidence and encourages dark patterns |
| Pixel polish before flow validation | Optimizes the wrong solution |

## Interaction with other skills

- [`ai-interface-design`](../ai-interface-design) — extends this baseline for AI-native interaction, model states, trust, provenance, controls, and product-value evidence.
- [`frontend-development`](../frontend-development) — implements the approved design in the real stack and verifies behavior.
- [`throwaway-prototype`](../throwaway-prototype) — explores disposable alternatives when the design direction is uncertain.
- [`brainstorming`](../brainstorming) — clarifies an ambiguous product idea before interface design begins.
- [`performance-optimization`](../performance-optimization) — measures and improves runtime performance after a real bottleneck is identified.
- [`security-hardening`](../security-hardening) — owns application security controls; frontend design must still make secure behavior understandable.
- [`code-review`](../code-review) — performs the final implementation review rather than substituting visual preference for code evidence.

## Verification checklist

- [ ] The primary user task, outcome, and assumptions are explicit.
- [ ] Information hierarchy and primary action are unambiguous.
- [ ] Loading, empty, error, permission, partial, and success states are covered where relevant.
- [ ] Responsive behavior uses realistic content and more than one viewport/input mode.
- [ ] Keyboard, focus, semantics, contrast, zoom, motion, and errors have explicit requirements.
- [ ] Existing components and tokens are reused or deviations are justified.
- [ ] Destructive, privacy-sensitive, and consent interactions protect user agency.
- [ ] Acceptance criteria are specific enough for implementation and testing.
- [ ] Accessibility claims match the evidence; no automated scan is described as full conformance.
