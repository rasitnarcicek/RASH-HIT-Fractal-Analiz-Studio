"""Stroke modeli denetimi: mevcut distance<=hw testi vs gercek SVG kaplama.
Proje dosyalarina DOKUNULMAZ. Salt okuma + bagimsiz olcum.
"""
from shapely.geometry import LineString, box
from shapely.ops import unary_union
import math

def koch(p, q, depth):
    if depth == 0:
        return [p]
    (x1,y1),(x2,y2) = p,q
    dx,dy = (x2-x1)/3.0, (y2-y1)/3.0
    a = (x1+dx, y1+dy); b = (x1+2*dx, y1+2*dy)
    ang = math.atan2(dy,dx) - math.pi/3
    L = math.hypot(dx,dy)
    c = (a[0]+L*math.cos(ang), a[1]+L*math.sin(ang))
    return koch(p,a,depth-1)+koch(a,c,depth-1)+koch(c,b,depth-1)+koch(b,q,depth-1)

pts = koch((0.0,0.0),(1000.0,0.0),4) + [(1000.0,0.0)]
line = LineString(pts)
print(f"Koch L4: {len(pts)} nokta, uzunluk {line.length:.1f}")
print(f"Kose sayisi: {len(pts)-2}  (her kosede 60 derece donus)\n")

print("MODEL KARSILASTIRMASI — ayni geometri, ayni kalinlik, farkli birlesim/uc modeli")
print("-"*78)
print(f"{'stroke':>8} {'ROUND alan':>14} {'MITER alan':>14} {'fark %':>9} {'BUTT-vs-ROUND uc':>18}")
print("-"*78)
for w in [0.25, 1.0, 3.0, 8.0]:
    hw = w/2.0
    # ROUND join+cap  ==  distance(line, X) <= hw  (mevcut motorun yaptigi sey)
    r = line.buffer(hw, cap_style=1, join_style=1, resolution=32)
    # MITER join + BUTT cap == SVG VARSAYILANI
    m = line.buffer(hw, cap_style=2, join_style=2, mitre_limit=4.0, resolution=32)
    d = (m.area - r.area)/r.area*100
    # sadece uc farki: yuvarlak uc iki uctan hw yaricapli yarim daire ekler
    cap_extra = math.pi*hw*hw
    print(f"{w:>8.2f} {r.area:>14.2f} {m.area:>14.2f} {d:>8.2f}% {cap_extra:>17.3f}")

print("\nNOT: ROUND sutunu = motorun SU AN olctugu sey.")
print("     MITER sutunu = bir tarayicinin/Illustrator'in EKRANDA cizdigi sey.")

# Kutu sayimi seviyesinde etkisi
print("\n\nKUTU SAYIMI FARKI (ayni izgara, iki model)")
print("-"*78)
minx,miny,maxx,maxy = line.bounds
side = max(maxx-minx, maxy-miny)
print(f"{'stroke':>8} {'seviye':>7} {'N round':>10} {'N miter':>10} {'fark':>8} {'fark %':>8}")
for w in [1.0, 3.0]:
    hw = w/2.0
    m = line.buffer(hw, cap_style=2, join_style=2, mitre_limit=4.0, resolution=16)
    for lvl in [5,6,7]:
        k = 2**lvl
        cs = side/k
        nr = nm = 0
        for i in range(k):
            for j in range(k):
                c = box(minx+i*cs, miny+j*cs, minx+(i+1)*cs, miny+(j+1)*cs)
                if line.distance(c) <= hw: nr += 1      # MEVCUT MOTOR
                if m.intersects(c):        nm += 1      # GERCEK SVG
        print(f"{w:>8.2f} {'L%02d'%lvl:>7} {nr:>10} {nm:>10} {nm-nr:>8} {(nm-nr)/nr*100:>7.2f}%")
