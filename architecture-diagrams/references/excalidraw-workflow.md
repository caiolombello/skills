# Excalidraw workflow

Use Excalidraw for workshops, teaching, incident narratives, comparisons, and
technical concepts where a spatial story matters more than formal notation.
Use Draw.io for strict BPMN/UML, dense cloud topology, and icon-heavy handoff.

## Contents

1. Scene template and semantic sections
2. Scene discipline
3. Validation and local rendering
4. Visual review

## Start from the template

Copy [../assets/excalidraw-template.json](../assets/excalidraw-template.json) to
the task output directory and rename it with an `.excalidraw` extension.

The source must remain an Excalidraw scene:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "architecture-diagrams",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

## Build in semantic sections

1. Add title, purpose, scope, and state metadata.
2. Create the primary reading spine: left-to-right, top-to-bottom, radial, or
   before/after.
3. Add boundaries and section labels behind their contents.
4. Add components with descriptive IDs.
5. Add relations and labels.
6. Add evidence snippets or annotations only where they teach something.
7. Add a compact legend and source/freshness note.

Use structure to express meaning:

| Meaning | Spatial pattern |
|---|---|
| One source to many consumers | Fan-out |
| Many inputs to one result | Convergence |
| Ordered states or incident evidence | Timeline |
| Transformation | Before -> process -> after |
| Feedback or lifecycle | Cycle |
| Alternatives or current/target | Side-by-side comparison |
| Ownership or trust | Nested boundaries |

Do not turn every label into an equal card. Use free text for titles,
annotations, and relation details; use containers for actual components,
decisions, boundaries, or grouped evidence.

## Scene discipline

- Use unique, descriptive string IDs and deterministic numeric seeds.
- Keep related element IDs prefixed by section, such as `ingress_api` and
  `ingress_api_label`.
- Use integer coordinates on a 20 px grid for primary alignment.
- Keep text as separate elements only when it remains correctly positioned and
  bound.
- Use `fontFamily: 2` (Helvetica) for formal, portable architecture labels.
  Use Excalidraw's hand-drawn families intentionally for workshop or narrative
  views; the renderer does not inline remote font files.
- Keep arrow `startBinding`, `endBinding`, and target `boundElements`
  consistent.
- Put boundaries before their child elements in scene order.
- Embed images in `files`; do not depend on local paths or remote URLs.
- Preserve official icon artwork and add a separate readable service label.

For large scenes, add one section at a time and validate between sections.

## Validate

```bash
python3 scripts/validate_excalidraw.py architecture.excalidraw --score
python3 scripts/validate_excalidraw.py architecture.excalidraw --strict --score
```

The validator checks scene shape, IDs, references, bindings, geometry, unsafe
links, images, and basic readability. It cannot prove that the architecture is
correct or that the rendered composition is attractive.

## Render locally

```bash
uv run --with playwright==1.62.0 \
  python scripts/render_excalidraw.py architecture.excalidraw \
  --svg architecture.svg --png architecture.png --scale 2
```

The renderer verifies and loads the vendored Excalidraw 0.18.1 browser bundle.
The browser is offline before any page content or private scene is injected;
rendering makes no CDN request. See
[excalidraw-runtime-provenance.md](excalidraw-runtime-provenance.md) for the
bundle hash, exact build lockfile, upgrade procedure, and third-party notices.

Install the matching Chromium once when Playwright requests it:

```bash
uv run --with playwright==1.62.0 playwright install chromium
```

Do not install dependencies without user approval in a managed environment.
The vendored renderer itself needs no npm install.

## Visual review

Inspect the rendered SVG/PNG, not only the JSON:

- Text is not clipped and remains readable at final size.
- Boundaries contain their intended children.
- Arrows attach to the intended nodes and do not cover labels.
- Hand-drawn roughness does not obscure exact technical meaning.
- The eye reaches the intended conclusion in the chosen reading direction.
- Official icons are intact, labeled, and not visually dominant.
- The result is understandable in grayscale and with its text description.

If rendering fails, retain the editable source and report the gap. Do not
replace visual validation with “the JSON parses.”
