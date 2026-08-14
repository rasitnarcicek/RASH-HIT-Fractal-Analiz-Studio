import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.regression import compute_loglog_regression, compute_fractal_dimension
from backend.confidence import evaluate_confidence
import inspect

print("=== URETIM YOLU: processor.py -> compute_loglog_regression ===")
print("imza:", inspect.signature(compute_loglog_regression))

# Dejenere durum: tum seviyelerde ayni dolu hucre sayisi (varyans = 0)
def mk(levels):
    out = []
    for i, n in enumerate(levels, start=1):
        cols = 4 * 2 ** (i - 1)
        out.append({
            "level": i, "cols": cols, "rows": cols,
            "total_cells": cols * cols, "filled_cells": n,
            "log_inv_epsilon": __import__("math").log(cols / 4.0) if i > 1 else 0.0,
            "scale_epsilon": 1.0 / cols,
        })
    return out

for label, data in [("DEJENERE (hepsi 100)", mk([100]*5)),
                    ("NORMAL   (10,40,160,640,2560)", mk([10,40,160,640,2560]))]:
    try:
        r = compute_loglog_regression(data)
        print("  %-32s Db=%.6f  R2=%s" % (label, r.db, r.r2))
        c = evaluate_confidence(db=r.db, r2=r.r2, valid_scales=len(data), svg_suitability_score=100.0)
        print("      -> guven skoru = %s / seviye = %s" % (getattr(c,'score',c), getattr(c,'level',getattr(c,'label',''))))
    except Exception as e:
        print("  %-32s HATA: %s" % (label, e))

print()
print("=== TEST-ONLY YOL: compute_fractal_dimension (README'nin anlattigi davranis) ===")
class R:
    def __init__(s, level, cols, rows, filled):
        s.level=level; s.cols=cols; s.rows=rows; s.filled_cells=filled
        s.total_cells=cols*rows; s.scale_epsilon=1.0/cols
        import math; s.log_inv_epsilon=math.log(cols)
try:
    fa = compute_fractal_dimension([R(i, 4*2**(i-1), 4*2**(i-1), 100) for i in range(1,6)])
    print("  dejenere -> Db=%s  R2=%s" % (fa.db, fa.r2))
except Exception as e:
    print("  HATA:", e)
