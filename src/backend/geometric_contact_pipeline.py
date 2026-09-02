# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""GEOMETRIC_CONTACT pipeline — pure NumPy edition (ported from the RASH-HIT
v1.0 engine; CPU reference path only, no Shapely/GEOS, no GPU dependency).

Wires the supercover segment engine into a box-counting run over an SVG's
open line segments:

    SVG (line/path M-L-H-V-Z/polyline/polygon/rect/circle/ellipse)
      --extract--> segments
      -> per level L1..Lmax: supercover cell set -> occupied count
      -> log-log regression (existing OLS core) -> fractal_dimension, r_squared
      -> manifest dict (measure_mode, engine_mode, per_level, ...)

``measure_mode="geometric_contact"`` is a DIFFERENT result type from area
mode: open strokes are measured as their supercover cell set, not as filled
regions.  The manifest records the exact mode and engine used.
"""
from __future__ import annotations

import math
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.backend.supercover_reference import (
    SupercoverGrid, build_supercover_grid, supercover_cells, to_fixed_point,
)
from src.backend.grid_planner import create_grid_plan
from src.backend.fractal_analyzer import compute_fractal_dimension  # type: ignore  # noqa: F401

SCHEMA = "rashhit.geometric_contact/v1"

# ---------------------------------------------------------------------------
# Segment extraction (stdlib xml.etree; no external XML dependency needed for
# this geometry-only extractor — the main loader keeps defusedxml protection)
# ---------------------------------------------------------------------------


def extract_line_segments(xml_text: str) -> Tuple[Tuple[float, float, float, float], List[Tuple[float, float, float, float]]]:
    """Parse an SVG string into (viewBox, segments).

    ``viewBox`` = (min_x, min_y, width, height); segments are (x0, y0, x1, y1)
    in user units. Supported: <line>, <polyline>, <polygon>, <rect>, <circle>,
    <ellipse>, <path>. Unsupported elements are skipped safely.
    Zero-length, NaN, and Inf segments are filtered out.
    """
    if not xml_text or not xml_text.strip():
        raise ValueError("Cannot extract geometry: SVG input is empty (0 bytes).")

    # Remove null bytes if present
    clean_xml = xml_text.replace("\x00", "")

    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(clean_xml)
    except Exception as e:
        raise ValueError(f"XML parse error: malformed SVG content ({e})") from e

    tag_clean = root.tag.split("}")[-1].lower() if "}" in root.tag else root.tag.lower()
    if tag_clean != "svg":
        raise ValueError(f"Invalid root element: expected <svg>, found <{tag_clean}>")

    vb = root.get("viewBox") or root.get("viewbox")
    viewbox: Optional[Tuple[float, float, float, float]] = None
    if vb:
        parts_str = [p.strip() for p in vb.replace(",", " ").split() if p.strip()]
        if len(parts_str) == 4:
            try:
                parts = [float(p) for p in parts_str]
                if all(math.isfinite(p) for p in parts) and parts[2] > 0 and parts[3] > 0:
                    viewbox = (parts[0], parts[1], parts[2], parts[3])
            except ValueError:
                pass

    if viewbox is None:
        try:
            w_str = re.sub(r"[^\d.]", "", root.get("width", "100")) or "100"
            h_str = re.sub(r"[^\d.]", "", root.get("height", "100")) or "100"
            w = float(w_str)
            h = float(h_str)
            if math.isfinite(w) and math.isfinite(h) and w > 0 and h > 0:
                viewbox = (0.0, 0.0, w, h)
        except Exception:
            pass

    if viewbox is None:
        raise ValueError("Invalid or degenerate viewBox: width and height must be positive finite numbers.")

    segments: List[Tuple[float, float, float, float]] = []

    def _add_segment(x0: float, y0: float, x1: float, y1: float):
        if math.isfinite(x0) and math.isfinite(y0) and math.isfinite(x1) and math.isfinite(y1):
            if (x0, y0) != (x1, y1):
                segments.append((float(x0), float(y0), float(x1), float(y1)))

    def _tag(e) -> str:
        return e.tag.rsplit("}", 1)[-1].lower()

    for el in root.iter():
        tag = _tag(el)
        try:
            if tag == "line":
                x1 = float(el.get("x1", "0")); y1 = float(el.get("y1", "0"))
                x2 = float(el.get("x2", "0")); y2 = float(el.get("y2", "0"))
                _add_segment(x1, y1, x2, y2)
            elif tag == "polyline":
                pts = _parse_points(el.get("points", ""))
                for k in range(len(pts) - 1):
                    _add_segment(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1])
            elif tag == "polygon":
                pts = _parse_points(el.get("points", ""))
                for k in range(len(pts) - 1):
                    _add_segment(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1])
                if len(pts) > 2 and (pts[0][0], pts[0][1]) != (pts[-1][0], pts[-1][1]):
                    _add_segment(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1])
            elif tag == "rect":
                x = float(el.get("x", "0"))
                y = float(el.get("y", "0"))
                w = float(el.get("width", "0"))
                h = float(el.get("height", "0"))
                if w > 0 and h > 0:
                    _add_segment(x, y, x + w, y)
                    _add_segment(x + w, y, x + w, y + h)
                    _add_segment(x + w, y + h, x, y + h)
                    _add_segment(x, y + h, x, y)
            elif tag == "circle":
                cx = float(el.get("cx", "0"))
                cy = float(el.get("cy", "0"))
                r = float(el.get("r", "0"))
                if r > 0 and math.isfinite(r):
                    steps = 24
                    for i in range(steps):
                        a1 = (i / steps) * 2 * math.pi
                        a2 = ((i + 1) / steps) * 2 * math.pi
                        _add_segment(cx + r * math.cos(a1), cy + r * math.sin(a1),
                                     cx + r * math.cos(a2), cy + r * math.sin(a2))
            elif tag == "ellipse":
                cx = float(el.get("cx", "0"))
                cy = float(el.get("cy", "0"))
                rx = float(el.get("rx", "0"))
                ry = float(el.get("ry", "0"))
                if rx > 0 and ry > 0 and math.isfinite(rx) and math.isfinite(ry):
                    steps = 24
                    for i in range(steps):
                        a1 = (i / steps) * 2 * math.pi
                        a2 = ((i + 1) / steps) * 2 * math.pi
                        _add_segment(cx + rx * math.cos(a1), cy + ry * math.sin(a1),
                                     cx + rx * math.cos(a2), cy + ry * math.sin(a2))
            elif tag == "path":
                for seg in _path_segments(el.get("d", "")):
                    _add_segment(seg[0], seg[1], seg[2], seg[3])
        except Exception:
            continue

    return viewbox, segments


def _parse_points(s: str) -> List[Tuple[float, float]]:
    pts: List[Tuple[float, float]] = []
    nums: List[float] = []
    for v in s.replace(",", " ").split():
        try:
            val = float(v)
            if math.isfinite(val):
                nums.append(val)
        except ValueError:
            pass
    for k in range(0, len(nums) - 1, 2):
        pts.append((nums[k], nums[k + 1]))
    return pts


def _path_segments(d: str) -> List[Tuple[float, float, float, float]]:
    """M/m L/l H/h V/v C/c S/s Q/q T/t A/a Z/z -> flattened line segments."""
    if not d or not d.strip():
        return []
    from src.backend.geometry_engine import parse_svg_path
    try:
        subpaths = parse_svg_path(d)
    except Exception:
        return []
    out: List[Tuple[float, float, float, float]] = []
    for pts in subpaths:
        for k in range(len(pts) - 1):
            p0 = pts[k]
            p1 = pts[k + 1]
            if math.isfinite(p0[0]) and math.isfinite(p0[1]) and math.isfinite(p1[0]) and math.isfinite(p1[1]):
                if (p0[0], p0[1]) != (p1[0], p1[1]):
                    out.append((float(p0[0]), float(p0[1]), float(p1[0]), float(p1[1])))
    return out


# ---------------------------------------------------------------------------
# Run orchestration
# ---------------------------------------------------------------------------


class _LevelResult:
    """Minimal adapter so the existing OLS core can consume supercover counts."""

    def __init__(self, grid_level, filled_count: int):
        self.level = grid_level
        self.filled_count = filled_count


def run_geometric_contact(
    svg_path: str | Path,
    max_level: int = 7,
    fixed_point_scale: int = 1 << 20,
) -> Dict:
    """Run GEOMETRIC_CONTACT box-counting on an SVG's open line segments.

    Pure CPU reference path: every level is computed with the exact
    supercover engine (Liang-Barsky closed-box intersection test).
    """
    t_total0 = time.perf_counter()

    xml_text = Path(svg_path).read_text(encoding="utf-8")
    viewbox, segments = extract_line_segments(xml_text)
    s_count = len(segments)

    grid_cache: Dict[int, SupercoverGrid] = {
        lv: build_supercover_grid(viewbox, lv, fixed_point_scale)
        for lv in range(1, max_level + 1)
    }
    base = grid_cache[1]

    per_level: Dict[str, Dict] = {}
    occupied_by_level: Dict[int, int] = {}

    for lv in range(1, max_level + 1):
        grid = grid_cache[lv]
        fp = to_fixed_point(segments, grid)
        cells = supercover_cells(fp, grid)
        occupied_by_level[lv] = int(cells.shape[0])

    for lv in range(1, max_level + 1):
        grid = grid_cache[lv]
        occupied = int(occupied_by_level.get(lv, 0))
        total = grid.cols * grid.rows
        per_level[str(lv)] = {
            "cols": grid.cols,
            "rows": grid.rows,
            "total_cells": total,
            "occupied_cells": occupied,
            "empty_cells": total - occupied,
            "occupancy_ratio": round(occupied / total, 6),
        }

    # Box-counting regression reusing the project's exact OLS core.
    # (canvas_aspect behaviour is this planner's default aspect-ratio rule.)
    plan = create_grid_plan(svg_viewbox=viewbox, svg_width=viewbox[2],
                            svg_height=viewbox[3], num_levels=max_level)
    results = [_LevelResult(plan.levels[lv - 1], per_level[str(lv)]["occupied_cells"])
               for lv in range(1, max_level + 1)]
    dim = compute_fractal_dimension(results)

    occupied_count_by_level = {
        f"L{lv:02d}": occupied_by_level[lv] for lv in range(1, max_level + 1)}

    manifest = {
        "schema_version": SCHEMA,
        "engine_mode": "cpu_reference",
        "backend": "cpu",
        "gpu_name": None,
        "measure_mode": "geometric_contact",
        "boundary_policy": "touch_counts",
        "grid_policy": "fixed_origin",
        "level_formula": "cols=rows=4*2^(level-1) (square viewBox, canvas_aspect)",
        "base_rows": base.rows,
        "base_columns": base.cols,
        "validation_enabled": True,
        "cpu_reference_executed": True,
        "engine": "cpu_reference_supercover",
        "fixture_name": Path(svg_path).stem,
        "viewBox": list(viewbox),
        "segments": s_count,
        "segment_count": s_count,
        "fixed_point_scale": fixed_point_scale,
        "requested_max_level": max_level,
        "total_compute_seconds": round(time.perf_counter() - t_total0, 6),
        "occupied_count_by_level": occupied_count_by_level,
        "per_level": per_level,
        "fractal_dimension": round(float(dim.fractal_dimension_db), 6),
        "r_squared": round(float(dim.r2_score), 6),
        "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return manifest
