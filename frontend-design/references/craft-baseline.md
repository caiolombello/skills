# Craft Baseline

Load when building or restyling UI and the project has no stricter system. Every number is a default, not a law: deviate when the brief, brand, or existing design system says otherwise, and record why.

## Contents

- [Typography](#typography)
- [Color](#color)
- [Space and layout](#space-and-layout)
- [Shape and depth](#shape-and-depth)
- [Interaction states](#interaction-states)
- [Motion](#motion)
- [Icons and imagery](#icons-and-imagery)
- [Content and microcopy](#content-and-microcopy)
- [Finish line](#finish-line)

## Typography

Type does most of the work of hierarchy. Get it right in grayscale before adding color.

**Choose by role.** Define display (heroes, page titles), body (running text and UI), and optionally mono (code, IDs, tabular data). Two families is the ceiling; one well-chosen family with weight contrast is often better. Pick from the direction ([visual-direction.md](visual-direction.md)); for dense product UI the existing system font or a neutral UI sans is correct, not a failure of taste.

**Load fonts deliberately.**

- Self-host or use the framework's font loader (for example `next/font`, Fontsource); only the weights and subsets you use.
- `font-display: swap`, a metric-compatible fallback stack, and `preload` only for the one or two faces above the fold.
- Verify the face actually rendered: `visual_qa` reports declared fonts that fell back. A stack that names a font you never loaded is a common silent failure.

**Scale.** Pick a ratio and stop adding sizes.

| Use | Product UI (px) | Marketing / editorial (px) | Token |
|---|---|---|---|
| Caption, meta | 12 | 14 | `--text-xs` / `--text-sm` |
| Secondary, table | 14 | 16 | `--text-sm` / `--text-base` |
| Body | 16 (14 in dense data UI) | 18 | `--text-base` / `--text-lg` |
| Section heading | 20 | 24–30 | `--text-xl` / `--text-2xl`–`--text-3xl` |
| Page title | 24–30 | 36–48 | `--text-2xl`–`--text-3xl` / `--text-4xl`–`--text-5xl` |
| Display | — | 40–72, fluid | `--text-display` |

Use rem in CSS. For display sizes only, a bounded fluid size is fine: `font-size: clamp(2.5rem, 1.6rem + 3vw, 4.5rem)`. Never size text with `vw` alone (it breaks zoom), and keep panel, sidebar, and dashboard headings small.

**Line height and spacing.**

- Body 1.5–1.65; UI labels and buttons 1.25–1.4; headings 1.1–1.25, tighter as size increases.
- Letter spacing 0 by default. Display ≥ 40px may use −0.01 to −0.02em. All-caps labels need +0.04 to +0.08em and should stay rare.
- Paragraph spacing ≈ 0.75–1em; heading space-above ≥ 1.5× space-below so headings bind to what follows.

**Measure and wrapping.** Running text 45–75 characters (`max-width: 65ch`). `text-wrap: balance` for headings and `text-wrap: pretty` for paragraphs as progressive enhancements. Allow long words and URLs to break (`overflow-wrap: anywhere` in user-generated content).

**Numbers.** `font-variant-numeric: tabular-nums` for tables, prices, metrics, timers, and anything that updates; right-align numeric columns; format with `Intl.NumberFormat` and `Intl.DateTimeFormat` in the user's locale.

**Weight.** 400 body, 500 labels and navigation, 600 headings. Reserve 700+ for display. Emphasize with weight or color, not underline (links only) or ALL CAPS sentences.

## Color

**Build roles, not swatches.** Every color in a component comes from a role token (named `--color-<role>` in [design-tokens.css](../assets/design-tokens.css)):

| Role | Use |
|---|---|
| `bg`, `surface`, `surface-2` | Page, raised panels, subtle fills (table headers, hover) |
| `border`, `border-strong` | Dividers; control boundaries (≥ 3:1 where the border identifies the control) |
| `text`, `text-muted`, `text-subtle` | Primary, secondary, and tertiary text — all ≥ 4.5:1 on their surfaces |
| `accent`, `accent-hover`, `on-accent`, `accent-subtle`, `accent-text` | Primary actions, selection, links, highlights |
| `success`, `warning`, `danger`, `info` (+ `-subtle`) | Status only; always paired with text or an icon |
| `focus` | Focus ring (≥ 3:1 against adjacent colors) |

**Neutrals carry the interface.** Tint the neutral ramp slightly toward the accent's temperature (OKLCH chroma 0.002–0.012) so grays feel intentional. Pure `#000` text on `#fff` is harsher than needed; near-black on off-white reads better.

**One accent, used sparingly.** The accent marks what is interactive or selected — primary buttons, active navigation, focus, key data. When everything is accented, nothing is. Additional hues are for data visualization and status, not decoration.

**OKLCH makes ramps predictable.** Keep hue and chroma, vary lightness:

```css
--color-accent: oklch(0.53 0.17 var(--hue-accent));         /* white text on top */
--color-accent-hover: oklch(0.47 0.15 var(--hue-accent));
--color-accent-subtle: oklch(0.965 0.015 var(--hue-accent)); /* selected rows, tags */
--color-accent-text: oklch(0.48 0.15 var(--hue-accent));     /* links on light surfaces */
```

Contrast varies with hue: green, teal, and cyan accents need lower lightness (≈ 0.45–0.48) to carry white text. Check every pair with `<skill-dir>/scripts/contrast.py` and the rendered page with `visual_qa`.

**Dark mode is a second palette, not an inversion.** Near-black surfaces (L ≈ 0.16–0.22), off-white text (L ≈ 0.93–0.96), muted text that still passes 4.5:1, lighter surfaces for elevation instead of shadows, and an accent that is lighter and slightly less saturated (often with dark text on it). Set `color-scheme: light dark` so native controls and scrollbars follow. Ship dark mode only when the product needs it, and then test it like the light theme.

**State colors never stand alone.** Error fields get a message and an icon or border change; status badges carry text; charts use labels or patterns as well as hue.

## Space and layout

**One spacing scale.** 4px base: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Use the scale for padding, gaps, and margins; one-off values (13px, 22px) are almost always a mistake.

**Proximity is structure.** Space between groups ≥ 2× the space inside a group. A section that needs a border to look separate usually needs more space instead.

**Containers.**

- Marketing content max ≈ 1200–1280px with 24px gutters (16px on phones); reading column ≈ 65ch.
- App shells use the full width: sidebar 220–280px, content padded 16–32px, max widths only on forms and reading content.
- Align to a few strong edges. Left-aligned text with a consistent left edge reads faster than centered text beyond two lines.

**Intrinsic layout first.**

```css
.grid { display: grid; gap: var(--space-6); grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr)); }
.stack > * + * { margin-block-start: var(--space-4); }
.cluster { display: flex; flex-wrap: wrap; gap: var(--space-2) var(--space-3); align-items: center; }
.reading { max-width: 65ch; }
```

Container queries (`container-type: inline-size` + `@container`) let a component adapt to its slot instead of the viewport. Media-query breakpoints come from content pressure; common landmarks are 640, 768, 1024, and 1280px.

**Viewport units.** Full-height sections use `min-height: 100svh` (or `100dvh`) with `100vh` as a fallback; subtract fixed headers with `calc(100svh - var(--header-h))`. Marketing heroes usually stop short of that (≈ 80–90svh) so the next section peeks into view. Respect `env(safe-area-inset-*)` for fixed bottom bars on phones.

**Stable layout.** Reserve space for images (`width`/`height` or `aspect-ratio`), async content (skeletons sized like the result), and fixed-format UI (toolbars, counters, tiles) so hover states and late data never shift the page. Use `scrollbar-gutter: stable` on scroll containers whose scrollbar appears and disappears.

## Shape and depth

**Radius** comes from the direction and stays consistent: sharp (0–2px), crisp (4–6px), soft (8–12px), or round (16px+). Default product UI: 6–8px for controls and cards. Nested elements: inner radius = outer radius − padding. Pills (full radius) are for tags, toggles, and avatars, not every button.

**Depth** tells what floats:

| Level | Use | Treatment (light) |
|---|---|---|
| 0 | Page and inline content | No border or a hairline divider |
| 1 | Cards, panels, inputs | 1px `border` and/or `0 1px 2px rgb(0 0 0 / 0.06)` |
| 2 | Popovers, menus, dropdowns | `0 4px 12px rgb(0 0 0 / 0.08), 0 1px 3px rgb(0 0 0 / 0.06)` |
| 3 | Dialogs, drawers | `0 16px 40px rgb(0 0 0 / 0.14)` plus a scrim |

In dark mode, raise elevation with a lighter surface and a subtle border; shadows barely read. A design that only looks finished with heavy shadows usually has a hierarchy problem.

## Interaction states

Interactive elements need these states where they apply, designed rather than defaulted:

| State | Treatment |
|---|---|
| Hover | Subtle background or color shift (pointer devices only: `@media (hover: hover)`) |
| Focus-visible | 2px ring in `focus` with 2px offset, ≥ 3:1 against adjacent colors, never removed without replacement |
| Active / pressed | Slightly darker fill or a 1px inset; immediate |
| Selected / current | Accent-subtle fill or indicator plus `aria-current` / `aria-selected` |
| Disabled | Reduced contrast plus `cursor: not-allowed`; explain why nearby when it is not obvious |
| Loading | Spinner or progress inside the control, label preserved, width stable, duplicate submits blocked |
| Invalid | Danger border plus message text linked with `aria-describedby` |

```css
:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```

Prefer native elements: a `<button>` gets keyboard, focus, and semantics for free; a clickable `<div>` gets none of them.

## Motion

Motion explains change: where something came from, what responded, what is loading. If it explains nothing, remove it.

| Kind | Duration | Easing |
|---|---|---|
| Feedback (hover, press, toggle) | 100–150ms | ease-out |
| Small enter (menu, tooltip, toast) | 150–250ms | `cubic-bezier(0.2, 0, 0, 1)` |
| Large enter (drawer, dialog, page section) | 250–350ms | same, or a gentle spring |
| Exit | ~75% of enter | ease-in |

- Animate `transform` and `opacity`; name properties instead of `transition: all`.
- Do not animate frequent actions (typing, table sorting) or block input during a transition.
- Visually led pages can carry two or three deliberate motions — an entrance sequence, one scroll-linked or depth effect, and a hover or reveal that clarifies affordance. Product UI usually needs only feedback and enter/exit.
- Staggers: 30–60ms per item, at most ~6 items.
- Reduced motion keeps the information without the movement:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; scroll-behavior: auto !important; }
}
```

Content revealed on scroll must be visible without JavaScript and with reduced motion.

## Icons and imagery

- One icon set (the project's, else Lucide), one stroke width, sized to the adjacent text (16px with 14px text, 20px with 16px text) and vertically centered on the text, not the line box.
- Icons support labels. Icon-only buttons are for universally understood actions (close, search, menu, more) and need `aria-label` plus a tooltip.
- Emoji are content, not UI icons: they render differently per platform and carry their own color.
- Imagery shows the real subject: the product UI, the place, the people, or the data. Real screenshots beat illustrations; illustrations beat abstract gradients. Never use decorative blobs as the main visual.
- If no imagery exists, design a typographic or product-led composition rather than inventing stock-like visuals. Use generated or searched images only when the agent has that capability and reuse rights are clear.
- Images: `width`/`height` or `aspect-ratio`, `object-fit: cover` with a chosen focal point, `loading="lazy"` below the fold, meaningful `alt` (or `alt=""` when decorative). Keep a calm area behind any overlaid text, or add a scrim and verify contrast.

## Content and microcopy

- **Utility first in product UI.** Headings name the area ("Overdue invoices", "Last sync"), not the value proposition. If a sentence could appear in an ad, rewrite it.
- **Buttons are verb + object:** "Create invoice", "Send 3 reminders", "Delete project" — not "Submit", "OK", or "Click here".
- **Errors** say what happened and how to fix it, in the user's terms, next to the field: "Enter an email like name@company.com."
- **Empty states** explain why it is empty and offer the next action; first-use, no-results, and cleared states differ.
- **Confirmations** name the consequence: "Delete 'Q3 report'? This removes 14 shared links."
- **Numbers and dates:** locale formatting, units, relative times with absolute tooltips, correct pluralization ("1 file", "2 files").
- **Truncation:** ellipsis plus the full value in a tooltip or detail view; never truncate the only identifier.
- **Sample data** looks real for the domain (names, amounts, dates) and is labeled as sample where users could mistake it for theirs. Never invent testimonials, customer logos, or performance claims.
- Sentence case, no exclamation marks in system messages, consistent terminology (pick "project" or "workspace", not both).

## Finish line

The details that separate "fine" from "finished":

- `<title>`, favicon, `lang`, viewport meta without zoom limits, `meta name="theme-color"` per theme.
- `color-scheme` set; native controls tinted with `accent-color`; `::selection` uses the accent.
- Icons optically centered with text; numeric columns aligned; baselines aligned across a row.
- No orphaned single word on large headings (`text-wrap: balance` or a manual non-breaking space).
- Avatar and image fallbacks (initials, neutral placeholder) instead of broken-image icons.
- Long names, long numbers, empty values, and localization expansion (+30–40% for German or Portuguese) tested.
- Every visible control works, links go somewhere, and nothing explains the interface in visible text unless it is onboarding the user asked for.
- Print or export styles where users print (invoices, reports).
