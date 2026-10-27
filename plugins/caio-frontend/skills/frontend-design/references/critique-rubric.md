# Critique Rubric

Load for every render–critique–fix round and for Review mode. The rubric turns "looks good" into scored, evidenced judgments. Score what the screenshots show, not what the code intends.

## Contents

- [Protocol](#protocol)
- [Quick tests](#quick-tests)
- [Composition and comparison checks](#composition-and-comparison-checks)
- [Dimensions and anchors](#dimensions-and-anchors)
- [Round output](#round-output)
- [Fix order](#fix-order)

## Protocol

1. **Collect evidence.** Run `visual_qa.mjs` (or use supplied screenshots). Open the first-viewport screenshots, narrowest first, then full pages, dark theme, and captured states.
2. **Describe before judging.** For each screenshot write two or three plain sentences: what is on screen, what the eye lands on first, second, and third, and anything that looks broken. This prevents grading the design you meant to build.
3. **Name defects first.** List at least three concrete defects, each with location, why it matters to the user, and the fix. If you cannot find three, look again at the narrowest width, the longest text, the empty or error state, and the dark theme. Zero defects after that is possible, but say where you looked.
4. **Then score** each dimension 0–3 with a one-line justification that cites a screenshot or audit finding.
5. **Fold in the tools.** An unexplained `error` from `ui_lint` or `visual_qa` caps the matching dimension at 1 until it is fixed: contrast → color; overflow, clipping, overlap → responsiveness; names, labels, focus, targets, zoom → accessibility; dead links, placeholder copy → content; console exceptions and broken images → components and states. An error you explain (pre-existing, third-party widget, false positive with the reason) does not cap. `warn` findings are fixed or accepted with a reason.
6. **Decide.** Pass when no dimension is below 2 and the average is ≥ 2.5. In Build mode, otherwise fix in [fix order](#fix-order) and run another round (three rounds at most, then report what still falls short). In Review mode, report instead of fixing unless asked.
7. **Score what you can see.** Mark a dimension "n/a" when the evidence cannot show it (screenshots alone cannot prove keyboard access or behavior at other widths); leave n/a out of the average and list it as unverified.

Be your own harshest reviewer: compare the result with the best products of the same type, not with the first draft.

## Quick tests

| Test | How | Fails when |
|---|---|---|
| Three seconds | Glance at the first-viewport screenshot | You cannot say what it is and what to do next |
| Squint | View the screenshot small or blurred | Nothing dominates, or the wrong thing does |
| Grayscale | Imagine it without color | Hierarchy or state disappears |
| Headline scan | Read only the headings | The story or structure is unclear |
| Brand | Hide the logo and name | It could be any product |
| Swap | Replace the product name with a competitor's | Every sentence still works |
| No decoration | Remove shadows, gradients, and badges mentally | It falls apart (the hierarchy was faked) |
| Thumb and keyboard | Narrow screenshot; `visual_qa` focus walk | Primary action out of reach; focus invisible or lost |
| Worst case | Longest name, empty list, error, 320px | Layout breaks or meaning is lost |

## Composition and comparison checks

- Follow the alignment edges of related headings, text, media, and controls at
  each captured width. Identify inconsistent container padding or a dropped
  column; asymmetric editorial composition and sidebar layouts can be deliberate.
- Inspect the first screen and lower sections for a missing title, covered
  content, accidental empty columns, or blank regions left by a failed asset,
  hidden element, or removed component. Explain the effect on the task instead
  of treating any gap, unequal margin, or multi-line heading as an automatic bug.
- Preserve intentional whitespace, familiar components, and reduced/static
  motion when they suit the brief. A quota of images, animated elements, cards,
  or section variations does not prove completeness or quality.
- For a redesign, compare the same route, content, state, theme, and viewport
  before and after. Name both an improvement and any observed regression; if a
  baseline or comparable state is unavailable, state that limit. Pixel
  differences alone are not a regression, and an attractive screenshot cannot
  prove retained behavior or keyboard access.

When evaluating a change to the skill itself, use the separate
[comparative evaluation procedure](../evals/visual-comparison.md); ordinary UI
tasks do not require an A/B experiment.

## Dimensions and anchors

**0** blocks or misleads the user · **1** works but has obvious problems or reads as generic · **2** solid and consistent, no notable defect · **3** deliberate and refined; holds up next to best-in-class products of its kind.

| # | Dimension | 1 looks like | 3 looks like |
|---|---|---|---|
| 1 | **Purpose and hierarchy** | Several elements compete; primary action unclear or duplicated | One clear focal point per region; reading order matches importance; the primary action is obvious |
| 2 | **Layout and composition** | Everything centered or evenly spaced; weak alignment; boxes inside boxes | Strong alignment edges, intentional grid, grouping by proximity, composition that fits the content |
| 3 | **Typography** | Many sizes and weights, long lines, default stack by habit, cramped headings | A small, consistent scale; comfortable measure and leading; typefaces that fit the direction and actually load |
| 4 | **Color and contrast** | Several accents, gray-on-gray text, color as the only state signal, stock palette | Restrained palette from tokens; one accent with clear roles; every text and UI pair passes contrast in each theme |
| 5 | **Spacing and density** | Off-scale gaps, cramped controls, or vast empty areas | One spacing scale; density matched to the task; groups separated more than their contents |
| 6 | **Components and states** | Default-looking controls; missing hover, focus, loading, empty, or error states; dead controls | Every control and data view has designed states; consistent component voice; the right control for each data type |
| 7 | **Responsiveness** | Works at one width; overflow, clipped text, or unreachable actions elsewhere | Reflows at 320px with no loss; layouts adapt by content pressure; touch and pointer both considered |
| 8 | **Accessibility** | Missing names or labels, invisible focus, small targets, blocked zoom, motion without a reduced path | Semantic structure, visible focus, ≥ 4.5:1 text, adequate targets, reduced motion honored, keyboard paths complete |
| 9 | **Content and copy** | Placeholder or cliché copy, invented proof, explanatory text in product UI | Specific, concise, domain-true copy; verbs on buttons; helpful errors and empty states; honest proof |
| 10 | **Distinctiveness and polish** | Generic-AI tells, nothing memorable, misaligned icons, inconsistent radii | A coherent direction with one signature detail; finish-line details done; nothing feels default |

A **2** sits between the two columns: no notable defect, but not yet deliberate or memorable.

## Round output

```markdown
### Critique round N — <surface>, <viewports/themes/states viewed>
Observed: <2–3 sentences per key screenshot>

Defects (highest impact first)
1. <location> — <problem> → <why it matters> → <fix>
2. …
3. …

Scores: hierarchy 2 · layout 2 · type 3 · color 2 · spacing 2 · states 1 · responsive 2 · a11y 2 · copy 3 · distinctiveness 2 → avg 2.1 (fail: states < 2)
Tool findings: ui_lint 0 errors / 2 warnings (accepted: …) · visual_qa 1 error (horizontal overflow at 320px)
Next: fix 1–3, re-run visual_qa
```

## Fix order

1. **Broken:** overflow, clipping, overlap, console errors, unreadable contrast, invisible focus, dead controls.
2. **Unclear:** hierarchy, primary action, labels, error and empty states, navigation.
3. **Inconsistent:** off-scale spacing, extra font sizes, stray colors and radii, mixed icon styles.
4. **Generic:** stock palette, default fonts by habit, card soup, cliché copy, missing signature.
5. **Unpolished:** alignment, wrapping, motion timing, finish-line details.

Fix the cause, not the symptom: if three sections overflow at 320px, fix the shared container or grid, not each section.
