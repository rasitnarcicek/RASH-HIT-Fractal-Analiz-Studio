
## B.3 SVG'yi gerçekten kim okuyor?

**FracPaQ.** SVG desteği bir XML ayrıştırıcısı değil, satır bazlı metin
aramasıdır (`convertSVG2txt_colour2.m`). Dosya `readtext(fName, '>', ...)`
ile bölünür ve `strfind`/`contains` ile etiket aranır. Desteklenmeyen komutlar
açıkça atlanır:

```matlab
SVG_cmd_pattern = ["A", "C", "H", "Q", "V", "S", "T", "Z"] ;
if contains(upper(sPoints), SVG_cmd_pattern)
    disp('***Error: SVG <path has non-M command. FracPaQ cannot read this line, skipping') ;
    continue ;
```

Buna göre desteklenmeyenler: Bézier eğrileri (C/S/Q/T), yaylar (A), H/V
kısayolları, Z kapatma, **küçük harfli (bağıl) koordinatlar**, `transform=`
özniteliği (depoda hiç aranmıyor), `viewBox`, `<g>` grup dönüşümleri, CSS
`<style>` blokları ve `<rect>`/`<circle>`/`<ellipse>` öğeleri. Renk okuması
yalnızca 6 haneli hex ile sınırlıdır; `stroke="red"` veya `rgb()` çalışmaz.
Ayrıca ayrıştırıcı satır sonu biçimine bağımlıdır
(`if strcmp(sThisLine(end), '/')`), dolayısıyla tek satıra sıkıştırılmış
(minified) SVG'lerde kırılır.

**FractDim.** SVG ayrıştırma tamamen Apache Batik'e devredilmiştir
(`SquareCounter.java:140-153`, `TranscoderInput` / `FDTranscoder`); kendi yol
ayrıştırıcısı yoktur. Ancak `FDGraphics2D.java:39,48` grafik bağlamındaki
dönüşümü bilinçli olarak yok sayar:

```java
private final AffineTransform rawTransform = AffineTransform.getScaleInstance(1.0d, 1.0d);
PathIterator pit = s.getPathIterator(rawTransform);
```

**Fractalyse 3, GeoFractalLines, Multiscale-BC.** Hiçbiri SVG okumaz.
İlki GeoPackage/GeoJSON/Shapefile, diğer ikisi QGIS katmanı
(`iface.activeLayer()`, `QgsProcessingParameterVectorLayer`) gerektirir.

**RASH-HIT.** Kendi SVG yükleyicisi (`backend/svg_loader.py`) ve dönüşüm
motoru bulunur; `backend/geometry_engine.py:28` belgelenmiş kapsam:
"Supports matrix, translate, scale, rotate, skewX, skewY." Ayrıca
`backend/svg_health.py` ile girdi uygunluk denetimi yapılır.

**Değerlendirme.** İncelenen kaynaklar içinde, SVG'yi tam yol ve dönüşüm
semantiğiyle ayrıştırıp bu vektör geometri üzerinde doğrudan kesin geometrik
kutu sayımı yapan bir sisteme rastlanmamıştır. Kesin kesişim yapanlar CBS
formatı istemekte; SVG okuyanlar (FractDim, FracPaQ) ise kesin kesişim
yapmamakta ve SVG'yi eksik ayrıştırmaktadır. Bu, kesin bir "ilk" iddiası
değil, incelenen küme içinde doğrudan eşleşme bulunamadığı yönünde ölçülü
bir tespittir.

## B.4 Uzamsal hızlandırma ve hiyerarşik budama

| Sistem | Uzamsal indeks | Hiyerarşik budama |
|---|---|---|
| FracPaQ | Yok (daire×iz×segment üçlü döngü + N×N kesişim matrisi) | Yok |
| FractDim | Yok (`GridSquareStore` düz HashSet/TreeSet) | Yok |
| GeoFractalLines | Yok (kesişim yapmadığı için gerekmiyor) | Yok |
| Multiscale-BC | `QgsSpatialIndex` var | Yok — n×n hücre düz taranır |
| Fractalyse 3 | Harici `FeatureCoverage` zarf indeksi var | Yok — yalnız iki sezgisel algoritma seçimi |
| **RASH-HIT** | **STRtree (toplu vektörize)** | **Var — negatif uzay önbelleği** |

RASH-HIT'in `backend/intersection_hierarchical.py` başlığında belgelenen kural:

```
EMPTY parent  -> children skipped (safe: if parent misses geometry, children do too).
PARTIAL/NON-EMPTY -> subdivided into 4 children, each re-evaluated exactly.
FULL shortcut NOT used (caused overcounting vs CPU baseline for dense SVGs).
```

Ek olarak sayım döngüsü Python düzeyinde değil, toplu C++ çağrılarıyla
yürütülür: `shapely.box(dizi)` → `STRtree.query(cell_array)` →
`shapely.intersects()` ufunc.

İncelenen beş rakip sistemin hiçbirinde boş uzayın hiyerarşik olarak
budanması bulunmamaktadır. Bu, yöntemsel değil **algoritmik/yazılımsal** bir
katkıdır ve ölçülebilir niteliktedir: aynı kesin GEOS sonucunu üretirken
gereken kesin kesişim testi sayısını düşürür. Makalede savunulabilecek en
somut teknik katkı budur.

`FULL shortcut NOT used` yorumunun kodda açıkça belgelenmiş olması, budama
kuralının doğruluk lehine muhafazakâr seçildiğini göstermektedir; bu, makalede
bilinçli bir tasarım kararı olarak sunulabilir.

## B.5 Lisans uyumluluğu uyarısı

FractDim ve Fractalyse **GPLv3** lisanslıdır. FractDim'de ayrı bir LICENSE
dosyası bulunmamakla birlikte lisans `code/modules/pom.xml:8-14` içinde ve her
`.java` dosyasının başlığında açıkça tanımlıdır ("Copyright (c) 2009, 2010,
2011 Daniel Rendall … GNU General Public License … version 3"). Fractalyse'de
de lisans `pom.xml` ve dosya başlıklarındadır.

RASH-HIT Apache-2.0 lisanslıdır (kaynak dosyalarındaki SPDX başlıkları:
`SPDX-License-Identifier: Apache-2.0`, `Copyright 2026 Mehmet Raşit Narçiçek`).
GPL bulaşıcı (copyleft) bir lisans olduğundan, bu iki depodan **kod
kopyalanmamalıdır**; aksi hâlde projenin lisansının değiştirilmesi gerekir.
Mekanizmaların okunup bağımsız olarak yeniden uygulanması ve kaynak gösterilmesi
uygundur. QGIS tabanlı iki depo ve FracPaQ MIT lisanslıdır; hukuken daha
esnektir, ancak yine bağımsız uygulama önerilir.

Ayrıca FractDim'in akademik bir rakip olmadığı belirtilmelidir: README'si tek
satırdır ve "fractal dedication" (dimension değil) yazmaktadır; kişisel bir
projedir. Buna karşın SVG + kutu sayma birleşiminin 2011'de denendiğinin
kanıtıdır ve literatür taramasında **prior art** olarak alıntılanmalı, neden
yetersiz kaldığı (dolgu yok sayma, nokta örnekleme, dönüşüm yok sayma)
belirtilmelidir.
