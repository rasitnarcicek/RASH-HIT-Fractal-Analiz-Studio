
import sys; P=r"C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio"
sys.path.insert(0,P)
import backend.grid_planner as gp
orig = gp.create_grid_plan
def spy(**kw):
    print("  >>> create_grid_plan grid_mode=", kw.get("grid_mode"), " geometry_bounds=", kw.get("geometry_bounds"))
    r = orig(**kw)
    print("  >>> SONUC bounds=", (r.xmin,r.ymin,r.xmax,r.ymax), "L1 box=", r.levels[0].cell_w)
    return r
gp.create_grid_plan = spy
import backend.processor as pr
pr.create_grid_plan = spy
p = pr.AnalysisProcessor(input_path=r"C:\Users\RaşitNarçiçek\rakip_analiz\shift_test\koch_t100.svg",
    output_dir=r"C:\Users\RaşitNarçiçek\rakip_analiz\spyout", levels=3,
    grid_mode="square_bbox", overwrite=True, profile="lean", lang="tr")
print("processor.grid_mode =", p.grid_mode)
res = p.run()
print("status:", res.status)
