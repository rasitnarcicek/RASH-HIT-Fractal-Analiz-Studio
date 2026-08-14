import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from shapely.geometry import LineString
from backend.grid_planner import create_grid_plan
from backend.intersection_hierarchical import compute_hierarchical_box_counting
from backend.regression import compute_loglog_regression

class MockGeometry:
    def __init__(self, shapely_obj, geom_type):
        self.shapely_obj = shapely_obj
        self.geom_type = geom_type
        self.stroke_width = 0.0

def generate_koch_curve(order=4):
    points = [(0, 0), (1, 0)]
    for _ in range(order):
        new_points = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]
            v = (p2[0]-p1[0], p2[1]-p1[1])
            v1 = (p1[0] + v[0]/3, p1[1] + v[1]/3)
            v3 = (p1[0] + 2*v[0]/3, p1[1] + 2*v[1]/3)
            angle = np.deg2rad(60)
            v_tip = (v[0]/3, v[1]/3)
            v_tip_rot = (v_tip[0]*np.cos(angle) - v_tip[1]*np.sin(angle),
                         v_tip[0]*np.sin(angle) + v_tip[1]*np.cos(angle))
            v2 = (v1[0] + v_tip_rot[0], v1[1] + v_tip_rot[1])
            new_points.extend([p1, v1, v2, v3])
        new_points.append(points[-1])
        points = new_points
    return LineString(points)

geom = generate_koch_curve(order=4)
minx, miny, maxx, maxy = geom.bounds
vw, vh = (maxx - minx), (maxy - miny)
vw = max(vw, 1.0)
vh = max(vh, 1.0)
grid_plan = create_grid_plan(
    svg_viewbox=(minx, miny, vw, vh),
    svg_width=vw,
    svg_height=vh,
    manual_grids=[(8, 8), (16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512)],
    num_levels=7
)
geoms = [MockGeometry(geom, 'stroke')]
lvl_models, _ = compute_hierarchical_box_counting(geoms, vw, vh, grid_plan=grid_plan)

print("Level | Grid | Cell Width | Filled Cells")
for lm in lvl_models:
    print(f"{lm.level} | {lm.grid_label} | {lm.cell_w:.5f} | {lm.filled_cells}")
