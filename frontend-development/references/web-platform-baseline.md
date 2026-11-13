# Web Platform Baseline

Load this reference before hand-writing or adding a dependency for a UI primitive,
overlay, layout, animation, form behavior, or client-side utility that the browser
may already provide. Models often reproduce older patterns from training data; the
platform frequently has a smaller, faster, more accessible native answer.

## Contents

- [Browser-support policy](#browser-support-policy)
- [Native first, library second](#native-first-library-second)
- [Common legacy reflexes](#common-legacy-reflexes)
- [Fallbacks and feature detection](#fallbacks-and-feature-detection)
- [Frameworks and SSR](#frameworks-and-ssr)
- [Optional guide lookup](#optional-guide-lookup)
- [Primary sources](#primary-sources)

## Browser-support policy

Use the project's declared policy first: the rules file (`AGENTS.md`, `CLAUDE.md`,
`.cursor/rules/`), `browserslist`, build targets, or a documented support matrix.
Runtime constraints such as Electron, Tauri, kiosks, or embedded webviews override
public-web defaults.

When no policy exists, default to [Baseline](https://web.dev/baseline):

| Status | Meaning | Default use |
|---|---|---|
| **Widely available** | Supported across the core browser set for about 30 months after interoperability | Use without a fallback |
| **Newly available** | Recently interoperable across the core browser set | Use with feature detection or a graceful degradation path |
| **Limited** | Not yet supported in every core browser | Use only as progressive enhancement, or choose another approach |

Check the current status of the exact feature on the feature's MDN page or
[webstatus.dev](https://webstatus.dev); do not assert a Baseline year from memory.
For a `Baseline YYYY` target, a feature qualifies when its "Baseline since" year is
at or before `YYYY`.

If the user hesitates over a fallback's size, targets a restricted runtime, or asks
whether a feature is safe, propose recording a one-line policy in the project rules
file (for example: "Browser support: Baseline widely available; newly available
features only with feature detection and a fallback under ~20 lines, no polyfill
dependencies"). Writing the rules file still needs the user's request or approval.

## Native first, library second

Prefer the native capability when it meets the requirement and the support policy;
reach for an accessible headless library when the platform does not cover the
behavior (for example a full combobox with async search, a complex date-range
picker, or a virtualized data grid).

| Need | Start with |
|---|---|
| Modal or non-modal dialog | `<dialog>` with `showModal()`/`show()` (or declarative invoker commands where supported); the native modal supplies inert background, focus containment, top layer, `::backdrop`, Escape, and focus return |
| Menus, toasts, tooltips, pickers | The `popover` attribute, with anchor positioning where supported |
| Disclosure and accordion | `<details>`/`<summary>`, optionally the `name` attribute for exclusive groups |
| Form validation | Constraint validation (`required`, `pattern`, `type`, `setCustomValidity`) plus accessible error text; `:user-invalid` for styling after interaction |
| Autofill | Correct `autocomplete` tokens and input types rather than custom scripts |
| Component-responsive layout | Container queries instead of viewport breakpoints for component internals |
| Parent-dependent styling | `:has()` instead of class toggling from script |
| Entry/exit and state animations | CSS transitions with `@starting-style`, `transition-behavior: allow-discrete`, and View Transitions for state or page changes |
| Scroll-linked effects | Scroll-driven animations instead of scroll listeners |
| Offscreen rendering cost | `content-visibility` with `contain-intrinsic-size` |
| Loading priority | `fetchpriority`, `loading="lazy"` on below-the-fold images, and correct `width`/`height` |
| Dates, numbers, relative time | `Intl` APIs; `Temporal` only where supported or polyfilled by policy |
| Untrusted HTML | Avoid HTML injection; when unavoidable, a vetted sanitizer and the platform sanitizer API where available |
| Passwordless sign-in | WebAuthn passkeys through the project's auth provider |

The native element is still a decision about behavior: verify keyboard, focus,
screen-reader names, and dismissal on the rendered result.

## Common legacy reflexes

| Reflex | Prefer |
|---|---|
| `div` overlay with `role="dialog"`, a manual focus trap, and an Escape handler | Native `<dialog>`; do not add `role="dialog"` or `aria-modal` to a native modal |
| Scroll lock by `overflow: hidden` or `position: fixed` on `html`/`body` | `overscroll-behavior: contain` on the modal and its backdrop handling, verified on touch devices |
| JavaScript positioning library for a simple anchored popup | `popover` plus anchor positioning, with a simple fallback placement |
| `IntersectionObserver` or scroll handlers for reveal/parallax | Scroll-driven animations, with a reduced-motion path |
| Date libraries for formatting only | `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat` |
| `transition: all` or animating `top`/`left`/`width`/`height` | Named `transform`/`opacity` transitions |
| `100vw` for full-bleed sections | Percent or container-relative widths; `100vw` includes the scrollbar and causes horizontal overflow |
| Heavy polyfill for a newly available feature | Feature detection plus a small fallback or a simpler design |

## Fallbacks and feature detection

- Detect features, not browsers: `@supports`, `CSS.supports()`, `'showPopover' in HTMLElement.prototype`, and similar checks.
- A fallback keeps the task possible; it does not need to replicate polish.
- Keep an existing library as the fallback when a guide or the policy requires it, rather than deleting working behavior.
- Do not add a polyfill dependency without the user's or project's acceptance of its size and maintenance.
- Content must remain readable and actions operable when an enhancement or script is unavailable, where the product's architecture permits.

## Frameworks and SSR

Vanilla platform guidance still applies inside frameworks:

- Pass newly shipped attributes through the framework (spread, attribute binding) instead of dropping them when types lag; prefer an updated type package or a narrow typed wrapper over broad `any`.
- Call imperative APIs (`showModal()`, `showPopover()`) through refs on nodes the framework does not re-render away.
- Guard `window`, `document`, and `HTMLElement` access during server rendering; load client-only fallbacks in client effects.
- Generate per-instance IDs (`useId()` or equivalent) for `commandfor`, `aria-*` relationships, and `anchor-name` values.
- Keep `:root`, `@property`, and `@starting-style` rules where the styling system does not scope them away.

## Optional guide lookup

[Modern Web Guidance](https://developer.chrome.com/docs/modern-web-guidance)
(GoogleChrome, Apache-2.0, stewarded with Edge, Firefox, and MDN contributors)
publishes searchable, eval-calibrated guides for these patterns. Use it when it is
available and network use is acceptable; it is a source, not a mandatory first step.

- Pin the CLI version instead of `@latest`; reviewed version 1.0.0 on 2026-11-13. Running `npx` downloads and executes package code, so treat a version bump like any dependency update.
- `npx -y modern-web-guidance@1.0.0 search "<2-5 word capability>"`, then `retrieve "<id>"`. Search one capability per query, without framework or product names.
- `legacy-scan <path> --json` covers only a deterministic subset of patterns; use it only for an explicit broad modernization or audit request, and verify each finding before editing.
- Cross-check retrieved guidance against the project's support policy and installed framework versions. Report which guides shaped non-obvious choices when that helps the reviewer.
- When the network or approval is unavailable, use MDN and web.dev directly through [`docs-verified-coding`](../../docs-verified-coding).

## Primary sources

- [Baseline](https://web.dev/baseline) and [Web Platform Status](https://webstatus.dev)
- [MDN Web Docs](https://developer.mozilla.org/)
- [HTML Living Standard](https://html.spec.whatwg.org/)
- [Modern Web Guidance source](https://github.com/GoogleChrome/modern-web-guidance-src) — reviewed at `9e3f3f65c8a6aac2b1029869ee8a05d4cd461f73`; no guide text is vendored here.
