"""Izgara yanliligi (grid bias) testi — FractDim'in yaptigi acisal/kaydirmali
taramayi RASH-HIT yapmiyor. Ne kadar onemli? Bagimsiz olarak olculuyor.
Proje dosyalarina DOKUNULMAZ.
"""
import math
import numpy as np
from shapely.geometry import LineString, box, Polygon
from shapely import affinity

def koch(p,q,d):
    if d==0: return [p]
    (x1,y1),(x2,y2)=p,q
    dx,dy=(x2-x1)/3.0,(y2-y1)/3.0
    a=(x1+dx,y1+dy); b=(x1+2*dx,y1+2*dy)
    ang=math.atan2(dy,dx)-math.pi/3; L=math.hypot(dx,dy)
    c=(a[0]+L*math.cos(ang),a[1]+L*math.sin(ang))
    return koch(p,a,d-1)+koch(a,c,d-1)+koch(c,b,d-1)+koch(b,q,d-1)

def sierpinski(depth):
    tris=[[(0,0),(1000,0),(500,866.03)]]
    for _ in range(depth):
        nt=[]
        for (A,B,C) in tris:
            m=lambda P,Q:((P[0]+Q[0])/2,(P[1]+Q[1])/2)
            AB,BC,CA=m(A,B),m(B,C),m(C,A)
            nt += [[A,AB,CA],[AB,B,BC],[CA,BC,C]]
        tris=nt
    from shapely.ops import unary_union
    return unary_union([Polygon(t) for t in tris])

def db(geom, hw, levels=8, dx=0.0, dy=0.0, ang=0.0):
    g = geom
    if ang: g = affinity.rotate(g, ang, origin='center')
    minx,miny,maxx,maxy = g.bounds
    side = max(maxx-minx, maxy-miny)*1.02
    cx,cy=(minx+maxx)/2,(miny+maxy)/2
    ox,oy = cx-side/2 + dx*side, cy-side/2 + dy*side
    xs,ys=[],[]
    for lvl in range(3, 3+levels):
        k=2**lvl; cs=side/k
        if cs < 1e-9: break
        n=0
        # kaba on-eleme: bbox kesisimi
        for i in range(k):
            x0=ox+i*cs; x1=x0+cs
            if x1 < g.bounds[0] or x0 > g.bounds[2]: continue
            for j in range(k):
                y0=oy+j*cs; y1=y0+cs
                if y1 < g.bounds[1] or y0 > g.bounds[3]: continue
                c=box(x0,y0,x1,y1)
                if hw>0:
                    if g.distance(c)<=hw: n+=1
                else:
                    if g.intersects(c): n+=1
        if n>0:
            xs.append(math.log(1.0/cs)); ys.append(math.log(n))
    if len(xs)<3: return float('nan'), float('nan')
    A=np.polyfit(xs,ys,1); pred=np.polyval(A,xs)
    ss_res=float(np.sum((np.array(ys)-pred)**2)); ss_tot=float(np.sum((np.array(ys)-np.mean(ys))**2))
    return float(A[0]), 1-ss_res/ss_tot if ss_tot>0 else float('nan')

print("="*72)
print("IZGARA YANLILIGI TESTI — ayni sekil, ayni seviye, kaydirilan/dondurulen izgara")
print("="*72)

pts = koch((0.0,0.0),(1000.0,0.0),5)+[(1000.0,0.0)]
koch_line = LineString(pts)

for label, geom, hw, theo, LV in [
    ("Koch L5 (stroke 0.25)", koch_line, 0.125, 1.261859, 7),
    ("Sierpinski L5 (dolgu)", sierpinski(5), 0.0,  1.584963, 7),
]:
    print(f"\n--- {label} · teorik D = {theo:.6f} ---")
    print(f"{'kosul':>22} {'Db':>9} {'hata %':>9} {'R2':>8}")
    res=[]
    for name,dx,dy,ang in [("referans (0,0,0deg)",0,0,0),
                           ("kaydir x +0.25 hucre",0.25/2**7,0,0),
                           ("kaydir x,y +0.5 hucre",0.5/2**7,0.5/2**7,0),
                           ("dondur 15 derece",0,0,15),
                           ("dondur 30 derece",0,0,30),
                           ("dondur 45 derece",0,0,45)]:
        d,r2 = db(geom,hw,levels=LV,dx=dx,dy=dy,ang=ang)
        res.append(d)
        print(f"{name:>22} {d:>9.4f} {(d-theo)/theo*100:>8.2f}% {r2:>8.4f}")
    arr=np.array([r for r in res if not math.isnan(r)])
    print(f"{'YAYILIM (max-min)':>22} {arr.max()-arr.min():>9.4f}   std={arr.std():.4f}")
