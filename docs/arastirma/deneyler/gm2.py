
import sys; sys.path.insert(0,r"C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio")
from backend.svg_loader import load_svg_geometries
import inspect
r = load_svg_geometries(r"C:\Users\RaşitNarçiçek\rakip_analiz\shift_test\koch_t100.svg")
print("donen tip:", type(r))
geoms = r if isinstance(r,list) else getattr(r,"geometries",r)
try: n=len(geoms)
except: n="?"
print("geom sayisi:", n)
g = geoms[0] if isinstance(geoms,list) and geoms else None
print("eleman tipi:", type(g))
print("alanlar:", [a for a in dir(g) if not a.startswith("_")][:30])
so = getattr(g,"shapely_obj",None)
print("shapely_obj:", type(so), "empty=", (so.is_empty if so is not None else None))
print("bounds:", so.bounds if so is not None and not so.is_empty else None)
