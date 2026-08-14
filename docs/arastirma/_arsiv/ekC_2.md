
## C.3 BULGU 1 (Kritik) — Dolgu kuralı: üç kaynak birbiriyle çelişiyor

**İddia (README, "Fill Rule Topology Resolution"):**
> `nonzero` Fill Rule: Uses `shapely.ops.unary_union(polygons)` …
> `evenodd` Fill Rule: Evaluates sequential subpaths using `symmetric_difference` …

**İddia (svg_loader.py:250, kullanıcıya gösterilen uyarı):**
> "fill-rule='evenodd' detected. Default non-zero winding rule used in core v1.0."

**Kod (geometry_engine.py:510-531):** Dolgu kuralına göre **hiçbir dallanma
yoktur**. `fill_rule` adlı bir değişken, öznitelik veya parametre kod tabanında
hiç bulunmamaktadır (yalnızca bir yorum satırında ve loader uyarısında geçer).
Çok alt-yollu her yol için koşulsuz olarak şu uygulanır:

```python
polygons.sort(key=lambda p: p.area, reverse=True)
fill_obj = polygons[0]
for p in polygons[1:]:
    fill_obj = fill_obj.symmetric_difference(p)
```

`unary_union` dolgu için hiç kullanılmaz; yalnızca kontur çizgilerinin
birleştirilmesinde (satır 542) kullanılır.

**Deney (verify2.py).** İç içe iki kare, 100×100 dış ve 50×50 iç:

| Girdi | nonzero beklenen | evenodd beklenen | **Ölçülen** |
|---|---|---|---|
| Alt yollar **aynı** yönde sarılı | 10.000 | 7.500 | **7.500** |
| Alt yollar **ters** yönde sarılı | 7.500 | 7.500 | **7.500** |

**Sonuç.** Uygulanan davranış her koşulda **even-odd**'dur. Dolayısıyla:

- README'nin "kurala göre dallanır" iddiası yanlıştır.
- `svg_loader.py`'nin kullanıcıya gösterdiği "non-zero kullanıldı" uyarısı da
  yanlıştır — gerçekte tam tersi uygulanmaktadır.
- SVG standardında **varsayılan** dolgu kuralı `nonzero`'dur. Yani kural
  belirtilmemiş sıradan bir SVG, standardın varsayılanının aksine işlenmektedir.

**Neden önemli.** Bu, ölçülen fraktal boyutu doğrudan değiştirir. Aynı yönde
sarılmış iç içe halkalardan oluşan bir motif — Türk-İslam süslemesinde,
kilim bordürlerinde ve rozet/gül motiflerinde son derece yaygın bir yapı —
tarayıcıda **dolu** görünürken sistem tarafından **delikli** olarak
ölçülmektedir. Yukarıdaki basit örnekte kaplanan alan %25 azalmıştır.

Bu bulgu, EK BÖLÜM B.5'te FractDim'e yönelttiğim "dolgu semantiğini yok sayıyor"
eleştirisinin bu projede de farklı bir biçimde geçerli olduğunu göstermektedir
ve EK BÖLÜM B.11'de "güçlenen yön" olarak sıraladığım "dolgu semantiğinin doğru
ele alınması" maddesinin **geri çekilmesini** gerektirir. Düzeltilene kadar bu
madde özgünlük gerekçesi olarak kullanılmamalıdır.

## C.4 BULGU 2 (Kritik) — Dejenere regresyon R² = 1,0 ve "Yüksek güven" olarak raporlanıyor

**İddia (README, "Fit Quality"):**
> "If all occupied cell counts across levels are identical (zero variance
> Var(y) = 0), R² evaluates to `NaN` to signal a degenerate regression state
> **rather than overstating quality**."

**Kod.** `regression.py` içinde **iki ayrı** regresyon uygulaması vardır:

| Fonksiyon | Sıfır varyans davranışı | Kullanan |
|---|---|---|
| `compute_fractal_dimension` (satır 286-325) | `r2 = float("nan")` ✅ | **Yalnızca testler** (`tests/test_audit_gaps.py`) |
| `compute_loglog_regression` (satır 65-148) | `if ss_tot <= 1e-12: r2 = 1.0` ❌ | **Üretim** (`processor.py:435`) |

README'nin anlattığı NaN koruması, üretim hattında **kullanılmayan** geriye
dönük uyumluluk fonksiyonundadır. Üretim yolu tam tersini yapar: sıfır
varyansta R²'yi **1,0** olarak raporlar.

**Deney (verify6.py).** Beş seviyenin tamamında dolu hücre sayısı 100 (varyans
sıfır):

```
DEJENERE (100,100,100,100,100)   Db = 0,000000   R² = 1,0
   -> GÜVEN: skor = 92,0   seviye = "Yüksek"
```

Karşılaştırma için aynı hatta sınanan sağlıklı durumlar:

```
IDEAL D=2 (16,64,256,1024,4096)  Db = 2,000000   R² = 1,0   -> 92,0 "Yüksek"
IDEAL D=1 (4,8,16,32,64)         Db = 1,000000   R² = 1,0   -> 92,0 "Yüksek"
```

**Sonuç.** Tümüyle anlamsız bir ölçüm (Db = 0, hiçbir ölçekleme davranışı yok),
matematiksel olarak kusursuz iki ölçümle **birebir aynı** güven skorunu ve aynı
"Yüksek" etiketini almaktadır. Sistem, akademik kullanıcıya bu sonucun
"doğrudan yayına dahil edilebileceğini" bildirmektedir.

İkincil kusurlar aynı fonksiyonda:

- `regression.py:133-135` — `abs(denom) < 1e-12` durumunda `slope = 1.0`
  **sabit ataması** yapılır. Yani hesaplanamayan bir eğim, uyarı üretmeden
  D = 1,0 olarak raporlanır.
- `regression.py:150` — `db_val = abs(slope)`. Negatif eğim (ölçek arttıkça
  dolu hücrenin azalması; fiziksel olarak imkânsız, dolayısıyla bir hata
  göstergesi) mutlak değerle geçerli bir boyuta dönüştürülür ve hata gizlenir.

Bu üç davranış birlikte, EK BÖLÜM B.7'de gözlenen "üç farklı sonuç, aynı 92,5
güven skoru" olgusunun kök nedenini açıklar: güven skoru kademeli bir basamak
fonksiyonudur ve R² ≥ 0,99 olan her sonucu ayrımsız biçimde tam puanla
ödüllendirir.

## C.5 BULGU 3 (Yüksek) — Doyum (saturation) denetimi boş bir taslak

**Kod (regression.py:89-94):**

```python
if filled <= 0:
    included = False
    reason = "No occupied boxes (N(r) = 0)"
elif filled == total and l_idx > 1 and total > 64:
    # Saturation check if necessary
    pass
```

Doyum dalı bir `pass` ifadesidir — hiçbir şey yapmaz. Dolayısıyla
`included_in_fit` alanı yalnızca `filled == 0` olduğunda `False` olur.

**Deney (verify6.py).** Her seviyede ızgaranın tamamı dolu (tam doyum):

```
tamamen dolu grid -> Db = 2,000000   R² = 1,0   dışlanan seviye: YOK
```

**Sonuç.** Kutu sayma yönteminin en bilinen tuzağı olan üst-uç doyumu ve
alt-uç seyrekliği için etkin bir filtre yoktur. Bu, EK BÖLÜM B.9(c)'de
"otomatik ölçekleme penceresi seçimi yok" biçiminde belirttiğim eksikliğin
kod düzeyindeki kesin kanıtıdır ve o tespiti güçlendirir. `included_in_fit` /
`exclusion_reason` alanlarının çıktı şemasında bulunması, mekanizmanın
tasarlandığını ancak tamamlanmadığını göstermektedir.

Bu aynı zamanda EK BÖLÜM B.7'deki Koch sapmasını (gerçek 1,26186'ya karşı
ölçülen 1,169–1,199) büyük ölçüde açıklamaktadır: düşük seviyelerdeki birkaç
kutuluk ölçümler regresyona tam ağırlıkla girmektedir.
