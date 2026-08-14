
import sys; sys.path.insert(0,r"C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio")
from backend.grid_planner import create_grid_plan
# A) dogrudan fonksiyon testi: geometry_bounds gecerli, mod square_bbox
p=create_grid_plan(svg_viewbox=(0,0,800,800), svg_width=800, svg_height=800,
                   geometry_bounds=(100.0,227.0,700.0,400.0), num_levels=3, grid_mode="square_bbox")
print("A) square_bbox  bounds=",(p.xmin,p.ymin,p.xmax,p.ymax)," L1 box=",p.levels[0].cell_w)
p2=create_grid_plan(svg_viewbox=(0,0,800,800), svg_width=800, svg_height=800,
                   geometry_bounds=(100.0,227.0,700.0,400.0), num_levels=3, grid_mode="canvas_aspect")
print("B) canvas      bounds=",(p2.xmin,p2.ymin,p2.xmax,p2.ymax)," L1 box=",p2.levels[0].cell_w)

# C) processor icinde geom_bounds gercekten uretiliyor mu?
from backend.svg_loader import *
import backend.svg_loader as sl
print("\nsvg_loader disa acilanlar:", [n for n in dir(sl) if not n.startswith("_")][:25])
