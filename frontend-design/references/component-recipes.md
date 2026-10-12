# Component Recipes

Load when choosing controls or building common components. Prefer the project's component library and its accessible primitives (or headless libraries such as Radix, React Aria, Headless UI, Ark, or Melt) over hand-rolled widgets; these recipes describe what "done" looks like either way.

## Contents

- [Choose the right control](#choose-the-right-control)
- [Buttons and links](#buttons-and-links)
- [Form fields](#form-fields)
- [Forms and validation](#forms-and-validation)
- [Cards and lists](#cards-and-lists)
- [Tables](#tables)
- [Navigation](#navigation)
- [Overlays](#overlays)
- [Feedback: toasts, banners, inline alerts](#feedback-toasts-banners-inline-alerts)
- [Loading, empty, and error](#loading-empty-and-error)
- [Badges, avatars, tooltips](#badges-avatars-tooltips)
- [Dashboards and charts](#dashboards-and-charts)

## Choose the right control

| Data or intent | Control |
|---|---|
| A command ("Save", "Export") | Text button (verb + object) |
| A tool in a toolbar (bold, crop, zoom) | Icon button with `aria-label` and tooltip |
| Binary setting applied immediately | Switch |
| Binary choice submitted with a form | Checkbox |
| One of 2–5 visible modes or views | Segmented control or tabs |
| One of 2–7 options where comparison helps | Radio group |
| One of many options | Select or combobox (searchable beyond ~15 options) |
| Several of many | Checkbox list, or multi-select combobox with chips |
| A precise number | Number input with `inputmode`, or a stepper |
| An approximate value in a range | Slider (with a visible value and a text-entry fallback) |
| A color | Swatches, plus a picker only when arbitrary colors are needed |
| A date | Native date input or a date picker that also accepts typing |
| Navigation to another place | Link (`<a href>`), even when styled as a button |

Within the brief's scope, build the controls, states, and views a real user of this product expects. A demo with dead buttons is not a design; features the brief marks out of scope stay out.

## Buttons and links

- **Hierarchy:** one primary (filled accent) per view region; secondary (outline or tinted); tertiary (ghost or text); destructive (danger color, used for the confirming step, not the first click).
- **Sizes:** 32px (dense), 36–40px (default), 44–48px (touch-primary or hero). Horizontal padding 12–16px; icon 16–20px with a 6–8px gap.
- **States:** hover, focus-visible ring, pressed, disabled, loading (spinner replaces or precedes the label; width stays fixed; repeated clicks are ignored).
- **Placement:** in forms, the primary action ends the form and aligns with the fields' left edge; in dialogs, actions sit bottom right with the primary last (follow the platform or existing system if it differs).
- **Links** navigate and buttons act. Inline links are underlined or otherwise distinguishable without color alone.

## Form fields

- Visible label above the field (placeholder is never the label); optional helper text below; mark the minority (required or optional), consistently.
- Height matches buttons (36–40px; 44px+ on touch); text ≥ 16px on mobile to avoid iOS zoom.
- Border ≥ 3:1 against the surface when it is the only boundary; focus ring in `focus`; invalid state adds a danger border **and** a message linked with `aria-describedby`.
- Correct `type`, `inputmode`, `autocomplete`, and `name`; the width hints at the expected content (ZIP code fields are short).
- Group related fields with `fieldset` and `legend` (radio groups, addresses).

## Forms and validation

- Validate on blur or submit, not on every keystroke (except helpful live feedback like password rules).
- On submit failure: keep every value, focus the first invalid field (or an error summary for long forms), and explain each fix in place.
- Do not disable the submit button to signal invalid input; let users submit and tell them what to fix. Disable only while a submission is in flight.
- Long forms: logical sections, one column, progress for multi-step flows, saved drafts where loss would hurt.
- Success: confirm in place or navigate to the created object; offer undo where it is safe.

## Cards and lists

- Use a card when the item is a repeated, self-contained object (a project, a product, a person), a modal surface, or a framed tool. Page sections and single blocks of content do not need card chrome.
- Never nest cards; use spacing, dividers, or a subtle surface change inside one.
- A card has one primary action; make the whole card clickable only through a single link (stretched-link pattern) and keep secondary actions as separate buttons.
- Card grids: `repeat(auto-fit, minmax(min(18rem, 100%), 1fr))`; equal heights only when items are truly comparable.
- Lists of homogeneous rows (settings, files, people) are usually better as a list or table than as a card grid.

## Tables

- Text left-aligned, numbers right-aligned with `tabular-nums`, headers aligned with their data.
- Row height 40–48px (comfortable) or 32–36px (dense; 28px only in spreadsheet-like grids); zebra stripes optional, hover highlight useful for wide tables.
- Sticky header for long tables; frozen first column for wide ones; sortable headers with `aria-sort`.
- Keep short values (dates, amounts, statuses) on one line; truncate long text with a tooltip or detail view.
- Row actions at the row end (an overflow menu beyond two actions); bulk actions appear when rows are selected.
- Narrow screens: horizontal scroll inside a labeled container with the first column frozen, or transform rows into stacked items when columns are few.
- Loading uses skeleton rows; empty explains and offers the next action; errors keep filters and retry.

## Navigation

- Five to seven top-level destinations at most; current location shown visually and with `aria-current="page"`.
- App shell: left sidebar (220–280px, collapsible) for many destinations, top bar for few; breadcrumbs for deep hierarchies.
- Phones: a bottom tab bar for 3–5 primary destinations in apps; a menu button with a full-height panel for sites. Keep the primary action reachable by thumb.
- Menus and disclosure widgets follow the WAI-ARIA Authoring Practices keyboard model when they are custom.
- Provide a skip link to `main` when navigation precedes content.

## Overlays

| Need | Use |
|---|---|
| Short, focused decision or form (≤ ~5 fields) | Dialog |
| Longer task while keeping context | Drawer / side sheet |
| Contextual options or small editor | Popover |
| Non-essential hint on hover or focus | Tooltip |
| Complex multi-step work | A page, not an overlay |

Dialogs: focus moves in, stays in, and returns to the trigger; Escape closes; a visible close button; a scrim; scroll locked behind; destructive confirmations name the object and the consequence ("Delete project 'Atlas'"), with the destructive button labeled by its action, never "OK".

## Feedback: toasts, banners, inline alerts

| Situation | Pattern |
|---|---|
| Background action succeeded ("Saved", "Copied") | Toast, 4–6s, polite live region, pause on hover, undo when possible |
| An error the user must act on | Inline alert next to the cause, or a dialog when blocking — not a vanishing toast |
| System-wide state (offline, trial ending, maintenance) | Banner at the top of the content, dismissible when non-critical |
| Field-level problem | Inline message under the field |

## Loading, empty, and error

- **Loading:** skeletons shaped like the final content for page and list loads; a spinner only inside a control or for short indeterminate waits; delay spinners ~300ms to avoid flashes; never animate fake progress toward 100%.
- **Empty:** first use (explain the value and the first action), no results (show the query and how to broaden it), cleared (confirm the state). An illustration is optional; the action is not.
- **Error:** what happened in human terms, what still works, and how to recover (retry, edit, contact). Keep user input. Never show stack traces or internal IDs without a copy-able reference for support.
- **Partial and stale:** show what loaded, what did not, and when the data was last updated.

## Badges, avatars, tooltips

- **Badges** carry status or counts in text (plus color); use few, in consistent positions; do not badge everything.
- **Avatars:** image with initials fallback on a deterministic tinted background; consistent sizes (24/32/40px); alt text with the person's name when it adds information.
- **Tooltips** are supplementary: never the only place essential information lives, shown on hover and focus, dismissible with Escape, and not used on touch-only controls.

## Dashboards and charts

- Lead with the one or two numbers that answer the dashboard's question; give KPIs the context the data supports (comparison period, delta with direction and sign, target). Never invent a target or benchmark.
- Few chart types used well: line for trends, bar for comparisons, table for exact values. Avoid 3D, gauges for precise values, and pies beyond ~5 slices.
- Label data directly where possible, start bar axes at zero, use a sequential palette for magnitude and a categorical palette with ≤ 6–7 hues, and never encode meaning with color alone.
- Global filters (date range, segment) are persistent, visible, and reflected in the URL.
- Not everything belongs in a card: align charts on a grid and let whitespace group them.
