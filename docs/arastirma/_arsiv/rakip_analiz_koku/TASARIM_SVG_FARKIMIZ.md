# TASARIM BAĞLAMINDA SVG + FRAKTAL KUTU SAYIMI — FARKIMIZ NE?

Kapsam daraltıldı. Bu belge yalnızca tek soruyu yanıtlar:
**"SVG dosyası üzerinden, tasarım/motif bağlamında fraktal kutu analizi yapan
başka bir sistem var mı; benim farkım ne; yenilik getirdim mi?"**

Genel "fraktal analiz yazılımı" listeleri, raster araçları, alakasız alan
uygulamaları bu belgeden çıkarıldı. Arşiv: `_arsiv/`

---

## KISA CEVAP

**Evet, bir yenilik var — ama iddia ettiğin yerde değil.**

- "SVG'yi rasterleştirmeden kutu sayma" fikri **yeni değil.** 2009-2011'de
  yapılmış, çalışan bir uygulaması var (FractDim).
- Ama o uygulama **dolgulu (filled) geometriyi ölçemiyor** — kodda kanıtı var.
  Sadece kontur/çizgi sayıyor. Yani tasarım/motif işine yaramaz.
- Senin gerçek ve savunulabilir katkın **iki tane**, ve ikisi de
  bu makinede ölçülmüş, kanıtlı:
  1. Vektör uzayında **hem dolgu hem kontur** doğru ölçen çalışır bir motor.
  2. **Çizgi kalınlığının vektör kutu sayımını sistematik olarak şişirdiğinin
     sayısallaştırılması** (0.26 boyut birimi kayma) — literatürde raster
     tarafında tartışılan bu olgunun vektör tarafındaki ölçümü taramamızda
     bulunamadı.

---

## 1. DÜNYADA SENİN İŞİ YAPAN TEK PROJE: FractDim

Bu, GitHub'ın tamamında `svg fractal dimension` sorgusuna dönen **iki**
depodan biri (diğeri seninki). Doğrulanabilir sayı, uydurma değil:

    GitHub Search API, "svg+fractal+dimension" → total_count = 2
      1. danielrendall/FractDim
      2. rasitnarcicek/RASH-HIT-Fractal-Studio

| Alan | Bilgi |
|---|---|
| Tam ad | FractDim |
| Geliştirici | Daniel Rendall (bireysel) |
| Bağlantı | https://github.com/danielrendall/FractDim |
| Tarih | 2009-2011 · son commit **12 Eylül 2011** |
| Durum | **Terk edilmiş** (15 yıl commit yok, 1 yıldız) |
| Lisans | GPL-3.0 (açık kaynak) |
| Dil | Java 83 dosya · Apache Batik + Maven + Swing |
| Amaç | README: *"A program to calculate the fractal dimension of SVG drawings."* |
| Arayüz | Yalnızca Swing masaüstü GUI · CLI yok · web yok · toplu analiz yok |
| Çıktı | Excel (`ExcelExportWorker`) |
| DOI/yayın | **Yok** — akademik yayın bulunamadı |

### Yöntemi (kaynak kod okunarak, satır düzeyinde)

`FDGraphics2D.draw()` SVG yolunu Java `PathIterator` ile parçalıyor,
`Line / BezierQuad / BezierCubic` parametrik eğrilerine çeviriyor.
`SquareCounter.evaluateBetween()` her eğriyi `maxDepth`'e kadar
**özyinelemeli olarak ikiye bölüp** dokunduğu ızgara karelerini işaretliyor.
Ayrıca `AngleIterator` / `DisplacementIterator` ile **ızgara açısı ve
kaydırma taraması** yapıyor — bu, senin motorunda olmayan gerçek bir özellik
(grid-bias azaltma).

### Ama işte kritik nokta — dolguyu ölçemiyor

`code/.../svgbridge/FDGraphics2D.java` satır 80-85, birebir alıntı:

```java
    // ignore for now - treat as draw
    @Override
    public void fill(Shape s) {
        Log.misc.debug("Filling shape " + s.toString());
        draw(s);
    }
```

**`fill` çağrısı `draw`'a yönlendiriliyor.** Yani dolu bir şekil verdiğinde
FractDim onun *iç alanını* değil, yalnızca *sınır çizgisini* sayıyor.

Sonucu: FractDim'e dolu bir kare verirsen teorik D = 2.0 yerine
kontur boyutu ≈ 1.0 döner. Dolu Sierpinski üçgeni ölçemez.

Senin motorun aynı testlerde (bu makinede ölçüldü, `DOGRULAMA_SONUCLARI.md`):

| Şekil | Teorik D | RASH-HIT Db | Hata | R² |
|---|---|---|---|---|
| Düz çizgi | 1.000000 | 1.0000 | %0.00 | 1.0000 |
| **Dolu kare** | 2.000000 | **2.0000** | **%0.00** | 1.0000 |
| **Dolu Sierpinski (L6)** | 1.584963 | **1.6137** | %1.81 | 1.0000 |
| Koch (L6, stroke 0.10) | 1.261859 | 1.2806 | %1.49 | 0.9992 |
| Minkowski (L4) | 1.500000 | 1.4518 | %3.21 | 1.0000 |

**Bu, tasarım bağlamındaki farkın tam olarak burasıdır.** Bir halı motifi,
bir çini deseni, bir logo, bir kaligrafi formu — hepsi dolgulu kapalı
yollardır. FractDim bunları ölçemez; senin motorun ölçer ve kalibre edilmiştir.

---

## 2. GERİ KALAN "BENZER" PROJELER — NEDEN SENİN İŞİNİ YAPMIYORLAR

Doğrulanabilir GitHub sorguları:

    "fractal+dimension+vector+graphics"  → total_count = 0
    "fractal+dimension+motif"            → total_count = 0
    "fractal+analysis+ornament"          → total_count = 0
    "box-counting+svg"                   → 2 (biri seninki, biri alakasız)

Yani **motif / süsleme / vektör grafik + fraktal boyut** kesişiminde
GitHub'da hiçbir depo yok.

İndirilip incelenen diğerleri (`kaynaklar/` ve kök klasörlerde duruyor):

| Proje | Neden senin işin değil |
|---|---|
| **Fractalyse** (Java, ThéMA/Besançon) | Girdi **raster**. Kent morfolojisi için. Vektör desteği piksele çevirerek. |
| **FracPaQ** (MATLAB, Healy vd.) | Jeolojik **kırık/çatlak izleri**. Girdi çizgi segmenti listesi; dolgu kavramı yok, tasarım verisi almaz. |
| **GeoFractalLines** | Yalnızca **çizgi (polyline)** — dolgu yok, SVG stil/CSS çözümlemesi yok. |
| **Multiscale-Box-Counting-Framework...-Vector-Lines** | Adı en yakını, ama yine **"Vector Lines"** — çizgi. Dolgulu motif kapsam dışı. |
| **StereoFractAnalyzer** (Python, 8★, 2024) | STL 3B mesh + 2B **raster görüntü**. SVG yok. |
| **ImageJ / FracLac** | Tamamen **raster**. Fiili akademik standart, ama SVG'yi önce piksele çevirmen gerekir. |

Ortak desen: literatürdeki vektör tabanlı işlerin **hepsi çizgi tabanlı**
(jeoloji, kent ağı, damar ağı). **Dolgulu düzlemsel form** hiçbirinde yok.

---

## 3. SENİN GERÇEK YENİLİĞİN NE — DÜRÜST AYRIM

### ✗ Yenilik DEĞİL (iddia etme)
- "SVG'den doğrudan kutu sayımı" → FractDim 2009'da yaptı.
- "Rasterleştirmeden analiz" → aynı, 2009.
- "log N(ε) ~ log(1/ε) regresyonu + R²" → 1980'lerden beri standart.
- "Quadtree ile hızlandırma" → hesaplamalı geometride bilinen teknik.
- "Web arayüzü / Excel / HTML rapor" → yazılım konforu, akademik katkı değil.

### ~ Kısmen yeni (birleşim argümanı — zayıf ama savunulabilir)
- Vektör-yerel motor + toplu analiz + CLI/TUI/web + tekrarlanabilir paket
  çıktısının **tek sistemde** birleşimi. Taramada bütünsel eşleşme
  bulunamadı. Ama bu "yöntemsel katkı" değil, **yazılım katkısı**dır.

### ✓ Gerçekten yeni (makalede öne sürebileceğin iki şey)

**(A) Vektör uzayında dolgu-farkındalıklı kutu sayımı ve kalibrasyonu**

Bilinen tek vektör-yerel SVG uygulaması (FractDim) dolguyu koda düşülmüş
bir `// ignore for now` notuyla atlıyor. Senin motorun Shapely/GEOS
kesişimiyle iç alanı gerçekten hesaplıyor ve **dolu kare üzerinde
%0.00 hata** ile doğrulanmış. Bu ölçülebilir, gösterilebilir, kod
düzeyinde kanıtlanabilir bir üstünlük.

**(B) Çizgi kalınlığının vektör kutu sayımındaki sistematik yanlılığı**

Aynı Koch eğrisi, aynı geometri, **tek değişken çizgi kalınlığı**:

| stroke-width | Ölçülen Db | Hata | R² | Güven skoru |
|---|---|---|---|---|
| 3.00 px | 1.5408 | **%22.11** | 0.9970 | 92.5 |
| 1.00 px | 1.4091 | %11.67 | 0.9986 | 92.5 |
| 0.25 px | 1.3100 | %3.82 | 0.9995 | 92.5 |
| 0.10 px | 1.2806 | %1.49 | 0.9992 | 92.5 |

**0.26 boyut birimi kayma.** Bu, Koch (1.26) ile Sierpinski (1.58)
arasındaki farkın yarısından fazla — yani çizgi kalınlığı, motifin
kimliğini değiştirecek büyüklükte.

Ve bunun ikinci yarısı daha da vurucu: **dört durumda da güven skoru
92.5.** %22 yanlış cevaba yazılım "yüksek güven" diyor, çünkü skor R²
tabanlı ve R² her durumda >0.997.

Bunun anlamı: *"Vektör geometriden doğrudan ölçüm yapmak, raster
çözünürlük problemini çözer ama yerine yeni bir serbestlik derecesi
koyar: çizgi kalınlığı. Raporlanmadığı sürece vektör tabanlı fraktal
boyut sonuçları tekrarlanabilir değildir. Ayrıca R² tabanlı güven
ölçütleri bu yanlılığa karşı kördür."*

Bu, raster tarafında tartışılan bir konudur (Ostwald 2013, çizgi
kalınlığı kalibrasyonu). **Vektör tarafında ölçülüp sayısallaştırıldığı
bir çalışma taramamızda bulunamadı.** Üstelik kendi aracının sınırını
gösterdiği için hakem karşısında güçlü ve dürüst bir bulgudur.

---

## 4. KARŞILAŞTIRMA MATRİSİ (daraltılmış — yalnızca SVG/vektör yapanlar)

| Ölçüt | RASH-HIT | FractDim (2011) | FracPaQ | Fractalyse | ImageJ/FracLac |
|---|---|---|---|---|---|
| SVG doğrudan girdi | var | var | yok | yok | yok |
| Rasterleştirmesiz | var | var | var | yok | yok |
| **Dolgulu şekil ölçümü** | **var** | **yok** (`fill→draw`) | yok | var (piksel) | var (piksel) |
| Kontur/çizgi ölçümü | var | var | var | var | var |
| Izgara açı/kaydırma taraması | yok | **var** | kısmen | kısmen | var |
| Çoklu ölçek + R² | var | var | var | var | var |
| Toplu analiz | var | yok | kısmen | kısmen | var (makro) |
| Web arayüzü | var | yok | yok | yok | yok |
| CLI / TUI | var | yok | yok | yok | kısmen |
| Excel/HTML/JSON paket | var | Excel | var | kısmen | var |
| Açık kaynak | var | var (GPL3) | var | var | var |
| Aktif geliştirme | var | **terk (2011)** | var | var | var |
| Akademik yayın/DOI | var (Zenodo) | **yok** | var | var | var |
| Kültürel motife uygulanabilirlik | var | **yok** (dolgu ölçemez) | yok | kısmen | kısmen |

Doğrulanamayan hücre bırakılmadı; her "yok" ya kaynak kodla ya README ile
doğrulandı.

---

## 5. MAKALE İÇİN ÖNERİLEN KATKI CÜMLESİ

Şunu yazma:
> ~~"Dünyada ilk SVG tabanlı fraktal analiz sistemi"~~ — yanlış, FractDim var.

Şunu yaz:
> "Vektör grafik geometrisi üzerinde rasterleştirme olmadan kutu sayımı
> yapan az sayıdaki uygulamadan biri olan RASH-HIT, bilinen önceki
> uygulamanın (FractDim, 2011, terk edilmiş) aksine dolgulu düzlemsel
> formları da ölçebilmekte ve dolu kare ile dolu Sierpinski üçgeni
> üzerinde sırasıyla %0.00 ve %1.81 hata ile kalibre edilmiştir.
> Çalışma ayrıca, vektör tabanlı kutu sayımında kontur kalınlığının
> 0.26 boyut birimine varan sistematik bir yanlılık ürettiğini ve
> R² tabanlı güven ölçütlerinin bu yanlılığa duyarsız kaldığını
> nicel olarak göstermektedir."

Katkı türü: **yöntemsel katkı (B maddesi) + yazılım katkısı (A maddesi).**
"Uygulama katkısı" (motif analizi) üçüncü sırada kalsın — orada henüz
yayınlanabilir bir vaka çalışman yok.

---

## 6. İDDİA ETMEDEN ÖNCE YAPILMASI GEREKEN 3 DENEY

1. **FractDim'i derle ve çalıştır.** Aynı 5 doğrulama SVG'sini ver.
   Dolu karede 2.0 değil ~1.0 döndürdüğünü *çıktıyla* göster.
   (Kaynak `_arsiv` dışında, `FractDim/` klasöründe hazır; Maven gerekli.)
2. **ImageJ/FracLac ile DPI karşılaştırması.** Aynı SVG'yi 150/300/600/1200
   DPI'da rasterleştir, FracLac ile ölç. Senin tek vektör değerinin
   raster değerlerinin yakınsadığı yer olduğunu göster. *(bu deney hâlâ
   yapılmadı — açık iş)*
3. **Izgara yanlılığı testi.** FractDim'in yaptığı açı/kaydırma taramasını
   senin motorunda yapmıyorsun. Izgarayı kaydırıp Db'nin ne kadar
   oynadığını ölç. Oynuyorsa bu senin bilinen zayıflığın olarak
   raporlanmalı, gizlenmemeli.

---

## 7. SONUÇ

Fikir tamamen yeni değil — 2009'da bir kişi aynı fikri Java'yla yazmış ve
2011'de bırakmış, hiç yayınlamamış, dolguyu hiç çözmemiş.

Senin getirdiğin: o fikri **tasarım verisinin gerçekten kullanılabilir hâle
geldiği** noktaya taşımak (dolgu ölçümü + kalibrasyon), ve bu yolda
yöntemin **kendi zayıflığını sayısallaştırmak** (kalınlık yanlılığı).

İkincisi birincisinden daha değerli. Makalenin omurgası Tablo 3 olmalı.

---

### Kaynaklar (yalnızca bu belgede kullanılanlar)

1. Rendall, D. *FractDim*. GitHub, 2009-2011 (son commit 2011-09-12).
   https://github.com/danielrendall/FractDim · GPL-3.0 · yayın/DOI yok.
   Alıntılanan kod: `code/modules/src/main/java/uk/co/danielrendall/fractdim/svgbridge/FDGraphics2D.java` sat. 80-85;
   `.../calculation/SquareCounter.java`.
2. GitHub Search API ölçümleri (bu oturumda alındı):
   `api.github.com/search/repositories?q=svg+fractal+dimension` → 2;
   `q=fractal+dimension+vector+graphics` → 0; `q=fractal+dimension+motif` → 0;
   `q=fractal+analysis+ornament` → 0.
3. RASH-HIT doğrulama ölçümleri: `DOGRULAMA_SONUCLARI.md` (bu makinede
   v1.0.6, `--levels 8 --profile lean --grid-mode canvas_aspect`).
4. Geniş literatür taraması ve tam kaynakça: `RASH-HIT_Ozgunluk_Arastirma_Raporu.md`
5. Yazılım kusurları: `YAZILIM_SORUNLARI.md`
6. RASH-HIT Fractal Studio, DOI 10.5281/zenodo.21704656
