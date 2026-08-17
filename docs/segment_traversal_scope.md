# RASH-HIT Fractal Studio — Segment-Traversal Prototype Scope (Stage 3.9)

Status: SCOPE DEFINITION for the FIRST GPU segment prototype (Stage 6).
Not implemented yet. This bounds what the prototype must and must not do.

## Supported in the first prototype
- Horizontal line
- Vertical line
- Diagonal line
- Arbitrary line segment
- Open polyline
- CPU-flattened open path (Bézier/arc already flattened to segments on CPU)
- Single-level cell enumeration derived to a coarser parent level when the
  nested grid relationship is verified (grid is doubling, so a fine cell maps
  deterministically to a coarse cell)

## NOT supported in the first prototype
- Polygon interior fill
- Holes
- evenodd / nonzero fill rules (these belong to the Stage 7 fill engine)
- Stroke width / linecap / linejoin expansion (Stage 7)
- Direct Bézier–grid intersection (curves are flattened on CPU first)
- Production L15 / L20 dense runs
- Multi-GPU

## Boundary test matrix (must be covered by prototype tests)
| Case | Description |
|------|-------------|
| center cross | segment passes through a cell center |
| edge touch | segment touches only a cell edge, not interior |
| corner touch | segment touches only a cell corner |
| along boundary | segment runs along a grid boundary line |
| zero length | segment start == end (degenerate) |
| outside area | segment entirely outside the analysis area |
| boundary start/end | segment starts or ends exactly on a grid boundary |

## Acceptance for the prototype (Stage 6, later)
GPU-occupied cell SET must equal CPU/Shapely reference occupied cell SET,
for every matrix case above, before any fill work begins.
