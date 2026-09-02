# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Pure NumPy supercover segment engine (ported from the RASH-HIT v1.0
geometric_contact engine; no Shapely/GEOS, no Taichi/GPU required).

PURPOSE
-------
A pure-NumPy supercover segment engine: the scientific reference of the
fractal studio's geometric_contact measure mode.  It enumerates the
supercover cell set of open line segments from fixed-point int64
coordinates, sorts the set lexicographically by (row, column) and emits
the canonical cell list.

METHOD
------
Supercover rule (boundary_policy="touch_counts"): a cell belongs to the
occupied set iff its CLOSED box [i*cw, (i+1)*cw] x [j*ch, (j+1)*ch] INTERSECTS
the segment (interior, edge touch or corner touch all count).  The engine
implements this definition DIRECTLY: for every cell in the segment's bounding
box, an exact segment-vs-box intersection test (Liang-Barsky clipping, closed
box) decides membership.  It is deliberately a different algorithm from the
traversal kernels so that an implementation error on either side is caught by
set comparison, not masked by a shared bug.

Coordinate convention
---------------------
Input segments are fixed-point int64: ``round((coord - origin) * scale)``.
The grid (origin, cell sizes, cols/rows) follows the FIXED_ORIGIN grid plan
for the same viewBox and level, so all cell indices are (row, column) pairs
on the same lattice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Grid definition (FIXED_ORIGIN: cols = rows = 4 * 2^(level-1), anchored at
# the viewBox minimum; aspect-ratio rule for non-square viewBox).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SupercoverGrid:
    """Fixed-point lattice definition."""

    origin_x: int        # fixed-point origin x (viewBox min x * scale)
    origin_y: int        # fixed-point origin y (viewBox min y * scale)
    cell_w: int          # fixed-point cell width
    cell_h: int          # fixed-point cell height
    cols: int            # number of columns
    rows: int            # number of rows
    fixed_point_scale: int = 1

    @property
    def width_fp(self) -> int:
        return self.cols * self.cell_w

    @property
    def height_fp(self) -> int:
        return self.rows * self.cell_h


def build_supercover_grid(
    viewbox: Tuple[float, float, float, float],
    level: int,
    fixed_point_scale: int = 1,
) -> SupercoverGrid:
    """Build the FIXED_ORIGIN grid for a level.

    ``viewbox`` = (min_x, min_y, width, height).  Grid size follows the
    square-grid rule: ``cols = rows = 4 * 2^(level-1)``, which for a square
    viewBox reproduces the reference lattice (L2 -> 8x8, L10 -> 2048x2048).
    For a NON-square viewBox the aspect-ratio rule is applied
    (base 4 on the smaller axis, rounded), keeping the cell set comparable
    to the area grid.
    """
    vx, vy, vw, vh = viewbox
    s = fixed_point_scale
    n_side = 4 * (2 ** (level - 1))
    if vw > 0 and vh > 0 and abs(vw - vh) > 1e-9:
        ar = vw / vh
        if ar > 1000.0 or ar < 1e-3:
            raise ValueError(f"Extreme aspect ratio ({ar:.4g}) exceeds maximum supported limits (1e-3 .. 1e3).")
        if ar >= 1.0:
            rows = n_side
            cols = max(1, int(round(n_side * ar)))
        else:
            cols = n_side
            rows = max(1, int(round(n_side / ar)))
    else:
        cols = rows = n_side
    cell_w = vw / cols if vw > 0 else 0.0
    cell_h = vh / rows if vh > 0 else 0.0
    return SupercoverGrid(
        origin_x=int(round(vx * s)),
        origin_y=int(round(vy * s)),
        cell_w=int(round(cell_w * s)),
        cell_h=int(round(cell_h * s)),
        cols=cols,
        rows=rows,
        fixed_point_scale=s,
    )


def to_fixed_point(
    segments: Sequence[Tuple[float, float, float, float]],
    grid: SupercoverGrid,
) -> np.ndarray:
    """Convert user-unit segments to fixed-point int64 (S, 4) relative to origin.

    ``x_fp = round((x - origin_x_user) * scale)`` — both sides of the
    pipeline consume identical coordinates.
    """
    s = grid.fixed_point_scale
    ox = grid.origin_x / s
    oy = grid.origin_y / s
    arr = np.asarray(segments, dtype=np.float64).reshape(-1, 4)
    # Clamp extremely large coordinates to avoid int64 overflow
    max_safe = 1e9
    arr = np.clip(np.nan_to_num(arr, nan=0.0, posinf=max_safe, neginf=-max_safe), -max_safe, max_safe)
    out = np.empty((arr.shape[0], 4), dtype=np.int64)
    max_i64 = float((1 << 62) - 1)
    out[:, 0] = np.clip(np.nan_to_num(np.rint((arr[:, 0] - ox) * s), nan=0.0), -max_i64, max_i64).astype(np.int64)
    out[:, 1] = np.clip(np.nan_to_num(np.rint((arr[:, 1] - oy) * s), nan=0.0), -max_i64, max_i64).astype(np.int64)
    out[:, 2] = np.clip(np.nan_to_num(np.rint((arr[:, 2] - ox) * s), nan=0.0), -max_i64, max_i64).astype(np.int64)
    out[:, 3] = np.clip(np.nan_to_num(np.rint((arr[:, 3] - oy) * s), nan=0.0), -max_i64, max_i64).astype(np.int64)
    return out


# ---------------------------------------------------------------------------
# Exact segment-vs-closed-box intersection (Liang-Barsky, float64).
# Fixed-point int64 coordinates are <= 2^53 for scale <= 2^30, so float64
# represents them EXACTLY; the test is therefore exact on the lattice.
# ---------------------------------------------------------------------------


def _seg_intersects_box(
    x0: float, y0: float, x1: float, y1: float,
    xmin: float, ymin: float, xmax: float, ymax: float,
) -> bool:
    """Closed-box intersection: boundary touches count (touch_counts policy)."""
    dx = x1 - x0
    dy = y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - xmin, xmax - x0, y0 - ymin, ymax - y0)
    t0, t1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0.0:
            if qi < 0.0:
                return False  # parallel to this axis and outside the box
        else:
            r = qi / pi
            if pi < 0.0:
                if r > t1:
                    return False
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return False
                if r < t1:
                    t1 = r
    return t0 <= t1  # closed interval overlap (touches at t0 == t1 count)


def supercover_cells(
    segments_fp: np.ndarray,
    grid: SupercoverGrid,
) -> np.ndarray:
    """Supercover cell set for one or more fixed-point segments.

    Returns an int64 (N, 2) array of (row, column) pairs, DEDUPLICATED and
    sorted lexicographically by (row, column) — the canonical ordering.
    """
    cw = float(grid.cell_w)
    ch = float(grid.cell_h)
    cells: List[Tuple[int, int]] = []
    s = segments_fp.reshape(-1, 4)
    for x0, y0, x1, y1 in s:
        cells.extend(_segment_supercover(x0, y0, x1, y1, grid, cw, ch))
    if not cells:
        return np.empty((0, 2), dtype=np.int64)
    arr = np.asarray(sorted(set(cells)), dtype=np.int64)
    return arr


def _segment_supercover(
    x0: int, y0: int, x1: int, y1: int,
    grid: SupercoverGrid, cw: float, ch: float,
) -> List[Tuple[int, int]]:
    """Supercover cells of ONE fixed-point segment (bounding-box enumeration)."""
    fx0, fy0, fx1, fy1 = float(x0), float(y0), float(x1), float(y1)
    lo_x, hi_x = min(fx0, fx1), max(fx0, fx1)
    lo_y, hi_y = min(fy0, fy1), max(fy0, fy1)
    i_lo = int(np.floor(lo_x / cw)) if cw > 0 else 0
    i_hi = int(np.floor(hi_x / cw)) if cw > 0 else 0
    j_lo = int(np.floor(lo_y / ch)) if ch > 0 else 0
    j_hi = int(np.floor(hi_y / ch)) if ch > 0 else 0
    # CLOSED-box rule: an endpoint lying exactly ON a cell boundary also
    # touches the neighbouring cell box (touch_counts).  Widen the scan
    # range by one cell on that side — the intersection test then decides.
    if lo_x % cw == 0.0:
        i_lo -= 1
    if hi_x % cw == 0.0:
        i_hi += 1
    if lo_y % ch == 0.0:
        j_lo -= 1
    if hi_y % ch == 0.0:
        j_hi += 1
    # clamp to the lattice
    i_lo = max(0, min(grid.cols - 1, i_lo))
    i_hi = max(0, min(grid.cols - 1, i_hi))
    j_lo = max(0, min(grid.rows - 1, j_lo))
    j_hi = max(0, min(grid.rows - 1, j_hi))
    out: List[Tuple[int, int]] = []
    for j in range(j_lo, j_hi + 1):
        ymin = j * ch
        ymax = (j + 1) * ch
        for i in range(i_lo, i_hi + 1):
            xmin = i * cw
            xmax = (i + 1) * cw
            if _seg_intersects_box(fx0, fy0, fx1, fy1, xmin, ymin, xmax, ymax):
                out.append((j, i))  # (row, column)
    return out


def supercover_cells_for_polyline(
    points: Sequence[Tuple[float, float]],
    grid: SupercoverGrid,
) -> np.ndarray:
    """Supercover cells of an open polyline (sequence of segments, dedup)."""
    pts = list(points)
    segs = [(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1])
            for k in range(len(pts) - 1)]
    fp = to_fixed_point(segs, grid)
    return supercover_cells(fp, grid)
