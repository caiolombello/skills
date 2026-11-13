# Official icon sources and provenance

Use official vendor or foundation assets. Treat logos and service icons as
trademarked materials even when the downloadable files are freely available.
Review current terms before external or commercial distribution.

## Sources

| Ecosystem | Primary source | Operational rule |
|---|---|---|
| AWS | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) | Use the current official package; AWS refreshes it periodically. Preserve product names, colors, proportions, and grouping guidance. |
| Microsoft Azure | [Azure architecture icons](https://learn.microsoft.com/azure/architecture/icons/) | Keep the product name near the icon. Do not crop, rotate, distort, recolor, or use a Microsoft icon as a logo for a third-party product. |
| Google Cloud | [Google Cloud product icons](https://cloud.google.com/icons) | Prefer the current product icon set over legacy artwork; keep names and proportions intact. |
| Kubernetes/CNCF | [CNCF artwork repository](https://github.com/cncf/artwork) and [CNCF brand guidelines](https://www.cncf.io/brand-guidelines/) | Use project artwork from the official source and observe Linux Foundation/CNCF trademark terms. Do not use certification marks without qualification. |
| Draw.io built-ins | Bundled shape index derived from [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp) and diagrams.net libraries | Resolve exact styles with `scripts/shapesearch.py`; see [licenses/shape-index-notice.md](licenses/shape-index-notice.md). |

## Selection policy

- Use a service icon only for a concrete service. Use a neutral shape for a
  capability, generic database, generic cluster, team, or business process.
- Keep one icon family/version per vendor on a page.
- Pair every icon with a readable official service/project name.
- Do not invent a Draw.io `mxgraph.*` style. Search the bundled catalog and
  render-test the result.
- For Excalidraw, embed the official SVG/PNG into the scene so the editable file
  does not depend on a local filesystem path or remote URL.
- Do not copy complete vendor icon packs into this skill. Fetch the required
  official pack into task-local working storage, record provenance, and include
  only assets needed for the deliverable.

## Provenance record

For an externally shared diagram, record one row per asset family:

| Field | Example |
|---|---|
| Vendor/foundation | AWS |
| Asset/package | Architecture Icons |
| Official source URL | https://aws.amazon.com/architecture/icons/ |
| Version or download date | YYYY-MM-DD |
| Files used | EKS, RDS, CloudFront |
| Modifications | None |
| Terms reviewed | URL and date |

The bundled Draw.io shape index is a search aid, not evidence that a vendor's
current branding terms were reviewed. When brand fidelity matters, compare the
rendered icon with the current official package.

## Prohibited practices

- Mixing current and legacy icon generations without a declared reason.
- Recoloring vendor icons to fit a theme.
- Using icons without labels or as decorative bullets.
- Using a provider logo to imply certification, partnership, or endorsement.
- Downloading icon archives from third-party mirrors when an official source
  exists.
- Treating open-source licensing as permission to ignore trademark policy.
