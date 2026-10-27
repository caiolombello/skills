# Layout Patterns

Load when composing a page or screen. Each pattern lists the structure that usually works, how it adapts to narrow screens, and the failure models most often produce. Start from the user's task, not from the pattern.

## Contents

- [App shell](#app-shell)
- [Dashboard](#dashboard)
- [List and detail](#list-and-detail)
- [Record or detail page](#record-or-detail-page)
- [Settings](#settings)
- [Forms and multi-step flows](#forms-and-multi-step-flows)
- [Authentication](#authentication)
- [Marketing and landing pages](#marketing-and-landing-pages)
- [Pricing](#pricing)
- [Docs and long-form reading](#docs-and-long-form-reading)
- [First run and system pages](#first-run-and-system-pages)

## App shell

- **Structure:** persistent navigation (sidebar for many destinations, top bar for few), a page header with title and primary action, and a workspace that owns the scroll.
- **Narrow:** sidebar becomes a menu panel or a bottom tab bar (3–5 destinations); the page header keeps the title and the primary action.
- **Failure:** a marketing hero inside the app; navigation that hides the current location; a header with three equal-weight buttons.

## Dashboard

- **Structure:** a header that names the area ("Revenue"), with the question it answers in the subtitle ("October, compared with September"); a short KPI row with context; the one primary chart; then supporting breakdowns and a table of exact values. Filters persist at the top.
- **Narrow:** KPIs in a two-column grid or a horizontal scroller, charts full width, tables as scroll containers.
- **Failure:** every widget in a card with equal weight; eight KPIs with no comparison; decorative sparklines; colors with no legend.

### Data meaning and dashboard QA

- State the question, selected scope, time range, units, and freshness needed to
  interpret the screen. Make the most important answer discoverable without
  forcing every requested block above the fold at an unreadable density.
- Keep measured zero distinct from unavailable, not yet collected, loading,
  redacted, or failed data. Use a clear label or explained missing-value mark;
  do not coerce missing values to zero or draw a measured line through a gap.
- Name both comparison periods and preserve their scope and units. When periods
  are not comparable or the baseline is zero/missing, show the available absolute
  values and the limitation; do not manufacture a percentage or trend.
- Use documented formulas for aggregates and make totals reconcile with their
  scope. Do not sum non-additive metrics or backfill sample values to make a chart
  attractive. Clearly identify permitted synthetic data in prototypes.
- A rising metric is not inherently good: increased errors and increased revenue
  have different meanings. Apply the domain's known interpretation with text or
  symbols as well as color; if desirability is unknown, show a neutral change.
- At wide and narrow widths, check meaningful labels, units, filters, table/chart
  alignment, and access to the primary task. Keep deliberate table scrolling
  within its container, make it discoverable, and verify that offscreen columns
  can be reached without losing row context. No marketing hero, imagery, or decorative motion is
  required for an operational screen.

## List and detail

- **Structure:** a searchable, filterable list (or table) and a detail view — side by side on wide screens, as separate routes on narrow ones. Selection is reflected in the URL.
- **Narrow:** list first; the detail opens as its own screen with a clear back path that preserves list position and filters.
- **Failure:** losing scroll position and filters on return; a detail view squeezed into a 300px column.

## Record or detail page

- **Structure:** a header with the object's name, status, and primary actions; key facts in a scannable definition list; related items and activity below or in tabs.
- **Narrow:** actions collapse into a primary button plus an overflow menu; tabs scroll horizontally.
- **Failure:** IDs and timestamps given the same weight as the name; every field in its own card.

## Settings

- **Structure:** grouped sections with a title and a one-line explanation; label, control, and help text aligned in rows; a section-level save or auto-save with clear feedback; dangerous actions isolated at the end.
- **Narrow:** a single column with the section navigation as a list or select.
- **Failure:** a giant form with one save button at the bottom; switches that need a separate save; destructive actions next to routine ones.

## Forms and multi-step flows

- **Structure:** one column, labels above fields, logical groups, a primary action at the end. Multi-step flows show progress ("Step 2 of 4"), allow going back without losing data, and summarize before committing.
- **Narrow:** the same single column; sticky bottom actions only when the form is long and the keyboard does not cover them.
- **Failure:** two-column forms that break reading order; wizards that split three fields into three steps; validation that erases input.

## Authentication

- **Structure:** product name or logo, one focused form, clear alternatives (SSO, magic link), the path to sign up or recover access, and minimal distraction. Support password managers (`autocomplete="username"`, `current-password`, `new-password`, `one-time-code`).
- **Narrow:** the form fills the width with comfortable margins; no decorative panel.
- **Failure:** a split screen with a stock gradient panel; unclear password rules; blocking paste.

## Marketing and landing pages

Derive sections from the argument: what visitors must understand, believe, and do. Then:

- **First viewport:** the brand or product is a hero-level signal; one headline (the category or literal offer, with the value in supporting copy), one short supporting sentence, one call-to-action group, and one dominant visual — the real product, a real photo, or a strong typographic composition. Budget the viewport: a fixed header counts against it, and a hint of the next section should stay visible, so size the hero at roughly 80–90svh minus the header rather than a full screen.
- **Sections:** each has one job, one headline, and usually one short supporting sentence. Show the product early and often; prefer concrete specifics (numbers you can source, real workflows, real customers) over adjectives. Five or six sections usually suffice.
- **Proof:** real, attributed quotes and logos you have rights to use, or none.
- **Narrow:** the same story order; the call to action stays visible early; images keep their subject in frame.
- **Failure:** the default stack (centered hero, logo strip, three icon cards, testimonial grid, pricing, FAQ, CTA) with interchangeable copy; floating badges and chips over hero media; hero text inside a card; split text/media heroes chosen by habit; gradient blobs as the main visual.

## Pricing

- **Structure:** two to four plans, the recommended one marked with text (not only color), prices with billing period and currency, the differences that matter first, and a full comparison table below. Explain limits and overage honestly.
- **Narrow:** plans stack in recommended order; the comparison table scrolls with the plan names frozen.
- **Failure:** hidden fees, pre-selected add-ons, fake urgency, or the cheapest option made hard to find.

## Docs and long-form reading

- **Structure:** a reading column ≈ 65ch, a table of contents on wide screens, clear heading hierarchy with anchor links, code blocks with copy buttons, and previous/next navigation.
- **Narrow:** the table of contents collapses into a disclosure at the top; code blocks scroll horizontally inside themselves.
- **Failure:** full-width text; low-contrast code themes; headings that differ only by size.

## First run and system pages

- **First run:** show the value with the user's own first action, not a tour of every feature; sample data clearly labeled; a path to real data.
- **404 / errors:** say what happened, offer search and the main destinations, keep the navigation.
- **Maintenance and offline:** what is affected, what still works, and when to retry.
