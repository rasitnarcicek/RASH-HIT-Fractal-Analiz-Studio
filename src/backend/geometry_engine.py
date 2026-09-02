# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

"""
geometry_engine.py — SVG Geometry Parser, Curve Flattening & 2D Matrix Transform Engine.
Parses path data (M, L, H, V, C, S, Q, T, A, Z), rect, circle, ellipse, line, polyline, polygon.
Applies 2D affine transformation matrices and emits pure line-segment lists for the
supercover engine (v1.2.0: no Shapely/GEOS dependency anywhere in the pipeline).
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Tuple, Optional, Iterable
import numpy as np

from src.backend.svg_loader import SVGNode


# ============================================================================
# 2D Affine Transform Matrix Helper
# ============================================================================

def parse_transform_string(transform_str: str) -> np.ndarray:
    """
    Parses SVG transform attribute string into a 3x3 homogeneous transformation matrix.
    Supports matrix, translate, scale, rotate, skewX, skewY.
    """
    M = np.eye(3, dtype=np.float64)
    if not transform_str:
        return M

    commands = re.findall(r'([a-zA-Z]+)\s*\(([^)]+)\)', transform_str)
    for cmd, args_str in commands:
        cmd = cmd.strip().lower()
        args = [float(p) for p in re.split(r'[\s,]+', args_str.strip()) if p]

        T = np.eye(3, dtype=np.float64)
        if cmd == 'matrix' and len(args) == 6:
            a, b, c, d, e, f = args
            T = np.array([[a, c, e],
                          [b, d, f],
                          [0, 0, 1]], dtype=np.float64)
        elif cmd == 'translate':
            tx = args[0]
            ty = args[1] if len(args) > 1 else 0.0
            T = np.array([[1, 0, tx],
                          [0, 1, ty],
                          [0, 0, 1]], dtype=np.float64)
        elif cmd == 'scale':
            sx = args[0]
            sy = args[1] if len(args) > 1 else sx
            T = np.array([[sx, 0, 0],
                          [0, sy, 0],
                          [0, 0, 1]], dtype=np.float64)
        elif cmd == 'rotate':
            angle = math.radians(args[0])
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            if len(args) == 3:
                cx, cy = args[1], args[2]
                T_trans1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]], dtype=np.float64)
                T_rot = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]], dtype=np.float64)
                T_trans2 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]], dtype=np.float64)
                T = T_trans2 @ T_rot @ T_trans1
            else:
                T = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]], dtype=np.float64)
        elif cmd == 'skewx':
            tan_a = math.tan(math.radians(args[0]))
            T = np.array([[1, tan_a, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
        elif cmd == 'skewy':
            tan_a = math.tan(math.radians(args[0]))
            T = np.array([[1, 0, 0], [tan_a, 1, 0], [0, 0, 1]], dtype=np.float64)

        M = M @ T

    return M


def transform_points(points: List[Tuple[float, float]], M: np.ndarray) -> List[Tuple[float, float]]:
    """Applies 3x3 transformation matrix M to a list of (x, y) coordinates."""
    if len(points) == 0:
        return []
    pts_arr = np.column_stack([np.array(points), np.ones(len(points))])  # (N, 3)
    transformed = (M @ pts_arr.T).T  # (N, 3)
    return [(float(row[0]), float(row[1])) for row in transformed]


# ============================================================================
# Curve Flattening Helpers (Bezier & Arc)
# ============================================================================

def sample_cubic_bezier(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    num_steps: int = 16
) -> List[Tuple[float, float]]:
    """Evaluates a Cubic Bezier curve at uniform t steps."""
    pts = []
    for i in range(1, num_steps + 1):
        t = i / num_steps
        t2 = t * t
        t3 = t2 * t
        mt = 1.0 - t
        mt2 = mt * mt
        mt3 = mt2 * mt

        x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
        y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
        pts.append((x, y))
    return pts


def sample_quadratic_bezier(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    num_steps: int = 12
) -> List[Tuple[float, float]]:
    """Evaluates a Quadratic Bezier curve at uniform t steps."""
    pts = []
    for i in range(1, num_steps + 1):
        t = i / num_steps
        mt = 1.0 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def sample_ellipse_outline(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    num_steps: int
) -> List[Tuple[float, float]]:
    """Samples a closed ellipse (or circle when rx == ry) outline at uniform angle steps."""
    pts = []
    for i in range(num_steps + 1):
        ang = (i / num_steps) * 2 * math.pi
        pts.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    return pts


def sample_elliptical_arc(
    p0: Tuple[float, float],
    rx: float,
    ry: float,
    phi_deg: float,
    large_arc: bool,
    sweep: bool,
    p1: Tuple[float, float],
    num_steps: int = 16
) -> List[Tuple[float, float]]:
    """Converts SVG endpoint arc parameterization to center parameterization and samples points."""
    x1, y1 = p0
    x2, y2 = p1

    if x1 == x2 and y1 == y2:
        return []

    rx = abs(rx)
    ry = abs(ry)
    if rx == 0 or ry == 0:
        return [(x2, y2)]

    phi = math.radians(phi_deg % 360.0)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    # Step 1: Compute (x1', y1')
    dx = (x1 - x2) / 2.0
    dy = (y1 - y2) / 2.0
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy

    # Correct radii if needed
    prx = rx * rx
    pry = ry * ry
    px1p = x1p * x1p
    py1p = y1p * y1p

    radii_check = px1p / prx + py1p / pry
    if radii_check > 1.0:
        rx *= math.sqrt(radii_check)
        ry *= math.sqrt(radii_check)
        prx = rx * rx
        pry = ry * ry

    # Step 2: Compute (cx', cy')
    sign = -1.0 if large_arc == sweep else 1.0
    sq = max(0.0, (prx * pry - prx * py1p - pry * px1p) / (prx * py1p + pry * px1p))
    coef = sign * math.sqrt(sq)
    cxp = coef * ((rx * y1p) / ry)
    cyp = coef * (-(ry * x1p) / rx)

    # Step 3: Compute (cx, cy)
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2.0
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2.0

    # Step 4: Compute angles theta1 and delta_theta
    def vector_angle(u, v):
        dot = u[0] * v[0] + u[1] * v[1]
        len_uv = math.sqrt(u[0]**2 + u[1]**2) * math.sqrt(v[0]**2 + v[1]**2)
        if len_uv == 0:
            return 0.0
        val = max(-1.0, min(1.0, dot / len_uv))
        ang = math.acos(val)
        if (u[0] * v[1] - u[1] * v[0]) < 0:
            ang = -ang
        return ang

    v1 = ((x1p - cxp) / rx, (y1p - cyp) / ry)
    v2 = ((-x1p - cxp) / rx, (-y1p - cyp) / ry)

    theta1 = vector_angle((1.0, 0.0), v1)
    d_theta = vector_angle(v1, v2)

    if not sweep and d_theta > 0:
        d_theta -= 2 * math.pi
    elif sweep and d_theta < 0:
        d_theta += 2 * math.pi

    pts = []
    for i in range(1, num_steps + 1):
        th = theta1 + (i / num_steps) * d_theta
        cos_th = math.cos(th)
        sin_th = math.sin(th)
        x = cos_phi * (rx * cos_th) - sin_phi * (ry * sin_th) + cx
        y = sin_phi * (rx * cos_th) + cos_phi * (ry * sin_th) + cy
        pts.append((x, y))

    return pts


# ============================================================================
# Path Parser
# ============================================================================

def parse_svg_path(d_str: str, tolerance_steps: int = 16) -> List[List[Tuple[float, float]]]:
    """
    Parses SVG path d attribute string into subpaths (lists of 2D points).
    Handles M, L, H, V, C, S, Q, T, A, Z (both uppercase absolute and lowercase relative).
    """
    if not d_str:
        return []

    # Tokenize path commands and numbers
    tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][-+]?\d+)?)', d_str)
    raw_list = []
    for cmd, num in tokens:
        if cmd:
            raw_list.append(cmd)
        elif num:
            raw_list.append(float(num))

    subpaths: List[List[Tuple[float, float]]] = []
    current_path: List[Tuple[float, float]] = []

    curr_x, curr_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    last_cubic_cp: Optional[Tuple[float, float]] = None
    last_quad_cp: Optional[Tuple[float, float]] = None

    valid_commands = {'M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'Z'}
    if not raw_list:
        return []

    if not isinstance(raw_list[0], str) or raw_list[0].upper() not in valid_commands:
        raise ValueError(f"Malformed SVG path: must start with valid command (got '{raw_list[0]}')")

    idx = 0
    num_tokens = len(raw_list)

    cmd = ''
    while idx < num_tokens:
        tok = raw_list[idx]
        if isinstance(tok, str):
            if tok.upper() not in valid_commands:
                raise ValueError(f"Unknown or unsupported SVG path command: '{tok}'")
            cmd = tok
            idx += 1

        is_rel = cmd.islower()
        c = cmd.upper()

        def abs_pt(dx: float, dy: float) -> Tuple[float, float]:
            """Resolves a command parameter pair against the relative/absolute mode."""
            return (dx + (curr_x if is_rel else 0.0), dy + (curr_y if is_rel else 0.0))

        def get_args(count: int) -> List[float]:
            nonlocal idx
            if idx + count > num_tokens:
                raise ValueError(f"Malformed SVG path: command '{cmd}' expects {count} parameters, but only {num_tokens - idx} remain")
            args = []
            for k in range(count):
                val = raw_list[idx + k]
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Malformed SVG path: command '{cmd}' expects numeric parameter, got '{val}'")
                args.append(float(val))
            idx += count
            return args

        if c == 'M':
            a = get_args(2)
            x, y = abs_pt(a[0], a[1])
            curr_x, curr_y = x, y
            start_x, start_y = x, y

            if current_path:
                subpaths.append(current_path)
            current_path = [(curr_x, curr_y)]
            cmd = 'l' if is_rel else 'L'

        elif c == 'L':
            a = get_args(2)
            x, y = abs_pt(a[0], a[1])
            curr_x, curr_y = x, y
            current_path.append((curr_x, curr_y))

        elif c == 'H':
            a = get_args(1)
            x = a[0] + (curr_x if is_rel else 0.0)
            curr_x = x
            current_path.append((curr_x, curr_y))

        elif c == 'V':
            a = get_args(1)
            y = a[0] + (curr_y if is_rel else 0.0)
            curr_y = y
            current_path.append((curr_x, curr_y))

        elif c == 'C':
            a = get_args(6)
            x1, y1 = abs_pt(a[0], a[1])
            x2, y2 = abs_pt(a[2], a[3])
            x, y = abs_pt(a[4], a[5])

            pts = sample_cubic_bezier((curr_x, curr_y), (x1, y1), (x2, y2), (x, y), num_steps=tolerance_steps)
            current_path.extend(pts)
            last_cubic_cp = (x2, y2)
            curr_x, curr_y = x, y

        elif c == 'S':
            if last_cubic_cp:
                x1 = 2 * curr_x - last_cubic_cp[0]
                y1 = 2 * curr_y - last_cubic_cp[1]
            else:
                x1, y1 = curr_x, curr_y

            a = get_args(4)
            x2, y2 = abs_pt(a[0], a[1])
            x, y = abs_pt(a[2], a[3])

            pts = sample_cubic_bezier((curr_x, curr_y), (x1, y1), (x2, y2), (x, y), num_steps=tolerance_steps)
            current_path.extend(pts)
            last_cubic_cp = (x2, y2)
            curr_x, curr_y = x, y

        elif c == 'Q':
            a = get_args(4)
            x1, y1 = abs_pt(a[0], a[1])
            x, y = abs_pt(a[2], a[3])

            pts = sample_quadratic_bezier((curr_x, curr_y), (x1, y1), (x, y), num_steps=tolerance_steps)
            current_path.extend(pts)
            last_quad_cp = (x1, y1)
            curr_x, curr_y = x, y

        elif c == 'T':
            if last_quad_cp:
                x1 = 2 * curr_x - last_quad_cp[0]
                y1 = 2 * curr_y - last_quad_cp[1]
            else:
                x1, y1 = curr_x, curr_y

            a = get_args(2)
            x, y = abs_pt(a[0], a[1])

            pts = sample_quadratic_bezier((curr_x, curr_y), (x1, y1), (x, y), num_steps=tolerance_steps)
            current_path.extend(pts)
            last_quad_cp = (x1, y1)
            curr_x, curr_y = x, y

        elif c == 'A':
            a = get_args(7)
            rx, ry, phi = a[0], a[1], a[2]
            large_arc = bool(a[3])
            sweep = bool(a[4])
            x, y = abs_pt(a[5], a[6])

            pts = sample_elliptical_arc((curr_x, curr_y), rx, ry, phi, large_arc, sweep, (x, y), num_steps=tolerance_steps)
            current_path.extend(pts)
            curr_x, curr_y = x, y

        elif c == 'Z':
            curr_x, curr_y = start_x, start_y
            if current_path and current_path[0] != current_path[-1]:
                current_path.append((start_x, start_y))

        if c not in ('C', 'S'):
            last_cubic_cp = None
        if c not in ('Q', 'T'):
            last_quad_cp = None

    if current_path:
        subpaths.append(current_path)

    return subpaths


# ============================================================================
# Element Shape Parser & Geometry Factory
# ============================================================================

class ParsedGeometry:
    """Container for a resolved geometry in pure segment representation.

    v1.2.0: the engine measures line geometry directly (geometric-contact
    semantics), so a geometry is its list of transformed subpaths. ``bounds``
    is computed from the vertices with NumPy — no external geometry library.
    """
    def __init__(
        self,
        geom_type: str,  # 'fill' or 'stroke'
        segments: List[Tuple[float, float, float, float]],
        stroke_width: float = 0.0,
        tag: str = 'path'
    ):
        self.geom_type = geom_type
        self.segments = segments
        self.stroke_width = stroke_width
        self.tag = tag
        self.bounds = _segments_bounds(segments)

    @property
    def area(self) -> float:
        """Total signed-magnitude ring area of the geometry's closed subpaths.

        Filled shapes resolve to the sum of |shoelace areas| of their closed
        subpaths (hole deductions under evenodd/nonzero are NOT applied —
        geometric-contact measures the drawn boundary set, and the boundary of
        a hole is drawn exactly like the boundary of a solid).
        """
        return _shoelace_area_of_segments(self.segments)

    def is_valid(self) -> bool:
        """True when every segment has finite endpoints and positive length."""
        return all(
            math.isfinite(x0) and math.isfinite(y0) and math.isfinite(x1) and math.isfinite(y1)
            and (x0, y0) != (x1, y1)
            for x0, y0, x1, y1 in self.segments
        )


def _segments_bounds(segments: Iterable[Tuple[float, float, float, float]]) -> Tuple[float, float, float, float]:
    """Axis-aligned bounding box (xmin, ymin, xmax, ymax) of a segment list."""
    if not segments:
        return (0.0, 0.0, 0.0, 0.0)
    arr = np.asarray(list(segments), dtype=np.float64).reshape(-1, 4)
    xs = np.concatenate([arr[:, 0], arr[:, 2]])
    ys = np.concatenate([arr[:, 1], arr[:, 3]])
    finite_x = xs[np.isfinite(xs)]
    finite_y = ys[np.isfinite(ys)]
    if finite_x.size == 0 or finite_y.size == 0:
        return (0.0, 0.0, 0.0, 0.0)
    return (float(finite_x.min()), float(finite_y.min()), float(finite_x.max()), float(finite_y.max()))


def _shoelace_area_of_segments(segments: List[Tuple[float, float, float, float]]) -> float:
    """Sum of |signed shoelace areas| over closed rings embedded in a segment list.

    Chains consecutive segments whose endpoints coincide; each closed chain
    (first point == last point) is treated as one ring. Open chains contribute 0
    (a stroked open path has no interior area).
    """
    if not segments:
        return 0.0
    # Build adjacency: endpoint -> list of (segment index, which_end).
    # Endpoints are clustered with a tolerance so curve-sampled closures
    # (float drift ~1e-16) still chain.
    from collections import defaultdict
    adjacency: dict = defaultdict(list)
    cluster_ids: Dict[Tuple[float, float], Tuple[float, float]] = {}
    clusters: List[Tuple[float, float]] = []

    def _cluster_key(pt: Tuple[float, float]) -> Tuple[float, float]:
        for c in clusters:
            if _points_coincide(pt, c):
                cluster_ids[pt] = c
                return c
        clusters.append(pt)
        cluster_ids[pt] = pt
        return pt

    for i, (x0, y0, x1, y1) in enumerate(segments):
        k0 = _cluster_key((x0, y0))
        k1 = _cluster_key((x1, y1))
        adjacency[k0].append((i, 0))
        adjacency[k1].append((i, 1))

    visited = [False] * len(segments)
    total_abs_area = 0.0

    for start in range(len(segments)):
        if visited[start]:
            continue
        # Walk the chain in both directions until it closes or ends
        chain_points: List[Tuple[float, float]] = []
        seg_idx = start
        # Orientation pass: collect points following segment direction
        x0, y0, x1, y1 = segments[seg_idx]
        chain_points = [(x0, y0), (x1, y1)]
        visited[seg_idx] = True
        # Extend forward from (x1, y1)
        while True:
            tail_key = _cluster_key(chain_points[-1])
            nexts = [(i, e) for (i, e) in adjacency[tail_key] if not visited[i]]
            if not nexts:
                break
            i, e = nexts[0]
            visited[i] = True
            sx0, sy0, sx1, sy1 = segments[i]
            if e == 0:  # tail matches this segment's start
                chain_points.append((sx1, sy1))
            else:       # tail matches this segment's end; traverse backwards
                chain_points.append((sx0, sy0))
        # Extend backward from (x0, y0)
        while True:
            head_key = _cluster_key(chain_points[0])
            prevs = [(i, e) for (i, e) in adjacency[head_key] if not visited[i]]
            if not prevs:
                break
            i, e = prevs[0]
            visited[i] = True
            sx0, sy0, sx1, sy1 = segments[i]
            if e == 0:  # head matches this segment's start; prepend its far end
                chain_points.insert(0, (sx1, sy1))
            else:       # head matches this segment's end; prepend its start
                chain_points.insert(0, (sx0, sy0))
        if len(chain_points) >= 4 and _points_coincide(chain_points[0], chain_points[-1]):
            pts_arr = np.asarray(chain_points, dtype=np.float64)
            xs_, ys_ = pts_arr[:, 0], pts_arr[:, 1]
            signed2 = float(np.dot(xs_[:-1], ys_[1:]) - np.dot(xs_[1:], ys_[:-1]))
            total_abs_area += abs(signed2) / 2.0
    return total_abs_area


def _points_coincide(p: Tuple[float, float], q: Tuple[float, float], abs_tol: float = 1e-9) -> bool:
    """Exact-or-near endpoint equality (curve sampling closure has ~1e-16 float drift)."""
    return abs(p[0] - q[0]) <= abs_tol and abs(p[1] - q[1]) <= abs_tol


def extract_node_geometries(
    node: SVGNode,
    transform_stack: List[str],
    tolerance: str = 'high'
) -> List[ParsedGeometry]:
    """
    Parses an SVGNode into one or more transformed ParsedGeometry objects (fill & stroke).

    v1.2.0 semantics: a geometry is the set of transformed centerline segments of
    the rendered element. For filled shapes the fill boundary segments are
    emitted (geometric-contact measures the contacted line geometry: every
    boundary the renderer draws — outer contour and hole contours alike).
    """
    num_steps = 24 if tolerance == 'high' else (12 if tolerance == 'medium' else 6)

    # Build cumulative transform matrix
    M = np.eye(3, dtype=np.float64)
    for tf_str in transform_stack:
        M = M @ parse_transform_string(tf_str)

    subpaths: List[List[Tuple[float, float]]] = []

    tag = node.tag
    attr = node.attribs

    if tag == 'path':
        d = attr.get('d', '')
        subpaths = parse_svg_path(d, tolerance_steps=num_steps)

    elif tag == 'rect':
        x = float(attr.get('x', 0))
        y = float(attr.get('y', 0))
        w = float(attr.get('width', 0))
        h = float(attr.get('height', 0))
        if w > 0 and h > 0:
            subpaths = [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]

    elif tag == 'circle':
        cx = float(attr.get('cx', 0))
        cy = float(attr.get('cy', 0))
        r = float(attr.get('r', 0))
        if r > 0:
            subpaths = [sample_ellipse_outline(cx, cy, r, r, num_steps)]

    elif tag == 'ellipse':
        cx = float(attr.get('cx', 0))
        cy = float(attr.get('cy', 0))
        rx = float(attr.get('rx', 0))
        ry = float(attr.get('ry', 0))
        if rx > 0 and ry > 0:
            subpaths = [sample_ellipse_outline(cx, cy, rx, ry, num_steps)]

    elif tag == 'line':
        x1 = float(attr.get('x1', 0))
        y1 = float(attr.get('y1', 0))
        x2 = float(attr.get('x2', 0))
        y2 = float(attr.get('y2', 0))
        subpaths = [[(x1, y1), (x2, y2)]]

    elif tag in ('polyline', 'polygon'):
        pts_str = attr.get('points', '')
        raw_num = [float(p) for p in re.split(r'[\s,]+', pts_str.strip()) if p]
        pts = [(raw_num[i], raw_num[i+1]) for i in range(0, len(raw_num)-1, 2)]
        if tag == 'polygon' and pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        if len(pts) >= 2:
            subpaths = [pts]

    geoms: List[ParsedGeometry] = []
    if not subpaths:
        return geoms

    # Transform all subpaths to world coordinates
    transformed_subpaths = [transform_points(pts, M) for pts in subpaths if len(pts) >= 2]

    # Calculate effective stroke width transformed scale factor
    det_m = abs(M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0])
    scale_factor = math.sqrt(det_m) if det_m > 0 else 1.0
    effective_stroke_width = node.stroke_width * scale_factor

    def _to_segments(subs: List[List[Tuple[float, float]]]) -> List[Tuple[float, float, float, float]]:
        out: List[Tuple[float, float, float, float]] = []
        for pts in subs:
            for k in range(len(pts) - 1):
                p0, p1 = pts[k], pts[k + 1]
                if math.isfinite(p0[0]) and math.isfinite(p0[1]) and math.isfinite(p1[0]) and math.isfinite(p1[1]):
                    if (p0[0], p0[1]) != (p1[0], p1[1]):
                        out.append((float(p0[0]), float(p0[1]), float(p1[0]), float(p1[1])))
        return out

    # Fill geometry: the boundary segments of the filled shape (all subpath
    # rings — outer contours and hole contours — are drawn boundaries).
    if node.has_fill:
        fill_segments = _to_segments(transformed_subpaths)
        if fill_segments:
            geoms.append(ParsedGeometry('fill', fill_segments, tag=tag))

    # Stroke geometry: the centerline segments of the stroked outline.
    if node.has_stroke:
        stroke_segments = _to_segments(transformed_subpaths)
        if stroke_segments:
            geoms.append(ParsedGeometry('stroke', stroke_segments,
                                        stroke_width=effective_stroke_width, tag=tag))

    return geoms
