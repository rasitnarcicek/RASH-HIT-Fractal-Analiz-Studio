import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 1) BEZIER DUZLESTIRME HATASI (sarkma/sagitta) vs L-seviye hucre boyutu ===")
from backend.geometry_engine import parse_svg_path
from shapely.geometry import LineString
# 800 birimlik canvasta ceyrek daire yayina yakin kubik bezier
K = 0.5522847498
R = 400.0
d = "M0,%f C%f,%f %f,0 %f,0" % (R, K*R, R, R-K*R, R)
for steps in (6,12,24):
    pts = parse_svg_path(d, tolerance_steps=steps)[0]
    # gercek daire yayina en buyuk sapma
    worst = 0.0
    ls = LineString(pts)
    for i in range(len(pts)-1):
        ax,ay = pts[i]; bx,by = pts[i+1]
        mx,my = (ax+bx)/2.0,(ay+by)/2.0
        r = math.hypot(mx,my)
        worst = max(worst, abs(R-r))
    print("  steps=%-3d kiris sarkmasi(max) = %.4f birim" % (steps, worst))
print("  --- 800 birimlik analiz kutusunda hucre boyutlari ---")
for L in range(1,12):
    print("      L%02d hucre = %8.4f birim" % (L, 800.0/(4*2**(L-1))))

print()
print("=== 2) REGRESYON: sifir varyansta R2 NaN mi? ===")
from backend.regression import *
import backend.regression as RG
print("  regression.py fonksiyonlari:", [n for n in dir(RG) if not n.startswith('_') and callable(getattr(RG,n))][:12])

print()
print("=== 3) svg_loader: defusedxml gercekten kullaniliyor mu? ===")
import inspect, backend.svg_loader as SL
s = inspect.getsource(SL)
print("  'defusedxml' gecisi:", s.count("defusedxml"))
for line in s.splitlines():
    if "defusedxml" in line or "ElementTree" in line or "import" in line and "xml" in line:
        print("   ", line.strip()[:100])

print()
print("=== 4) tolerance parametresi CLI'dan ayarlanabiliyor mu? ===")
import subprocess
r = subprocess.run([sys.executable,"run_analysis.py","--help"],capture_output=True,text=True)
out = (r.stdout or "") + (r.stderr or "")
import re
print("  --tolerance var mi:", "--tolerance" in out)
print("  --grid-mode var mi:", "--grid-mode" in out)
print("  bayraklar:", sorted(set(re.findall(r"--[a-z\-]+", out))))
