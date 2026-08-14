
## B.8 Doğrulama Deneyi 3 — `--grid-mode square_bbox` seçeneğinin etkisiz olduğunun tespiti

B.7'deki tabloda `canvas_aspect` ve `square_bbox` modlarının **birebir aynı**
sonuçları üretmesi beklenmedik bir bulgudur ve ayrıca incelenmiştir.

**Beklenen davranış.** `square_bbox` modunda ızgara, geometrinin sınır
kutusundan türetilmelidir. Test geometrisinin sınırları
(100,0; 500,0; 700,0; 673,2) olduğundan analiz karesi 600×600 olmalı ve
1. seviye hücre boyutu 600/4 = 150 çıkmalıdır.

**Gözlenen davranış.** Her iki modda da 1. seviye hücre boyutu 200,0
(= 800/4, yani viewBox tabanlı) ölçülmüştür. Yani `square_bbox` seçeneği
sonuca hiçbir etki etmemektedir.

**İzolasyon testi.** `create_grid_plan` fonksiyonu doğrudan çağrıldığında
doğru çalışmaktadır:

```
square_bbox   -> bounds=(100,0; 13,5; 700,0; 613,5)   L1 hücre = 150,0
canvas_aspect -> bounds=(0; 0; 800; 800)              L1 hücre = 200,0
```

Ayrıca geometri sınırlarının üretim hattında doğru hesaplandığı doğrulanmıştır
(`backend/processor.py:357-361`, `unary_union(...).bounds` →
(100,0; 500,0; 700,0; 673,2051)) ve `grid_mode` parametresinin komut satırından
işlemciye kadar doğru taşındığı görülmüştür
(`run_analysis.py:281` → `processor.grid_mode = "square_bbox"`).

**Kök neden.** İşlem sırasında `create_grid_plan` **iki kez** çağrılmaktadır.
Birinci çağrı doğru parametrelerle yapılır; ikinci çağrı ise doğru planı ezer.
Enstrümantasyonla elde edilen çağrı izi:

```
>>> create_grid_plan grid_mode=square_bbox  geometry_bounds=(100.0, 500.0, 700.0, 673.2051)
>>> SONUÇ bounds=(100.0, 286.6, 700.0, 886.6)  L1 hücre = 150.0
>>> create_grid_plan grid_mode=None          geometry_bounds=None
>>> SONUÇ bounds=(0.0, 0.0, 800.0, 800.0)      L1 hücre = 200.0
```

İkinci çağrının kaynağı `backend/intersection_hierarchical.py:491`:

```python
grid_plan = create_grid_plan(
    svg_viewbox=(0.0, 0.0, vw, vh),
    svg_width=vw,
    svg_height=vh,
    manual_grids=grid_specs,
    num_levels=len(grid_specs)
)
```

Bu çağrı `grid_mode` ve `geometry_bounds` parametrelerini hiç iletmez; yalnızca
birinci plandan gelen satır/sütun sayılarını (`grid_specs`) yeniden kullanır.
Sonuç olarak **hücre sayıları** birinci plandan, **analiz sınırları** ise her
zaman viewBox'tan gelir.

**Sonuçları.** (i) Belgelenen ve komut satırında sunulan `square_bbox` modu
fiilen çalışmamaktadır. (ii) Sistem, tasarım sınır kutusuna demirleme yeteneğine
kodda sahip olmasına rağmen bunu kullanamamaktadır — dolayısıyla B.7'deki
öteleme duyarlılığı, tasarımsal bir tercih değil bir hata sonucudur.
(iii) `grid_mode` bilgisi `result.json` çıktısına da yazılmamaktadır; bu,
yeniden üretilebilirlik kaydında ayrı bir eksikliktir.

Bu bulgu, yazılımın kusuru olarak değil, **iç doğrulamanın (bilinen-değer ve
değişmezlik testlerinin) neden zorunlu olduğunun somut kanıtı** olarak
değerlendirilmelidir: mevcut test kümesi bu hatayı yakalamamıştır.

## B.9 Rakiplerde bulunup RASH-HIT'te bulunmayan bileşenler

Aşağıdaki bileşenler, incelenen rakip kaynak kodlarında doğrulanmış olarak
mevcuttur; RASH-HIT'te bulunmamaktadır.

**(a) Çoklu ızgara orijini / rotasyon.**
Fractalyse: `createTranslatedGrid(dx,dy)`, ölçek başına minimum sayım
(`if(!curve.containsKey(size) || sum < curve.get(size))`).
FractDim: nAçı × nÇözünürlük × nDeplasman² kartezyen çarpımı; deplasmanlar
arası minimum, açılar arası ortalama.
Multiscale-BC: 8 rotasyon × 3×3 kaydırma = 72 konfigürasyon ortalaması.
GeoFractalLines: 8×8 = 64 offset ortalaması.
RASH-HIT: tek sabit ızgara.

**(b) Bootstrap güven aralığı.**
Fractalyse: `getBootStrapConfidenceInterval()` (10.000 örnek), ayrıca
`getSignificance()` p-değeri ve %95 güven aralığı.
GeoFractalLines: 500 yinelemeli CI95.
Multiscale-BC: ölçek-bloğu bootstrap CI95 + jackknife standart sapması.
RASH-HIT: yalnızca R² bildirilmektedir; güven aralığı yoktur.
R² noktaların doğruya yakınlığını ölçer; eğimin kendi belirsizliğini ölçmez.

**(c) Otomatik ölçekleme penceresi seçimi.**
GeoFractalLines: `_find_best_scaling_window` — AIC ile en iyi log-log penceresi
+ `_validate_residual_quality` yerel R² filtresi.
Multiscale-BC: R² pencere taraması (`find_top_windows`) + Benjamini-Yekutieli
FDR düzeltmesi (`apply_by_fdr`) + Spearman ve eğrilik doğrusallık testleri.
Fractalyse: `getDefaultMin`/`getDefaultMax` ile otomatik ölçek aralığı tahmini.
RASH-HIT: sabit yedi seviyeli doubling (`generate_doubling_grid_spec`).
`result.json` içindeki `included_in_fit` ve `exclusion_reason` alanları
mevcuttur ancak B.7 deneyinde hiçbir seviye dışlanmamıştır (tüm seviyeler
`fit=True`); yani alan tanımlı olmakla birlikte etkin bir seçim mekanizması
çalışmamaktadır. B.7'deki 0,06–0,09'luk sapma büyük ölçüde bununla
ilişkilidir.

**(d) Multifraktal spektrum.**
GeoFractalLines: bölüşüm fonksiyonu Z(q), τ(q), genelleştirilmiş boyutlar Dq,
entropiden D1 ve Legendre f(α) spektrumu, q ∈ [−5, 5].
Fractalyse: `MultiFracBoxCountingVectorMethod` — geometri tipine göre gerçek
ağırlık (nokta → adet, çizgi → uzunluk, poligon → alan).
RASH-HIT: yoktur.

Bu bileşen, diğer üçünden farklı olarak bir eksiklik değil **kapsam kararı**
olarak değerlendirilmelidir. Multifraktal analiz monofraktal sonucun
doğruluğuna bağımlı olduğundan, (a) ve (c) çözülmeden eklenmesi önerilmez;
makalede "gelecek çalışma" olarak konumlandırılması ve mevcut alan/dolgu
altyapısının buna hazır olduğunun belirtilmesi daha savunulabilirdir.

**(e) Bilinen-değer (ground-truth) doğrulaması.**
GeoFractalLines: `generate_koch_curve` + `validate_algorithm` ile Koch
boyutuna (1,26186) karşı kendi kendini sınama.
RASH-HIT: yoktur.
