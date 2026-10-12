<!--
Paste the section below into a repository's AGENTS.md / CLAUDE.md (or a system prompt)
to make the UI quality bar always-on. Replace SKILL_DIR with the installed skill path,
e.g. ~/.agents/skills/frontend-design, or with a vendored copy such as tools/ui-qa.
Fill in the "This project" lines; delete lines that do not apply.
-->

## Frontend quality bar

Applies to any change that adds or restyles UI. Use the `frontend-design` skill (and `frontend-development` for production code) when available.

This project:
- Design system / tokens: <path, e.g. src/styles/tokens.css> · Components: <library or path> · Icons: <set>
- Fonts: <display / body / mono> · Accent: <role and token> · Themes: <light only | light + dark>
- Run the app: <command and URL>

Before code, write a short brief: user and job, primary action, direction, type, color, density, one signature detail, rejected defaults, and what is out of scope. Reuse existing tokens and components; never hard-code colors or one-off sizes in components.

Defaults (deviate only with a reason):
- ≤ 2 type families (+ mono), ~6 font sizes per view, body 16px (dense UI 14px), line-height 1.5–1.65, running text ≤ 65ch, tabular numbers in tables.
- 4px spacing scale; one radius scale; hairline borders before shadows; one accent plus semantic colors; text ≥ 4.5:1 contrast.
- Every control has hover, focus-visible, active, disabled, and loading states; every data view has loading, empty, and error states.
- Apps open on the usable product, not a marketing page. Product copy is specific and utilitarian; no placeholder text, invented proof, or dead links.
- Avoid unless the brief asks: purple/indigo gradients, gradient text, glow blobs, glass panels, emoji icons, cards inside cards, an eyebrow on every heading, `transition: all`.

Done means verified on the rendered UI:
1. `python3 SKILL_DIR/scripts/ui_lint.py src` → no errors.
2. `node SKILL_DIR/scripts/visual_qa.mjs --url <app url>` → no errors; open the screenshots it lists (390px and 1440px, dark theme if any) and describe what you see.
3. Name at least three defects, fix them, and re-run until no rubric dimension scores below 2 (rubric: SKILL_DIR/references/critique-rubric.md).
4. If the UI cannot be rendered, say "visually unverified" and list what was not checked.

Keep `.ui-qa/` out of version control.
