
import sys; sys.path.insert(0,r"C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio")
from backend.svg_loader import load_svg_geometries
from shapely.ops import unary_union
a,b,c = load_svg_geometries(r"C:\Users\RaşitNarçiçek\rakip_analiz\shift_test\koch_t100.svg")
for i,x in enumerate((a,b,c)):
    print(i, type(x), (len(x) if hasattr(x,"__len__") else x))
geoms = next(x for x in (a,b,c) if isinstance(x,list) and x and hasattr(x[0],"shapely_obj"))
print("geoms:", len(geoms))
gb = unary_union([g.shapely_obj for g in geoms if g.shapely_obj and not g.shapely_obj.is_empty]).bounds
print("GEOMETRY BOUNDS:", gb)
print("genislik/yukseklik:", gb[2]-gb[0], gb[3]-gb[1])
