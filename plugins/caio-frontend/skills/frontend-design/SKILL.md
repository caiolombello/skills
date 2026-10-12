---
name: frontend-design
description: "Use when creating, redesigning, polishing, or reviewing user-facing web UI: layout, visual direction, typography/color/spacing, states, responsiveness, accessibility, or design systems. Owns the visual quality bar and a screenshot-critique loop; pair with frontend-development for production code."
---

<!-- Informed by OpenAI's and Anthropic's published frontend guidance; independently written. See ../CREDITS.md -->

# Frontend Design

Make interfaces people understand at a glance, can operate with any input, and remember for the right reasons — then prove it on the rendered pixels, not on the code. This skill owns design decisions and the visual quality bar; [`frontend-development`](../frontend-development) owns production engineering.

## When to use

- Create or redesign a page, screen, flow, component family, dashboard, or form.
- Polish UI that works but looks generic, cluttered, inconsistent, or "off".
- Review or critique an interface from a URL, screenshots, or code.
- Define or extend tokens, a design system, or a visual direction.
- Turn requirements, sketches, or reference screenshots into implementation-ready decisions.

## When not to use

- Implement an approved design with no open visual decisions; use [`frontend-development`](../frontend-development) (it still applies this skill's quality gate when visuals change).
- Compare disposable alternatives hands-on; use [`throwaway-prototype`](../throwaway-prototype).
- Design model states, streaming, tool runs, or AI trust; pair with [`ai-interface-design`](../ai-interface-design).
- Design an API or SDK contract; use [`api-and-interface-design`](../api-and-interface-design). Generic code review; use [`code-review`](../code-review).

## Pick the mode first

| Mode | When | Output |
|---|---|---|
| **Build** | The user wants working UI (new or redesign), or code is the natural deliverable | Brief → implementation (with `frontend-development`) → render–critique loop → short report |
| **Review** | The user asks for a critique, audit, or "what is wrong with this UI" | Ranked findings with evidence and fixes; apply them only if asked |
| **Spec** | The user asks for a design document, or someone else implements | Specification from [references/design-review.md](references/design-review.md) |

Default to **Build** when the user asked for an interface; do not stop at a document. Inside an existing product, inherit its design system: the job is to fit it and raise the bar, not to reinvent it.

## Definition of done

Check these on the rendered UI at a narrow (~390px) and a wide (≥1280px) viewport, plus the most layout-sensitive non-happy state:

1. **Purpose in three seconds.** The first viewport shows what this is and the primary action (for read-only views, the key information). One primary action per view region.
2. **Nothing broken.** No horizontal scroll at 320px; no clipped, overlapping, or covered text and controls; no console errors; no dead controls (`href="#"`, no-op buttons).
3. **One system.** Color, type, space, radius, shadow, and motion come from tokens: ≤ 2 type families (+ optional mono), ~6 font sizes per view, one spacing scale, one radius scale, one accent hue plus semantic colors.
4. **States designed.** Controls have hover, focus-visible, active, disabled, and loading states. Data views have loading, empty, and error states (plus partial, stale, and permission where relevant).
5. **Accessible baseline.** Landmarks and heading order, names and labels, text contrast ≥ 4.5:1 (large text and UI parts ≥ 3:1), visible focus, targets ≥ 24px (≥ 44px when touch is primary), zoom not blocked, reduced motion honored.
6. **Real content.** Domain-specific copy and plausible data. No lorem ipsum, "Feature 1", invented logos, testimonials, or metrics, and no visible text explaining how to use the UI unless onboarding was requested.
7. **Not generic.** No unjustified tell from the [generic-AI table](#generic-ai-tells); the direction is visible and fits the audience.
8. **Critique passes.** [Rubric](references/critique-rubric.md): no dimension below 2, average ≥ 2.5 of 3.

When you cannot render, say "visually unverified", list what remains unchecked, and still meet everything checkable in code.

## Build workflow

### 1. Inspect before deciding

Read the project rules file (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, or equivalent). Then inspect existing tokens, components, fonts, icon set, adjacent screens, real data shapes, and the supported browsers, devices, themes, and languages. The existing system wins: reuse its primitives and record any deviation with its reason.

### 2. Write the brief before any UI code

Keep it to about 12 lines in your notes or reply:

```text
Brief
- User, job, success signal:
- Surface: app workspace | dashboard | form flow | marketing page | editorial | other
- First viewport: what it must show; primary action:
- Direction: <name> — three mood words; why it fits this audience
- Type: display / body / mono, with fallbacks and how they load
- Color: neutral temperature, one accent (hue and role), semantic set, light/dark plan
- Shape, depth, density: radius scale; borders or shadows; control height; base spacing
- Motion: none | subtle | expressive — each motion and its purpose
- Signature: one memorable detail derived from the domain
- Rejected defaults: generic choices you are deliberately not making
- Out of scope: features and sections you will not add
```

For a small change inside an existing product, three lines suffice: what changes, which existing patterns it reuses, and which states it touches. Choose the direction with [references/visual-direction.md](references/visual-direction.md).

### 3. Structure before style

Content inventory → flow → layout regions and reading order → hierarchy through size, weight, spacing, and position (it must read correctly in grayscale) → only then color, depth, and motion.

- **Apps and tools:** the usable product is the first screen. Do not add a marketing landing page unless asked.
- **Marketing pages:** one H1, one primary call to action above the fold, one job per section (usually ≤ 6 sections), and the brand or product unmistakable in the first viewport.
- Surface patterns: [references/layout-patterns.md](references/layout-patterns.md). Components, controls, and states: [references/component-recipes.md](references/component-recipes.md).

### 4. Tokens before components

Use the project's tokens. When none exist, start from [assets/design-tokens.css](assets/design-tokens.css) and change hues, fonts, radius, and density to match the brief; shipping it unchanged produces a generic result. Components take color, type, spacing, radius, and shadow from tokens — no raw hex values or one-off sizes.

### 5. Apply the craft defaults

Deviate when the brief or the existing system says so, and note why. Full rules and snippets: [references/craft-baseline.md](references/craft-baseline.md).

| Area | Default |
|---|---|
| Type families | ≤ 2 plus optional mono. Product UI: the system's UI sans is fine. Brand surfaces: a pairing with character, loaded properly (only used weights, `font-display: swap`). |
| Type scale | Product UI 12/14/16/20/24/30px; marketing 14/16/18/24/32/48/64px; ~6 sizes per view. Body 16px (dense data UI 14px). Hero-scale type only in true heroes. |
| Weight and case | 400 body, 500 labels, 600 headings; 700+ for display only. Sentence case in UI. |
| Line height | Body 1.5–1.65; UI labels 1.25–1.4; headings 1.1–1.25, tighter as size grows. |
| Letter spacing | 0 by default; display ≥ 40px may use −0.01 to −0.02em; all-caps labels +0.04 to +0.08em. |
| Measure and numbers | Running text 45–75ch (`max-width: 65ch`). `tabular-nums` and right alignment for numeric columns, prices, and metrics. |
| Spacing | 4px base: 4, 8, 12, 16, 24, 32, 48, 64, 96. Space between groups ≥ 2× space within a group. |
| Controls | Height 36–40px (dense 32, touch 44–48); horizontal padding 12–16px; icons 16–20px with a 6–8px gap. |
| Color | Tinted neutral ramp + one accent + success/warning/danger/info. The accent covers roughly ≤ 10% of the surface and is never the only signal of state. |
| Shape and depth | One radius scale (e.g. 4/6/8 or 8/12/16); nested radius = outer − padding. Hairline borders first; ≤ 3 elevation levels; dark mode elevates with lighter surfaces. |
| Motion | Feedback 100–150ms, small enter 150–250ms, large 250–350ms, exits faster; ease-out to enter; animate transform and opacity; provide a reduced-motion path. |
| Layout | Mobile-first; content max ≈ 1200–1280px; reading column ≈ 65ch; content pressure sets breakpoints. |
| Icons and imagery | One icon set (the project's, else Lucide) at one stroke width; icon-only buttons get `aria-label` and a tooltip. Imagery shows the real subject or product. |
| Copy | Product UI uses utility language (headings name the area); buttons are verb + object; errors say what happened and how to fix it. |

### 6. Run the render–critique–fix loop

`$SKILL_DIR` is the folder containing this file.

1. **Lint the source:** `python3 $SKILL_DIR/scripts/ui_lint.py src` — fix every error and triage warnings.
2. **Render:** start the app, then run `node $SKILL_DIR/scripts/visual_qa.mjs --url http://localhost:5173/` (or `--serve dist`, or `--file index.html`; add `--steps states.json` to capture error, empty, or open states). It writes screenshots and `report.md` under `.ui-qa/` — keep that folder out of git.
3. **Look:** open every screenshot it lists with your image viewer, narrowest first. Describe literally what you see — layout, what draws the eye first, anything broken — before judging.
4. **Critique:** score the [rubric](references/critique-rubric.md) and name at least three concrete defects (where, why it matters, the fix). If you cannot find three, re-inspect the narrow viewport, the dark theme, and a non-happy state; if they are still clean, say where you looked rather than inventing defects.
5. **Fix** in impact order — broken, then unclear, then inconsistent, then unpolished — and repeat steps 1–4.
6. **Stop** when the definition of done holds, or after three rounds; report what still falls short.

`visual_qa.mjs` needs Node and Playwright (`npm i -D playwright && npx playwright install chromium`). If your agent has its own browser tool instead, evaluate `scripts/ui_audit.js` in the page and call `__uiAudit()`. Check color pairs while choosing them: `python3 $SKILL_DIR/scripts/contrast.py "oklch(0.53 0.17 255)" "#ffffff"`.

### 7. Report

State the brief in two or three lines, what you built, the evidence (screenshots viewed, lint and audit summary, rubric scores), deviations from the defaults with reasons, and remaining gaps with how to verify them.

## Generic-AI tells

Models drift toward the statistical center of the web. Default away from these; keep one only when the brief or brand calls for it, and say so.

| Tell | Default instead |
|---|---|
| Purple/indigo → pink gradients, gradient text, glow orbs, bokeh blobs | One accent derived from the brand or domain; atmosphere from real imagery, texture, or typography |
| A palette that lands in a stock family — purple-blue, cream/beige "editorial", navy/slate dark, espresso/orange — with no reason in the brief | Choose neutral temperature and accent hue from the domain; check the final palette against this list |
| The default font stack on a brand surface, or this season's replacement default (e.g. Space Grotesk) everywhere | A pairing chosen for the direction; a generic UI sans only where the product system uses one |
| Centered hero + logo strip + three equal icon cards + testimonial grid | Structure from the argument or the task; show the actual product early; asymmetric or editorial composition |
| Cards everywhere, cards inside cards, page sections styled as floating cards | Cards for repeated items, modals, and framed tools; otherwise spacing, alignment, and dividers |
| An eyebrow label over every heading, pill and badge overload, emoji as icons, sparkles meaning "AI" | One label system used sparingly; icons from one set; text labels |
| Clichés ("supercharge", "seamless", "unlock") or instructional text inside product UI | Concrete, product-specific copy; headings that name the area |
| Invented proof: logos, testimonials, "10k+ teams", "99.9% uptime" | Real, sourced proof or nothing; sample data labeled as sample |
| Light-gray body text; 10–12px text that carries meaning | Muted text still ≥ 4.5:1; body ≥ 16px (dense UI ≥ 14px) |
| Heavy drop shadows, glass panels, `rounded-3xl` on everything | Hairline borders, one or two shadow levels, radius from the scale |
| `transition: all`, bouncing or infinite decorative motion, motion on every hover | Named properties, short durations, motion only where it explains a change |
| Dark mode by inverting to #000 and #fff | Separately tuned tokens: near-black surfaces, off-white text, desaturated accent |
| Every control at the same weight, several primary buttons | One primary per region; secondary and tertiary styles for the rest |

## Review mode

1. **Gather evidence.** Render with `visual_qa.mjs` when possible; otherwise use the supplied screenshots and read the code for semantics.
2. **Assess in order:** task and information architecture → states and recovery → accessibility and input methods → responsive behavior with realistic data → hierarchy and system consistency → distinctiveness and polish.
3. **Report** a table of location, issue, user impact, evidence label (Observed, Specified, Inferred, Preference — see [design-review](references/design-review.md#evidence-levels)), fix, and severity (blocker, major, minor, polish). Lead with the three highest-impact fixes and include the rubric scores.

Distinguish defects from preferences. Never present inferred user behavior, research, or analytics as observed.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| A spec when the user asked for working UI | Delays the result and leaves craft decisions to whoever implements |
| Styling before structure | Decorates a layout that does not work |
| Judging the UI from code alone | Clipping, overlap, contrast, and hierarchy only show up in pixels |
| "Looks great" self-review with no listed defects | Self-praise misses obvious breaks; name defects first, then score |
| Replacing the existing design system for novelty | Creates inconsistency and implementation cost |
| Mobile as a scaled-down desktop | Ignores content priority, thumb reach, and input differences |
| Accessibility as a final audit | Structural problems become expensive to fix |
| Unfounded conversion claims, manufactured urgency, hidden costs | Opinion presented as evidence; erodes trust and user agency |

## Interaction with other skills

- [`frontend-development`](../frontend-development) — implements in the real stack; runs this skill's lint, render, and critique gate whenever visuals change.
- [`ai-interface-design`](../ai-interface-design) — extends this baseline for model states, streaming, tools, provenance, and AI trust.
- [`throwaway-prototype`](../throwaway-prototype) — compares disposable directions when the brief is genuinely uncertain.
- [`brainstorming`](../brainstorming) — clarifies an ambiguous product idea before interface design starts.
- [`performance-optimization`](../performance-optimization) — measures runtime cost of fonts, images, and motion when a budget matters.
- [`security-hardening`](../security-hardening) — owns security controls; design keeps them understandable.
- [`code-review`](../code-review) — final implementation review.
- Running this skill with OpenAI/Codex, Claude, Gemini, or smaller models, and making the bar always-on in a repository: [references/model-notes.md](references/model-notes.md).

## Verification checklist

- [ ] Mode chosen; in Build mode the brief exists and its rejected defaults are honored.
- [ ] Existing tokens and components reused, or deviations justified.
- [ ] First viewport states purpose and primary action at narrow and wide widths.
- [ ] Lint has no errors; `visual_qa` has no errors, or each remaining one is explained.
- [ ] Screenshots were opened and described before scoring; at least three defects were named per round.
- [ ] Loading, empty, error, and relevant permission or partial states are designed and rendered.
- [ ] Keyboard focus is visible, contrast passes, targets are large enough, zoom is not blocked, and reduced motion is honored.
- [ ] Copy is real and specific; no placeholder content, invented proof, or dead controls.
- [ ] Rubric: no dimension below 2 and average ≥ 2.5, or the report says what falls short.
- [ ] Accessibility claims match the evidence; no automated check is described as full conformance.
