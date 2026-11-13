# Draw.io workflow

Use Draw.io for formal, icon-rich, multipage, or long-lived technical
artifacts. Keep the `.drawio` source authoritative; regenerate all exports
from it.

## Contents

1. Runtime prerequisites
2. Bundled tools
3. Shape search and graph JSON
4. Terraform, Kubernetes, and C4
5. Validation and export

## Runtime prerequisites

| Capability | Requirement |
|---|---|
| Shape search and structural validation | Python 3 standard library |
| Kubernetes YAML ingestion | PyYAML; JSON input needs no extra package |
| Automatic graph layout | Graphviz `dot`; `tred` improves Terraform edge reduction |
| SVG/PNG/PDF export | Draw.io desktop CLI |

Run `python3 scripts/preflight.py` before a new environment. Do not install
missing system tools without user approval.

## Bundled tools

| Script | Purpose |
|---|---|
| `shapesearch.py` | Search 10,000+ Draw.io shape styles without guessing |
| `tfimports.py` | Terraform configuration to graph JSON |
| `tfstate.py` | `terraform show -json` state/plan to graph JSON |
| `k8simports.py` | Kubernetes YAML/JSON to graph JSON |
| `autolayout.py` | Graph JSON through Graphviz to editable Draw.io |
| `c4.py` | Multipage C4 model with drill-down links |
| `edgeports.py` | Spread stacked edge attachment points |
| `validate.py` | Structural and readability lint |
| `repair_png.py` | Repair a known truncated IEND in editable PNG exports |

The Python tools are curated from Agents365-ai/drawio-skill under MIT. See
[licenses/Agents365-drawio-skill-MIT.txt](licenses/Agents365-drawio-skill-MIT.txt).
The shape index has separate Apache-2.0 provenance; see
[licenses/shape-index-notice.md](licenses/shape-index-notice.md).

## Work from the skill root

```bash
DIAGRAM_SKILL=/path/to/architecture-diagrams
cd "$DIAGRAM_SKILL"
```

Write task outputs outside `DIAGRAM_SKILL`.

## Search exact icons

```bash
python3 scripts/shapesearch.py "aws lambda"
python3 scripts/shapesearch.py "azure kubernetes service"
python3 scripts/shapesearch.py "gcp cloud sql" --json
python3 scripts/shapesearch.py "kubernetes ingress"
```

Copy the returned complete style string. Render-test it; a valid-looking
`mxgraph.*` name can still produce a blank box.

## Graph JSON contract

```json
{
  "direction": "LR",
  "title": "Orders platform · production",
  "subtitle": "Current state · reviewed 2026-08-18",
  "ranksep": 0.8,
  "nodesep": 0.6,
  "nodes": [
    {
      "id": "api",
      "label": "Orders API",
      "group": "Production / Platform",
      "width": 140,
      "height": 70,
      "style": "rounded=1;whiteSpace=wrap;html=1"
    }
  ],
  "edges": [
    {
      "source": "api",
      "target": "orders-db",
      "label": "Read/write · TLS",
      "style": "edgeStyle=orthogonalEdgeStyle;endArrow=block;html=1"
    }
  ]
}
```

Use stable, XML-safe IDs. Make edge direction and labels match the evidence.
Groups accept slash-separated nesting.

## Terraform

Desired configuration:

```bash
python3 scripts/tfimports.py ./infra --group -o graph.json
python3 scripts/autolayout.py graph.json --tune -o desired.drawio
```

Recorded state or saved plan:

```bash
terraform show -json |
  python3 scripts/tfstate.py - --group -o graph.json
python3 scripts/autolayout.py graph.json --tune -o recorded.drawio
```

Do not call state “live infrastructure.” Terraform state is recorded state and
may be stale. A saved plan is proposed state. State dependencies come from an
optional recorded `depends_on` field when present; saved-plan dependencies come
from [official configuration expression references](https://developer.hashicorp.com/terraform/internals/json-format#expression-representation).
Terraform can collapse `count`/`for_each` dependencies to a static resource
address. When the JSON does not preserve the instance mapping, `tfstate.py`
omits the instance-level edge and warns instead of guessing. Literal target
indexes and singleton targets remain representable; a static reference to a
multi-instance resource is ambiguous because the JSON does not distinguish a
computed index from an aggregate/splat. If no dependency evidence is
available, the script emits an explicit
inventory-only warning. Label each result accurately.

## Kubernetes

Manifest set:

```bash
python3 scripts/k8simports.py ./manifests --group -o graph.json
python3 scripts/autolayout.py graph.json --tune -o desired-cluster.drawio
```

Read-only cluster snapshot, only after loading `kubectl-workflows`:

```bash
kubectl --context CONTEXT get all,ing,cm,secret,pvc -A -o json |
  python3 scripts/k8simports.py - --group -o graph.json
```

The importer derives a limited set of static references. Verify selectors,
controllers, service meshes, CRDs, policies, external dependencies, and runtime
traffic separately.
Known built-in namespaced objects without `metadata.namespace` are treated as
`default`; use `--default-namespace NAME` when the manifest set is interpreted
elsewhere. API group is part of object identity. A custom/unknown resource with
no explicit namespace remains `scope unknown` because its CRD, not its kind
name, determines scope.

## C4 multipage

Create JSON with `levels[].name`, `elements[]`, and `relations[]`. Element
types are `person`, `system`, `external`, `container`, `component`,
and `database`. A `children` value links an element to another level name.

```bash
python3 scripts/c4.py c4.json --direction LR -o system.drawio
```

Use unique element IDs across all pages.

## Validate without destructive edits

```bash
python3 scripts/validate.py architecture.drawio --score
python3 scripts/edgeports.py architecture.drawio --dry-run
python3 scripts/edgeports.py architecture.drawio -o architecture-routed.drawio
python3 scripts/validate.py architecture-routed.drawio --strict --score
```

Compare source and routed variants visually before replacing the source.

## Export

```bash
drawio --version
drawio -x -f svg -e -o architecture.svg architecture.drawio
drawio -x -f png -s 2 -o architecture.png architecture.drawio
drawio -x -f pdf -e -o architecture.pdf architecture.drawio
```

On Linux headless systems, the desktop CLI may require Xvfb. Use only a local
renderer for confidential diagrams. Never send architecture XML to an online
conversion service without explicit permission.

For the specific truncated-IEND defect in an editable PNG exported with `-e`,
run `python3 scripts/repair_png.py architecture.drawio.png`. It validates the
PNG and writes `architecture.drawio.repaired.png` by default. Inspect the new
file with an independent PNG reader before replacing anything; `--in-place` is
an explicit, recoverability-sensitive option.
