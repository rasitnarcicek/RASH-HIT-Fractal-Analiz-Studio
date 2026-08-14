
## C.8 BULGU 6 (Orta) — Phase 8 varsayılan sabitleri README ile uyuşmuyor

README, Phase 8 politikasının varsayılanlarını bir kod bloğu olarak verir ve
metinde defalarca "L10+" ve "L11+" davranışından söz eder.

| Parametre | README | **Kod (`output_profiles.py`)** | Fark |
|---|---|---|---|
| `max_excel_cell_map_level` | 8 | 8 (satır 36) | ✅ |
| `disable_raw_cell_indices_after_level` | 8 | 8 (satır 38) | ✅ |
| `force_svg_rle_after_level` | 9 | 9 (satır 40) | ✅ |
| `summary_only_after_level` | **9** | **8** (satır 42) | ❌ bir seviye |
| `svg_only_after_level` | **10** | **9** (satır 43) | ❌ bir seviye |

Kod `level > summary_only_after_level` karşılaştırmasını kullandığından
(satır 203), gerçek davranış **L9+ yalnızca özet**, **L10+ yalnızca SVG**'dir.
README ise L10+ ve L11+ demektedir. Bir kullanıcı L9 çalıştırdığında,
README'ye göre hücre verisi beklerken sistem yalnızca özet üretecektir.

Bu tek başına küçük bir hatadır; ancak yeniden üretilebilirlik iddiası taşıyan
bir yazılımda çıktı politikası belgelenen değerle eşleşmelidir. Ayrıca
`reproducible` profili bu alanları ayrıca ezmektedir (satır 80-83), dolayısıyla
profile göre davranış değişmektedir — README bu farkı göstermez.

## C.9 BULGU 7 (Orta) — Ölçek parametresi ε iki farklı biçimde tanımlanmış

README ve `grid_planner.py` ölçek parametresini şöyle tanımlar:

$$\varepsilon = \frac{\max(W_{cell}, H_{cell})}{\max(W_{analysis}, H_{analysis})}, \qquad \log(1/\varepsilon) = \ln(1/\varepsilon)$$

`GridLevel` bu değeri `scale_epsilon` ve `log_inv_epsilon` alanlarında hesaplar
(satır 27-30) ve bu alanlar çıktı tablolarına yazılır.

Ancak regresyonu fiilen yapan `compute_loglog_regression`, bu alanları
**hiç kullanmaz**. Kendi eksenini yeniden kurar (`regression.py:80-84`):

```python
avg_size  = (cell_w + cell_h) / 2.0      # MAKS degil ORTALAMA
inv_r     = 1.0 / avg_size                # analiz boyutuna normalize EDILMEZ
log_inv_r = math.log10(inv_r)             # ln degil log10
log_nr    = math.log10(filled)
```

Üç fark vardır: (i) maksimum yerine ortalama hücre kenarı, (ii) analiz kutusuna
normalizasyon yok, (iii) doğal logaritma yerine 10 tabanlı logaritma.

**Eğim üzerindeki etkisi.** Katlama şeması hücre en-boy oranını tüm seviyelerde
sabit tuttuğundan, `max` ile `mean` arasındaki oran sabittir; normalizasyon da
sabit bir çarpandır. Her ikisi de logaritmada **sabit bir kaymaya** dönüşür ve
yalnızca kesişimi (intercept) etkiler. Her iki eksen de aynı tabanda olduğundan
taban değişimi de eğimi etkilemez. Dolayısıyla **bildirilen Db değeri bu
tutarsızlıktan etkilenmemektedir**; C.2/18'deki sentetik doğrulama bunu
göstermektedir.

**Yine de neden raporlanmalı.** Çıktı paketlerinde iki farklı ölçek sütunu yan
yana bulunur: `scale_epsilon` / `log_inv_epsilon` (grid_planner, ln, normalize)
ve `inv_box_size` / `log_inv_r` (regression, log10, normalize değil). Bir hakem
veya ikincil kullanıcı, yayımlanan tablodaki `log_inv_epsilon` sütununu
kullanarak regresyonu yeniden kurmaya kalktığında **farklı bir kesişim** elde
edecektir. Yeniden üretilebilirlik iddiası taşıyan bir çıktı için tek bir ε
tanımı benimsenip belgelenmelidir.

## C.10 BULGU 8 (Düşük) — Paralellik "L04+" değil, aday hücre sayısına bağlı

README: "Candidate cells at **levels L04+** are evaluated in parallel across CPU
cores."

Kod (`intersection_hierarchical.py:211`): kapı seviye değil **adet** temellidir:

```python
if n < 4000 or max_workers <= 1:
    return _bulk_fill_decision_single(...)
```

Kod tabanında seviye tabanlı bir paralellik kapısı yoktur. README'nin kendi
tablosuna göre L04 toplam 2.048 hücredir; bu 4.000 eşiğinin altındadır,
dolayısıyla L04 tipik olarak **tek iş parçacığında** çalışır. Üstelik budama
sonrası aday sayısı toplam hücre sayısından daha da azdır, yani paralellik
pratikte README'nin ima ettiğinden bir-iki seviye daha geç devreye girer.

Ayrıca README "~85%–90% of available logical CPU threads" der; kod tek bir sabit
kullanır: `int(cpus * 0.85)`. Bir aralık değil, tam olarak %85'tir.

## C.11 BULGU 9 (Düşük) — "%100 mükemmel kare hücre" iddiası genel olarak doğru değil

`grid_planner.py` modül docstring'i: "generates optimal multi-level grid series
where cells are **100% square**". Fonksiyon docstring'i (satır 71-72):
"so that **EVERY SINGLE CELL IS A 100% PERFECT SQUARE** on the canvas."

Kod, sütun sayısını yuvarlar: `base_cols = max(1, int(round(base_rows * ar)))`.
Yuvarlama olduğu sürece hücreler ancak *yaklaşık* karedir. Örnek: AR = 1,3 ve
base_cells = 4 için base_rows = 4, base_cols = round(5,2) = 5;
hücre en-boy oranı = (1,3·H/5)/(H/4) = 1,04 — kare değil.

Kodun kendisi bunu zaten kabul etmektedir: `GridLevel` sınıfı ayrı bir
`cell_aspect_ratio` alanı hesaplayıp raporlamaktadır; hücreler her zaman kare
olsaydı bu alan gereksiz olurdu.

README bu noktada koddan **daha doğrudur** ("as square as possible"). Düzeltilmesi
gereken, kod içi docstring'lerdir. Küçük bir sorundur, ancak "100%" gibi kesin
bir nicel ifade kaynak kodda yer aldığında hakem incelemesinde güvenilirlik
kaybına yol açar.

## C.12 BULGU 10 (Olumlu, nitelikli) — Kontur kesişimi zarif ve kesin çözülmüş

Bu bir kusur değil, doğrulanmış bir **güçlü yöndür** ve makalede
vurgulanmalıdır.

`geometry_engine.py:542` konturu bir `LineString` birleşimi olarak saklar ve
kalınlığı **tampon (buffer) uygulamadan** meta veri olarak taşır. Kesişim
kararı `intersection_hierarchical.py:176-184`'te verilir:

```python
hw    = stroke_widths[gi] / 2.0
zw    = hw <= 0.0
if zw.any():                                    # sifir kalinlik: dogrudan kesisim
    hits_z = shapely.intersects(g_arr[zw], c_arr[zw])
if (~zw).any():                                 # kalin kontur: mesafe yuklemi
    dists  = shapely.distance(g_arr[~zw], c_arr[~zw])
    hits_d = dists <= hw[~zw]
```

`distance(çizgi, hücre) ≤ w/2` koşulu, konturun Minkowski tamponunun hücreyle
kesişmesiyle **matematiksel olarak eşdeğerdir**. Yani sistem, milyonlarca
tamponlanmış poligon üretmeden kesin sonuca ulaşır. Bu, EK BÖLÜM B'de incelenen
beş rakip sistemin hiçbirinde bulunmayan bir tekniktir ve gerçek bir yazılım
katkısıdır.

**Nitelik.** Mesafe yüklemi, konturu yuvarlak uçlu ve yuvarlak köşeli
(`round` cap/join) varsayar. SVG'nin varsayılanları ise `butt` uç ve `miter`
köşedir. `stroke-linecap` ve `stroke-linejoin` öznitelikleri kod tabanında hiç
ayrıştırılmaz. Sonuç: uç noktalarda w/2 yarıçaplı bir fazla kaplama, keskin
miter köşelerinde ise bir eksik kaplama oluşur. Sapma kontur kalınlığı
mertebesindedir ve yalnızca hücre boyutu kontur kalınlığına yaklaştığında
(yüksek seviyeler) anlamlı hâle gelir. Makalede belgelenmiş bir yaklaşım olarak
sunulması yeterlidir.
