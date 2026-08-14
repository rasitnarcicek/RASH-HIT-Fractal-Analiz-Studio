import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.geometry_engine import extract_node_geometries, parse_svg_path
from backend.svg_loader import SVGNode
import inspect
print("SIGNATURE:", inspect.signature(extract_node_geometries))

d_same = "M0,0 L100,0 L100,100 L0,100 Z M25,25 L75,25 L75,75 L25,75 Z"      # ayni yon (CW,CW)
d_opp  = "M0,0 L100,0 L100,100 L0,100 Z M25,25 L25,75 L75,75 L75,25 Z"      # ters yon (CW,CCW)

for name, d in [("AYNI YON (nonzero=10000, evenodd=7500)", d_same),
                ("TERS YON (nonzero=7500,  evenodd=7500)", d_opp)]:
    node = SVGNode("path", {"d": d}, {"fill": "black", "stroke": "none"}, "")
    try:
        geoms = extract_node_geometries(node)
    except TypeError:
        import numpy as np
        geoms = extract_node_geometries(node, np.identity(3))
    for g in geoms:
        print("  %-42s tip=%-6s alan=%.1f" % (name, g.geom_type, g.geom.area))

print()
print("=== BEZIER DUZLESTIRME: sabit mi adaptif mi? ===")
# Cok buyuk bir yay: 24 adim yeterli mi?
big = "M0,0 C0,1000 1000,1000 1000,0"
small = "M0,0 C0,1 1,1 1,0"
for lbl, dd in [("buyuk egri (1000 birim)", big), ("kucuk egri (1 birim)", small)]:
    for steps in (6, 12, 24):
        sp = parse_svg_path(dd, tolerance_steps=steps)
        n = sum(len(s) for s in sp)
        print("  %-24s tolerance_steps=%-3d -> uretilen nokta = %d" % (lbl, steps, n))
