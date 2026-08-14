import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.geometry_engine import parse_svg_path

# Merkezi orijinde, R=400 ceyrek daire: (0,R) -> (R,0)
# Dogru kubik bezier kontrol noktalari: (K*R, R) ve (R, K*R)
K = 0.5522847498
R = 400.0
d = "M0,{r} C{a},{r} {r},{a} {r},0".format(r=R, a=K*R)

print("path d =", d)
print()
print("=== Kubik Bezier duzlestirme hatasi (gercek daire yayina sapma) ===")
for steps in (6, 12, 24, 48, 96):
    pts = parse_svg_path(d, tolerance_steps=steps)[0]
    # (a) ornekleme noktalarinin yaya sapmasi (bezier'in kendi yaklasim hatasi)
    node_err = max(abs(math.hypot(x, y) - R) for x, y in pts)
    # (b) kiris orta noktalarinin yaya sapmasi (duzlestirme/sagitta hatasi)
    chord_err = 0.0
    for i in range(len(pts) - 1):
        mx = (pts[i][0] + pts[i+1][0]) / 2.0
        my = (pts[i][1] + pts[i+1][1]) / 2.0
        chord_err = max(chord_err, abs(math.hypot(mx, my) - R))
    print("  steps=%-3d nokta=%-4d  dugum hatasi=%.6f  KIRIS SARKMASI=%.6f birim"
          % (steps, len(pts), node_err, chord_err))

print()
print("=== Bu hata hangi seviyede hucre boyutunu asiyor? (800 birim analiz kutusu, base 4) ===")
pts24 = parse_svg_path(d, tolerance_steps=24)[0]
err24 = 0.0
for i in range(len(pts24) - 1):
    mx = (pts24[i][0] + pts24[i+1][0]) / 2.0
    my = (pts24[i][1] + pts24[i+1][1]) / 2.0
    err24 = max(err24, abs(math.hypot(mx, my) - R))
print("  Uretimde kullanilan steps=24 icin kiris sarkmasi = %.6f birim" % err24)
for L in range(1, 12):
    cell = 800.0 / (4 * 2 ** (L - 1))
    flag = "  <-- SARKMA HUCREDEN BUYUK" if err24 > cell else ""
    print("      L%02d hucre=%8.4f  sarkma/hucre = %7.3f%s" % (L, cell, err24 / cell, flag))
