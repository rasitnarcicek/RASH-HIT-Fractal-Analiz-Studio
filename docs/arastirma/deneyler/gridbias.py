
import numpy as np, math
from shapely.geometry import LineString
from shapely.strtree import STRtree
import shapely

def koch(n=5):
    pts=[(0.0,0.0),(1.0,0.0)]
    for _ in range(n):
        new=[pts[0]]
        for a,b in zip(pts,pts[1:]):
            ax,ay=a; bx,by=b; dx=(bx-ax)/3; dy=(by-ay)/3
            p1=(ax+dx,ay+dy); p3=(ax+2*dx,ay+2*dy)
            ang=math.atan2(dy,dx)-math.pi/3
            L=math.hypot(dx,dy)
            p2=(p1[0]+L*math.cos(ang), p1[1]+L*math.sin(ang))
            new += [p1,p2,p3,b]
        pts=new
    return LineString(pts)

g=koch(5)
tree=STRtree([g])
minx,miny,maxx,maxy=g.bounds
W=max(maxx-minx,maxy-miny)*1.05

def count(nb, ox, oy):
    s=W/nb
    x0=minx-W*0.025+(ox-1.0)*s; y0=miny-W*0.025+(oy-1.0)*s
    xs=np.arange(nb+2)*s+x0; ys=np.arange(nb+2)*s+y0
    X,Y=np.meshgrid(xs,ys)
    cells=shapely.box(X.ravel(),Y.ravel(),X.ravel()+s,Y.ravel()+s)
    idx=tree.query(cells)
    ci=idx[0]
    hit=shapely.intersects(cells[ci], g)
    return int(np.unique(ci[hit]).size)

levels=[8,16,32,64,128,256]
offs=[(i/4,j/4) for i in range(4) for j in range(4)]

def D(counts):
    x=np.log([1.0/(W/n) for n in levels]); y=np.log(counts)
    return np.polyfit(x,y,1)[0], np.corrcoef(x,y)[0,1]**2

fixed=[count(n,0,0) for n in levels]
allc={o:[count(n,*o) for n in levels] for o in offs}
mins=[min(allc[o][k] for o in offs) for k in range(len(levels))]
means=[float(np.mean([allc[o][k] for o in offs])) for k in range(len(levels))]

print("GERCEK DEGER: Koch egrisi D = log4/log3 = 1.261860")
print()
print("olcek | sabit | min(16 off) |   ort   | max | yayilma%")
for k,n in enumerate(levels):
    v=[allc[o][k] for o in offs]
    print(f"{n:5d} | {fixed[k]:5d} | {min(v):11d} | {np.mean(v):7.1f} | {max(v):4d} | {100*(max(v)-min(v))/min(v):6.1f}")
print()
for name,c in [("SABIT tek izgara (RASH-HIT bugun)",fixed),("MIN over 16 offset (Fractalyse)",mins),("ORTALAMA 16 offset (QGIS ikilisi)",means)]:
    d,r2=D(c); print(f"{name:36s} D={d:.6f}  hata={abs(d-1.26186):.6f}  R2={r2:.6f}")

ds=[D(allc[o])[0] for o in offs]
print()
print("Sadece izgara ORIJINI degistirilerek elde edilen D:")
print(f"  min={min(ds):.6f}  max={max(ds):.6f}  yayilma={max(ds)-min(ds):.6f}  std={np.std(ds):.6f}")
