# Frontend Verification Matrix

Load this reference when choosing proportional checks for a frontend change. Prefer project-defined commands and existing test infrastructure.

## Contents

- [Match risk to evidence](#match-risk-to-evidence)
- [Behavioral states](#behavioral-states)
- [Accessibility checks](#accessibility-checks)
- [Responsive and visual checks](#responsive-and-visual-checks)
- [Async and network checks](#async-and-network-checks)
- [Security and privacy checks](#security-and-privacy-checks)
- [Command evidence](#command-evidence)
- [Primary technical sources](#primary-technical-sources)

## Match risk to evidence

| Change | Minimum evidence | Add when risk is higher |
|---|---|---|
| Static content or style | Targeted render/story, lint, visual check | Responsive and zoom checks |
| Interactive component | Behavior test, keyboard check, states | Screen-reader and integration test |
| Form or mutation | Validation/error tests, duplicate-submit check | End-to-end test, slow/failure network checks |
| Routing or auth UI | Integration test, focus/navigation check | End-to-end permission matrix |
| Shared primitive or token | Consumer tests, visual regression, build | Cross-browser and broad story coverage |
| Performance-sensitive surface | Baseline measurement and post-change measurement | Field data or controlled lab profile |

## Behavioral states

Check relevant states with realistic data:

- Initial, deferred, and background loading.
- Empty, filtered-empty, and first-use.
- Validation, network, service, and unknown errors.
- Partial, stale, offline, retrying, and conflicting data.
- Unauthenticated, unauthorized, limited permission, and read-only.
- Disabled, duplicate submit, rate limit, and quota.
- Optimistic update, rollback, undo, and success.
- Long text, missing optional values, large collection, and localization expansion.

## Accessibility checks

### Automated

- Run the project’s configured accessibility rules in component or end-to-end tests.
- Treat violations as actionable regressions.
- Record tool, scope, route/component, state, and result.

### Manual

- Navigate using keyboard only; verify visible focus and logical order.
- Open and close overlays; verify focus entry, containment when required, and restoration.
- Trigger validation and errors; verify focus and understandable messages.
- Zoom and enlarge text; verify reflow without loss of content or action.
- Enable reduced motion and inspect meaningful alternatives.
- Inspect accessible names, roles, states, relationships, and announcements.
- Use a supported screen reader for critical journeys when practical.

Automated success is not accessibility conformance.

## Responsive and visual checks

Observe the interface with:

- Narrow and wide widths chosen from content pressure or project breakpoints.
- Long labels, validation messages, large numbers, and missing values.
- Empty, loading, error, permission, and success states.
- Browser zoom and text enlargement.
- Touch-sized interaction, pointer hover, and keyboard focus.
- Tables, charts, menus, dialogs, sticky elements, and virtual-keyboard pressure.

Capture screenshots or visual-regression artifacts for changed states when the project supports them. Compare behavior and hierarchy, not only pixel similarity.

## Async and network checks

- Slow response: progress remains understandable and layout stays stable.
- Failure: valid user input survives and retry is safe.
- Reordered responses: stale data does not overwrite newer state or manual edits.
- Duplicate action: submission is prevented or idempotently handled.
- Cancellation/navigation: abandoned work does not update an unrelated screen.
- Partial response: usable data and limitations are both clear.

## Security and privacy checks

- Unauthorized calls fail on the trusted boundary even if UI controls are manipulated.
- Sensitive values do not appear in HTML, client logs, URLs, analytics, or error messages.
- Untrusted content renders in the correct context without executable injection.
- External links, redirects, uploads, downloads, and rich content follow project policy.
- Destructive and consent actions communicate scope and consequence.

## Command evidence

Use commands declared by the project rather than assuming a package manager:

```markdown
Verified:
- `<targeted test command>`: pass; covers retry and duplicate submit
- `<typecheck command>`: pass
- `<lint command>`: pass
- `<build command>`: pass
- Manual: keyboard and focus checked on `<route>` in loading, error, and success states

Not verified:
- Screen reader: unavailable in this environment
- Cross-browser visual regression: CI-only
```

## Primary technical sources

- [W3C Web Content Accessibility Guidelines overview](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [WAI-ARIA Authoring Practices patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
- [web.dev Learn Responsive Design](https://web.dev/learn/design)
- [web.dev Web Vitals](https://web.dev/articles/vitals)
- [Testing Library documentation](https://testing-library.com/docs/)
- [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing)
- [Storybook accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing)

Verify current project requirements and official documentation before choosing framework-specific APIs or making conformance claims.
