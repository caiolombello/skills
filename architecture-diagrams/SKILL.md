---
name: architecture-diagrams
description: "Use when creating or reviewing professional technical diagrams for software, cloud, Kubernetes, networks, data flows, C4, sequence, BPMN, or infrastructure. Produces editable Draw.io or Excalidraw sources plus validated exports; not UI mockups or data charts."
---

<!-- Informed by coleam00/excalidraw-diagram-skill; Draw.io tooling adapted from Agents365-ai/drawio-skill (MIT). See ../CREDITS.md. -->

# Architecture Diagrams

Create technical diagrams that answer a specific question, remain editable, use
accurate notation and icons, and survive visual and structural review. Treat the
diagram as an engineering artifact, not decoration.

## Scope boundaries

Use this skill for:

- Software, cloud, platform, Kubernetes, network, security, deployment, and
  data-flow architecture.
- C4, UML sequence, BPMN, topology, dependency, integration, and operational
  diagrams.
- Creating, converting, updating, or reviewing `.drawio` and
  `.excalidraw` files.
- Turning Terraform, Terraform state, or Kubernetes manifests into a reviewable
  architecture baseline.

Do not use it as the primary workflow for:

- Choosing the architecture itself. Pair with the relevant architecture or
  security skill; this skill owns visual modeling and artifact quality.
- UI flows, wireframes, or product screens — use
  [`frontend-design`](../frontend-design).
- Quantitative charts or analytical dashboards.
- Decorative illustrations with no technical semantics.

## Required deliverables

Unless the user narrows the request, produce:

1. Editable source: `.drawio` or `.excalidraw`.
2. Review format: SVG preferred; PNG at 2x when raster is needed.
3. A concise textual description or alt text for externally shared diagrams.
4. Validation evidence: exact commands, results, and any unverified visual gap.

Keep title, purpose, scope/environment, version, date, and source freshness
inside the diagram or its adjacent description. Do not write outputs inside the
skill directory.

## Choose the representation

Read [references/notation-selection.md](references/notation-selection.md) and
[references/visual-quality.md](references/visual-quality.md) before authoring.

| Need | Default |
|---|---|
| Formal cloud, Kubernetes, network, C4, BPMN, or UML artifact | Draw.io |
| Vendor icon libraries, multipage drill-down, or corporate handoff | Draw.io |
| Workshop, teaching narrative, incident story, or conceptual explanation | Excalidraw |
| Hand-drawn collaboration with a small number of technical components | Excalidraw |
| User explicitly requests one format | Use it unless it would misrepresent the notation; explain the tradeoff |

Prefer Draw.io when exact vendor icons, strict notation, print/export, or
long-term maintenance matter. Prefer Excalidraw when the spatial story and
collaboration matter more than formal notation.

## Workflow

### 1. Establish evidence and intent

- Identify the one question the diagram must answer, the audience, decision,
  scope, environment, and expected shelf life.
- Inspect the actual code, IaC, manifests, configuration, or supplied evidence
  before drawing technical facts.
- Mark inputs as `observed`, `required`, `assumed`, or `unknown`.
- Never infer deployed state from desired-state files without labeling it.
- Treat live inventory as read-only unless the user separately authorizes
  operational changes.

Use [references/architecture-brief.md](references/architecture-brief.md) for a
high-stakes or underspecified diagram.

### 2. Select one primary notation and zoom

- Start at the smallest zoom that answers the question.
- Use C4 Context or Container for software structure; add Component only where
  it changes a decision.
- Use a deployment/topology view for runtime placement and failure boundaries.
- Use UML sequence for ordering and request/response behavior.
- Use BPMN for business process roles, events, and gateways.
- Split viewpoints instead of mixing C4, BPMN, network topology, and sequence
  semantics on one canvas.

### 3. Build the semantic model before styling

List:

- Nodes with stable IDs, official names, type, owner, environment, and status.
- Boundaries with nesting and explicit meaning.
- Directed relations with protocol/event, purpose, trust change, and
  synchronous/asynchronous behavior.
- Sources and unresolved facts.

Remove anything that does not help answer the primary question. For medium or
large Draw.io diagrams, store this model as graph JSON and generate layout from
it.

### 4. Construct the editable source

For Draw.io, read
[references/drawio-workflow.md](references/drawio-workflow.md). Use the bundled
scripts where they match the evidence:

```bash
# Find exact built-in cloud/Kubernetes shape styles.
python3 scripts/shapesearch.py "aws elastic kubernetes service"

# Terraform configuration -> graph -> editable Draw.io.
python3 scripts/tfimports.py ./infra -o graph.json
python3 scripts/autolayout.py graph.json --tune -o architecture.drawio

# Kubernetes manifests -> graph -> editable Draw.io.
python3 scripts/k8simports.py ./manifests --group -o graph.json
python3 scripts/autolayout.py graph.json --tune -o architecture.drawio
```

Load [references/official-icon-sources.md](references/official-icon-sources.md)
whenever vendor or CNCF icons are involved.

For Excalidraw, read
[references/excalidraw-workflow.md](references/excalidraw-workflow.md). Build
the scene in coherent sections with descriptive IDs. Use official icons only
when their source and terms are known; otherwise use neutral shapes with
explicit labels.

### 5. Apply the visual system

- Show hierarchy through position, enclosure, type, and whitespace before
  using color.
- Keep boundaries visually behind their contents and nest them consistently.
- Use one direction for the primary reading path.
- Use orthogonal connectors for formal topology; use curved connectors only
  when they improve a narrative.
- Label every non-obvious relation. Show protocols, events, ports, encryption,
  or direction only when verified and relevant.
- Separate data, control, identity, and observability flows by line treatment
  and a compact legend.
- Pair every icon with text. Never rely on logo recognition or color alone.
- Preserve official icon aspect ratio, colors, and naming.

### 6. Validate structure

Draw.io:

```bash
python3 scripts/validate.py architecture.drawio --score
python3 scripts/edgeports.py architecture.drawio --dry-run
python3 scripts/edgeports.py architecture.drawio -o architecture-routed.drawio
python3 scripts/validate.py architecture-routed.drawio --strict
```

Excalidraw:

```bash
python3 scripts/validate_excalidraw.py architecture.excalidraw --strict --score
```

Treat errors as blockers. Investigate warnings; suppress none without a reason.
Importers provide a baseline, not proof that every inferred relation is
correct.

### 7. Render, inspect, and refine

Render the actual editable source; do not review a separately redrawn preview.

Draw.io example:

```bash
drawio -x -f svg -e -o architecture.svg architecture.drawio
drawio -x -f png -s 2 -o architecture.png architecture.drawio
```

Excalidraw example:

```bash
uv run --with playwright==1.62.0 \
  python scripts/render_excalidraw.py architecture.excalidraw \
  --svg architecture.svg --png architecture.png --scale 2
```

Open the SVG/PNG and inspect it visually. Check at both fit-to-page and 100%:

- No overlap, clipping, broken icon, orphan edge, or connector through a node.
- Readable labels, balanced whitespace, clear entry point, and stable eye path.
- Boundaries, environments, trust zones, and failure domains are unambiguous.
- Legend matches actual line, color, and icon semantics.
- Grayscale and color-deficient reading retain meaning.
- The diagram still answers its stated question without narration.

Iterate on the editable source and rerun validation after every material visual
change. If rendering is unavailable, state that visual QA is unverified; do not
claim the diagram is production-ready.

## Architecture conventions

- Nest from broad to narrow: provider/on-premises -> organization/account/
  project/subscription -> region -> network -> zone/subnet -> cluster ->
  namespace -> workload.
- Draw a managed service at the boundary where it actually operates. Do not
  place a provider-managed service inside a subnet merely because access is
  private.
- Represent abstraction with neutral shapes; reserve product icons for concrete
  deployed or proposed services.
- Distinguish current, proposed, external, and out-of-scope elements with a
  legend and labels, not color alone.
- Show HA/DR only when replicas, zones, regions, failover direction, state, and
  recovery assumptions are known.
- Keep secrets, credentials, customer identifiers, private hostnames, and
  sensitive IPs out of externally shared diagrams.

## Review format

For a diagram review, report:

1. Fidelity defects — facts, boundaries, direction, notation, or icon misuse.
2. Comprehension defects — hierarchy, density, labels, crossings, or ambiguity.
3. Production defects — clipping, broken exports, inaccessible color, missing
   metadata, or non-editable handoff.
4. Recommended corrections in priority order.
5. Verification performed and remaining gaps.

## Interaction with other skills

- [`aws-security-architecture`](../aws-security-architecture) — define AWS
  trust boundaries and controls; use this skill to render them.
- [`terraform-iac-expert`](../terraform-iac-expert) — verify Terraform
  semantics before visualizing configuration or state.
- [`kubectl-workflows`](../kubectl-workflows) — govern any live Kubernetes
  inventory command with explicit context and namespace.
- [`frontend-design`](../frontend-design) — own UI flows and screen design,
  not infrastructure or software architecture diagrams.

## Verification checklist

- [ ] The audience, question, scope, environment, and freshness are explicit.
- [ ] Observed, proposed, assumed, and unknown facts are distinguishable.
- [ ] The notation and zoom match the question; overloaded views were split.
- [ ] Every component, boundary, and relation has defensible semantics.
- [ ] Vendor icons came from an official or attributable source and remain
      labeled.
- [ ] Editable source and review export were both produced.
- [ ] Structural validation passed with warnings reviewed.
- [ ] The rendered source was visually inspected at fit and 100%.
- [ ] Accessibility, confidentiality, metadata, and textual description were
      checked.
- [ ] Unverified claims and tooling gaps are disclosed.
