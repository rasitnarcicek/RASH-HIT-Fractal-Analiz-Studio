# RASH-HIT Fractal Studio — GPU Intermediate Geometry Format (Stage 3.8)

Status: DESIGN ONLY. No code converts geometry to this format yet.
This document is the data contract that Stage 6-7 GPU kernels will consume.

## Goal
Pass the normalized geometry from `svg_loader` / `geometry_engine` to a GPU
kernel in as FEW transfers as possible, using contiguous NumPy arrays with
explicit dtypes and shapes (little-endian-agnostic logical contract).

## Canonical arrays (all contiguous, C-order, explicit dtype)

| Array | dtype | shape | meaning |
|-------|-------|-------|---------|
| `vertices` | float64 | (V, 2) | all polygon vertices / path points |
| `line_segments` | int64 | (S, 2) | index pairs into `vertices` for explicit segments |
| `polygon_ring_offsets` | int64 | (R+1,) | start index of each ring in `vertices` |
| `polygon_ids` | int64 | (R,) | which polygon each ring belongs to |
| `hole_flags` | int8 | (R,) | 1 = hole ring, 0 = outer |
| `fill_rules` | int8 | (P,) | 0 = evenodd, 1 = nonzero (per polygon) |
| `stroke_polygon_ids` | int64 | (K,) | polygons produced by stroke expansion |
| `geometry_bounds` | float64 | (2, 2) | [[minx,miny],[maxx,maxy]] |
| `transform_applied` | int8 | () | 1 if geometry is already in user units |

### Fixed-point scale metadata
- `fixed_point_scale: int64` — multiplier to convert float64 user units to
  integer grid coordinates on the GPU (e.g. 1e6). GPU kernels operate on
  int64 to avoid float drift; the host provides `fixed_point_scale` and the
  grid origin so the kernel can map `round(coord * scale)` -> cell index.

## Invariants
- Every ring's vertex range is contiguous in `vertices` (offsets define it).
- `polygon_ring_offsets[-1] == V`.
- `len(polygon_ids) == len(hole_flags) == R == len(polygon_ring_offsets)-1`.
- Explicit `line_segments` cover open polylines / paths not expressed as
  closed rings (used by the Stage 6 segment-traversal prototype).
- Nothing here assumes a specific endianness; the contract is logical
  (shape + dtype). Transport may reinterpret bytes but values are portable.

## Out of scope (this stage)
- Actual conversion code (Stage 6).
- Bézier/grid direct intersection (Stage 6); curves are flattened on CPU
  first (existing `geometry_engine`), then passed as segments/vertices.
- Stroke-width expansion GPU kernel (Stage 7) — CPU expansion feeds
  `stroke_polygon_ids`.
