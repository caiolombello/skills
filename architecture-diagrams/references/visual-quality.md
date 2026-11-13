# Visual quality system

Apply these rules at the final delivery size. A diagram that only works while
zoomed deeply in is not finished.

## Contents

1. Composition and hierarchy
2. Boundaries, nodes, and connectors
3. Color and accessibility
4. Metadata, legend, and quality gates

## Composition

- Choose canvas shape from the destination: wide for slides/screens, portrait
  for documents, scalable SVG for repositories and web.
- Establish one primary reading direction. Put the entry point where that
  reading naturally begins.
- Use progressive disclosure instead of shrinking labels to fit.
- Group by real semantics: ownership, trust, deployment, phase, or domain.
  Never group merely to make a symmetrical grid.
- Keep whitespace around major boundaries and between unrelated flows.
- Align repeated peers to a grid; allow deliberate asymmetry when it expresses
  fan-out, convergence, hierarchy, or sequence.

## Hierarchy

Use, in order:

1. Position and enclosure.
2. Size and typography.
3. Shape and line treatment.
4. Color.
5. Icons.

Do not make color or icon recognition carry the meaning alone.

Use at most three useful text levels:

- Title and viewpoint.
- Boundary or section heading.
- Component and relation labels.

At final size, target at least 16 px for screen text or 10–12 pt for print.
Increase it for executive or projected views.

## Boundaries and nodes

- Draw broad boundaries before narrow ones and keep their nesting consistent.
- Use quiet fills or no fill for containers so boundaries do not compete with
  components.
- Give concrete services an official icon plus a text label.
- Give abstractions a neutral shape plus responsibility; do not assign a
  product logo to a conceptual capability.
- Keep icons at a consistent optical size and preserve their aspect ratio,
  official colors, and clear space.

## Connectors

- Prefer orthogonal routes for formal architecture and network views.
- Route around nodes and labels. Avoid edge crossings; where unavoidable, use
  line jumps or split the view.
- Put arrows on directed relations and label non-obvious direction.
- Label purpose first, then protocol/event if relevant: `Submit order · HTTPS`
  is clearer than `HTTPS`.
- Use separate arrows for materially different request/response or write/read
  paths.
- Define dashed, colored, or animated line meanings in a legend. Do not assume
  a universal convention for asynchronous or control traffic.

## Color and accessibility

- Use a restrained semantic palette with a neutral base and a few roles.
- Maintain readable text/background contrast; use
  [WCAG 2.2 contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
  as the baseline for screen delivery.
- Pair color with shape, label, border, or pattern.
- Test a grayscale export and a color-vision-deficiency simulation when color
  carries status.
- Avoid low-opacity text, thin pale arrows, textured backgrounds, gradients,
  and dark-mode-only contrast.
- Provide a textual description for relationships that cannot be expressed as
  alt text inside the chosen file format.

## Metadata and legend

Include what the audience needs:

- Title and viewpoint.
- System/workload and environment.
- Current, target, comparison, or historical state.
- Version, date, and source freshness.
- Author/owner when required.
- Legend for status, boundary, line, and abbreviation semantics.
- External source/asset attribution when terms require it.

Keep the legend compact and true. Delete unused entries.

## Quality gates

Review at fit-to-page and 100%:

- Semantic fidelity: names, relations, direction, boundaries, placement.
- Visual integrity: no clipping, overlap, broken icons, orphan lines, or
  invisible labels.
- Comprehension: clear entry point, hierarchy, reading path, and conclusion.
- Density: labels remain readable in the intended destination.
- Consistency: same concept uses the same shape, icon treatment, and line
  semantics.
- Accessibility: meaning survives grayscale and is described in text.
- Handoff: source remains editable; export is generated from that source.

For a formal diagram, ask a reviewer unfamiliar with the implementation to
state the diagram's question and main flow. If they cannot, simplify or split
the view.
