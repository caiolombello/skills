# Frontend Design Review and Handoff

Load this reference when producing a formal design review or an implementation handoff.

## Contents

- [Review record](#review-record)
- [Evidence levels](#evidence-levels)
- [State coverage](#state-coverage)
- [Responsive review](#responsive-review)
- [Accessibility review](#accessibility-review)
- [Primary technical sources](#primary-technical-sources)

## Review record

```markdown
# <Surface or flow>

## Context
- User and job:
- Entry point:
- Completion:
- Product outcome:
- Existing design-system primitives:
- Constraints:
- Evidence:
- Assumptions:

## Flow
1. ...

## Hierarchy
- Primary information:
- Primary action:
- Secondary actions:
- Safe exit or recovery:

## Components
| Need | Existing primitive | Variant or composition | New primitive justified? |
|---|---|---|---|

## States
| Surface | State | Trigger | Content | Action | Focus or announcement | Recovery |
|---|---|---|---|---|---|---|

## Responsive behavior
| Content pressure or viewport | Layout | Navigation | Overflow | Hidden or reordered content |
|---|---|---|---|---|

## Accessibility
- Semantic structure:
- Accessible names and descriptions:
- Keyboard order and shortcuts:
- Focus entry, restoration, and error focus:
- Contrast and non-color cues:
- Zoom, reflow, and text enlargement:
- Motion and reduced-motion behavior:
- Status and error announcements:

## Acceptance criteria
- [ ] ...

## Open decisions
- ...
```

## Evidence levels

Label each finding:

- **Observed:** directly reproduced in the running interface or supplied artifact.
- **Specified:** required by an accepted product, design-system, or accessibility policy.
- **Inferred:** a recommendation based on the current context; validate before treating it as a requirement.
- **Preference:** aesthetic option with no demonstrated usability or policy impact.

Do not promote preference to defect. Do not present inferred analytics, research, or user behavior as observed.

## State coverage

Check only states relevant to the surface, but look deliberately for:

- Initial, deferred, and background loading.
- No data, no search results, and filtered-empty.
- Validation, network, service, and unknown errors.
- Partial data, stale data, offline, and retry.
- Unauthenticated, unauthorized, and limited permission.
- Disabled, read-only, rate-limited, and quota-limited.
- Optimistic update, conflict, undo, success, and destructive completion.
- First use, returning use, localization expansion, and large datasets.

## Responsive review

Test content pressure, not device names alone:

- Narrow width with long labels and validation messages.
- Wide width with readable line lengths rather than stretched content.
- Browser zoom and enlarged text.
- Keyboard-only and touch/pointer interaction.
- Portrait and landscape when the product supports mobile use.
- Tables, charts, dialogs, menus, sticky regions, and virtual keyboards.

Record whether content reflows, wraps, scrolls, collapses, or becomes a different component. Preserve reading and focus order.

## Accessibility review

Use native HTML behavior as the baseline. For custom widgets, compare expected keyboard and semantic behavior with the relevant WAI-ARIA Authoring Practices pattern.

Review:

- Headings, landmarks, labels, names, descriptions, and relationships.
- Keyboard reachability, visible focus, logical order, and focus restoration.
- Error identification, instructions, status announcements, and time limits.
- Contrast, non-color cues, text resizing, reflow, target usability, and motion.
- Captions, transcripts, text alternatives, and data-visualization alternatives.

State the evidence accurately:

- Automated checks find only a subset of accessibility issues.
- Manual keyboard, zoom, screen-reader, and cognitive walkthroughs remain necessary.
- A design review or automated scan is not a conformance certification.

## Primary technical sources

- [W3C Web Content Accessibility Guidelines overview](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [W3C WCAG supporting documents](https://www.w3.org/WAI/standards-guidelines/wcag/docs/)
- [WAI-ARIA Authoring Practices patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
- [WAI-ARIA Authoring Practices introduction and scope](https://www.w3.org/WAI/ARIA/apg/about/introduction/)
- [web.dev Learn Responsive Design](https://web.dev/learn/design)

Verify the project’s required standard and the current official guidance before making compliance claims.
