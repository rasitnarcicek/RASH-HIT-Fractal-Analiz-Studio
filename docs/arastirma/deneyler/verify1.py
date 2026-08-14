import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.svg_loader import parse_length

print("=== parse_length BIRIM TESTI ===")
for v in ["10px","12pt","1em","1rem","2rem","10.5mm","5cm","1in","2pc","50%","3","abc"]:
    print("  %-8s -> %s" % (repr(v), parse_length(v, default=-999.0)))

print()
print("=== FILL RULE TESTI (ic ice 2 kare) ===")
from backend.geometry_engine import build_geometry_from_node
from backend.svg_loader import SVGNode
# outer 0..100, inner 25..75 ayni yonde (nonzero -> dolu kare, evenodd -> delik)
d = "M0,0 L100,0 L100,100 L0,100 Z M25,25 L75,25 L75,75 L25,75 Z"
node = SVGNode("path", {"d": d}, {"fill": "black", "stroke": "none"}, "")
geoms = build_geometry_from_node(node)
for g in geoms:
    print("  tip=%s alan=%.1f (nonzero beklenen=10000, evenodd beklenen=7500)" % (g.kind if hasattr(g,'kind') else g.geom_type, g.geom.area))

print()
print("=== RashHitEngine VARSAYILANLARI ===")
from backend.output_profiles import OutputProfile, get_profile
pr = get_profile("lean")
for f in ["max_excel_cell_map_level","disable_raw_cell_indices_after_level",
          "force_svg_rle_after_level","summary_only_after_level","svg_only_after_level"]:
    print("  %-38s = %s" % (f, getattr(pr, f, "YOK")))

print()
print("=== confidence.py AGIRLIKLARI ===")
import inspect, backend.confidence as C
src = inspect.getsource(C)
for line in src.splitlines():
    if any(k in line.lower() for k in ["weight","0.4","0.3","0.2","r2","r_squared"]):
        print("  " + line.strip()[:110])
