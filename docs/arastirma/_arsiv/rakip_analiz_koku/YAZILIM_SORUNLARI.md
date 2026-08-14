# RASH-HIT Fractal Studio — YAZILIM SORUNLARI VE İDDİA–KOD UYUŞMAZLIKLARI

> Bu dosya **yazılım kusurlarını** toplar. Özgünlük / literatür araştırması ana raporda:
> `RASH-HIT_Ozgunluk_Arastirma_Raporu.md`
>
> Kapsam: proje belgelerindeki (README, CODE_PROVENANCE, CITATION.cff, docstring)
> iddiaların kaynak kodla birebir karşılaştırılması ve çalıştırma ile doğrulanması.
> Proje kaynağı **salt okunur** incelendi; hiçbir dosya değiştirilmedi.
> Testler projenin `~/rakip_analiz/_proje_kopya` kopyasında çalıştırıldı.

**Durum özeti:** 34 belge iddiası sınandı → 21 doğru, 10 yanlış, 3 kısmen.
Ayrıca depo/sürüm düzeyinde 5 ek bulgu (Bölüm D) eklendi.

---

## İÇİNDEKİLER

- Bölüm C — İddia–kod doğrulaması (C.1–C.17): kritik hesaplama kusurları
- Bölüm D — Depo, sürüm, provenance ve test altyapısı bulguları (D.1–D.6)

---

# BÖLÜM C — PROJE BELGELERİNDEKİ İDDİALARIN KAYNAK KODLA BİREBİR DOĞRULANMASI

Bu bölüm, önceki bölümlerden yöntemsel olarak ayrılır. EK BÖLÜM A belge/kılavuz
taramasına, EK BÖLÜM B rakip kaynak kodlarının okunmasına dayanıyordu.
EK BÖLÜM C ise **projenin kendi belgelerinde (README.md, modül docstring'leri,
kod içi yorumlar) ileri sürülen her teknik iddiayı tek tek çıkarıp, aynı iddiayı
uygulayan kod satırını okuyarak ve mümkün olan her durumda çalıştırılabilir bir
deneyle sınayarak** doğrular.

Gerekçe: bir makalenin "Yöntem" bölümü yazılımın README'sinden türetilecekse,
README'nin kodu doğru anlatıp anlatmadığı hakemlik sürecinden önce
kanıtlanmalıdır. Aşağıdaki bulguların bir kısmı, EK BÖLÜM B'de rakiplere
yönelttiğim eleştirilerin bir bölümünün bu projede de geçerli olduğunu
göstermektedir; bunlar açıkça belirtilmiştir.

## C.1 Yöntem

README.md (601 satır) ve modül docstring'lerinden **sınanabilir** 34 teknik iddia
çıkarıldı. Her iddia için: (i) iddiayı uygulaması gereken kod konumu bulundu,
(ii) kod okundu, (iii) mümkünse doğrulama betiği çalıştırıldı.

Betikler: `C:\Users\RaşitNarçiçek\rakip_analiz\verify1.py` … `verify6.py`.
Betikler proje dizinine geçici olarak kopyalanıp çalıştırıldı ve **hemen
silindi**; proje dosyalarında hiçbir kalıcı değişiklik yapılmadı. Doğrulama
tamamen salt-okunur import ve fonksiyon çağrısı düzeyindedir; hiçbir analiz
çıktısı `outputs/` altına yazılmamıştır.

Sonuç dağılımı: 34 iddiadan **21'i doğrulandı**, **10'u yanlış veya eksik
bulundu**, **3'ü kısmen doğrulandı**.

## C.2 Kodla doğrulanan iddialar

Aşağıdakiler okunarak ve/veya çalıştırılarak **doğru** bulunmuştur ve makalede
güvenle ileri sürülebilir:

1. **Rasterleştirme yok.** Depo genelinde hiçbir raster kütüphanesi (PIL,
   OpenCV, imread) çağrılmaz; tüm kesişimler Shapely/GEOS üzerinden yapılır.
2. **Kesin geometrik kesişim.** `intersection_hierarchical.py:153`
   `shapely.intersects(fill_obj_arr[...], cell_boxes[...])` — gerçek GEOS
   yüklemi, nokta örnekleme değil.
3. **STRtree toplu sorgulama.** `stroke_tree.query(cell_boxes)` ile vektörize
   (2, K) çift dizisi; Python düzeyinde hücre döngüsü yok.
4. **Boş ebeveyn budaması, FULL kısayolu yok.** `known_empty_contrib` ile
   torun katkısı taşınır; dolu ebeveynler her seviyede yeniden değerlendirilir.
   Kodda açıkça belgelenmiştir. EK BÖLÜM B.4'teki tespit doğrulanmıştır.
5. **Kesin 2^i katlama.** `grid_planner.py:132-136`, `multiplier = 2 ** i`.
6. **En-boy oranı formülü.** `ar >= 1.0` → `base_rows = base_cells`,
   `base_cols = round(base_rows * ar)`; aksi hâlde simetriği. README ile birebir.
7. **Analiz kutusu önceliği.** viewBox → width/height → geometri sınırları →
   (0,0,100,100) yedeği; `grid_planner.py:76-85`.
8. **Tamamlayıcı boş hücre sayımı.** `N_empty = N_total - N_filled`; boş hücre
   nesnesi hiç oluşturulmaz.
9. **Desteklenen SVG öğeleri.** `svg_loader.py:282`
   `render_tags = {'path','rect','circle','ellipse','line','polyline','polygon'}`
   — README'deki yedi öğe listesiyle birebir.
10. **Dönüşüm fonksiyonları.** matrix, translate, scale, rotate, skewX, skewY
    — `geometry_engine.py:25-79`'da uygulanmıştır.
11. **Kontur genişliği ölçeklemesi.** `geometry_engine.py:506-508`,
    `sqrt(|a·d − b·c|)` — README'deki formülle birebir.
12. **defusedxml XXE sertleştirmesi.** `svg_loader.py`'da defusedxml import
    edilir; kurulu değilse stdlib'e düşer ve **açık uyarı üretir**. Sessiz
    düşüş yoktur — doğru davranış.
13. **Eğri düzleştirme adım sayıları.** `high=24, medium=12, low=6`
    (`geometry_engine.py:435`) — README ile birebir (ancak bkz. C.7).
14. **Eliptik yay dönüşümü.** Uç-nokta parameterizasyonundan merkez
    parameterizasyonuna geçiş (`sample_elliptical_arc`, satır 133-200) doğru
    uygulanmıştır; yarıçap düzeltmesi (radii correction) dâhildir.
15. **İş parçacığı sayısı örneği.** `_get_default_max_workers()` =
    `int(cpus * 0.85)`; 20 iş parçacıklı CPU → 17. README'deki örnek doğru.
16. **Güven skoru ağırlıkları.** R² %40, geçerli ölçek sayısı %30, SVG sağlığı
    %30 (`confidence.py:65-86`). EK BÖLÜM B.6'da kullandığım "%40" değeri
    doğrulanmıştır.
17. **Sürüm koruması.** Var olan paket sessizce ezilmez; zaman damgalı yeni
    klasör üretilir.
18. **Regresyon çekirdeği doğrudur.** Sentetik veriyle sınandı:
    N = (16, 64, 256, 1024, 4096) → **Db = 2,000000**;
    N = (4, 8, 16, 32, 64) → **Db = 1,000000**. OLS eğim hesabı kusursuzdur.
    Bu önemli bir güçlü yöndür: sistemin ürettiği hatalar regresyon
    matematiğinden değil, girdi/ölçek katmanından kaynaklanmaktadır.
19. **RLE sıkıştırma** ve **yüksek seviye çıktı kısıtlama** mekanizmaları
    gerçekten uygulanmıştır (sabit değerleri için bkz. C.8).
20. **Kontur kesişimi mesafe yüklemiyle kesin çözülür** (bkz. C.12).
21. **Paralel yürütme gerçek çok-çekirdeklidir**; `ThreadPoolExecutor` ile
    parçalara bölünür ve sonuçlar birleştirilir.

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

## C.6 BULGU 4 (Yüksek) — CSS birim dönüşüm tablosunun yarısı uygulanmamış

README, dokuz satırlık bir birim dönüşüm tablosu sunar (px, pt, pc, mm, cm, in,
em, rem, %) ve her biri için bir çarpan verir.

**Kod (svg_loader.py:109-129).** `parse_length` yalnızca üç ek duruma bakar:
`px` (sonek atılır), `pt` (×1,33333) ve `em`/`rem` (×16,0). Diğerleri için
`float(val_str)` çağrısı `ValueError` fırlatır ve fonksiyon **sessizce
`default` değerini döndürür**.

**Deney (verify1.py), `default = −999,0`:**

| Girdi | README'ye göre | **Ölçülen** | Durum |
|---|---|---|---|
| `10px` | 10,0 | 10,0 | ✅ |
| `12pt` | 16,0 | 15,99996 | ✅ |
| `1em` | 16,0 | 16,0 | ✅ |
| `3` (birimsiz) | 3,0 | 3,0 | ✅ |
| `1rem` | 16,0 | **−999,0** | ❌ |
| `10.5mm` | 39,69 | **−999,0** | ❌ |
| `5cm` | 188,98 | **−999,0** | ❌ |
| `1in` | 96,0 | **−999,0** | ❌ |
| `2pc` | 32,0 | **−999,0** | ❌ |
| `50%` | ViewBox oranı | **−999,0** | ❌ |

`rem` hatasının nedeni ayrıca ilginçtir: `'1rem'.endswith('em')` doğru olduğu
için ilk dal yakalar, ardından `val_str[:-2]` yalnızca `"em"` kırpar ve geriye
`"1r"` kalır → `ValueError` → varsayılan. Yani `rem` desteği eklenmiş
görünmekte ama işlememektedir.

Fonksiyonun kendi docstring'i de yanıltıcıdır: örnek olarak `'10.5mm'` verir,
oysa bu değeri ayrıştıramaz.

**Neden önemli.** `mm` ve `cm`, Adobe Illustrator ve Inkscape'in **baskı amaçlı
SVG dışa aktarımlarında varsayılan birimlerdir**. Projenin hedef veri türü olan
motif, tekstil ve süsleme çizimleri tam olarak bu araçlardan gelmektedir.
Somut sonuçları:

- `stroke-width="0.5mm"` → varsayılan `1.0` px'e düşer; kontur kalınlığı
  yanlış, dolayısıyla C.12'deki mesafe yüklemi yanlış eşikle çalışır.
- `width="210mm" height="297mm"` (A4) → her ikisi de `0.0` döner. Bu durumda
  `grid_planner` width/height dalını atlar; viewBox varsa kurtarır, yoksa
  analiz kutusu 100×100 yedeğine düşer ve tüm ölçek ekseni bozulur.

Hata sessizdir: kullanıcıya hiçbir uyarı verilmez.

## C.7 BULGU 5 (Orta-Yüksek) — Eğri düzleştirme "adaptif" değil, sabit adımlı; yüksek seviyelerde sayısal tavan oluşturuyor

**İddia (README):** "SVG paths contain parametric curves that are **adaptively
sampled** into linear segments based on tolerance configuration."

**Kod.** `sample_cubic_bezier`, `sample_quadratic_bezier` ve
`sample_elliptical_arc` fonksiyonlarının tamamı `for i in range(1, num_steps+1):
t = i / num_steps` biçiminde **düzgün (uniform) t adımlarıyla** örnekler.
Eğrilik, kiriş hatası veya yay uzunluğu hiçbir yerde değerlendirilmez.

**Deney (verify2.py).** 1000 birimlik bir eğri ile 1 birimlik bir eğri, aynı
tolerans ayarında **aynı sayıda** noktaya indirgenir:

| Eğri | steps=6 | steps=12 | steps=24 |
|---|---|---|---|
| Büyük eğri (1000 birim) | 7 nokta | 13 nokta | 25 nokta |
| Küçük eğri (1 birim) | 7 nokta | 13 nokta | 25 nokta |

Örnekleme yoğunluğu geometrik ölçekten tümüyle bağımsızdır. Bu tanım gereği
adaptif değildir. (Karşılaştırma: EK BÖLÜM B.2'de incelenen FractDim, bu sorunu
tam olarak önlemek için adaptif ikiye bölme kullanmaktadır — bu tek eksende
rakip yaklaşım üstündür.)

**Deney (verify4.py) — sayısal sonucun ölçülmesi.** R = 400 yarıçaplı çeyrek
daireyi temsil eden standart kübik Bézier (kontrol noktası katsayısı
K = 0,5522847498), 800 birimlik bir analiz kutusu içinde:

| tolerance_steps | Üretilen nokta | Düğüm hatası | **Kiriş sarkması** |
|---|---|---|---|
| 6 | 7 | 0,100938 | 3,562725 birim |
| 12 | 13 | 0,103477 | 0,901970 birim |
| **24 (üretimde kullanılan)** | **25** | **0,108977** | **0,226823 birim** |
| 48 | 49 | 0,108977 | 0,056865 birim |

Üretim ayarındaki kiriş sarkması **0,2268 birimdir**. Bunu ızgara hücre
boyutuyla karşılaştırdığımızda:

| Seviye | Hücre boyutu | Sarkma / hücre |
|---|---|---|
| L07 | 3,1250 | 0,073 |
| L08 | 1,5625 | 0,145 |
| L09 | 0,7813 | 0,290 |
| L10 | 0,3906 | **0,581** |
| L11 | 0,1953 | **1,161** ← sarkma hücreden büyük |

**Sonuç.** README'nin "**seviye sayısında kesin bir sınır yoktur**" (`no hard
limit`) iddiası hesaplama açısından doğrudur, ancak **ölçüm açısından
yanıltıcıdır**. Yaklaşık L9'dan itibaren düzleştirme hatası hücre boyutunun
anlamlı bir kesrine ulaşır; L11'de hücreyi tamamen aşar. Bu seviyelerde sistem
artık SVG eğrisini değil, onun 24 kirişlik çokgen yaklaşımını ölçmektedir.

Bu, EK BÖLÜM A ve B'de projenin güçlü yönü olarak sunduğum
"≈8,4 milyon kutu / L10'a ölçeklenme" ifadesinin **niteliklendirilmesini**
gerektirir: ölçeklenme başarımsal olarak gerçektir, ancak ölçüm geçerliliği
düzleştirme toleransıyla sınırlıdır. Makalede bu sınır açıkça belirtilmeli veya
tolerans eğri uzunluğuna/hücre boyutuna bağlı hâle getirilmelidir.

Ek olarak `--tolerance` bayrağı komut satırında **hiç sunulmamaktadır**
(mevcut bayraklar: `--batch`, `--batch-profile`, `--engine`, `--grid-mode`,
`--input`, `--lang`, `--levels`, `--measure`, `--output`, `--overwrite`,
`--profile`, `--show-technical`). Tolerans üretimde `'high'` değerine sabitlidir
ve kullanıcı bunu değiştiremez.

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

## C.13 İddia–kod uyum tablosu

| # | Belgedeki iddia | Kaynak | Kod durumu | Kanıt |
|---|---|---|---|---|
| 1 | Rasterleştirme yok | README | ✅ Doğru | raster kütüphanesi yok |
| 2 | Kesin GEOS kesişimi | README | ✅ Doğru | ih.py:153 |
| 3 | STRtree toplu sorgu | README | ✅ Doğru | ih.py:166 |
| 4 | Boş ebeveyn budama, FULL yok | README | ✅ Doğru | ih.py:381 |
| 5 | Kesin 2^i katlama | README | ✅ Doğru | gp.py:132-136 |
| 6 | AR tabanlı taban ızgara | README | ✅ Doğru | gp.py:120-125 |
| 7 | Analiz kutusu önceliği | README | ✅ Doğru | gp.py:76-85 |
| 8 | Tamamlayıcı boş sayım | README | ✅ Doğru | — |
| 9 | 7 SVG öğesi | README | ✅ Doğru | sl.py:282 |
| 10 | 6 dönüşüm fonksiyonu | README | ✅ Doğru | ge.py:25-79 |
| 11 | Kontur ölçeği √&#124;det&#124; | README | ✅ Doğru | ge.py:506-508 |
| 12 | defusedxml XXE | README | ✅ Doğru | sl.py |
| 13 | Tolerans 24/12/6 | README | ✅ Doğru | ge.py:435 |
| 14 | Yay merkez parameterizasyonu | README | ✅ Doğru | ge.py:133+ |
| 15 | 20 iş parçacığı → 17 işçi | README | ✅ Doğru | ih.py:190-192 |
| 16 | Güven: R² %40 / ölçek %30 / sağlık %30 | kod | ✅ Doğru | conf.py:65-86 |
| 17 | Ezme koruması / sürümleme | README | ✅ Doğru | — |
| 18 | OLS eğim hesabı | README | ✅ Doğru | D=2,000000 / D=1,000000 |
| 19 | RLE + yüksek seviye kısıtlama | README | ✅ Doğru | op.py |
| 20 | Kontur mesafe yüklemi | kod | ✅ Doğru (nitelikli) | ih.py:176-184 |
| 21 | Çok çekirdekli yürütme | README | ✅ Doğru | ih.py:220-233 |
| 22 | **nonzero → unary_union, evenodd → sym.diff** | README | ❌ **Yanlış** — her zaman even-odd | ge.py:510-531; ölçüm 7500/7500 |
| 23 | **"Varsayılan non-zero kullanıldı" uyarısı** | sl.py:250 | ❌ **Yanlış** — even-odd uygulanıyor | aynı |
| 24 | **Sıfır varyansta R² = NaN** | README | ❌ **Yanlış** — üretimde R² = 1,0 | reg.py:145-146; ölçüm |
| 25 | **Doyum denetimi** | reg.py:92-94 | ❌ **Boş `pass`** | ölçüm: dışlanan yok |
| 26 | **mm / cm / in / pc / % birimleri** | README | ❌ **Uygulanmamış** | ölçüm: tümü default |
| 27 | **rem birimi** | README | ❌ **Bozuk** (`[:-2]` → `"1r"`) | ölçüm: default |
| 28 | **Eğriler "adaptif" örnekleniyor** | README | ❌ **Yanlış** — sabit adım | ölçüm: 1000 br = 1 br |
| 29 | **summary_only_after_level = 9** | README | ❌ Kod: 8 | op.py:42 |
| 30 | **svg_only_after_level = 10** | README | ❌ Kod: 9 | op.py:43 |
| 31 | **Paralellik "L04+"** | README | ❌ Kapı `n ≥ 4000` | ih.py:211 |
| 32 | **"%100 mükemmel kare hücre"** | gp.py docstring | ❌ Yuvarlama var | gp.py:122 |
| 33 | ε tanımı (maks / normalize / ln) | README+gp.py | ⚠️ Kısmen — regresyon farklı eksen kullanıyor (eğim etkilenmez) | reg.py:80-84 |
| 34 | "Seviye sayısında sınır yok" | README | ⚠️ Kısmen — hesaplama evet, ölçüm geçerliliği ≈L9'da tükeniyor | ölçüm: sarkma/hücre |

(Kısaltmalar: ge = geometry_engine.py, gp = grid_planner.py,
ih = intersection_hierarchical.py, sl = svg_loader.py, reg = regression.py,
op = output_profiles.py, conf = confidence.py.)

## C.14 Bu bulguların EK BÖLÜM A ve B'deki değerlendirmeye etkisi

**Geri çekilmesi gereken.**

- EK BÖLÜM B.11'de "güçlenen yön" olarak sıraladığım **"dolgu semantiğinin
  doğru ele alınması"** maddesi geçerliliğini yitirmiştir (C.3). FractDim'in
  dolguyu kontura indirgemesini eleştirmiştim; bu proje ise dolguyu SVG
  standardının varsayılanının aksine even-odd olarak çözmektedir. Farklı bir
  hata, ama yine bir hata. Düzeltilene kadar üstünlük iddiası olarak
  kullanılmamalıdır.
- EK BÖLÜM A ve B'de vurgulanan **"L10 / 8,4 milyon kutuya ölçeklenme"**
  ifadesi, C.7'deki düzleştirme tavanı nedeniyle bir *başarım* iddiası olarak
  korunmalı, bir *çözünürlük/doğruluk* iddiası olarak kullanılmamalıdır.

**Güçlenen.**

- **Hiyerarşik negatif-uzay budaması** (B.4) kod düzeyinde doğrulanmıştır ve
  incelenen beş rakipte bulunmamaktadır. Projenin en savunulabilir teknik
  katkısı olmayı sürdürmektedir.
- **Kontur mesafe yüklemi** (C.12) beklenmedik bir ikinci özgün katkıdır;
  önceki bölümlerde fark edilmemişti. Rakiplerin hiçbiri kontur kalınlığını
  bu biçimde kesin ve tamponsuz ele almamaktadır. Makalede ayrı bir teknik
  katkı olarak sunulabilir.
- **Regresyon çekirdeğinin doğruluğu** sentetik olarak kanıtlanmıştır (C.2/18).
  Bu, B.7'deki Koch sapmasının bir kodlama hatasından değil, ölçek penceresi ve
  ızgara hizası eksikliğinden kaynaklandığını göstermektedir — yani sorun
  düzeltilebilir niteliktedir.

**Değişmeyen.** B.9'daki eksiklikler (çoklu ızgara orijini, bootstrap güven
aralığı, otomatik ölçek penceresi, multifraktal, bilinen-değer doğrulaması)
aynen geçerlidir; C.4 ve C.5 bunların ikisini kod düzeyinde kanıtlamıştır.

**Genel değerlendirme.** Projenin **mimarisi ve çekirdek geometri motoru
sağlamdır**; bulunan on kusurun hiçbiri mimari değildir. Sekizi yerel
düzeltmelerle (tek fonksiyon veya tek koşul) giderilebilir. Buna karşılık
bulguların üçü (C.3 dolgu kuralı, C.4 dejenere R², C.5 doyum denetimi)
**bildirilen sayısal sonucu doğrudan etkilemektedir** ve düzeltilmeden
yayımlanacak herhangi bir ölçüm tablosu savunulamaz.

## C.15 Öncelikli düzeltme listesi (C bulguları)

Etki × düzeltme maliyeti sırasına göre:

| Sıra | Bulgu | Düzeltme | Tahmini kapsam |
|---|---|---|---|
| 1 | C.4 dejenere R² = 1,0 | `ss_tot <= 1e-12` dalını `float("nan")` yap; `abs(slope)` kaldır; `slope = 1.0` yedeğine uyarı ekle | 3 satır |
| 2 | C.3 dolgu kuralı | `SVGNode`'a `fill_rule` ekle; nonzero'da `unary_union`, evenodd'da mevcut yol; loader uyarısını düzelt | ~15 satır |
| 3 | C.5 doyum denetimi | `pass` yerine `included = False` + gerekçe; alt-uç seyreklik filtresi ekle | ~8 satır |
| 4 | C.6 CSS birimleri | `parse_length`'e mm/cm/in/pc/% ekle; `rem` kırpmasını `[:-3]` yap | ~12 satır |
| 5 | B.8 `square_bbox` etkisiz | `ih.py:491`'deki ikinci `create_grid_plan` çağrısına `grid_mode` + `geometry_bounds` ilet | 2 satır |
| 6 | C.7 düzleştirme tavanı | Toleransı eğri yay uzunluğu / hedef hücre boyutuna bağla; `--tolerance` bayrağı ekle | ~25 satır |
| 7 | C.9 ε tanımı | Regresyonu `grid_planner`'ın `log_inv_epsilon` alanından besle | ~5 satır |
| 8 | C.8 Phase 8 sabitleri | README'yi koda göre düzelt (veya tersi) | belge |
| 9 | C.10 paralellik açıklaması | README'yi `n ≥ 4000` ve %85 olarak düzelt | belge |
| 10 | C.11 "%100 kare" | docstring'leri "as square as possible" yap | belge |

1–5 arası maddeler toplam ~40 satırdır ve bildirilen sayısal sonucu etkileyen
kusurların tamamını kapatır.

## C.16 Makale açısından sonuç

C bölümündeki doğrulama, projenin özgünlük iddiasını **zayıflatmamakta**,
tersine onu savunulabilir bir zemine oturtmaktadır. Ayırt edici iki teknik
unsur — hiyerarşik negatif-uzay budaması ve tamponsuz kontur mesafe yüklemi —
kaynak kodla doğrulanmış ve incelenen beş rakipte bulunamamıştır. Buna karşılık
bu unsurların çevresindeki ölçüm katmanı (dolgu kuralı, dejenere durum
raporlaması, ölçek penceresi, birim ayrıştırma) hâlihazırda yayımlanabilir
olgunlukta değildir.

Bu nedenle önerilen sıralama şudur: önce C.15'teki 1–5 maddeleri düzeltilmeli,
ardından EK BÖLÜM B.12'deki bilinen-değer ve değişmezlik testleri
çalıştırılmalı, sonuçlar bu düzeltmelerden **önce ve sonra** raporlanmalıdır.
Bu "önce/sonra" tablosu, makalenin doğrulama (validation) bölümünü tek başına
taşıyabilecek güçte bir kanıt oluşturur ve yazılım katkısının ciddiyetini
gösterir.

Kesin bir "ilk" veya "benzersiz" ifadesi bu bölümden de türetilmemektedir;
tespitler "incelenen kaynaklar ve okunan kaynak kodlar içinde doğrudan eşleşme
bulunamadı" düzeyinde tutulmuştur.

## C.17 Üretim kayıtları

Doğrulama betikleri: `C:\Users\RaşitNarçiçek\rakip_analiz\verify1.py` …
`verify6.py`. Her biri proje köküne geçici adla (`_v1_tmp.py` … `_v6_tmp.py`)
kopyalanıp çalıştırılmış ve aynı komut içinde silinmiştir.

Proje dizini denetimi: kalıcı olarak oluşturulan, değiştirilen veya silinen
dosya yoktur; `outputs/` altına hiçbir analiz paketi yazılmamıştır.
`backend/` dosyalarının değişiklik zamanları bu oturumdan öncedir.


---

# BÖLÜM D — DEPO, SÜRÜM, PROVENANCE VE TEST ALTYAPISI BULGULARI

Bu bölüm, kaynak kod okumasının ötesinde **yayımlanmış depo, sürüm kaydı ve
test altyapısı** üzerinde yapılan doğrulamaların sonuçlarıdır. Tümü
2026-08-07 tarihinde canlı uçlardan doğrulanmıştır.

## D.1 Yayın kimlikleri doğrulandı (olumlu bulgu)

Projenin ilan ettiği kalıcı kimliklerin üçü de **canlı ve geçerlidir**:

| Kimlik | Değer | Doğrulama |
|:---|:---|:---|
| Zenodo DOI | `10.5281/zenodo.21704656` | HTTP 200 → `https://zenodo.org/records/21704656`, başlık "RASH-HIT Fractal Studio" |
| Concept DOI | `10.5281/zenodo.21693694` | Zenodo API `conceptdoi` alanı |
| GitHub deposu | `rasitnarcicek/RASH-HIT-Fractal-Studio` | GitHub API 200, `private: false`, Apache-2.0 |
| ORCID | `0009-0005-3423-255X` | ORCID public API, ad "Mehmet Raşit Narçiçek" doğrulandı |

**Önem:** Bu, proje için **2026-07-29/30 tarihli belgelenebilir bir öncelik
(priority) tarihi** oluşturur. Özgünlük tartışmasında lehte kullanılabilir:
depo `created_at = 2026-07-29T21:56:37Z`, ilk sürüm `v1.0.0` aynı gün.

## D.2 BULGU 11 (Orta) — CITATION.cff sürümü ile yayımlanan DOI uyuşmuyor

| Kaynak | Sürüm |
|:---|:---|
| Yerel `CITATION.cff` | `version: "1.0.6"`, `date-released: "2026-07-30"` |
| DOI `10.5281/zenodo.21704656` çözümlenen kayıt | **v1.0.5** (`publication_date: 2026-07-30`) |
| GitHub `releases` listesi | en yüksek etiket **v1.0.5** (2026-07-30T13:42:37Z); v1.0.6 **yok** |

`CITATION.cff` v1.0.6 sürümünü ilan ederken, aynı dosyadaki DOI v1.0.5
kaydına işaret ediyor. Bir kullanıcı bu dosyayla atıf yaparsa, **elindeki
koddan farklı bir sürümü** atıflamış olur.

**Tekrarlanabilirlik açısından etkisi:** Projenin en güçlü iddialarından biri
"tam tekrarlanabilirlik". Atıf meta verisinin sürüm-DOI bağının kopuk olması
bu iddiayı doğrudan zayıflatır. Makale yazılacaksa **önce** v1.0.6 için ayrı
bir Zenodo sürümü basılmalı veya `CITATION.cff` v1.0.5'e çekilmelidir.

## D.3 BULGU 12 (Orta) — `intersection_cpu_area.py` ölü kod, ancak provenance'ta çekirdek katkı sayılıyor

`CODE_PROVENANCE.md` şunu beyan ediyor:

> `backend/intersection_cpu_area.py` | Mehmet Raşit Narçiçek | Original CPU **Exact Vector Geometry Engine**.

Kodun gerçeği (50 satır, bunun ~30'u gövde):

```python
def analyze_grid_cpu_area(...):
    hier_results, _ = analyze_grid_hierarchical(...)   # tum is burada
    for hr in hier_results:
        res = CPULevelResult(...)                       # sadece tip donusumu
    return results
```

Modül **hiçbir geometri hesabı yapmıyor**; `analyze_grid_hierarchical`
çağırıp sonucu `CPULevelResult` tipine kopyalayan bir adaptör.

Dahası, çağrı grafiği taraması `analyze_grid_cpu_area`'nın **üretimde hiç
çağrılmadığını** gösteriyor:

```
grep -rn "analyze_grid_cpu_area" --include=*.py .
  backend/intersection_cpu_area.py:19   (tanim)
  tests/test_full_project_contract.py:51 (yalnizca dosyanin VAR OLDUGUNU listeler)
```

**Çelişki:** v1.0.5 sürüm notları "Removed unreachable legacy backend modules
from the public runtime path" diyor; bu modül erişilemez olmasına rağmen
kalmış ve provenance'ta çekirdek özgün katkı olarak sayılmaya devam ediyor.

**Öneri:** Makalede mimari anlatılırken "Exact Vector Geometry Engine" adı
gerçek motora (`intersection_hierarchical.py`) verilmeli; bu dosya ya
silinmeli ya da adaptör olduğu açıkça yazılmalıdır.

## D.4 BULGU 13 (Yüksek) — Çekirdek hesaplama modüllerinin test kapsamı %0 (bağımsız kaynakla teyitli)

Depodaki **açık PR #10** (devin-ai-integration bot, 2026-08-02) şunu ölçmüş:

> Measured coverage of `backend/` with the existing suite (`pytest --cov=backend`):
> **25% overall**, with `intersection_hierarchical.py` and
> `intersection_cpu_area.py` at **0%**, `geometry_engine.py` at 28%,
> `artifact_validator.py` at 44%, `svg_loader.py` at 54%.

Bu, bu raporda bağımsız olarak bulunan kusurların **neden fark edilmediğini
açıklayan yapısal nedendir**: sayısal sonucu üreten iki modül
(hiyerarşik kesişim motoru ve alan modu) hiç çalıştırılmıyor.

Bu bulgu, C.3 (fill_rule hiç tanımlı değil), C.4 (dejenere regresyon
R²=1,0) ve C.5 (boş `pass` doyum denetimi) bulgularıyla **tutarlıdır** —
492 test bu hataların hiçbirini yakalamıyor.

**Kaynak:** https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio/pull/10
(erişim 2026-08-07, durum: açık/birleştirilmemiş)

## D.5 BULGU 14 (Orta) — Depoda birleştirilmemiş 4 düzeltme PR'ı bekliyor

2026-08-07 itibarıyla açık ve **birleştirilmemiş** düzeltmeler:

| PR | Konu | Önem |
|:---|:---|:---|
| #8 | `artifact_validator.py` XXE / decompression-bomb sertleştirmesi (stdlib `ElementTree` → `defusedxml`) | Güvenlik |
| #9 | Yutulan hataların yayılması: `run_analysis.py` export hatasında yine de **exit 0** dönüyordu | Doğruluk |
| #10 | En düşük kapsamlı modüllere test (%25 → %56) | Kalite |
| #11 | `academic_exporter.py` (~2k satır) yinelenen desenlerin ayrıştırılması | Bakım |

PR #9 özellikle önemlidir: **dışa aktarma başarısız olsa bile CLI başarı
kodu döndürüyordu.** Toplu (batch) akademik üretimde sessiz veri kaybı riski.
`svg_loader.py` zaten `defusedxml` kullanırken `artifact_validator.py`'nin
kullanmaması (PR #8) tutarsız bir güvenlik duruşudur.

## D.6 BULGU 15 (Yüksek) — Test paketi tamamlanıyor ancak 15 test **tekrarlanabilir biçimde başarısız**

> **Düzeltme notu:** Bu bölümün ilk taslağında "paket ~40 dakikadan uzun sürer"
> ve "toplam hata sayısı doğrulanamadı" denmişti. Her iki ifade de **yanlıştı**;
> paket iki bağımsız koşuda da sonuna kadar tamamlanmıştır. Aşağıdaki veriler
> ölçülmüş değerlerdir.

### Koşu sonuçları (projenin birebir kopyası, `~/rakip_analiz/_proje_kopya`)

| Koşu | Komut | Sonuç | Süre |
|:---|:---|:---|:---|
| 1 | `python -m pytest -q` | **15 failed, 432 passed, 45 skipped**, 22 subtest passed, 7 warning | 709,19 s (11 dk 49 sn) |
| 2 | `python -m pytest -v -p no:cacheprovider` | **15 failed, 433 passed, 44 skipped**, 22 subtest passed, 6 warning | 644,66 s (10 dk 44 sn) |

**Aynı 15 test her iki koşuda da başarısız** — sonuç deterministik, rastgele
(flaky) değil. `pytest-timeout` ve `pytest-xdist` kurulu değil; paralel
çalıştırma yok, bu nedenle ~11 dakikalık süre tek çekirdeğe bağlı.

### Kritik nitelendirme: hatalar çekirdek matematikte DEĞİL

Bu, özgünlük değerlendirmesi açısından **önemli bir ayrımdır**. Başarısız 15
testin hiçbiri kutu sayma, kesişim veya regresyon çekirdeğinde değildir;
tamamı arayüz sözleşmesi, i18n, belge tutarlılığı ve bir güvenlik kapısıdır.
`test_academic_engine.py`'deki altın örnek testleri (`test_golden_sample_db_range`,
16/16A/16B/16C → Db ∈ [1,5–2,0]) ve Phase 8 motor doğruluk testleri **geçmiştir**.

### Başarısız testlerin tam listesi ve nedenleri

| # | Test | Ölçülen neden |
|:--|:---|:---|
| 1 | `test_dead_css_audit.py::test_every_main_css_class_used_in_html_or_js` | Kullanılmayan CSS sınıfları kalmış |
| 2 | `test_docs_contract.py::test_checklist_counts_match_pytest_collection` | `docs/test_checklist.md`'deki sayı, gerçek test toplamıyla uyuşmuyor |
| 3 | `test_frontend_static_contract.py::test_all_js_ids_exist_in_html` | JS'in beklediği `['file-picker-btn', 'overwrite-hint']` id'leri HTML'de yok |
| 4 | `...::test_overwrite_checkbox_present_and_unchecked` | Aynı eksik id kümesi |
| 5 | `...::test_required_control_ids_present` | Aynı |
| 6 | `...::test_start_button_initially_disabled` | Aynı |
| 7 | `test_frontend_static_contract.py::TestDataTestIds::test_accordion_testids` | `data-testid` eşleşmiyor |
| 8 | `test_i18n_contract.py::TestLocaleParity::test_no_empty_values` | Locale sözlüğünde boş değer(ler) var |
| 9 | `...::test_tr_translation_differs_from_en_for_content` | Bazı TR girdileri EN ile birebir aynı (çevrilmemiş) |
| 10 | `...::TestFrontendWiring::test_i18n_js_defines_L_and_english_default` | `frontend/js/i18n.js` içinde `const DEFAULT_LANG = 'tr'`; sözleşme `'en'` bekliyor |
| 11 | `...::TestBackendI18nCore::test_t_returns_english_by_default` | Backend varsayılanı da EN değil |
| 12 | `...::TestBackendI18nCore::test_tr_translation_roundtrip` | TR gidiş-dönüş çevirisi bozuk |
| 13 | `test_live_server_api.py::test_dashboard_shell_served` | Canlı sunucu dashboard kabuğunu servis edemiyor |
| 14 | `test_phase8_negative_space_cache.py::test_high_level_artifacts_skipped` | Etiket uyuşmazlığı: üretilen `'L01 Map'`, beklenen `'Level 01 Map'` |
| 15 | `test_security_path_contract.py::test_small_in_cap_server_path_analyze_starts_job` | `0 != 1 : in-cap file must reach job dispatch` — **sınır içi dosya işe alınmıyor** |

### En ciddi iki kalem

**(a) #15 — güvenlik/boyut kapısı sözleşmesi bozuk.** Boyut sınırı *içindeki*
bir dosyanın iş kuyruğuna girmesi gerekirken girmiyor. Yani sınır denetimi
meşru girdileri de reddediyor. Bu, toplu (batch) akademik üretimde sessiz
atlama riskidir ve PR #9'daki "yutulan hata" bulgusuyla aynı aileden.

**(b) #10–#12 — i18n varsayılan dili çelişkisi.** `i18n.js` başındaki
docstring "EN is code-authoritative" ve "the default (no-JS) text is English"
diyor; hemen altındaki kod ise `const DEFAULT_LANG = 'tr'` tanımlıyor.
**Belge ile kod yine çelişiyor** — bu, C bölümündeki `fill_rule` ve "adaptif
eğri" uyuşmazlıklarıyla aynı desendir: docstring güncellenmeden kod değişmiş.

### Etkisi ve öneri

Paket 11 dakikada bitiyor, dolayısıyla "çalıştırılamaz" değil; ancak
**depo, 15 kırmızı testle yayımlanmış durumda** (v1.0.5, DOI'li sürüm).
Makale gönderiminde hakem depoyu klonlayıp `pytest` çalıştırırsa doğrudan
15 hata görecektir — bu, "tekrarlanabilir araştırma" iddiası için ciddi bir
zaaftır.

Öneri: (1) #15 ve #10–#12 gönderim öncesi düzeltilmeli; (2) `pytest-xdist`
ile paralelleştirme; (3) ağır uçtan-uca testler `@pytest.mark.slow` ile
ayrılmalı; (4) CI'da yeşil paket zorunlu hâle getirilmeli.

Not: D.4'teki %0 kapsam bulgusuyla birlikte okunmalıdır — çekirdek hesaplama
modülleri hiç çalıştırılmadığı için, bu 15 hata **çekirdekteki C bölümü
kusurlarını temsil etmez**; onlar hâlâ hiçbir test tarafından yakalanmıyor.

## D.7 Bu bölümün üretim kayıtları

| İşlem | Komut / uç | Tarih |
|:---|:---|:---|
| DOI çözümleme | `curl -sL https://doi.org/10.5281/zenodo.21704656` → 200 | 2026-08-07 |
| Zenodo meta | `https://zenodo.org/api/records/21704656` | 2026-08-07 |
| GitHub depo meta | `https://api.github.com/repos/rasitnarcicek/RASH-HIT-Fractal-Studio` | 2026-08-07 |
| Sürüm listesi | `.../releases` (6 sürüm, en yüksek v1.0.5) | 2026-08-07 |
| Issue/PR listesi | `.../issues?state=all` (13 kayıt) | 2026-08-07 |
| ORCID | `https://pub.orcid.org/v3.0/0009-0005-3423-255X/person` | 2026-08-07 |
| Test paketi (koşu 1) | `python -m pytest -q` → 15 failed/432 passed, 709,19 s | 2026-08-07 |
| Test paketi (koşu 2) | `python -m pytest -v -p no:cacheprovider` → 15 failed/433 passed, 644,66 s | 2026-08-07 |
| Ölü kod taraması | `grep -rn "analyze_grid_cpu_area" --include=*.py .` | 2026-08-07 |
