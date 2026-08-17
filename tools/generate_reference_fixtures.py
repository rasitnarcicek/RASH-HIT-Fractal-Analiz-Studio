# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek
"""Generate the Stage 3.4 reference SVG fixtures.

These are small, deterministic, single-behaviour SVGs used to freeze CPU
reference results (L1-L10) for later GPU comparison. They intentionally avoid
any license-bearing or private geometry: every shape is synthetic and minimal.

Run:  .venv\Scripts\python.exe tools/generate_reference_fixtures.py
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "svg_reference"

# Each entry: (filename, svg_text)
FIXTURES = {
    "empty.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"></svg>
""",
    "horizontal_line.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <line x1="10" y1="50" x2="90" y2="50"/>
</svg>
""",
    "vertical_line.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <line x1="50" y1="10" x2="50" y2="90"/>
</svg>
""",
    "diagonal_line.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <line x1="10" y1="10" x2="90" y2="90"/>
</svg>
""",
    "boundary_aligned_line.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <line x1="0" y1="50" x2="100" y2="50"/>
</svg>
""",
    "corner_touch_line.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <line x1="0" y1="0" x2="50" y2="50"/>
</svg>
""",
    "open_polyline.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <polyline points="10,90 30,30 50,70 70,20 90,60" fill="none" stroke="black"/>
</svg>
""",
    "filled_rectangle.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="20" y="20" width="60" height="40" fill="black"/>
</svg>
""",
    "stroked_rectangle.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="20" y="20" width="60" height="40" fill="none" stroke="black" stroke-width="4"/>
</svg>
""",
    "filled_circle.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="30" fill="black"/>
</svg>
""",
    "filled_ellipse.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <ellipse cx="50" cy="50" rx="35" ry="20" fill="black"/>
</svg>
""",
    "simple_polygon.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <polygon points="50,10 90,90 10,90" fill="black"/>
</svg>
""",
    "polygon_with_hole.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path fill-rule="evenodd" d="M10,10 H90 V90 H10 Z M30,30 H70 V70 H30 Z"/>
</svg>
""",
    "evenodd_path.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path fill-rule="evenodd" d="M20,20 H80 V80 H20 Z M40,40 H60 V60 H40 Z"/>
</svg>
""",
    "nonzero_path.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path fill-rule="nonzero" d="M20,20 H80 V80 H20 Z M40,40 H60 V60 H40 Z"/>
</svg>
""",
    "transformed_group.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <g transform="translate(20,20) rotate(15)">
    <rect x="0" y="0" width="40" height="30" fill="black"/>
  </g>
</svg>
""",
    "cubic_bezier.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M10,90 C10,10 90,10 90,90" fill="none" stroke="black" stroke-width="2"/>
</svg>
""",
    "quadratic_bezier.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M10,90 Q50,10 90,90" fill="none" stroke="black" stroke-width="2"/>
</svg>
""",
    "arc.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M10,80 A40,40 0 0 1 90,80" fill="none" stroke="black" stroke-width="2"/>
</svg>
""",
    "mixed_fill_and_stroke.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="15" y="15" width="30" height="30" fill="black"/>
  <circle cx="75" cy="75" r="15" fill="none" stroke="black" stroke-width="3"/>
  <line x1="15" y1="60" x2="85" y2="60" stroke="black" stroke-width="2"/>
</svg>
""",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in FIXTURES.items():
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"  wrote {name}")
    print(f"\n{len(FIXTURES)} reference fixtures in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
