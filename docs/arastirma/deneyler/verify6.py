import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.regression import compute_loglog_regression
from backend.confidence import evaluate_confidence
import inspect
print("evaluate_confidence imzasi:", inspect.signature(evaluate_confidence))

def mk(counts, analysis=800.0, base=4):
    out = []
    for i, n in enumerate(counts, start=1):
        c = base * 2 ** (i - 1)
        cw = analysis / c
        out.append({"level": i, "cell_w": cw, "cell_h": cw,
                    "filled_cells": n, "total_cells": c * c})
    return out

cases = [
    ("DEJENERE  (100,100,100,100,100)", [100]*5),
    ("IDEAL D=2 (16,64,256,1024,4096)", [16,64,256,1024,4096]),
    ("IDEAL D=1 (4,8,16,32,64)",        [4,8,16,32,64]),
]
print()
for label, counts in cases:
    r = compute_loglog_regression(mk(counts))
    inc = sum(1 for s in r.scale_table if s.included_in_fit)
    exc = [(s.level, s.exclusion_reason) for s in r.scale_table if not s.included_in_fit]
    print("%-34s Db=%.6f  R2=%-8s  fit'e dahil=%d/%d  dislanan=%s"
          % (label, r.db, round(r.r2,6), inc, len(r.scale_table), exc or "YOK"))
    c = evaluate_confidence(db=r.db, r2=r.r2, valid_scales=r.valid_scales_count,
                            svg_suitability_score=100.0, total_shape_elements=50)
    print("     -> GUVEN: skor=%.1f  seviye=%s" % (c.score, getattr(c,'level',getattr(c,'label',''))))
    print("     -> yorum: %s" % (getattr(c,'commentary','')[:120]))
    print()

print("=== DOYUM (saturation) DISLAMASI CALISIYOR MU? ===")
# tum seviyelerde grid tamamen dolu -> doyum; dislanmali
sat = mk([16,64,256,1024,4096])
for d in sat:
    d["filled_cells"] = d["total_cells"]
r = compute_loglog_regression(sat)
print("  tamamen dolu grid -> Db=%.6f R2=%s  dislanan=%s"
      % (r.db, round(r.r2,6), [(s.level,s.exclusion_reason) for s in r.scale_table if not s.included_in_fit] or "YOK (hicbiri dislanmadi)"))
