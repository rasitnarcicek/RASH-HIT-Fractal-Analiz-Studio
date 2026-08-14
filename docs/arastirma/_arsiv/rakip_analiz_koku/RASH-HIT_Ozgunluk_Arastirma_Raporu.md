# RASH-HIT Fractal Studio — Özgünlük ve Benzer Sistemler Araştırma Raporu

Tarih: 2026-08-07 · Hazırlayan: Hermes Agent
Kapsam: Proje kod incelemesi (salt-okunur) + yazılım ekosistemi + akademik literatür + kültürel miras/tekstil alanyazını
NOT: Proje dosyalarında hiçbir değişiklik yapılmamıştır. Bu rapor proje klasörünün DIŞINA yazılmıştır.

**KANONİK KONUM (2026-08-07 itibarıyla):**
`C:\Users\RaşitNarçiçek\rakip_analiz\RASH-HIT_Ozgunluk_Arastirma_Raporu.md`
Bundan sonraki tüm güncellemeler bu dosyada yapılır. Masaüstündeki kopya
(`Desktop\RASH-HIT_Ozgunluk_Arastirma_Raporu.md`) artık **arşivdir**, güncellenmez.

Aynı çalışma dizinindeki destekleyici materyal:
- Klonlanmış rakip kaynak kodları: `FracPaQ/`, `Fractalyse/`, `FractDim/`,
  `GeoFractalLines/`, `Multiscale-Box-Counting-Framework-.../`
- Doğrulama betikleri: `verify1.py` … `verify6.py` (EK BÖLÜM C kanıtları)
- Deney çıktıları: `shift_dbg/`, `shift_out/`, `spyout/`, `shift_test/`
- Yardımcı betikler: `gm.py`, `gm2.py`, `gm3.py`, `gridbias.py`, `spy.py`
- Bölüm taslakları: `ekB_1..5.md`, `ekC_1..5.md`

İncelenen proje (SALT OKUNUR, değiştirilmez):
`C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio`

---

## 0. EN ÖNEMLİ BULGULAR (özet maddeler)

> ### 🔴 3. TUR — RAPORUN EN KRİTİK TEK BULGUSU
>
> **Douglass, R. (2025), *Fractal and Fractional* 9(10):633, DOI 10.3390/fractalfract9100633** (yayın 29 Eylül 2025, MDPI, hakemli, CC-BY) özetinde birebir şunu yazmaktadır:
> *"Unlike traditional pixelated approaches that suffer from rasterization artifacts, the method used directly analyzes geometric line segments."*
>
> Bu, RASH-HIT'in Zenodo öncelik tarihinden (**29 Temmuz 2026**) **yaklaşık 10 ay ÖNCEDİR**. Dolayısıyla **"rasterizasyonsuz doğrudan geometrik kutu sayma" bir YÖNTEM YENİLİĞİ olarak artık iddia edilemez.** Bu DOI ana oturumda Crossref'ten bağımsız teyit edilmiştir.
>
> **Sonuç:** Katkının ağırlık merkezi *yeni yöntem* → ***yazılım + uygulama (kültürel motif) katkısı*** olarak kaydırılmalıdır. Ayrıntı: **EK BÖLÜM D.1** ve **Bölüm 15.A**.
>
> **TAM METİN OKUNDU (bkz. `kaynaklar/ANALIZ_Douglass_2025_vs_RASHHIT.md`).** İki önceki kayıt düzeltilmiştir:
> (a) Douglass'ın **kodu açıktır** — github.com/rwdlnk/Fractal-Dimension-Analyzer (Python3). "Paket bulunamadı" kaydı YANLIŞTI.
> (b) Kesişim motoru **Liang–Barsky çizgi kırpma** + hiyerarşik uzamsal bölümlemedir; Shapely/GEOS değil, poligon desteği yoktur.
>
> Buna karşılık Douglass, yazarın kendi ifadesiyle *"limited to two-dimensional line segment analysis"*tir: **alan poligonlarını kapsamaz**, girdi olarak **hiçbir tasarım dosya formatı (SVG/DXF/EPS/AI) okumaz** — tam metinde "SVG" kelimesi **0 kez** geçer; veri, kod içinde üretilen segment listesidir. Uygulama alanı matematiksel fraktaller ve akışkan arayüzüdür; tasarım/tekstil/motif hiç geçmez.
>
> **Douglass'ın BİZDEN ÜSTÜN olduğu 3 nokta (kabul edilmeli):** otomatik ölçek aralığı seçimi (sliding window — makalenin ana katkısı), grid offset optimizasyonu, doğrulama titizliği (5 fraktal, R²≥0.9988, Koch %0.11 hata).

- Vektör/SVG geometrisi üzerinde **doğrudan** kutu sayma yapan sistemler VARDIR — yani "dünyada ilk" denemez. Ancak bulunanlar ya çok dar (yalnız çizgi geometrisi) ya ölü ya da farklı dilde/alanda.
- En ciddi rakip: **Fractalyse 3** (ThéMA, Univ. Franche-Comté; Java, GPL). Sitesi birebir "bitmap images, VECTOR images and networks" diyor. Olgun, akademik, aktif.
- Bilinen tek diğer **SVG-doğrudan** araç: **FractDim** (Daniel Rendall, Java, GitHub) — "calculate the fractal dimension of SVG drawings". Son commit 2011, lisanssız → fiilen terk edilmiş.
- 2026'da çıkan **roko-gis** ailesi (Multiscale Box-Counting for Vector Lines, GeoFractalLines, GeoFractBox1D — Python, MIT, Zenodo DOI'li) RASH-HIT ile aynı dönemde ve aynı "rasterizasyonsuz vektör" felsefesinde; ama yalnız ÇİZGİ geometrisi. İstatistiksel doğrulamaları (bootstrap CI, BY-FDR, multifraktal spektrum) RASH-HIT'ten güçlü.
- Klasik baseline'ların TAMAMI raster-only: ImageJ FracLac, ImageJ Fractal Box Count, Benoit, HarFA, CRAN fractaldim/fractD, MATLAB boxcount (Moisy)/hausDim, porespy.
- Literatürde en yakın yöntemsel akrabalar: **Roy, Perfect, Dunne & McKay (2007)** kırık ağlarında çizgi-segment/kutu kesişimi; **Bouda, Caplan & Saiers (2016)** kök sistemlerinde segment tabanlı, kuantizasyon hatasını yapısal olarak yok eden box-counting; **FracPaQ** (MATLAB, vektör çatlak desenleri).
- Kültürel miras/motif alanında taranan 13 çalışmanın 12'si RASTER girdi kullanıyor (ImageJ/FracLac, ArchImage). Vektör kullanan iki istisna (L-sistem çalışmaları) fraktal boyut ÖLÇMÜYOR, desen ÜRETİYOR.
- Aramalarda "fractal dimension shapely" sorgusunun tek anlamlı sonucu RASH-HIT'in kendisi oldu; "fractal dimension geopandas / vector shapefile / dxf" → sonuç yok.
- Dolayısıyla ölçülü ifade: **"İncelenen kaynaklar içinde, genel amaçlı SVG geometrisini (CSS+stil çözümleme, affine transform, Bézier/arc düzleştirme) tam olarak ayrıştırıp poligon+çizgi karışık geometride kesin GEOS kesişim predikatlarıyla, STRtree + quadtree negatif-alan budamasıyla kutu sayımı yapan ve tekrarlanabilirlik manifestosu üreten ikinci bir sistem bulunamadı."**
- Kritik boşluk: YÖK Ulusal Tez Merkezi ve DergiPark bot/JS koruması nedeniyle taranamadı. Türkiye'de yayımlanmamış bir tezin benzer yaklaşımı denemiş olma ihtimali **elenemedi**.

---

## 1. YÖNETİCİ ÖZETİ

RASH-HIT Fractal Studio, SVG vektör geometrisini rasterize etmeden kutu sayma (box-counting) fraktal boyutu hesaplayan, Python tabanlı, akademik çıktı paketi üreten bir araştırma yazılımıdır. Araştırma, projenin temel fikrinin (raster-free vektör box-counting) daha önce uygulanmış olduğunu, ancak RASH-HIT'in özelleştiği bileşim — tam SVG semantiği + kesin GEOS predikatları + hiyerarşik budama + bileşik güven skoru + tekrarlanabilirlik manifestosu + motif odaklı raporlama — açısından doğrudan bir eşleşme bulunmadığını göstermektedir.

Özgünlük iddiası "yöntemsel buluş" olarak değil, **yazılım/mühendislik katkısı + uygulama katkısı** olarak kurulmalıdır. Yöntemsel katkı iddiası ancak raster-vs-vektör sistematik karşılaştırma deneyi ve Fractalyse/FracLac ile birebir kıyaslama yapıldıktan sonra savunulabilir.

### 1.1 İKİNCİ TUR DERİN DOĞRULAMA — EN ÖNEMLİ DÖRT BULGU (ayrıntı: EK BÖLÜM A)

Bu bulgular rakip araçların **kaynak kodu/resmi kılavuzu birebir okunarak** ve RASH-HIT **canlı çalıştırılıp ölçülerek** elde edilmiştir; ilk turdaki değerlendirmeleri önemli ölçüde RASH-HIT lehine düzeltmektedir.

1. **Fractalyse 3 SVG'yi GİRDİ olarak KABUL ETMİYOR.** Resmi kılavuz (manual-en.pdf, 2022) yalnızca GeoPackage / GeoJSON / Shapefile kabul ettiğini yazıyor; SVG onda sadece çıktı formatıdır. Yani "en ciddi rakip" bir SVG aracı değil, coğrafi veri aracıdır. Bu, Bölüm 4'teki A-1 değerlendirmesini yumuşatır.
2. **FractDim SVG'yi okur ama kendi mantığı yoktur ve yöntemi farklıdır.** Kaynak kod: SVG ayrıştırma tamamen Apache Batik 1.7'ye devredilmiş; `fill()` çağrısı `draw()`'a yönlendirilip **dolgular yok sayılmış** ("treat as draw" yorumu); **transform yığını uygulanmıyor** (`AffineTransform.getScaleInstance(1,1)` birim matris); doluluk kararı kesin kesişim değil **nokta örneklemesi + adaptif bisection**; uzamsal indeks/quadtree yok; 2011'den beri ölü ve lisanssız.
3. **Ölçülen hız (bu makinede, 16D.svg 426 KB):** L8 sayım 1.5 s · L9 4.8 s · **L10 (8.388.608 kutu, 3.110.338 dolu) sayım 15.8 s, 10 seviyenin tümü 24.6 s**; Db=1.8229, R²=0.9997, güven 100/100. Tüm dosya/paket üretimi dahil L10 toplam 81.5 s (uç senaryo). Buna karşılık **ne FractDim'in ne Fractalyse'ın yayımlanmış tek bir sayısal hız ölçümü yoktur** — alanda wall-clock benchmark geleneği neredeyse hiç yok.
4. **Uygulama alanı ayrışması net:** Fractalyse=kentsel/coğrafi, Roy/FracPaQ/roko-gis=jeoloji, Bouda=botanik, FracLac/ArchImage=raster görüntü ve mimari cephe. **RASH-HIT=tasarım alanı (vektörel tasarım öğeleri, illüstrasyon, motif).** İncelenen kaynaklar içinde tasarım SVG'lerini birincil hedef alan vektör-yerli, kesin kesişimli bir fraktal analiz aracı bulunamadı.

---
## 2. İNCELENEN PROJENİN TEKNİK TANIMI

### 2.1 Kod incelemesinden çıkarılan mimari

Kök: `C:\Users\RaşitNarçiçek\Desktop\ANTİGRAVİTY\RASH-HIT Fraktal Studio` (208 dosya; node_modules/.git hariç). Apache-2.0, CITATION.cff, Concept DOI 10.5281/zenodo.21693694, Version DOI 10.5281/zenodo.21704656, ORCID 0009-0005-3423-255X.

Boru hattı (kaynak koddan doğrulandı):

1. `backend/svg_loader.py` — defusedxml ile güvenli XML ayrıştırma (XXE sertleştirme), `<style>` CSS bloğu çözümleme (tinycss2, regex yedeği), sınıf/inline stil/presentation attribute öncelik kuralları, görünmez eleman filtreleme, clipPath/mask/fill-rule tespiti ve uyarı kaydı.
2. `backend/geometry_engine.py` (545 satır) — path komutları M,L,H,V,C,S,Q,T,A,Z + rect, circle, ellipse, line, polyline, polygon ayrıştırma; `parse_transform_string` ile matrix/translate/scale/rotate/skewX/skewY → 3×3 homojen matris yığını; kübik/kuadratik Bézier ve eliptik yay düzleştirme; Shapely `Polygon`/`LineString` + `unary_union`.
3. `backend/grid_planner.py` — analiz sınır kutusu, AR=W/H, `canvas_aspect` modunda **her hücrenin %100 kare** olmasını sağlayan (cols₁, rows₁) türetimi; `square_bbox`/`square_canvas` alternatifi; her seviye için ε = max(cell_w,cell_h)/max(W,H) ve log(1/ε).
4. `backend/intersection_hierarchical.py` (570 satır) — vektörleştirilmiş quadtree motoru: `shapely.box(...)` ile tüm hücreler tek C++ çağrısında; `STRtree.query(cell_array)` toplu sorgu; `shapely.intersects()` ufunc'ları; aktif ebeveyn kümesi NumPy (M,2) int32; **budama kuralı: yalnız BOŞ ebeveyn budanır** (FULL kısayolu bilinçli olarak KULLANILMIYOR — yorum satırında yoğun SVG'lerde fazla sayıma yol açtığı belirtilmiş). Round-based early-exit ile yinelenen (hücre,geometri) çiftleri GEOS'a gönderilmiyor. ThreadPoolExecutor ile paralellik. "negative-space cache" metrikleri (candidate_count, active_growth_rate, empty_descendants_skipped_estimate, storage_mode: raw|rle|summary_only|svg_only) denetlenebilir biçimde raporlanıyor.
5. `backend/intersection_cpu_area.py` / `intersection_cpu.py` — hiyerarşik motoru saran alan-modu arayüzü; AABB-only karar YOK, gerçek fill/stroke teması.
6. `backend/regression.py` (327 satır) — log₁₀(N(r)) − log₁₀(1/r) en küçük kareler; ölçek tablosu (level, grid_label, box_size, inv_box_size, occupied, total, log değerleri, `included_in_fit`, `exclusion_reason`); N(r)=0 olan seviyeler dışlanıyor; saf SVG log-log grafiği üretimi.
7. `backend/confidence.py` — 0–100 bileşik güven skoru: R² %40 + geçerli ölçek sayısı %30 + SVG sağlık skoru %30; "Yüksek/Orta/Düşük" etiketi, akademik yorum ve öneri metni; `MotifProfile` (karmaşıklık sınıfı, doğrusal yoğunluk, boşluk-doluluk dengesi, ölçek tutarlılığı) — Türkçe etiketli.
8. Çıktı katmanı — `academic_exporter.py`, `backend/export/html_templates/*`, `artifact_validator.py`, `output_profiles.py` (lean/standard/full), `package_index.py`, `batch_processor.py`: report.html/pdf/md, workbook.xlsx (ExcelJS), tables (CSV/XLSX/ASCII/JSON), **saf vektör SVG ızgara haritaları**, `manifest.json` (SHA-256), `terminal.txt`, `result.json`.
9. Arayüzler — `run_analysis.py` (CLI: -i/-o/-m fast|balanced|precise|academic|batch /-l/-p/-e cpu|gpu), `backend/tui.py` (TUI), `backend/web_server.py` + `frontend/` (REST + web stüdyo), `bin/rash-hit.js` (npm launcher), `locales/tr.json|en.json` + `backend/i18n.py` (TR/EN).
10. Kalite altyapısı — `tests/` (pytest), `.github/workflows/codeql.yml`, dependabot, `.githooks/pre-commit`, lisans/citation/locale doğrulayıcı scriptler, CODE_PROVENANCE.md, THIRD_PARTY_NOTICES.md, 41 KB CHANGELOG.

### 2.2 150–250 kelimelik teknik tanım (arama sorguları bundan türetildi)

> RASH-HIT Fractal Studio, ölçeklenebilir vektör grafiklerinin (SVG) fraktal boyutunu rasterizasyona başvurmadan hesaplayan, araştırma sınıfı bir Python yazılımıdır. Sistem, SVG belgesini CSS stil blokları, sınıf ve satır içi stiller, görünürlük kuralları ve 2B afin dönüşüm yığınlarıyla birlikte çözümler; Bézier eğrilerini ve eliptik yayları düzleştirerek Shapely/GEOS poligon ve çizgi geometrilerine dönüştürür. Ardından tuval en-boy oranını dikkate alan, hücreleri tam kare olacak biçimde türetilmiş çok seviyeli bir ızgara serisi üretir ve her hücrenin doluluğunu piksel testiyle değil, kesin geometrik kesişim predikatlarıyla belirler. Hesaplama, STRtree uzamsal indeksi ve boş ebeveyn bloklarının çocuklarını eleyen hiyerarşik quadtree "negatif alan" budamasıyla hızlandırılır; budama yalnızca kanıtlanabilir biçimde boş bölgelerde uygulandığı için sonuç, kaba kuvvet kesin sayımla eşdeğer kalır. Doluluk sayıları log-log en küçük kareler regresyonuna sokularak kutu sayma boyutu Db ve uyum kalitesi R² elde edilir; ölçek tablosu, dışlanan ölçekler ve gerekçeleri açıkça raporlanır. Regresyon uyumu, geçerli ölçek sayısı ve SVG yapısal sağlığını birleştiren 0–100 aralığında bileşik bir güven skoru ile sonucun akademik kullanılabilirliği değerlendirilir. Yazılım; toplu analiz, HTML/PDF/Markdown/Excel/CSV raporlama, saf vektör ızgara haritaları, SHA-256 sağlama toplamlı tekrarlanabilirlik manifestosu, web arayüzü, komut satırı ve terminal arayüzü ile Türkçe-İngilizce yerelleştirme sunar.

---

## 3. ARAŞTIRMA YÖNTEMİ VE KULLANILAN SORGULAR

Yöntem: (a) salt-okunur kod incelemesi, (b) üç paralel araştırma kolu (yazılım ekosistemi / akademik metodoloji / kültürel miras-tekstil).

Kullanılan erişim kanalları: GitHub Search API, PyPI JSON API, CRAN paket sayfaları, Zenodo API, MATLAB File Exchange, imagej.net, doğrudan ürün siteleri; Crossref API, OpenAlex API, Semantic Scholar API, arXiv.

Örnek sorgular: "fractal dimension SVG", "vector box counting", "fractal analysis dxf", "fractal dimension shapely", "fractal dimension geopandas", "box counting quadtree acceleration", "raster free fractal dimension", "exact intersection box counting", "fracture network box counting line segments", "cartographic line fractal dimension", "automatic scale range selection box counting", "fractal dimension carpet motif", "fractal analysis Islamic geometric pattern", "fractal dimension ornament textile", "kutu sayma fraktal boyut", "fraktal boyut motif", "mimari cephe fraktal boyut".

Erişilemeyen kaynaklar (açıkça belirtilir): Google/Bing/DuckDuckGo bu makinede engelli; Brave Search CAPTCHA verdi. **tez.yok.gov.tr** JS-gated (arama yapılamadı), **dergipark.org.tr** doğrudan aramada 302/bot koruması, SourceForge dizin araması JS-gated, Semantic Scholar hız sınırı. Bu nedenle YÖK tez taraması YAPILAMAMIŞTIR ve hiçbir tez numarası verilmemiştir.

---
## 4. DOĞRUDAN BENZER YAZILIMLAR (Kategori A)

### A-1. Fractalyse 3 — EN CİDDİ RAKİP
- Geliştirici: Gilles Vuidel; araştırma ekibi Pierre Frankhauser, Cécile Tannier (ThéMA, Univ. Franche-Comté, Besançon)
- URL: https://thema.univ-fcomte.fr/productions/software/fractalyse/ (HTTP 200 ile doğrulandı)
- Kaynak: `git clone https://git.renater.fr/anonscm/git/fractalyse/fractalyse.git` · Açık kaynak: EVET (GPL) · Dil: Java 8+ · DOI: Doğrulanamadı
- Yöntem: Kutu sayma, korelasyon, radyal analiz. **Site birebir "bitmap images (raster), VECTOR images and networks" diyor.**
- Veri türleri: raster, vektör, ağ. Amaç: kentsel doku/mimari fraktal analizi.
- Benzerlik: Vektör girdi + box-counting + GUI + akademik kullanım. Kategori A.
- Fark: SVG CSS/inline stil çözümleme, affine transform yığını, Bézier/arc düzleştirme, Shapely/GEOS `intersects()`, STRtree+quadtree negatif-alan budaması, 0-100 güven skoru, SHA-256 manifest, TR/EN i18n, CLI/TUI/web REST YOK. Java, Python değil.
- Önemi: Kıyaslama (benchmark) için ZORUNLU referans. Durum: Aktif (2024 ISTE-Wiley kitap atfı). Güvenilirlik: Çok yüksek.

### A-2. FractDim — Daniel Rendall
- URL: https://github.com/danielrendall/FractDim · Java · Lisans YOK (belirtilmemiş)
- Oluşturma 2010-12-18, son push 2011-09-12 → **terk edilmiş (≈15 yıl)**
- Depo açıklaması birebir: "Application to calculate the fractal dimension of SVG drawings."
- Benzerlik: Bilinen TEK diğer **SVG-doğrudan** box-counting aracı. Kategori A.
- Fark: Rapor/istatistik/güven skoru/manifest yok, GEOS predikatı yok, ölü ve lisanssız (yeniden kullanılamaz).
- Önemi: "SVG box-counting fikri daha önce denenmiş" kanıtı — ancak RASH-HIT'in "aktif, lisanslı, üretim kalitesinde tek SVG motoru" konumunu güçlendirir. Güvenilirlik: Orta (metadata doğrulandı, akademik yayın yok).

### A-3. Multiscale Box-Counting Framework for Fractal Dimension Analysis of Vector Lines
- Geliştirici: roko-gis · https://github.com/roko-gis/Multiscale-Box-Counting-Framework-for-Fractal-Dimension-Analysis-of-Vector-Lines
- DOI: 10.5281/zenodo.20685864 (2026-06-14) · Python · MIT · son push 2026-07-01 · AKTİF
- Yöntem: Vektör çizgilerde box-counting + ensemble istatistik + BY-FDR çoklu test düzeltmesi + scale-block bootstrap güven aralığı.
- Benzerlik: Rasterizasyonsuz vektör box-counting, Python, açık kaynak, DOI'li, tekrarlanabilirlik vurgusu. Kategori A.
- Fark: Yalnız LINE geometrisi (poligon/alan, SVG semantiği, CSS, Bézier yok). Buna karşılık istatistiksel doğrulaması RASH-HIT'in R²+güven skorundan **daha güçlü**.
- Önemi: RASH-HIT ile aynı dönemde ortaya çıkan en yakın çağdaş; makalede mutlaka tartışılmalı.

### A-4. GeoFractalLines v1.0.0
- roko-gis (Ranguelov & Iliev ekolü) · https://github.com/roko-gis/GeoFractalLines · DOI: 10.5281/zenodo.20960565 (2026-06-27) · Python/QGIS · MIT · AKTİF
- Yöntem: Adaptif box-counting + **multifraktal spektrum** + CSR testleri, vektör hat geometrisi.
- Fark: RASH-HIT'te multifraktal spektrum yok → belirgin eksik. Kategori A/B sınırı.

### A-5. GeoFractBox1D
- Ranguelov, Boyko; Iliev, Rosen · DOI: 10.5281/zenodo.21099450 (2026-07-01) · Python · MIT · 1B vektör hat box-counting. Kategori B.

### A-6. FracPaQ
- Healy, D.; Rizzo, R.E.; Cornwell, D.G.; Farrell, N.J.C. ve ark., 2017, Journal of Structural Geology 95:1-16 · DOI: 10.1016/j.jsg.2016.12.003
- MATLAB, açık kaynak. Vektör (traced polyline) çatlak desenlerinde uzunluk dağılımı, yoğunluk, yönelim, fraktal ölçekleme.
- Benzerlik: RASH-HIT'in en yakın **yayınlanmış yazılım** muadili — vektör girdi + açık kaynak + tekrarlanabilirlik. Kategori A/B.
- Fark: MATLAB (ticari platform), jeoloji-özel, GEOS predikatı/quadtree budama/genel SVG desteği/güven skoru yok.

---

## 5. İLİŞKİLİ AÇIK KAYNAK PROJELER (Kategori B/E — hepsi raster veya nokta/voksel)

| # | Ad | Geliştirici | Dil/Lisans | Son güncelleme | Girdi | Kategori |
|---|---|---|---|---|---|---|
| 1 | ImageJ **FracLac** | A. Karperien (Charles Sturt Univ.); Jelinek, Buchan, T.R. Roy katkıları | Java / ImageJ açık kaynak | ~2013 (v2.5) | Yalnız binary/gri RASTER | B |
| 2 | ImageJ dahili *Fractal Box Count* | NIH / W. Rasband | Java / public domain | Aktif (ImageJ1) | RASTER | B |
| 3 | CRAN **fractaldim** v0.8-5 | H. Sevcikova, D. Percival, T. Gneiting | R / GPL-2\|3 | 2021-10-07 | Zaman serisi + 2B veri | B |
| 4 | CRAN **fractD** v0.1.0 | F.P. Mancuso | R / GPL-3 | 2021-02-05 | 2B/3B dilim görüntü (imager) → RASTER | B |
| 5 | MATLAB FEX **boxcount** | F. Moisy | MATLAB | 2006-07-10 (~22.2K indirme) | 1B/2B/3B dizi | B |
| 6 | MATLAB FEX **hausDim** | A. Costa | MATLAB | 2011 | Binary görüntü | B |
| 7 | **porespy** 3.0.4 | PMEAL (J. Gostick grubu) | Python / MIT | AKTİF | 3B voksel | E |
| 8 | **boxcounting** (PyPI 1.0.0.3) | Phoenixfire1081 | Python / MIT | 2024-04-24 | Moisy portu, dizi | B |
| 9 | **sphractal** (PyPI 1.1.17) | Jon-Ting | Python / MIT | 2026-08-04 AKTİF | 3B örtüşen küre yüzeyleri | B |
| 10 | **StereoFractAnalyzer** | comp-comb / kmmukut | Python / MIT | 2024-04-03 | **STL 3B MESH** + 2B görüntü | B (3B'de rasterizasyonsuz muadil) |
| 11 | brian-xu/FractalDimension | B. Xu | Python / MIT (31★) | 2020 | RASTER | E |
| 12 | AndriyGonda/dbc | A. Gonda | Python | 2019 | Differential box counting, raster | E |
| 13 | lsaravia/mfsba | L. Saravia | C++ (8★) | 2016 | Multifraktal, raster | E |
| 14 | MultifractalTools.jl | — | Julia | 2026-08-06 AKTİF | Multifraktal | E |
| 15 | nolds / antropy | — | Python MIT/BSD | Aktif | Zaman serisi (Higuchi, korelasyon boyutu) | E |

**Negatif bulgular (RASH-HIT lehine kanıt):**
- GitHub "fractal analysis dxf" → 0 anlamlı sonuç (DXF/CAD üzerinde doğrudan box-counting paketi yok).
- "fractal dimension shapely" → tek anlamlı sonuç RASH-HIT'in kendisi.
- "fractal dimension geopandas", "fractal dimension vector shapefile" → 0 sonuç.
- PyPI'de `boxcount`, `fractal-dimension`, `pyfracdim`, `fractal-analysis` paketleri MEVCUT DEĞİL (404).
- Hugging Face'te box-counting fraktal boyut modeli/space'i yok.
- SourceForge dizini JS-gated → **Doğrulanamadı**.

---

## 6. TİCARİ ARAÇLAR

| Ad | Sağlayıcı | Erişim | Durum |
|---|---|---|---|
| **Benoit** | TruSoft International | https://www.trusoft-international.com/ (200); /benoit.html içerik boş döndü | Ticari, kapalı kaynak, Windows; raster + zaman serisi. Ürün detayları ve güncellik **Doğrulanamadı**; uzun süredir güncellenmemiş görünüyor. |
| **HarFA** (Harmonic and Fractal Image Analyzer) | VUT Brno, Image Science | http://imagesci.fch.vut.cz/ (200); ?content=harfa alt sayfası 404 | Freeware/kapalı, Windows, raster-only box-counting + harmonik analiz. Muhtemelen terk edilmiş; **Doğrulanamadı**. |
| **ArchImage** | M.J. Ostwald / J.H. Lee ekolü | Yayınlarda atıflı, kamuya açık indirme bağlantısı **Doğrulanamadı** | Mimari cephe fraktal analizi; raster girdi. Kültürel miras literatüründe fiilî standart. |
| **MATLAB** platformu | MathWorks | mathworks.com | boxcount/hausDim scriptleri ücretsiz ama platform ticari — tekrarlanabilirlik engeli (RASH-HIT lehine argüman). |

Hiçbir ticari araçta doğrudan SVG vektör geometrisi üzerinde kesin kesişim tabanlı box-counting belgelenememiştir.

---
## 7. AKADEMİK MAKALELER

Aşağıdaki kayıtların başlık/yazar/yıl/DOI bilgileri Crossref/OpenAlex API'lerinden **canlı sorgulanarak** doğrulanmıştır. Hiçbir DOI uydurulmamıştır.

### 7.1 Klasik temeller (Kategori B)
1. **Mandelbrot, B.B. (1967)** "How Long Is the Coast of Britain? Statistical Self-Similarity and Fractional Dimension", *Science* 156(3775):636-638. DOI 10.1126/science.156.3775.636 — Pergel (divider) yöntemi, kartografik **poliçizgi (vektör)** verisi. Benzerlik: vektör üzerinde doğrudan ölçüm fikrinin kurucusu. Fark: kutu sayma değil; regresyon kalitesi/güven yok. Güvenilirlik: çok yüksek.
2. **Liebovitch, L.S.; Toth, T. (1989)** "A fast algorithm to determine fractal dimensions by box counting", *Physics Letters A* 141(8-9):386-390. DOI 10.1016/0375-9601(89)90854-2 — bit-interleaving/anahtar sıralama ile O(N log N); **örtük quadtree hızlandırma**. Benzerlik: RASH-HIT quadtree budamasının kanonik atfı. Fark: yalnız nokta kümeleri; poligon kesişim predikatı yok. Kategori B — **RASH-HIT makalesinde atıf ZORUNLU**.
3. **Sarkar, N.; Chaudhuri, B.B. (1994)** "An efficient differential box-counting approach to compute fractal dimension of image", *IEEE Trans. SMC* 24(1):115-120. DOI 10.1109/21.259692 (öncülü ICPR 1992, DOI 10.1109/icpr.1992.201575) — DBC, tamamen raster. Önemi: RASH-HIT'in karşı-tez referansı (kuantizasyon hatasının kaynağı).
4. **Buczkowski, S.; Kyriacos, S.; Nekka, F.; Cartilier, L. (1998)** "The modified box-counting method: Analysis of some characteristic parameters", *Pattern Recognition* 31(4):411-418. DOI 10.1016/s0031-3203(97)00054-x (öncülü Fractals 1994, DOI 10.1142/s0218348x94000417) — ızgara ofseti/başlangıç artefaktı. Benzerlik: RASH-HIT'in kare-hücre ızgara tasarımıyla aynı kaygı.

### 7.2 Ölçek aralığı, yanlılık ve regresyon kalitesi (Kategori B — RASH-HIT güven skorunun dayanağı)
5. **Gonzato, G.; Mulargia, F.; Marzocchi, W. (1998)** "Practical application of fractal analysis: problems and solutions", *Geophysical Journal International* 132(2):275-282. DOI 10.1046/j.1365-246x.1998.00461.x — sonlu ölçek aralığı, ızgara konumu, doygunluk; otomatik "scaling window" seçimi. **Otomatik ölçek seçimi için birincil referans.**
6. **Gonzato, G.; Mulargia, F.; Ciccotti, M. (2000)** "Measuring the fractal dimensions of ideal and actual objects…", *GJI* 142(1):108-116. DOI 10.1046/j.1365-246x.2000.00133.x — Koch/Sierpinski üzerinde sistematik hata. Benzerlik: RASH-HIT'in analitik SVG referans şekilleriyle doğrulama stratejisiyle birebir.
7. **Foroutan-pour, K.; Dutilleul, P.; Smith, D.L. (1999)** "Advances in the implementation of the box-counting method of fractal dimension estimation", *Applied Mathematics and Computation* 105(2-3):195-210. DOI 10.1016/s0096-3003(98)10096-6 — en büyük/en küçük kutu sınırlarının nesnel seçimi. Uygulamalı box-counting'in en çok atıflı metodoloji makalesi.
8. **Bouda, M.; Caplan, J.S.; Saiers, J.E. (2016)** "Box-Counting Dimension Revisited: Presenting an Efficient Method of Minimizing Quantization Error and an Assessment of the Self-Similarity of Structural Root Systems", *Frontiers in Plant Science* 7:149. DOI 10.3389/fpls.2016.00149 — kök sistemleri **3B çizgi-segment (vektör) modeli** olarak işlenir; kuantizasyon hatası yapısal olarak elenir. **RASH-HIT'in en güçlü "önceki sanat" (prior art) referansı — makalede mutlaka tartışılmalı.** Fark: GEOS predikatı/STRtree/SVG boru hattı/alan poligonları yok.
9. **Nayak, D.R.; Mishra, R. ve ark. (2021)** "Fractal dimension-based generalized box-counting technique with application to grayscale images", *Fractals* 29(3):2150055. DOI 10.1142/s0218348x21500559 — modern raster hattının hâlâ kuantizasyon hatasıyla uğraştığının kanıtı.
10. **Feng, J.; Lin, W.-C.; Chen, C.-T. (1996)** "Fractional box-counting approach to fractal dimension estimation", ICPR'96. DOI 10.1109/icpr.1996.547197 — kısmi doluluk oranıyla sayım; RASH-HIT'in kesin kesişim hesabına kavramsal öncül, ama hâlâ piksel ızgarasında yaklaşık.
11. **Cutler, C.D. (1993)** "A review of the theory and estimation of fractal dimension", *Dimension Estimation and Models*, World Scientific. DOI 10.1142/9789814317382_0001 — log-log EKK regresyonunun yanlılığı/tutarlılığı; güven skorunun teorik dayanağı.

### 7.3 Vektör/çizgi geometrisi üzerinde kutu sayma — EN YAKIN YÖNTEMSEL KOMŞULAR (Kategori A/B)
12. **Roy, A.; Perfect, E.; Dunne, W.M.; McKay, L.D. (2007)** "Fractal characterization of fracture networks: An improved box-counting technique", *JGR: Solid Earth* 112:B12201. DOI 10.1029/2006jb004582 — kırık ağları **çizgi segmentleri olarak**; kutu-segment kesişimi doğrudan hesaplanır; kesme etkileri, ölçek aralığı, lakünarite. **Metodolojik olarak RASH-HIT'e en yakın makale.** Fark: yalnız çizgi ağları, uzamsal indeks/quadtree yok, ölçek seçimi manuel, yazılım/manifest yok.
13. **Bonnet, E.; Bour, O.; Odling, N.E.; Davy, P.; Main, I.; Cowie, P.; Berkowitz, B. (2001)** "Scaling of fracture systems in geological media", *Reviews of Geophysics* 39(3):347-383. DOI 10.1029/1999rg000074 — sonlu-boyut etkileri, örnekleme yanlılığı, geçerli ölçek penceresi.
14. **Muller, J.-C. (1986)** "Fractal Dimension and Inconsistencies in Cartographic Line Representations", *The Cartographic Journal* 23(2):123-130. DOI 10.1179/caj.1986.23.2.123 · ve **(1987)** "Fractal and Automated Line Generalization", 24(1):27-34. DOI 10.1179/caj.1987.24.1.27 — sayısal harita **vektör poliçizgileri** üzerinde fraktal boyut (SVG path'lere doğrudan analog).
15. **Klinkenberg, B. (1994)** "A review of methods used to determine the fractal dimension of linear features", *Mathematical Geology* 26(1):23-46. DOI 10.1007/bf02065874 — aynı çizgisel vektör veride divider/kutu/varyogram/spektral yöntemlerin FARKLI D vermesi. **Raster-vs-vektör karşılaştırma bölümünün temel referansı.**
16. **Goodchild, M.F. (1980)** "Fractals and the accuracy of geographical measures", *J. IAMG* 12(2):85-98. DOI 10.1007/bf01035241 — çözünürlüğe bağlı ölçüm hatasının teorik çerçevesi.
17. **Sevcik, C. (2006)** "On fractal dimension of waveforms", *Chaos, Solitons & Fractals* 28(2):579-580. DOI 10.1016/j.chaos.2005.07.003 — ızgarasız, geometriye doğrudan uygulanan tahmin (1B).
18. **Yang, H.; Chen, W.; Qian, T.; Shen, D. ve ark. (2015)** "The Extraction of Vegetation Points from LiDAR Using 3D Fractal Dimension Analyses", *Remote Sensing* 7(8):10815-10831. DOI 10.3390/rs70810815 — oktree benzeri uzamsal bölmeyle hızlandırma; nokta verisi.
19. **Malleswar, S.D.; Isoda, Y.; Nakaya, T. (2025)** "Box Height-Independent Differential Bar Cumulation (DBC) for 3D Raster Surface Fractal Dimension Analysis", *J. Geovisualization and Spatial Analysis*. DOI 10.1007/s41651-025-00216-5 — raster hattının süregelen zaafı.
20. 🔴 **Douglass, R. (2025)** "Automated Box-Counting Fractal Dimension Analysis: Sliding Window Optimization and Multi-Fractal Validation", ***Fractal and Fractional* 9(10):633**, yayın tarihi **29 Eylül 2025**, CC-BY. **DOI 10.3390/fractalfract9100633** (Crossref'ten doğrulandı: journal-article, MDPI, 2 atıf almış). Preprint sürümü: DOI 10.20944/preprints202508.1392.v1 (Ağustos 2025).
    - **ÖNCEKİ DEĞERLENDİRME DÜZELTİLDİ:** Bu kayıt raporun önceki turlarında "hakemsiz preprint, güvenilirlik DÜŞÜK" olarak işaretlenmişti. **Bu yanlıştır** — çalışma hakemli bir dergide yayımlanmıştır. Güvenilirlik: **YÜKSEK**.
    - Özetten birebir alıntı: *"Unlike traditional pixelated approaches that suffer from **rasterization artifacts**, the method used **directly analyzes geometric line segments**, providing superior accuracy for mathematical fractals..."*
    - Yöntem: Üç fazlı algoritma — ızgara ofset optimizasyonu + sınır artefaktı tespiti + kayan pencere (sliding window) ile **otomatik ölçek bölgesi seçimi**, manuel parametre ayarı olmadan. Koch, Sierpinski, Minkowski, Hilbert, Dragon eğrileriyle doğrulama; tüm optimize sonuçlarda **R² ≥ 0.9988**, Koch'ta %0.11 hata.
    - **RASH-HIT açısından önemi: BU, PROJENİN EN CİDDİ ÖNCEKİ SANAT (PRIOR ART) KAYNAĞIDIR.** RASH-HIT'in Zenodo öncelik tarihi 2026-07-29'dur; Douglass 2025 bundan **yaklaşık 10 ay ÖNCE** yayımlanmıştır. "Rasterizasyonsuz, doğrudan geometri üzerinde kutu sayma" fikri **yöntem düzeyinde önceIenmiştir**.
    - Ayrışan yönler (RASH-HIT lehine kalan): SVG girdi boru hattı (CSS/inline stil, affine transform, Bézier/arc düzleştirme), Shapely/GEOS `intersects` predikatı, **alan poligonları** (Douglass yalnızca çizgi segmentleri), STRtree uzamsal indeks, paketlenmiş açık kaynak dağıtım (CLI/TUI/web REST), SHA-256 manifest, toplu analiz, i18n. Douglass'ta yayımlanmış bir **yazılım paketi tespit edilememiştir** (**Doğrulanamadı**).
    - **Zorunlu eylem:** Makalede/README'de atıf verilmeli, karşılaştırma matrisine alınmalı ve mümkünse sayısal kıyaslama yapılmalıdır. "İlk/tek" dili kesinlikle kullanılmamalıdır.

### 7.4 Hızlı kutu sayma algoritmaları — "hiyerarşik hızlandırma" iddiasının önceki sanatı (Kategori B)

Bu alt bölüm 3. turda eklenmiştir; tüm DOI'ler Crossref'ten doğrulanmıştır. Toplu bulgu: **hiyerarşik/ağaç tabanlı box-counting hızlandırması 35 yıllık yerleşik bir literatürdür.**

21. **Hou, X.; Gilmore, R.; Mindlin, G.; Solari, H. (1990)** "An efficient algorithm for fast box counting", *Physics Letters A*. DOI 10.1016/0375-9601(90)90844-E — Liebovitch & Toth 1989'un hemen ardından gelen ikinci klasik hızlı algoritma.
22. **Kruger, A. (1996)** "Implementation of a fast box-counting algorithm", *Computer Physics Communications*. DOI 10.1016/0010-4655(96)00080-X
23. **Alevizos, P.; Vrahatis, M. (2010)** "Optimal Dynamic Box-Counting Algorithm", *Int. J. of Bifurcation and Chaos*. DOI 10.1142/S0218127410028197
24. **Mukundan, R. (2015)** "Parallel Implementation of the Box Counting Algorithm in OpenCL", *Fractals*. DOI 10.1142/S0218348X15500231 — GPU paralelleştirme.
25. **Nikolaidis, N.; Nikolaidis, I. (2016)** "The box-merging implementation of the box-counting algorithm", *J. of the Mechanical Behavior of Materials*. DOI 10.1515/jmbm-2016-0006
26. **Gonzato, G. (1998)** "A practical implementation of the box counting algorithm", *Computers & Geosciences*. DOI 10.1016/S0098-3004(97)00137-4 — Gonzato'nun ikinci, **yazılım odaklı** makalesi (raporun 5 numaralı GJI makalesinden farklıdır).
27. **Wang Chengdong; Ling Dan; Miao Qiang (2010)** "Automatic identification of fractal scaling region in GP algorithm", ICACIA 2010. DOI 10.1109/ICACIA.2010.5709897 — **otomatik ölçek aralığı seçimi**; güven skoru iddiasının önceki sanatı.
28. **Balel, Y.; Sağtaş, K. (2025)** "Single-click automated fractal analysis for dental radiographs: a comparative evaluation with classic ImageJ...", *BMC Oral Health*. DOI 10.1186/s12903-025-05932-4 — 2015 sonrası "tek tık otomatik" fraktal analiz aracı örneği; birleşik güven skoru içerdiğine dair kanıt yok.
29. **Karperien, A.; Jelinek, H.F. (2016)** "ImageJ in Computational Fractal-Based Neuroscience...", DOI 10.1007/978-1-4939-3995-4_32 (2024 güncellemesi: DOI 10.1007/978-3-031-47606-8_40) — FracLac'ın çoklu ızgara konumu, ortalama D, standart sapma ve r² raporladığının kanıtı: **çok metrikli kalite raporlaması zaten vardır**, ancak tek skalar skora indirgenmez.

---

## 8. YÜKSEK LİSANS VE DOKTORA TEZLERİ

**GÜNCELLEME (3. tur):** tez.yok.gov.tr ve ProQuest hâlâ erişilemez (JS-gated / abonelik duvarı). Ancak **OpenAlex `type:dissertation`** ve **Crossref `filter=type:dissertation`** API'leri üzerinden sistematik tarama YAPILMIŞTIR. Aşağıdaki kayıtlar API çıktısından birebir alınmıştır.

### 8.1 Tarama istatistiği (OpenAlex `type:dissertation`, başlık araması)

| Sorgu | Sonuç sayısı |
|---|---|
| `fractal dimension` | 117 |
| `box counting` | 9 (yalnızca 4'ü gerçek box-counting; kalanı terim çakışması) |
| `fractal ornament` | **1** (Kargic 2016) |
| `fractal textile` | **0** |
| `fractal motif` | **0** |
| `fractal carpet design` | **0** |
| `fractal facade` | **0** |

**Kategori A'da (doğrudan benzer) HİÇBİR tez bulunamamıştır.**

### 8.2 Alan bakımından en yakın tez (Kategori C/D)

**Kargic, Lejla (2016)** — "Application of Fractal Geometry Principles in Traditional Persian, Ottoman and Bosnian Sacral Architecture Ornaments", International Burch University (Saraybosna). http://eprints.ibu.edu.ba/3609/ · OpenAlex W2611320133 · DOI yok.
- Osmanlı/İslam **süsleme (ornament)** motiflerinde fraktal geometri. Box-counting kullanıp kullanmadığı ve veri türü **Doğrulanamadı** (tam metin çekilmedi).
- **Neden C:** RASH-HIT'in hedef alanıyla (Osmanlı/İslam süslemesi, kültürel miras) örtüşen tespit edilebilen tek tez. Ancak yazılım geliştirmemiştir, ölçüm motoru yoktur.
- **Önemi:** Alan konumlandırması için zorunlu atıf.

### 8.3 Yöntem bakımından en yakın tezler (Kategori B)

| Yazar / Yıl | Başlık | DOI/Kaynak | Veri türü | Neden B |
|---|---|---|---|---|
| **Backes, André Ricardo (2006)** | Implementation and comparison of fractal dimension estimative methods and their use on analysis and image processing | DOI yok (OpenAlex) | Raster | Farklı fraktal boyut kestirim yöntemlerinin **karşılaştırmalı implementasyonu** — RASH-HIT'in yazılım karşılaştırma bölümü için en değerli metodoloji tezi |
| **Röman, Jan R. M. (1995)** | Characterization of real fractal objects: analysis of the box-counting approach... | DOI yok | Raster/agregat | Box-counting'in doğruluk/kalibrasyon analizi; ölçek aralığı ve güven skoru bölümünün dayanağı |
| **Fiedler, Reno (1995)** | Application of the box-counting method in evaluating statistical homogeneity in rock masses | DOI yok | Çizgi ağı haritaları | Süreksizlik **çizgi ağları** üzerinde kutu sayma — RASH-HIT'in çizgi geometrisi yaklaşımına metodolojik komşu |
| **Dubuc, Benoit (1988)** | On estimating fractal dimension | 10.82308/19360 | — | Kestirim yöntemleri klasiği (variation method) |
| **Elicker, Craig T. (1994)** | Fractal analysis of images | 10.17918/00007575 (Drexel Univ.) | Raster | Görüntü tabanlı fraktal analiz |
| **Pinto, Silvia C. D. (2001)** | Estimating fractal dimension of SPM images | DOI yok | Raster | — |
| **Machado (—)** | Texture analysis using complex system models: fractal dimension, swarm systems and non-linear diffusion | 10.11606/t.55.2016.tde-24112016-113253 (USP) | Raster | **Doku (texture)** sınıflandırmada fraktal boyut — tekstil dokusu analizine bulunan en yakın tez |
| **Deal (—)** | Fractal analysis of fingerprints | 10.33915/etd.1852 (West Virginia Univ.) | Raster | Çizgisel desen (ridge pattern) analizi; motif analizine kavramsal yakınlık |

> ⚠ **Doğrulanamadı:** Winger, Kevin Ralph (2025), "Quantifizierung der Morphologie der Tumorinvasionsfront ... mittels der fraktalen Box-Counting-Dimension DB", DOI 10.25358/openscience-14974 — bu DOI Crossref'te **"Resource not found"** döndürmüştür (yerel repo DOI'si olabilir). Doğrulanana kadar atıf verilmemelidir.

### 8.4 Vektör geometrisi üzerinde çalışan tezler (Kategori B — RASH-HIT'e ikinci en yakın grup)

- **Peiravian, Farideddin (2015)** — "Geometric Complexity of Urban Road Networks". DOI yok. Veri: **vektör yol ağı grafiği**. Vektör geometrisi üzerinde geometrik karmaşıklık ölçümü; RASH-HIT'in "rasterizasyonsuz" iddiasının en yakın tez komşusu. Alan farklı (kentsel ulaşım).
- **Bonsu, Kofi (2024)** — "Urban hierarchy and the analysis of spatial patterns: towards explicit fractal modelling". DOI 10.70675/37c755d1z02fez4237za34ezfb8729b9cb64. Veri: CBS vektör (yüksek olasılık, **Doğrulanamadı**).
- **Jackson, Leeanne Nathalie (2014)** — "Graphical calculation of the fractal dimension for applications in geography". Veri türü **Doğrulanamadı**.

### 8.5 Türkiye kaynaklı tezler (OpenAlex'e yansıyan İngilizce başlıklar)

- **Ediz, Özgür Mehmet (2003)** — "A Generative Approach In Architectural Design Based On Fractals". Üniversite **Doğrulanamadı** (İTÜ olması muhtemel). Kategori C/D — fraktal **üretim**, ölçüm değil. Ostwald & Ediz 2014'ün öncülü.
- **Değirmenci, F. Betül (2009)** — "Fractal Geometry And Architectural Design With Generative Systems". Kategori D.
- **Gözübüyük, Gaye (2007)** — "Fractal Based Form Generation In Different Architectural Languages". Kategori D.
- **Ursavaş, Nazlı Bahar (2022)** — "Periodic analyzes and evaluation of the parks with fractal dimension and lacunarity calculations". Kategori B (kutu sayma + lakünarite, raster, peyzaj alanı).

### 8.6 Bu bölümün sınırlılıkları (açıkça beyan)

- Üniversite bilgisi OpenAlex `authorships.institutions` alanında tezlerin çoğunda **boştur**; yalnızca depo adından çıkarım yapılabilmiştir.
- Yöntem ve veri türü sütunları **başlık/alan çıkarımıdır**, tam metin doğrulaması yapılmamıştır.
- **OATD.org taraması yapılamamıştır** — Doğrulanamadı.
- **YÖK Ulusal Tez Merkezi doğrudan taranamamıştır.** Yalnızca OpenAlex'e yansıyan İngilizce başlıklı Türk tezleri görülebilmiştir; YÖK'te kutu sayma içeren ek tezlerin bulunma olasılığı **yüksektir**. Bu boşluk Bölüm 16'da birinci öncelikli manuel iş olarak durmaktadır.

---

## 9. TÜRKİYE'DE YAPILAN ÇALIŞMALAR

1. **Ostwald, M.J.; Ediz, Ö. (2014)** "Measuring Form, Ornament and Materiality in Sinan's Kılıç Ali Paşa Mosque: an Analysis Using Fractal Dimensions", *Nexus Network Journal*. DOI 10.1007/s00004-014-0219-3 — Kutu sayma (Bovill/ArchImage geleneği), cephe + **süsleme katmanları ayrı ayrı**. Yazılım: ArchImage (kesin teyit Doğrulanamadı). Veri: **RASTER** (CAD çizimlerinden rasterize). Kategori D. Önemi: ornament ayrıştırması fikriyle RASH-HIT'e en yakın Türkiye bağlantılı çalışma; ama girdi raster.
2. **Okuyucu, Ş.E.; Baştaş, M.S. (2022)** "Analysis based on fractal geometry of traditional housing facades: Afyonkarahisar traditional housing facade examples, Turkey", *Applied Nanoscience*. DOI 10.1007/s13204-021-02226-3 — Geleneksel Türk evi cepheleri, kutu sayma. Yazılım: Doğrulanamadı. Veri: RASTER. Kategori D. Güvenilirlik: orta-yüksek (dergi kapsamı konuya uzak — dikkatli atıf).
3. **Kuruçay, E.; Ediz, Ö. (2025)** "Mimaride görsel karmaşıklığın hesaplamalı analizi: Şehzade, Süleymaniye ve Selimiye Camileri", *Gazi Üniv. Müh.-Mim. Fak. Dergisi* (DergiPark). DOI 10.17341/gazimmfd.1476466 — hesaplamalı görsel karmaşıklık + fraktal boyut. Veri: RASTER. Kategori C/D. Önemi: RASH-HIT'in "karmaşıklık profili" fikriyle örtüşür; ancak SVG girdi ve Türkçe etiketli motif profilleyici yok.
4. **Kartal, S.; İnceoğlu, M. (2023)** "Evaluating Street Character Using the 3D Fractal Analysis Method: Lefkoşa", *Journal of Design Studio*. DOI 10.46474/jds.1368023 — 3B fraktal analiz, sokak dokusu. Veri: RASTER/3B model kesitleri. Kategori E. Güvenilirlik: orta.
5. **Tercan, N. (2023)** "Fractal Dimension and Perception of Order in Islamic Art", IntechOpen kitap bölümü. DOI 10.5772/intechopen.109432 — İslam sanatı desenlerinde fraktal boyut/algısal düzen. Veri: RASTER. Kategori D. Güvenilirlik: orta (kitap bölümü, hakemlik zayıf).
6. **Gondoputranto, O.; Dibia, I W. (2022)** "Use of Technology in Capturing Various Traditional Motifs and Ornaments: A Case Study of Batik Fractal (Indonesia) and TUDITA — Turkish Digital Textile Archive", *Humaniora*. DOI 10.21512/humaniora.v13i1.7408 — Türk dijital tekstil arşivi + jBatik. Veri: karma (jBatik vektör üretimi, arşiv raster). Kategori D. Önemi: "Türk tekstil motifi + fraktal" temasıyla en doğrudan kesişim; ancak Db/R² hesaplayan bir motor yok.

**Not:** DergiPark doğrudan taranamadı (302/bot koruması); yukarıdaki DergiPark kaynaklı kayıtlara OpenAlex üzerinden DOI ile ulaşıldı.

---

### 9.A ÜÇÜNCÜ TUR — OpenAlex/Crossref API ile bulunan YENİ Türkiye kaynaklı çalışmalar

Aşağıdaki kayıtların tamamı Crossref API'sinden **birebir doğrulanmıştır** (başlık, yıl, dergi, yazar, tür).

#### 9.A.1 ⭐ EN KRİTİK — Türkiye'nin doğrudan muadili (Kategori C)

**Çimen, M.E.; Boyraz, Ö.F.; Garip, Z.; Pehlivan, İ. (2021)** — "Görüntü İşleme Tabanlı Kutu Sayma Yöntemi ile Fraktal Boyut Hesabı için **Arayüz Tasarımı**", *Politeknik Dergisi*. **DOI 10.2339/politeknik.689421** (Crossref: journal-article, 2021 — doğrulandı).
- Yöntem: Kutu sayma + görüntü işleme; **fraktal boyut hesabı için kullanıcı arayüzü/yazılım geliştirme**.
- Veri türü: **RASTER** (başlıkta "görüntü işleme tabanlı" ifadesiyle açıkça belirtiliyor). Yazılım platformu (MATLAB?) **Doğrulanamadı**.
- **Neden C:** RASH-HIT ile amaç birebir örtüşüyor — "fraktal boyut hesaplayan bir arayüz/yazılım geliştirmek". Ayrım tam olarak RASH-HIT'in tez cümlesidir: bu çalışma **piksel/raster**, RASH-HIT **SVG vektör, rasterizasyonsuz**.
- **Önemi: RASH-HIT'in Türkçe makalesinde atıf verilmesi ZORUNLU en önemli Türkiye kaynaklı çalışmadır.** Katkı, doğrudan bu çalışmaya karşı "raster → vektör" ekseninde konumlandırılmalıdır.

**Sezer, Ebru Akçapınar (2010)** — "A computer program for fractal dimension (**FRACEK**) with application on type of mass movement characterization", *Computers & Geosciences*. **DOI 10.1016/j.cageo.2009.04.006** (doğrulandı; Crossref yılı 2010).
- Türkiye kaynaklı, uluslararası dergide yayımlanmış bir **fraktal boyut yazılımı**. Veri: RASTER.
- **Neden C:** "Türk araştırmacı tarafından geliştirilmiş fraktal boyut programı" öncülü — RASH-HIT'in yazılım katkısı iddiası için önemli yerel referans.

#### 9.A.2 Motif / süsleme / tekstil (Kategori B — RASH-HIT'in uygulama alanı)

| Yazar / Yıl | Başlık | DOI | Veri türü | Neden B |
|---|---|---|---|---|
| **Genç, I.; Aykal, F.D. (2026)** | Analysis of Traditional Savur (Mardin) House Ornaments from a Fractal Geometry Perspective: The Case of Abdüllatif Özbek Mansion | 10.30785/mbud.1770577 (*Mimarlık Bilimleri ve Uygulamaları Dergisi*) | RASTER (**Doğrulanamadı** — fotoğraf/çizim olması muhtemel) | **Geleneksel süsleme (ornament) + fraktal boyut**; RASH-HIT'in kültürel miras uygulamasıyla en doğrudan tematik örtüşme. **2026 tarihli — literatür taramasına mutlaka dahil edilmeli** |
| **Kabakulak, H. (2025)** | Giysi Tasarımında Fraktal Geometrik Boyut | 10.29228/kesit.78967 (*Kesit Akademi*) | **Doğrulanamadı** | **Tekstil alanında** Türkçe fraktal boyut çalışması — RASH-HIT'in halı/kilim/tekstil hedefine en yakın Türk yayını. Kutu sayma kullanıp kullanmadığı doğrulanmalı |
| **Çoban, G.; Okuyucu, Ş.E. (2023)** | Fractal Analysis of Façades of Historical Public Buildings with Box Count Method: The Case of Afyonkarahisar | 10.5772/intechopen.1001881 (IntechOpen kitap bölümü) | RASTER | Okuyucu & Baştaş 2022'nin devamı; başlıkta "box count" geçen az sayıdaki Türkiye kaynaklı çalışmadan biri. Güvenilirlik: orta (kitap bölümü) |

#### 9.A.3 Mimari / cephe kümesi (Kategori D)

| Yazar / Yıl | Başlık | DOI | Not |
|---|---|---|---|
| Topbaş, D.C.; Arslan, H.D. (2021) | Geleneksel Mersin ve Tarsus evlerinin fraktal boyuta dayalı cephe değerlendirmesi | 10.37246/grid.903020 | RASTER (kısmen Doğrulanamadı) |
| Kartal, S.; Dinçer, A.E. (2023) | Tarihi çevrede eski-yeni yapı uyumunun 3 boyutlu fraktal analiz yöntemi ile incelenmesi: Safranbolu örneği | 10.17714/gumusfenbil.1256557 | 3B model (voksel/mesh) — RASH-HIT 2B vektör |
| Ediz, Ö.; Çağdaş, G. (2007) | A Computational Architectural Design Model Based on Fractals | 10.1108/ohi-02-2007-b0005 | Üretken/geometrik model; **ölçüm değil sentez**. Ostwald & Ediz 2014 zincirinin başlangıcı |
| Ediz, Ö. (2009) | "Improvising" Architecture: A Fractal Based Approach | 10.52842/conf.ecaade.2009.593 | eCAADe bildirisi, üretken |

#### 9.A.4 Kentsel doku / peyzaj kümesi (Kategori D–E) — **tamamı RASTER/CBS**

İlhan, C. (2019) *Bursa* — 10.26835/my.546927 · Yılmaz, D.; Öztürk, S.; Işınkaralar, Ö. (2022) — 10.35674/kent.996119 · Öztürk, D.; Gündüz, U. (2020) *Samsun* — 10.21205/deufmd.2020226409 · Öztürk, D.; Kılıç-Gül, F. (2018) *CORINE/Ankara* — 10.15659/uzalcbs2018.6659 · Güzel, M. ve ark. (2022) *Ordu* — 10.29130/dubited.945017

> Bu küme **istisnasız raster/CBS tabanlıdır** ve RASH-HIT'in vektör yaklaşımının farkını vurgulamak üzere toplu atıf olarak kullanılabilir.

#### 9.A.5 Fraktal öznitelik çıkarımı (Kategori C/E)

- **Çimen, M.E.; Boyraz, Ö.F.; Yıldız, M.Z.; Boz, A.F. (2021)** — "A new dorsal hand vein authentication system based on fractal dimension box counting method", *Optik*. **DOI 10.1016/j.ijleo.2020.165438** (doğrulandı). RASTER, biyometri. Kategori C (kutu sayma ile öznitelik çıkarımı, alan farklı).
- Yılmaz, A.; Ünal, G. (2020) — "Multiscale Higuchi's fractal dimension method", *Nonlinear Dynamics*, 10.1007/s11071-020-05826-w. 1B sinyal, Higuchi (kutu sayma değil). Kategori E.

#### 9.A.6 Türkiye taramasının kritik sonucu

1. **Türkiye kaynaklı hiçbir çalışmada "vektör geometri üzerinde rasterizasyonsuz kutu sayma" tespit edilememiştir.** İncelenen tüm ölçüm çalışmaları raster (piksel/görüntü/CBS) tabanlıdır veya veri türü doğrulanamamıştır.
2. **Halı/kilim motifi + kutu sayma** başlıklı Türkiye kaynaklı hakemli yayın OpenAlex/Crossref'te **bulunamamıştır**. En yakın: Kabakulak 2025 (giysi tasarımı).
3. **Çini/tezhip + fraktal boyut ölçümü** için Türkiye kaynaklı eşleşen yayın **bulunamamıştır**. Bu, RASH-HIT için en net yerel boşluk alanıdır.
4. En yakın metodolojik rakip **Çimen ve ark. 2021**'dir; katkı bu çalışmaya karşı konumlandırılmalıdır.

**Bu turun sınırlılıkları:** OpenAlex günlük ücretsiz kotası tükendiği için `fractal textile`, `fractal pattern`, `fractal geometry traditional` başlık sorguları çalıştırılamamıştır (**Doğrulanamadı**). Veri türü/yazılım sütunları başlık ve dergi metaverisinden çıkarımdır; tam metin doğrulaması yapılmamıştır. DergiPark/TR Dizin siteleri bot koruması nedeniyle açılmamıştır.

---

## 10. MOTİF, TEKSTİL VE KÜLTÜREL MİRAS ALANINDAKİ ÇALIŞMALAR (Kategori D)

1. **Patuano, A.; Lima, M.F. (2021)** "The fractal dimension of Islamic and Persian four-folding gardens", *Humanities and Social Sciences Communications*. DOI 10.1057/s41599-021-00766-1 — Çahârbağ planlarında kutu sayma; yazılım ImageJ/FracLac (orta teyit). Veri: **RASTER** (plan görüntüsü rasterize). Güvenilirlik: yüksek (Nature Portfolio). Önemi: plan verisi aslında vektör kökenli olmasına rağmen rasterize edilmiş → RASH-HIT'in tam olarak eleştirdiği kayıp.
2. **Radović, Lj.; Zekić, A. (2024)** "Symmetry analysis of ornaments in Serbian medieval frescoes art", *Filomat*. DOI 10.2298/fil2433785r — simetri grupları + ornament sınıflandırma. Veri: RASTER. Kategori D/E.
3. **Alghar, M.Z.; Marhayati, M. (2023)** "Ethnomathematics: Exploration of Fractal Geometry in Gate Ornaments of the Sumenep Jamik Mosque Using the Lindenmayer System", *Indonesian J. of Science and Mathematics Education*. DOI 10.24042/ijsme.v6i3.18219 — L-sistemle süsleme **üretimi**; veri vektör/üretimsel ama **ölçüm motoru değil**. Kategori D.
4. **Lee, J.H.; Ostwald, M.J. (2021)** "Fractal Dimension Calculation and Visual Attention Simulation: Assessing the Visual Character of an Architectural Façade", *Buildings* 11(4):163. DOI 10.3390/buildings11040163 — ArchImage, RASTER. Güvenilirlik: yüksek.
5. **Katona, V. (2020/2021)** "Relief Method: The Analysis of Architectonic Façades by Fractal Geometry", *Buildings* 11(1):16. DOI 10.3390/buildings11010016 · devamı "The Hidden Dimension of Façades" (2023) DOI 10.3390/fractalfract7030257 — RASTER.
6. **Ali, ...; Mustafa, ... (2024)** "Fractal Dimensional Analysis of Building Facades: Office Buildings in Erbil", *Fractal and Fractional* 8(12):746. DOI 10.3390/fractalfract8120746 — RASTER, ImageJ/Fractalyse sınıfı araçlar.
7. Endüstriyel tekstil (kültürel miras değil, Kategori E): "Fabric Defect Detection Using a Hybrid and Complementary Fractal Feature Vector and FCM-based Novelty Detector" (2017, *Fibres and Textiles in Eastern Europe*, DOI 10.5604/01.3001.0010.5370; yazarlar Doğrulanamadı) ve "GLCM texture based fractal method for evaluating fabric surface roughness" (2009, IEEE CCECE, DOI 10.1109/ccece.2009.5090100; yazarlar Doğrulanamadı) — ikisi de RASTER.

**Alan bulgusu:** Taranan 13 kültürel miras/tekstil çalışmasının 12'si RASTER girdi kullanmaktadır. Vektör kullanan iki istisna fraktal boyut ölçmemekte, L-sistemle desen üretmektedir. **Bu alanda SVG/vektör girdi üzerinde rasterizasyonsuz, kesin geometrik kesişimle kutu sayma yapan bir çalışma bulunamamıştır.**

---
## 11. KARŞILAŞTIRMA MATRİSİ

Legend: ✔ var · ✘ yok · ◐ kısmen var · ? doğrulanamadı

| Ölçüt | RASH-HIT | Fractalyse 3 | FractDim (2011) | roko-gis Vector Lines | FracPaQ | ImageJ FracLac | ImageJ BoxCount | Benoit | CRAN fractD | MATLAB boxcount |
|---|---|---|---|---|---|---|---|---|---|---|
| Kutu sayma | ✔ | ✔ | ✔ | ✔ | ◐ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Raster görüntü desteği | ✘ (tasarım gereği) | ✔ | ✘ | ✘ | ✘ | ✔ | ✔ | ✔ | ✔ | ✔ |
| SVG / vektör desteği | ✔ (tam SVG semantiği) | ✔ (vektör+ağ) | ✔ (SVG) | ◐ (yalnız çizgi) | ◐ (polyline) | ✘ | ✘ | ✘ | ✘ | ✘ |
| Doğrudan geometrik hesaplama (kesin predikat) | ✔ GEOS/DE-9IM | ? | ? | ◐ | ◐ | ✘ | ✘ | ✘ | ✘ | ✘ |
| Uzamsal indeks + hiyerarşik budama | ✔ STRtree+quadtree | ? | ✘ | ✘ | ✘ | ✘ | ✘ | ? | ✘ | ✘ |
| Çoklu ölçek analizi | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Regresyon + uyum kalitesi (R²) | ✔ + dışlama gerekçesi | ✔ | ? | ✔ + bootstrap CI/FDR | ✔ | ✔ | ◐ | ✔ | ✔ | ◐ |
| Bileşik güven skoru (0-100) | ✔ | ✘ | ✘ | ◐ (istatistiksel) | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ |
| Multifraktal / lakünarite | ✘ | ◐ | ✘ | ✘ (GeoFractalLines'ta ✔) | ✘ | ✔ | ✘ | ✔ | ✘ | ✘ |
| Çoklu ızgara-başlangıcı ortalaması | ✘ | ? | ✘ | ✘ | ✘ | ✔ | ✘ | ? | ✘ | ✘ |
| Toplu (batch) analiz | ✔ | ◐ | ✘ | ✔ | ◐ | ✔ | ✘ | ? | ✔ | ✔ |
| Görsel raporlama | ✔ HTML/PDF/MD + vektör ızgara haritası | ✔ GUI grafik | ✘ | ◐ | ✔ | ✔ | ✘ | ✔ | ✘ | ◐ |
| Sonuç dışa aktarma | ✔ CSV/XLSX/JSON/MD/PDF | ✔ CSV | ? | ✔ CSV | ✔ | ✔ CSV | ◐ | ✔ | ✔ | ◐ |
| Web arayüzü | ✔ REST+SPA | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ |
| Masaüstü arayüzü | ◐ (TUI) | ✔ Java GUI | ✔ | ✘ | ✔ MATLAB GUI | ✔ | ✔ | ✔ | ✘ | ✘ |
| Komut satırı | ✔ | ? | ? | ✔ | ✘ | ◐ macro | ◐ macro | ✘ | ✔ R | ✔ |
| Açık kaynak | ✔ Apache-2.0 | ✔ GPL | ✘ lisanssız | ✔ MIT | ✔ | ✔ | ✔ | ✘ | ✔ GPL-3 | ◐ FEX |
| Tekrarlanabilirlik (hash manifest) | ✔ SHA-256 | ✘ | ✘ | ◐ DOI'li sürüm | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ |
| Akademik doğrulama (hakemli yayın) | ✘ (henüz) | ✔ | ✘ | ◐ Zenodo | ✔ JSG 2017 | ✔ | ✔ | ? | ✔ CRAN | ◐ |
| İşlem hızı | ? (ölçülmedi, kıyas gerekli) | ? | ? | ? | ? | ? | ? | ? | ? | ? |
| Kültürel motiflere uygulanabilirlik | ✔ (tasarım hedefi) | ◐ | ◐ | ✘ | ✘ | ✔ (fiilî standart) | ◐ | ◐ | ✘ | ◐ |
| Çok dilli (TR/EN) | ✔ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ |

Kaynaklar: Bölüm 4-6'daki doğrulanmış URL'ler. "?" işaretli hücreler kaynakta açıkça belirtilmediği için **doğrulanamadı** sayılmalıdır; özellikle işlem hızı satırı tamamen ölçüme muhtaçtır.

---

## 12. PROJENİN GÜÇLÜ VE FARKLILAŞAN YÖNLERİ

1. **Tam SVG semantiği.** Bulunan diğer vektör araçlarının hiçbiri CSS `<style>` blokları, sınıf/inline stil önceliği, görünürlük filtreleme, `fill-rule`, clipPath/mask uyarısı ve iç içe affine transform yığınını birlikte çözmüyor. Bu, "SVG'yi okuyabilmek" ile "SVG'yi doğru okuyabilmek" arasındaki farktır ve fraktal boyutu doğrudan etkiler.
2. **Kesin kesişim predikatı ile karışık geometri.** Poligon (alan) + çizgi (stroke) karışık geometride GEOS `intersects()` ile doluluk kararı; AABB-only kısayolu bilinçle reddedilmiş.
3. **Denetlenebilir hızlandırma.** Yalnız-boş-ebeveyn budaması matematiksel olarak güvenli (boş ebeveynin çocuğu boştur) ve FULL kısayolunun fazla sayım ürettiği kodda açıkça belgelenmiş. `negative_space_cached_cells`, `active_growth_rate` gibi metrikler budamanın etkisini şeffaf kılıyor — literatürde nadir bir dürüstlük.
4. **Şeffaf ölçek tablosu.** Her ölçek için `included_in_fit` ve `exclusion_reason` raporlanıyor; box-counting literatürünün en sık eleştirilen "hangi ölçekler regresyona girdi?" sorununa doğrudan yanıt (Gonzato 1998, Foroutan-pour 1999).
5. **Bileşik güven skoru.** R² + geçerli ölçek sayısı + SVG sağlığı üçlüsünü tek sayıya indiren, standartlaştırılmış bir raporlama; literatürde bu üçlünün birlikte skorlandığı bir örnek bulunamadı.
6. **Tekrarlanabilirlik altyapısı.** SHA-256 manifest + result.json + terminal log + sürümlenmiş paket + DOI + CITATION.cff. Fraktal boyut literatüründe neredeyse hiç görülmeyen bir olgunluk.
7. **Üç arayüz + i18n.** CLI, TUI ve web REST/SPA; TR/EN yerelleştirme. Türkçe motif karmaşıklık profilleyicisi alanyazında emsalsiz.
8. **Mühendislik kalitesi.** defusedxml ile XXE sertleştirme, CodeQL, dependabot, pre-commit hook, pytest, lisans/citation/locale doğrulayıcıları, CODE_PROVENANCE.md. Akademik yazılım için nadir.

---

## 13. ÖZGÜNLÜK BAKIMINDAN DİKKAT EDİLMESİ GEREKEN NOKTALAR

- **"SVG üzerinde box-counting" fikri yenidir denemez.** FractDim (2010-2011) tam olarak bunu yapıyordu; Fractalyse vektör girdiyi resmen destekliyor. Bu iki kaynağın makalede sessizce atlanması hakem tarafından yakalanır ve özgünlük iddiasını çökertir. Açıkça alıntılanıp farklar gerekçelendirilmelidir.
- **"Rasterizasyonsuz" iddiası da yeni değil.** Bouda ve ark. (2016) ve Roy ve ark. (2007) aynı motivasyonu farklı alanlarda uygulamıştır.
- **Aynı dönem rekabeti.** roko-gis ailesi (2026) hem çağdaş hem DOI'li; "önce biz yaptık" iddiası tarih karşılaştırmasına dayanmalı ve zaten dar bir kazanç sağlar. Daha güvenli konum: farklı ve daha geniş kapsam (genel SVG, alan+çizgi karışık geometri).
- **Doğrulama eksikliği.** Analitik olarak bilinen fraktallarda (Koch eğrisi D≈1.2619, Sierpinski üçgeni D≈1.5850, Minkowski/ Vicsek) sistematik doğrulama raporu görülmedi. Özgünlük iddiasından ÖNCE bu şart.
- **Hız iddiası ölçülmemiş.** Quadtree budamasının kazancı iç metriklerle raporlanıyor ama harici bir baseline'a (FracLac, Fractalyse, saf Python kaba kuvvet) karşı ölçülmemiş.
- **Eksik yaygın özellikler.** Çoklu ızgara-başlangıcı (grid-origin) ortalaması ve minimum-cover düzeltmesi (FracLac'te var), lakünarite, multifraktal spektrum, bootstrap güven aralığı yok. Hakem bunları sorar.
- **Güven skorunun ağırlıkları (%40/%30/%30) keyfîdir.** Literatür dayanağı veya duyarlılık analizi olmadan "akademik güven skoru" denmesi zayıf noktadır.
- **Regresyonda `log10(filled)`, filled=0 iken 0 yazılıyor** ancak bu satır `included=False` ile dışlanıyor — davranış doğru, fakat makalede açıkça belirtilmeli.
- **YÖK tez taraması yapılamadı** → "Türkiye'de benzeri yok" denemez.

---

## 14. LİTERATÜRDEKİ OLASI BOŞLUK

İncelenen kaynaklar içinde doğrudan eşleşme bulunamayan bileşim şudur:

> Genel amaçlı, alan (poligon) ve çizgi geometrisini birlikte destekleyen, tam SVG semantiğini (stil çözümleme + afin dönüşüm + eğri düzleştirme) koruyarak ayrıştıran, doluluk kararını kesin geometrik kesişim predikatlarıyla veren, hiyerarşik uzamsal budamayla ölçeklenen, ölçek dahil/hariç kararlarını ve bileşik bir güven ölçütünü şeffaf raporlayan ve çıktısını sağlama toplamlı bir manifestoyla tekrarlanabilir kılan açık kaynak bir kutu sayma motoru.

Bileşenler tek tek literatürde mevcuttur (vektör box-counting: Fractalyse, FractDim, Roy 2007, Bouda 2016; hiyerarşik hızlandırma: Liebovitch & Toth 1989; ölçek seçimi: Gonzato 1998; vektör hat aracı: FracPaQ, roko-gis). Boşluk **bileşimde ve genellikte**, bileşenlerin tek tek icadında değildir.

İkinci boşluk: fraktal boyut literatüründe **tekrarlanabilirlik manifestosu** (girdi hash'i, ızgara parametreleri, sürüm, ortam) neredeyse hiç ele alınmamıştır.

Üçüncü boşluk: kültürel miras/motif alanında **vektör-yerli** ölçüm yoktur; tüm alan raster fotoğraf + ImageJ/ArchImage üzerine kuruludur.

---

## 15. MAKALE VEYA TEZ İÇİN ÖNERİLEN ÖZGÜN KATKI TANIMI

Önerilen konumlandırma: **yazılım katkısı (birincil) + uygulama katkısı (ikincil)**; yöntemsel katkı iddiası ancak Deney 1-3 sonuçları destekliyorsa eklenmelidir.

Önerilen katkı cümlesi (makale için):

> Bu çalışma, SVG vektör geometrisini rasterize etmeden, stil ve dönüşüm semantiğini koruyarak kesin geometrik kesişim predikatlarıyla kutu sayma fraktal boyutu hesaplayan açık kaynaklı bir yazılım motoru sunmaktadır. Motor, boş uzayı hiyerarşik olarak budayan bir dörtlü-ağaç şeması ile kesin sayımı ölçeklenebilir kılar ve budamanın sonucu değiştirmediği kaba kuvvet sayımla doğrulanır. Katkı üç eksende tanımlanır: (i) vektör-yerli, rasterizasyon hatasından bağımsız bir ölçüm boru hattı; (ii) ölçek dahil/hariç kararlarını ve regresyon kalitesini şeffaf raporlayan, sağlama toplamlı bir tekrarlanabilirlik paketi; (iii) yöntemin kültürel motif korpuslarına uygulanması ve raster tabanlı ölçümlerle karşılaştırılması.

---

### 15.A ⚠ ÜÇÜNCÜ TUR SONRASI ZORUNLU REVİZYON — yukarıdaki katkı cümlesi ARTIK YETERSİZDİR

**Gerekçe:** EK BÖLÜM D.1'de belgelendiği üzere, **Douglass, R. (2025)**, *Fractal and Fractional* 9(10):633, DOI **10.3390/fractalfract9100633** (yayın 29 Eylül 2025, hakemli, CC-BY), RASH-HIT'in Zenodo öncelik tarihinden (29 Temmuz 2026) **yaklaşık 10 ay önce**, özetinde birebir şunu beyan etmektedir: *"Unlike traditional pixelated approaches that suffer from rasterization artifacts, the method used directly analyzes geometric line segments."*

Dolayısıyla yukarıdaki (i) maddesi — *"vektör-yerli, rasterizasyon hatasından bağımsız bir ölçüm boru hattı"* — **tek başına özgün katkı olarak sunulamaz.** Bu hâliyle hakem tarafından reddedilmesi olasıdır.

#### Revize edilmiş katkı cümlesi (önerilen)

> Doğrudan geometri üzerinde kutu sayma yaklaşımı, matematiksel fraktallerin çizgi segmentleri için daha önce ortaya konmuştur (Douglass, 2025). Bu çalışma, söz konusu yaklaşımı üç yönde genişletmektedir: (i) girdi olarak **tam SVG belge semantiğini** (CSS ve satır içi stil çözümleme, iç içe affine dönüşüm yığını, Bézier ve yay düzleştirme) tüketen bir ayrıştırma boru hattı; (ii) yalnızca çizgi geometrileriyle sınırlı kalmayıp **alan poligonlarını** da kapsayan, GEOS kesin kesişim predikatına dayalı bir sayım motoru; (iii) sağlama toplamlı bir tekrarlanabilirlik paketi (SHA-256 manifest), toplu analiz ve komut satırı/uçbirim/web arayüzleriyle **paketlenmiş, sürdürülen bir açık kaynak araç**. Yöntem, geleneksel motif ve süsleme korpuslarına uygulanmakta ve aynı korpusun raster tabanlı ölçümleriyle karşılaştırılmaktadır. İncelenen kaynaklar içinde bu bileşenlerin birlikte bulunduğu bir sisteme doğrudan eşleşme bulunamamıştır.

#### Katkı ağırlığının kayması

| Eksen | Önceki tur | 3. tur sonrası |
|---|---|---|
| Yöntemsel katkı | Orta (iddia ediliyordu) | **Düşük** — Douglass 2025 tarafından öncelendi |
| Yazılım katkısı | Birincil | **Birincil (güçlendi)** — Douglass'ta yayımlanmış paket tespit edilemedi |
| Uygulama katkısı | İkincil | **Birincile yükseldi** — tez taramasında `fractal motif`/`fractal textile`/`fractal carpet design` sorguları **0 sonuç** verdi; Türkiye'de çini/tezhip + fraktal ölçüm yayını bulunamadı |

**Net öneri:** Konumlandırma **"yazılım katkısı + uygulama (alan) katkısı"** olarak yapılmalı; **yöntemsel yenilik iddiası tamamen geri çekilmeli** veya yalnızca "çizgiden alan poligonlarına genişletme" gibi çok dar ve ölçülmüş bir alt iddiaya indirgenmelidir.

#### Kullanılması YASAK ifadeler

"Dünyada ilk", "tek", "daha önce hiç yapılmadı", "benzersiz", "literatürde bulunmayan". Bunların yerine: *"incelenen kaynaklar içinde doğrudan eşleşme bulunamamıştır"*, *"bildiğimiz kadarıyla yaygın değildir"*.

#### Makale gönderilmeden önce tamamlanması ZORUNLU üç iş

1. **Douglass 2025'in tam metni indirilip okunmalıdır** (CC-BY, serbest erişim). Segment-kutu kesişiminin nasıl hesaplandığı doğrulanmalı; RASH-HIT'in GEOS yaklaşımıyla farkı somutlaştırılmalıdır.
2. **Aynı test fraktalleri üzerinde sayısal kıyaslama** yapılmalıdır: Koch (D=1.2619), Sierpinski (D=1.5850), Minkowski (D=1.5), Hilbert, Dragon. Douglass R²≥0.9988 ve Koch'ta %0.11 hata raporlamaktadır — RASH-HIT bu çıtayı karşılamalı veya farkı açıklamalıdır.
3. **Güven skoru kalibrasyon deneyi** yapılmalıdır (bkz. D.3): skorun, bilinen teorik D'ye göre gerçek hata ile korelasyonu gösterilmelidir.

**Ek olarak** Çimen ve ark. 2021 (DOI 10.2339/politeknik.689421) Türkçe yayında, Kargic 2016 tezi ise alan konumlandırmasında atıf verilmelidir.

Önerilen hedef mecralar: *SoftwareX*, *Journal of Open Source Software (JOSS)*, *SoftwareImpacts* (yazılım katkısı); *Fractal and Fractional*, *Chaos Solitons & Fractals*, *Nexus Network Journal*, *Journal of Cultural Heritage* (uygulama katkısı).

---

## 16. DENEY VE KARŞILAŞTIRMA ÖNERİLERİ

**Deney 0 (ön koşul, elle):** YÖK Ulusal Tez Merkezi ve DergiPark'ta tarayıcıyla manuel arama ("fraktal boyut", "kutu sayma", "motif", "vektör"). Bu rapordaki en büyük boşluk budur; özgünlük iddiasından önce kapatılmalıdır.

**Deney 1 — Analitik doğrulama (zorunlu).** Koch eğrisi (D=log4/log3≈1.2619), Koch kar tanesi, Sierpinski üçgeni (≈1.5850) ve halısı (≈1.8928), Vicsek fraktalı, Minkowski sosisi SVG olarak üretilip ölçülür. Rapor: |Db_ölçülen − Db_teorik|, R², seviye sayısına göre yakınsama eğrisi.

**Deney 2 — Budama eşdeğerliği.** Aynı SVG'lerde quadtree budamalı ve budamasız (kaba kuvvet, tüm hücreler) sayım bit-bit karşılaştırılır. İddia: N(r) dizileri birebir aynı. Bu, "hızlandırma sonucu değiştirmiyor" iddiasının tek geçerli kanıtıdır.

**Deney 3 — Raster-vs-vektör (makalenin can damarı).** Aynı SVG'ler 300/600/1200/2400 dpi'da PNG'ye çevrilip ImageJ FracLac ve MATLAB boxcount ile ölçülür; RASH-HIT vektör sonucuyla karşılaştırılır. Beklenen bulgu: raster Db değeri çözünürlüğe göre kayar, vektör sonucu sabittir. Referans çerçeve: Klinkenberg 1994, Goodchild 1980, Bouda 2016.

**Deney 4 — Çapraz yazılım kıyası.** Aynı vektör girdilerde Fractalyse 3 (vektör modu) ve FracPaQ ile Db karşılaştırması; farklar için Bland-Altman analizi.

**Deney 5 — Performans.** Artan seviye (4→10) ve artan geometri karmaşıklığında duvar saati süresi ve bellek; baseline: saf Python kaba kuvvet, FracLac, Fractalyse. Budamanın hızlanma oranı (speedup) eğrisi.

**Deney 6 — Duyarlılık.** (a) Bézier düzleştirme adım sayısının (num_steps=16) Db üzerindeki etkisi; (b) `canvas_aspect` vs `square_bbox` ızgara modu farkı; (c) ızgara başlangıç ofsetinin etkisi (FracLac'in çoklu-origin yaklaşımı eklenirse); (d) güven skoru ağırlıklarının (%40/%30/%30) duyarlılık analizi.

**Deney 7 — Motif korpusu.** En az 50-100 SVG motiften oluşan bir korpus (halı/kilim/çini/işleme) üzerinde toplu analiz; Db dağılımı, motif tipine göre gruplama, ve Db ile uzman karmaşıklık algısı arasındaki korelasyon. Korpusun Zenodo'da veri kümesi olarak yayımlanması ek katkı olur.

**Deney 8 — Eksik özellik telafisi.** Çoklu ızgara-origin ortalaması, lakünarite ve bootstrap güven aralığı eklenip eklenmemesi kararı; en azından "neden eklenmedi" gerekçesi makalede yer almalı.

---

## 17. SONUÇ

RASH-HIT Fractal Studio'nun temel fikri — vektör geometrisi üzerinde rasterizasyonsuz kutu sayma — daha önce uygulanmıştır: 2010-2011'de FractDim (SVG, ölü), uzun süredir Fractalyse (vektör+ağ, olgun, Java), 2007'de Roy ve ark. (kırık ağları), 2016'da Bouda ve ark. (kök segmentleri), 2017'de FracPaQ (MATLAB), 2026'da roko-gis ailesi (Python, vektör çizgiler). Dolayısıyla "dünyada ilk" türü bir iddia savunulamaz ve kullanılmamalıdır.

Buna karşılık, **incelenen kaynaklar içinde**, tam SVG semantiğini koruyan + alan ve çizgi geometrisini birlikte kesin GEOS predikatlarıyla değerlendiren + hiyerarşik negatif-alan budamasıyla ölçeklenen + ölçek dahil/hariç kararlarını ve bileşik güven skorunu şeffaf raporlayan + SHA-256 manifestli tekrarlanabilir akademik paket üreten + CLI/TUI/web üçlüsü ve TR/EN yerelleştirmeyle gelen bir sisteme **doğrudan eşleşme bulunamamıştır**. Kültürel motif alanında ise vektör-yerli ölçüm yapan hiçbir çalışma bulunamamıştır; alan tümüyle raster tabanlıdır.

Projenin en savunulabilir konumu: **olgun bir yazılım katkısı + motif/kültürel miras alanına vektör-yerli ölçüm getiren bir uygulama katkısı.** Bu konum, Deney 1 (analitik doğrulama), Deney 2 (budama eşdeğerliği) ve Deney 3 (raster-vs-vektör) tamamlandığında güçlü biçimde savunulabilir hale gelir.

**Gelecekte incelenmesi gereken eksik kaynaklar:** YÖK Ulusal Tez Merkezi (taranamadı), DergiPark tam metin araması (bot koruması), ProQuest Dissertations (abonelik), SourceForge dizini (JS), Web of Science / Scopus / IEEE Xplore / ScienceDirect tam metin (abonelik), patent veritabanları (Espacenet/Google Patents — bu turda hiç taranmadı), Benoit ve HarFA ürün dokümantasyonu (sayfa içerikleri boş/404 döndü).

---

## 18. KAYNAKÇA (doğrulanmış bağlantılar)

**Yazılım**
- Fractalyse 3 — https://thema.univ-fcomte.fr/productions/software/fractalyse/ (kaynak: https://git.renater.fr/anonscm/git/fractalyse/fractalyse.git)
- FractDim — https://github.com/danielrendall/FractDim
- Multiscale Box-Counting for Vector Lines — https://github.com/roko-gis (DOI 10.5281/zenodo.20685864)
- GeoFractalLines — https://github.com/roko-gis/GeoFractalLines (DOI 10.5281/zenodo.20960565)
- GeoFractBox1D — DOI 10.5281/zenodo.21099450
- ImageJ FracLac — https://imagej.net/ij/plugins/fraclac/fraclac.html
- ImageJ Fractal Box Count — https://imagej.net/ij/docs/menus/analyze.html
- CRAN fractaldim — https://cran.r-project.org/web/packages/fractaldim/ (DOI 10.32614/CRAN.package.fractaldim)
- CRAN fractD — https://cran.r-project.org/web/packages/fractD/ (DOI 10.32614/CRAN.package.fractD)
- MATLAB FEX boxcount (Moisy) — https://www.mathworks.com/matlabcentral/fileexchange/13063-boxcount
- MATLAB FEX hausDim (Costa) — https://www.mathworks.com/matlabcentral/fileexchange/30329
- porespy — https://porespy.org · https://github.com/PMEAL/porespy
- Benoit (TruSoft) — https://www.trusoft-international.com/ (ürün detayı doğrulanamadı)
- HarFA — http://imagesci.fch.vut.cz/ (ürün detayı doğrulanamadı)
- RASH-HIT Fractal Studio — DOI 10.5281/zenodo.21693694 (concept), 10.5281/zenodo.21704656 (sürüm), ORCID 0009-0005-3423-255X

**Makaleler** — Bölüm 7 ve 9-10'da DOI'leriyle verilmiştir (Mandelbrot 1967; Liebovitch & Toth 1989; Sarkar & Chaudhuri 1994; Kyriacos ve ark. 1994; Buczkowski ve ark. 1998; Gonzato ve ark. 1998, 2000; Foroutan-pour ve ark. 1999; Bonnet ve ark. 2001; Bouda ve ark. 2016; Roy ve ark. 2007; Healy ve ark. 2017; Muller 1986, 1987; Klinkenberg 1994; Goodchild 1980; Sevcik 2006; Feng ve ark. 1996; Cutler 1993; Nayak ve ark. 2021; Yang ve ark. 2015; Malleswar ve ark. 2025; Douglass 2025 (preprint, düşük güvenilirlik); Ostwald & Ediz 2014; Okuyucu & Baştaş 2022; Kuruçay & Ediz 2025; Kartal & İnceoğlu 2023; Tercan 2023; Gondoputranto & Dibia 2022; Patuano & Lima 2021; Radović & Zekić 2024; Alghar & Marhayati 2023; Lee & Ostwald 2021; Katona 2020, 2023; Ali & Mustafa 2024).

**Doğrulama notu:** Tüm DOI ve URL'ler Crossref/OpenAlex/GitHub/PyPI/CRAN/Zenodo API'leri veya doğrudan HTTP isteğiyle kontrol edilmiştir. Kontrol edilemeyen alanlar metinde "Doğrulanamadı" olarak işaretlenmiştir. Hiçbir başlık, yazar, DOI veya tez numarası uydurulmamıştır.

---

# EK BÖLÜM A — SVG İÇİ KODU ANALİZ EDEN SİSTEMLER, KUTU SAYMA YÖNTEMİ EŞLEŞMESİ, HIZ KARŞILAŞTIRMASI VE "SVG MANTIĞI KİME AİT" SORUSU

Bu ek bölüm, kullanıcının açık talebi üzerine dört soruya odaklanır ve iddiaların hepsi ya iki rakip aracın **kaynak kodu birebir okunarak** ya da RASH-HIT'in bu makinede **canlı çalıştırılıp ölçülmesiyle** doğrulanmıştır.

## A.1 "SVG içindeki kodu analiz edip fraktal analiz yapan başka var mı?"

Kısa yanıt: SVG'yi **girdi olarak kabul edip** fraktal boyut hesaplayan yalnızca **iki** başka araç bulunabildi ve her ikisi de senin yaptığın işi yapmıyor.

### A.1.1 FractDim (danielrendall, Java, 2010-2011) — kaynak kodu okundu
Depo ağacı ve `.java` dosyaları GitHub API + raw.githubusercontent üzerinden çekilip incelendi. Bulgular:

- **SVG'yi kendi kodu ayrıştırmıyor; Apache Batik 1.7'ye devrediyor.** `pom.xml` batik-transcoder 1.7 bağımlılığını gösteriyor. `svg/Utilities.java` Batik `SAXSVGDocumentFactory` ile DOM kuruyor; `svgbridge/FDTranscoder.java` Batik'in `SVGAbstractTranscoder`'ından türeyip `root.paint(graphics)` çağırıyor. Yani **SVG semantiğini (stil, transform, eğri) çözen taraf FractDim değil, Batik motorudur.**
- `svgbridge/FDGraphics2D.java`: `fill(Shape)` çağrısı `draw()`'a yönlendiriliyor ve kodda "ignore for now - treat as draw" yorumu var → **dolgular (alanlar) sadece kontur gibi işleniyor; gerçek alan/doluluk kavramı yok.**
- **Transform yığını uygulanmıyor:** `draw()` içinde `s.getPathIterator(rawTransform)` çağrılıyor ve `rawTransform = AffineTransform.getScaleInstance(1,1)` (birim matris). Geçerli grafik dönüşümü (`gc.getTransform()`) hiçbir yerde uygulanmıyor.
- **Kutu "dolu" kararı geometrik kesişim değil, nokta örneklemesi + adaptif ikiye bölmedir.** `Grid.java`/`SquareCounter.doHandleCurve`: eğri t∈[0,1] üzerinde özyinelemeli bölünüp uç/orta noktaların düştüğü kareler işaretleniyor (`proximityThreshold = resolution/1000`). Bu, kutu ile geometri arasında analitik kesişim (predikat) HESAPLAMAZ; örneklem yoğunluğuna bağlı yaklaşık bir sayımdır.
- **Uzamsal indeks / quadtree YOK.** `GridSquareStore` sadece `HashSet<GridSquare>`. Tek "budama", eğri parametre uzayındaki adaptif bölünmedir.
- Performans sayısı yayımlanmamış; README tek cümle. Proje 2011'den beri ölü, lisans belirsiz.

### A.1.2 Fractalyse 3 (ThéMA, Java, GPL) — resmi kılavuz okundu (manual-en.pdf, 2022)
- **SVG'yi GİRDİ olarak KABUL ETMİYOR.** Kabul ettiği vektör formatları yalnızca coğrafi biçimlerdir: GeoPackage (.gpkg), GeoJSON, Shapefile (.shp). SVG onda sadece ÇIKTI formatıdır (grafik dışa aktarımı). Yani "SVG içindeki path/stil/transform kodunu okuyan" bir araç değildir.
- Vektör box-counting yapar (kılavuz 3.1.1: "point, line or polygon in case of vector data"), ama tasarım/CAD/illüstrasyon SVG'si değil coğrafi katman analiz eder. İç veri yapısının poligon-kutu kesişimi mi yoksa dahili ızgara indeksleme mi kullandığı kaynak seviyesinde **Doğrulanamadı** (kılavuz algoritma detayı vermiyor).

### A.1.3 Sonuç
İncelenen kaynaklar içinde, **bir tasarım/illüstrasyon SVG'sinin iç kodunu (path verisi + CSS/inline stil + transform + Bézier/yay) doğrudan okuyup, kutuları geometrinin kendisiyle kesin kesişim predikatıyla sayan** başka bir araç bulunamadı. FractDim SVG okur ama Batik'e devreder, dolguyu yok sayar, transform uygulamaz ve nokta örneklemesiyle sayar. Fractalyse SVG'yi hiç girdi almaz. Bu, senin projenin farkının "SVG destekliyor" cümlesinden çok daha derin olduğunu gösteriyor.

## A.2 "Kutuları benim yöntemimle sayan var mı?" — yöntem eşleşmesi

RASH-HIT'in sayım yöntemi (koddan doğrulanmış): kutu = Shapely `box()`; doluluk = GEOS `intersects()` **kesin geometrik predikatı** (DE-9IM); hızlandırma = STRtree uzamsal indeks + hiyerarşik quadtree'de **yalnız boş ebeveynin çocuklarını eleme**; sonuç kaba kuvvetle eşdeğer kalır.

| Araç | Kutu-geometri doluluk kararı | RASH-HIT ile aynı mı? |
|---|---|---|
| FractDim | Nokta örneklemesi + adaptif bisection | HAYIR — kesin kesişim değil, örneklem yaklaşık |
| Fractalyse (vektör) | Kılavuzda "hücre içinde en az bir nokta/çizgi/poligon"; iç mekanizma açıklanmamış | KISMEN/Doğrulanamadı — SVG girdi almaz zaten |
| ImageJ FracLac / BoxCount | Piksel ızgarasında siyah piksel sayımı (raster) | HAYIR — geometri yok, piksel var |
| MATLAB boxcount (Moisy) | İkili dizide dolu hücre (raster/dizi) | HAYIR |
| Roy vd. 2007 | Kutu-çizgi segmenti kesişimi (kesin, ama yalnız çizgi) | EN YAKIN — ama alan/poligon, SVG, uzamsal indeks yok |
| Bouda vd. 2016 | Çizgi-segment tabanlı, kuantizasyon hatasını eleyen | YAKIN motivasyon — ama kök segmentleri, GEOS/STRtree yok |
| roko-gis (2026) | Vektör çizgide box-counting + bootstrap | YAKIN — ama yalnız LINE, alan+karışık geometri ve SVG semantiği yok |

**Değerlendirme:** GEOS `intersects()` kesin predikatı + STRtree + boş-ebeveyn quadtree budaması + alan(poligon) ve çizgi karışık geometri **birlikte** kullanan; ve bunu genel SVG üzerinde yapan bir başka sistem incelenen kaynaklarda bulunamadı. En yakın yöntemsel komşu (Roy 2007) yalnızca çizgi ağlarında ve uzamsal indeks/quadtree olmadan çalışıyor.

## A.3 "Hız konusunda onlar nasıl yapmış? Benim hızım ne?" — ölçülmüş karşılaştırma

### A.3.1 RASH-HIT'in gerçek ölçülen hızı (bu makinede canlı çalıştırıldı)
Kaynak: (1) depodaki `outputs/16D/result.json` (mevcut kayıt); (2) bu oturumda `input_svgs/16D.svg` (426 KB) üzerinde `-l 10` ile CANLI çalıştırma (çıktı geçici dizine yazıldı, proje dizinine dokunulmadı).

Ölçülen sayım süreleri (16D, tek dosya, kesin kesişim):
- L5 (8.192 kutu): sayım 0.066 s
- L7 (131.072 kutu): 0.565 s
- L8 (524.288 kutu): 1.507 s
- L9 (2.097.152 kutu): 4.822 s
- **L10 (8.388.608 kutu, 3.110.338 dolu): sayım 15.8 s; 10 seviyenin tümü 24.6 s**
- Regresyon: Db=1.8229, R²=0.9997, güven 100/100 — anında (0.00 s)
- **Toplam (sayım + tüm dosya/paket üretimi, L10, EN AĞIR profil): 81.5 s**

Yani: kutu sayma + regresyon L10'a kadar **~25 saniyede** bitiyor; senin "1 dakikadan kısa sürede hem sayım hem dosya üretimi" ifaden L8-L9 seviyelerinde ve tipik SVG'lerde birebir doğrudur. En büyük dosyada (426 KB) mutlak sınır olan L10 + en ağır rapor profilinde toplam süre 81 s'ye çıkar; bu bir uç senaryodur ve sayımın kendisi yine 25 s altındadır. **Rapora bu ayrım dürüstçe yazılmalıdır: "sayım < 25 s @ L10; tam paket tipik seviyelerde < 60 s".**

Hızın kaynağı (koddan): (a) `shapely.box(...)` ile tüm hücreler tek vektörleştirilmiş C++ çağrısında; (b) `STRtree.query()` toplu uzamsal sorgu; (c) `shapely.intersects()` ufunc; (d) boş ebeveyn bloklarının milyonlarca çocuk hücresinin hiç oluşturulmaması (L10'da ~4.99M aday hücre budandı — kayıttan). Bu, "8.4M hücrenin hepsini tek tek test et" kaba kuvvetinden temel farktır.

### A.3.2 Rakipler hızı nasıl ele alıyor?
- **FractDim:** Yayımlanmış hız verisi YOK. Yöntemi nokta örneklemesi + adaptif bisection; uzamsal indeks yok. Ölçeklenebilirlik iddiası veya ölçümü bulunamadı.
- **Fractalyse:** Sayısal benchmark YOK. Kılavuz yalnız nitel: çok çekirdek paralellik (`-proc N`), OpenMPI ile küme (`-mpi`), 32-bit Java'da ~2 GB bellek tavanı uyarısı. "quad-core teorik olarak 4 kat hızlı" gibi teorik cümleler var, ölçüm yok.
- **ImageJ FracLac / MATLAB boxcount:** Bu araçların hızı esasen **görüntü çözünürlüğüne** bağlıdır (piksel sayısı). Yayımlanmış standart benchmark tablosu bu turda bulunamadı.
- **Kuramsal referans:** Liebovitch & Toth (1989, DOI 10.1016/0375-9601(89)90854-2) bit-interleaving ile box-counting'i O(N log N)'e indiren kanonik hızlandırma makalesidir; ancak nokta kümeleri içindir, poligon kesişimi içermez. RASH-HIT'in quadtree budaması bu fikrin geometriye taşınmış bir akrabasıdır.

> **Önemli dürüstlük notu:** Fraktal boyut literatüründe **yayımlanmış, karşılaştırılabilir çalışma-süresi (wall-clock) benchmark'ı neredeyse hiç yoktur.** Bu, senin lehine bir boşluktur: aynı SVG'leri hem RASH-HIT ile hem de FracLac (rasterize edip) ve mümkünse FractDim ile ölçüp yayımlarsan, alanda nadir bir "reproducible performance benchmark" katkısı yapmış olursun (bkz. Deney 5). Ancak makalede "en hızlı" demeden önce bu kıyas fiilen yapılmalıdır; şu an elimizde yalnız RASH-HIT'in kendi ölçümü var, rakiplerinki yok.

## A.4 "SVG mantığı başkasına mı ait?" — bağımlılık ve özgünlük sınırı

Bu, makale/tez savunmasında kritik ve dürüstçe belirtilmesi gereken noktadır:

- **RASH-HIT, SVG ayrıştırmasını kendi kodunda yapar.** `backend/svg_loader.py` (defusedxml ile XML) ve `backend/geometry_engine.py` (path komut ayrıştırma M/L/H/V/C/S/Q/T/A/Z + rect/circle/ellipse/line/polyline/polygon, `parse_transform_string` ile matrix/translate/scale/rotate/skew → 3×3 matris yığını, Bézier/yay düzleştirme). Yani SVG semantiğini çözen mantık **senin kodundur.** Alt katmanda geometri işlemleri için **Shapely/GEOS** (endüstri standardı, açık kaynak kütüphane) kullanılır — bu bir bağımlılıktır, ama SVG yorumlama mantığı değil, düşük seviye geometri motorudur.
- **Karşılaştırma:** FractDim'in SVG mantığı KENDİSİNE AİT DEĞİLDİR — tamamen Apache Batik'e devreder (parse, stil çözümleme, eğri, boyama hep Batik). Fractalyse ise SVG'yi hiç okumaz.
- **Sonuç:** "SVG'yi doğru okuma + tasarım geometrisini fraktal ölçüme hazırlama" mantığı senin özgün katkı alanındadır. Ancak makalede iki şey açıkça yazılmalı: (1) düşük seviye geometrik kesişim/birleştirme için Shapely/GEOS'a dayanıldığı (bu normaldir ve güç katar); (2) SVG stil/transform/eğri çözümlemesinin senin uygulaman olduğu. Bu ayrım yapılırsa "SVG mantığı bize ait mi?" sorusu net biçimde "evet, üst düzey SVG→geometri boru hattı bize ait; alt düzey geometri predikatları standart açık kaynak GEOS" olarak yanıtlanır.

## A.5 Uygulama alanı farkı — senin en güçlü ayrışman

Rakiplerin uygulama alanı ile senin alanın taban tabana farklı ve bu, özgünlük iddianın en sağlam ayağıdır:

- Fractalyse: **kentsel/coğrafi** doku (şehir formu, yol ağı, coğrafi katman).
- Roy 2007 / FracPaQ / roko-gis: **jeoloji** (kırık ağları, çatlak sistemleri, çizgisel yapılar).
- Bouda 2016: **botanik** (bitki kök mimarisi).
- ImageJ FracLac / ArchImage / Ostwald-Ediz: **mimari cephe** ve tıbbi/biyolojik **raster görüntü**.
- **RASH-HIT: tasarım alanı — vektörel tasarım öğelerinin (illüstrasyon, motif, desen, tasarım kompozisyonu) fraktal analizi.** İncelenen kaynaklar içinde, tasarım/illüstrasyon SVG'lerini birincil hedef alan, vektör-yerli, kesin kesişimli bir fraktal analiz aracı bulunamadı. Kültürel motif alanı bile (Bölüm 10) tümüyle raster fotoğraf tabanlıdır.

**Ölçülü özgünlük ifadesi (makale için önerilen):** "İncelenen kaynaklar içinde, tasarım kaynaklı vektör grafiklerin (SVG) iç geometrisini rasterize etmeden, tam stil/dönüşüm semantiğiyle çözüp kesin geometrik kesişimle kutu sayan ve bunu quadtree negatif-alan budamasıyla saniyeler mertebesinde yüksek çözünürlüğe (≈8,4 milyon kutu / L10) ölçekleyen bir sisteme doğrudan eşleşme bulunamamıştır." — "dünyada ilk" DEĞİL; "incelenen kaynaklar içinde doğrudan eşleşme bulunamadı" dili korunmalıdır.

---

# EK BÖLÜM B — RAKİP KAYNAK KODLARININ İNDİRİLİP OKUNMASI VE RASH-HIT ÜZERİNDE YAPILAN DOĞRULAMA DENEYLERİ

Bu bölüm, EK BÖLÜM A'daki belge/kılavuz temelli incelemenin ötesine geçerek
rakip yazılımların **kaynak kodlarının indirilip satır düzeyinde okunmasına**
ve bu iddiaların **RASH-HIT'in kendi motoru üzerinde çalıştırılan ölçümlerle**
sınanmasına dayanır. Bu bölümdeki tüm sayısal sonuçlar bu makinede üretilmiştir
ve tekrar üretilebilir; betikler `C:\Users\RaşitNarçiçek\rakip_analiz\` altındadır.

Analiz sırasında RASH-HIT proje dizinine hiçbir dosya yazılmamış, değiştirilmemiş
veya silinmemiştir; tüm incelemeler salt-okunur yapılmıştır.

## B.1 İndirilen ve okunan rakip kaynak kodları

| Yazılım | Dil | Satır | Lisans | Son sürüm/commit | Kaynak |
|---|---|---|---|---|---|
| FracPaQ | MATLAB | 20.512 | MIT | v2.8.0, Mart 2021 | github.com/DaveHealy-github/FracPaQ |
| Fractalyse 3 | Java | 16.380 | GPLv3 | v0.9.1, 5 Nisan 2022 | git.renater.fr/anonscm/git/fractalyse/fractalyse.git |
| FractDim | Java | 7.823 | GPLv3+ | 2009–2011 | github.com/danielrendall/FractDim |
| GeoFractalLines | Python | 1.476 | MIT | 2026 | github.com/roko-gis/GeoFractalLines |
| Multiscale Box-Counting Framework | Python | 742 | MIT | 2026 | github.com/roko-gis/Multiscale-Box-Counting-Framework-for-Fractal-Dimension-Analysis-of-Vector-Lines |

Karşılaştırma için RASH-HIT Fractal Studio: Python, 18.376 satır, Apache-2.0.

**Yöntem notu:** Bu bölümdeki her iddia, EK BÖLÜM A'daki gibi README veya
kılavuz metnine değil, doğrudan kaynak dosya yoluna ve kod satırına
dayandırılmıştır. Pazarlama ifadeleri kanıt olarak kullanılmamıştır.

## B.2 Temel yöntem ayrımı: kutu doluluğu nasıl belirleniyor?

Bu, projenin özgünlük iddiasının döndüğü teknik eksendir. Beş rakip
sistemin çekirdek sayım döngüsü okunmuştur.

**(a) Nokta örnekleme — FractDim**

`calculation/SquareCounter.java`, `doHandleCurve` → `evaluateBetween(curve, 0, 0.0, 1.0)`
metodu eğri üzerinde yalnızca **nokta** değerlendirir; kutu doluluğu
`Grid.java:263` içindeki tamsayı bölme ile belirlenir:

```java
int SquareelX = (int) Math.floor(p.x() / resolution);   // "todo - some serious testing!"
```

Segment ile kutu kenarı arasında geometrik kesişim testi hiçbir yerde
hesaplanmaz. Adaptif ikiye bölme (bisection) örnekleme sıklığını artırır ancak
yöntemi kesin kesişime dönüştürmez; `maxDepth` aşıldığında
`Log.app.warn("Max iteration depth reached - bailing out")` ile sessizce
eksik sayım yapılır.

Ayrıca dolgu (fill) semantiği tamamen devre dışıdır — `svgbridge/FDGraphics2D.java:81-86`:

```java
// ignore for now - treat as draw
@Override
public void fill(Shape s) {
    Log.misc.debug("Filling shape " + s.toString());
    draw(s);
}
```

Yani dolu bir şekil yalnızca konturundan sayılır. Bu, dolu alanların
boyutunun sistematik olarak düşük kestirilmesine yol açar.

**(b) Vertex binning — GeoFractalLines**

`_count_boxes_single` fonksiyonu geometriyi önce noktalara örnekler,
sonra bu noktaları tamsayı hücre indekslerine eşler:

```python
gx = np.floor((pts_array[:, 0] - min_xy[0]) / scale).astype(np.int32)
gy = np.floor((pts_array[:, 1] - min_xy[1]) / scale).astype(np.int32)
flat = np.ravel_multi_index((gx, gy), (nx, ny))
return np.unique(flat).size, flat
```

Kutu içinde çizgi bulunup bulunmadığı geometrik olarak sınanmaz; yalnızca
örneklenmiş köşe noktalarının düştüğü kutular sayılır. Doğruluk, örnekleme
yoğunluğuna (`ADAPTIVE_SAMPLING_FACTOR = 0.8`) bağlıdır ve seyrek örneklenmiş
uzun segmentlerde ara kutular kaçırılabilir.

**(c) Box-counting bulunmaması — FracPaQ**

Depo genelinde box-counting veya fraktal boyut hesabı **yoktur**;
`grep -ric "boxcount|box-count|fractal" --include=*.m .` sıfır eşleşme verir.
Mekânsal örüntü niceliği bunun yerine tek ölçekli **dairesel tarama
pencereleri** ile yapılır (`guiFracPaQ2Dpattern.m`, analitik segment-daire
sekant testi). Blok alanı analizi ise geometriyi diske BMP olarak basıp
geri okuyarak, yani fiilen rasterleştirerek yapılır
(`guiFracPaQ2Dlength.m:486-495`): `print(...,'-dbmp256')` → `imread` →
`imbinarize` → `bwconncomp`.

Bu nedenle FracPaQ, isim benzerliğine rağmen RASH-HIT'in **yöntemsel rakibi
değildir**; Kategori D/E'ye (alan/kısmi ilişki) aittir.

**(d) Kesin geometrik kesişim — Multiscale Box-Counting Framework**

```python
cell_orig = QgsRectangle(min(xs), min(ys), max(xs), max(ys))
candidates = spatial_index.intersects(cell_orig)      # bbox ön-eleme
if candidates:
    cell_geom = QgsGeometry.fromRect(cell_orig)
    for fid in candidates:
        if feature_geoms[fid].intersects(cell_geom):  # gerçek GEOS kesişimi
            count += 1
            break
```

**(e) Kesin geometrik kesişim — Fractalyse 3**

`method/vector/mono/BoxCountingMethod.java`, `BoxCountingTask.execute` (satır 74-94):

```java
Polygon cellGeom = grid.getCellGeom(x, y);
for(Feature f : coverage.getFeatures(cellGeom.getEnvelopeInternal())) {
    if(f.getGeometry().intersects(cellGeom)) { nb++; break; }
}
```

LocationTech JTS kullanılır (eski vividsolutions değil). Rasterleştirme
veya vertex binning yoktur.

**Sonuç:** İncelenen beş sistemin üçü (FractDim, GeoFractalLines, FracPaQ)
kesin geometrik kesişim yapmamaktadır. Kesin kesişim yapan iki sistem
(Fractalyse, Multiscale-BC) ise **SVG değil, coğrafi vektör formatları**
(GeoPackage/GeoJSON/Shapefile veya QGIS katmanı) okumaktadır.

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

## B.6 Doğrulama Deneyi 1 — Izgara konumu duyarlılığının ölçülmesi

**Amaç.** Rakiplerin tamamında bulunan "çoklu ızgara orijini" mekanizmasının
RASH-HIT'te bulunmamasının sayısal sonucunu ölçmek.

**Yöntem.** Koch eğrisi (5. yineleme), matematiksel kesin değeri
D = log4/log3 = 1.261860. Sayım yöntemi RASH-HIT ile aynı sınıfta:
`shapely` + `STRtree` + kesin `intersects`. Tek değişken ızgara orijinidir;
16 farklı orijin (4×4 kesirli kaydırma) denenmiştir. Ölçek seviyeleri:
8, 16, 32, 64, 128, 256. Betik: `rakip_analiz/gridbias.py`.

**Sonuçlar — ölçek başına dolu kutu sayısı:**

| Izgara bölmesi | Sabit orijin | 16 orijin min. | Ortalama | Maks. | Yayılma % |
|---|---|---|---|---|---|
| 8 | 16 | 12 | 16,9 | 20 | 66,7 |
| 16 | 32 | 32 | 39,5 | 49 | 53,1 |
| 32 | 91 | 81 | 89,2 | 101 | 24,7 |
| 64 | 227 | 191 | 208,7 | 227 | 18,8 |
| 128 | 494 | 489 | 501,0 | 516 | 5,5 |
| 256 | 1112 | 1088 | 1135,4 | 1185 | 8,9 |

**Elde edilen fraktal boyutlar:**

| Toplama kuralı | D | Mutlak hata | R² |
|---|---|---|---|
| Sabit tek ızgara (RASH-HIT'in bugünkü davranışı) | 1,250245 | 0,011615 | 0,997519 |
| 16 orijin üzerinden minimum (Fractalyse/FractDim kuralı) | 1,301461 | 0,039601 | 0,999195 |
| 16 orijin üzerinden ortalama (QGIS tabanlı iki depo) | 1,215872 | 0,045988 | 0,999913 |

**Yalnızca ızgara orijini değiştirilerek elde edilen D dağılımı:**
en küçük 1,182981 — en büyük 1,271940 — yayılma 0,088960 — standart sapma 0,023323.

**Yorum (temkinli).** Bu koşuda çoklu orijin toplama kuralları, sabit ızgaradan
**daha doğru** bir D üretmemiştir; sabit ızgaranın hatası (0,0116) minimum
(0,0396) ve ortalama (0,0460) kurallarından düşüktür. Dolayısıyla çoklu orijin
mekanizması "doğruluğu artırır" gerekçesiyle savunulamaz. Ancak bulgular üç
ayrı gerekçeyi desteklemektedir:

1. **Belirsizliğin nicelenmesi.** Aynı geometri, aynı algoritma ve aynı kesin
   kesişim ile yalnızca ızgara konumu değiştirildiğinde bildirilen D değeri
   1,18–1,27 aralığında değişmektedir (σ = 0,023). Tek bir nokta tahmin
   bildiren bir sistem, bu belirsizliği kullanıcıya aktaramaz. Motifler arası
   0,02 düzeyindeki farkların anlamlı olup olmadığı bu bilgi olmadan
   değerlendirilemez.
2. **Keyfiliğin giderilmesi.** Tek bir ızgara hizasının seçimi metodolojik
   olarak gerekçelendirilemez; buna karşılık "N konum denenip minimum alındı"
   kuralı literatürde yerleşiktir (Fractalyse, FractDim).
3. **Regresyon kalitesi.** Çoklu orijin ortalaması R²'yi 0,997519'dan
   0,999913'e yükseltmektedir. RASH-HIT'in `backend/confidence.py` modülü
   güven skorunda R²'ye %40 ağırlık verdiğinden, bu doğrudan bildirilen güven
   düzeyini etkiler.

## B.7 Doğrulama Deneyi 2 — RASH-HIT'in öteleme duyarlılığı

**Amaç.** "Sistem ızgarayı tasarımın en-boy oranına göre kurduğu için tasarımın
kanvas içinde kaydırılması sonucu etkilemez" varsayımını RASH-HIT'in kendi
üretim hattıyla sınamak.

**Yöntem.** Aynı Koch geometrisi (4. yineleme), aynı 800×800 viewBox içinde
yalnızca `transform="translate(T,100)"` değeri değiştirilerek üç SVG üretildi
(T = 100, 103, 150). Analiz RASH-HIT'in kendi komut satırı arayüzüyle
çalıştırıldı:

```
python run_analysis.py -i koch_tT.svg -l 7 --grid-mode <mod> --profile reproducible
```

**Sonuçlar:**

| Öteleme | grid-mode | D | R² | Güven skoru |
|---|---|---|---|---|
| translate(100,100) | canvas_aspect | 1,1690 | 0,9951 | 92,5 (Yüksek) |
| translate(103,100) | canvas_aspect | 1,1955 | 0,9992 | 92,5 (Yüksek) |
| translate(150,100) | canvas_aspect | 1,1986 | 0,9982 | 92,5 (Yüksek) |
| translate(100,100) | square_bbox | 1,1690 | 0,9951 | 92,5 (Yüksek) |
| translate(103,100) | square_bbox | 1,1955 | 0,9992 | 92,5 (Yüksek) |
| translate(150,100) | square_bbox | 1,1986 | 0,9982 | 92,5 (Yüksek) |

Seviye bazında dolu kutu sayıları da değişmektedir (T=100 → T=103):
L2: 20→16, L3: 40→35, L4: 82→76, L5: 172→169, L6: 410→400.

**Bulgu 1 — öteleme duyarlılığı doğrulanmıştır.** Tasarımın yalnızca 3 birim
sağa kaydırılması bildirilen fraktal boyutu 1,1690'dan 1,1955'e taşımaktadır
(Δ = 0,0265). Bunun nedeni, ızgaranın **tasarım sınır kutusuna değil, SVG
viewBox'ına (kanvasa) demirlenmiş olmasıdır**: `backend/grid_planner.py`
içindeki `create_grid_plan` fonksiyonu varsayılan `canvas_aspect` modunda
`raw_bounds` değerini viewBox'tan türetir. Sistemin en-boy oranını algılayıp
kareye yakın hücreler üretmesi doğrudur; ancak bu, ızgaranın *hizasını* değil
yalnızca *hücre biçimini* belirler.

**Bulgu 2 — güven skoru bu değişkenliği yansıtmamaktadır.** Her üç çalıştırmada
da güven skoru 92,5 ("Yüksek") ve akademik yorum "Sonuç doğrudan akademik
yayına dahil edilebilir" olarak üretilmiştir. Yani sistem, aynı motif için
birbirinden farklı üç sonucu eşit ve yüksek güvenle bildirmektedir.

**Bulgu 3 — doğruluk sapması.** Kesin değeri 1,261860 olan Koch eğrisi için
üretilen değerler 1,169–1,199 aralığındadır; mutlak hata yaklaşık 0,06–0,09
düzeyindedir. Bu, B.9'da açıklanan ölçekleme penceresi seçiminin
bulunmamasıyla tutarlıdır ve bilinen-değer doğrulamasının neden zorunlu
olduğunu göstermektedir.

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

## B.10 Güncellenmiş karşılaştırma matrisi (kaynak kodu doğrulamalı)

Yalnızca kaynak kodda doğrulanan özellikler işaretlenmiştir.

| Ölçüt | RASH-HIT | Fractalyse 3 | FractDim | GeoFractalLines | Multiscale-BC | FracPaQ |
|---|---|---|---|---|---|---|
| Kutu sayma | Var | Var | Var | Var | Var | Yok |
| SVG okuma | Var (tam) | Yok | Kısmen (Batik, dönüşüm yok sayılır) | Yok | Yok | Kısmen (yalnız M/L) |
| CBS vektör okuma | Yok | Var | Yok | Var | Var | Yok |
| Kesin geometrik kesişim | Var | Var | Yok (nokta örnekleme) | Yok (vertex binning) | Var | Yok |
| Dolgu (fill) semantiği | Var | Kısmen (poligon) | Yok (açıkça devre dışı) | Yok | Kısmen | Yok |
| Rasterleştirme gereksinimi | Yok | Yok | Yok | Yok | Yok | Var (blok analizi) |
| Uzamsal indeks | Var (STRtree) | Var | Yok | Yok | Var | Yok |
| Hiyerarşik budama | Var | Yok | Yok | Yok | Yok | Yok |
| Çoklu ızgara orijini | Yok | Var | Var | Var | Var | Yok |
| Izgara rotasyonu | Yok | Yok | Var | Yok | Var | Yok |
| Bootstrap güven aralığı | Yok | Var | Yok | Var | Var | Yok |
| Otomatik ölçek penceresi | Yok | Var | Yok | Var | Var | Yok |
| Çoklu test düzeltmesi | Yok | Yok | Yok | Yok | Var (BY-FDR) | Yok |
| Multifraktal spektrum | Yok | Var | Yok | Var | Yok | Yok |
| Bilinen-değer doğrulaması | Yok | Yok | Yok | Var | Yok | Yok |
| Toplu analiz | Var | Var | Kısmen | Kısmen | Var | Kısmen |
| Web arayüzü | Var | Yok | Yok | Yok | Yok | Yok |
| Masaüstü arayüzü | Var | Var | Var (Swing) | Yok | Var (QGIS) | Var (MATLAB) |
| Komut satırı | Var | Var | Doğrulanamadı | Var | Var | Yok |
| Açık kaynak | Var (Apache-2.0) | Var (GPLv3) | Var (GPLv3) | Var (MIT) | Var (MIT) | Var (MIT) |
| Etkin geliştirme | Var | Kısmen (2022) | Yok (2011) | Var (2026) | Var (2026) | Kısmen (2021) |
| Kültürel motife uygulama | Var | Yok | Yok | Yok | Yok | Yok |

## B.11 Özgünlük değerlendirmesinin gözden geçirilmiş hâli

Kaynak kodu incelemesi, EK BÖLÜM A'daki değerlendirmeyi iki yönde
değiştirmektedir.

**Güçlenen yönler.**

1. *SVG üzerinde kesin geometrik kutu sayımı.* İncelenen beş sistem içinde bu
   birleşimi sağlayan başka bir sisteme rastlanmamıştır. SVG okuyan iki sistem
   kesin kesişim yapmamakta (FractDim nokta örnekler, FracPaQ box-counting
   içermemektedir); kesin kesişim yapan iki sistem SVG okumamaktadır. Bu tespit
   kaynak kod satırlarıyla belgelenmiştir ve "ilk" iddiası içermemektedir.
2. *Hiyerarşik negatif-uzay budaması.* İncelenen hiçbir rakipte
   bulunmamaktadır. Ölçülebilir ve savunulabilir bir algoritmik katkıdır.
3. *Dolgu semantiğinin doğru ele alınması.* FractDim'in dolguyu bilinçli olarak
   kontura indirgemesi, RASH-HIT'in yaklaşımını karşılaştırmalı olarak
   değerlidir kılar; motif ve süsleme verisinde dolu alanlar baskındır.

**Zayıflayan yönler.**

1. İstatistiksel titizlik bakımından RASH-HIT, GeoFractalLines ve
   Multiscale-BC'nin gerisindedir (güven aralığı, otomatik ölçek penceresi,
   çoklu test düzeltmesi yok).
2. Izgara konumu duyarlılığı ölçülmüş ve doğrulanmıştır (B.7); rakiplerin
   tamamı bu sorunu ele almaktadır.
3. Bilinen-değer doğrulaması bulunmadığından, B.8'deki gibi sessiz hatalar
   yakalanamamaktadır.

**Önerilen özgünlük ifadesi (temkinli):**

> Bu çalışma, SVG vektör geometrisi üzerinde rasterleştirmeye başvurmadan,
> uzamsal indeksleme ve hiyerarşik negatif-uzay budaması ile hızlandırılmış
> kesin geometrik kesişim tabanlı bir kutu sayma yöntemi sunmakta ve bunu
> geleneksel motif korpusuna uygulamaktadır. İncelenen açık kaynak sistemler
> içinde bu bileşen birleşimine doğrudan bir eşleşme bulunamamıştır.

Katkı türü sıralaması: (1) yazılım/algoritma katkısı — en güçlü;
(2) uygulama katkısı (kültürel motif korpusu) — güçlü; (3) yöntemsel katkı —
en zayıf, çünkü kutu sayma yönteminin kendisi değiştirilmemektedir.

## B.12 Makale öncesi zorunlu görülen çalışmalar

Öncelik sırasına göre:

1. `square_bbox` hatasının giderilmesi (B.8). Tek çağrı noktası düzeltmesi;
   `grid_mode` ve `geometry_bounds` parametrelerinin ikinci `create_grid_plan`
   çağrısına iletilmesi yeterlidir. `grid_mode` alanının `result.json` içine
   yazılması da önerilir.
2. Bilinen-değer doğrulama takımı: Koch (1,26186), Sierpinski üçgeni (1,58496),
   Minkowski kolyesi (1,5), Cantor tozu (0,6309), dolu kare (2,0), düz çizgi
   (1,0). Hedef: %2'nin altında mutlak hata.
3. Değişmezlik testleri: öteleme, ölçekleme ve döndürme altında D'nin
   kararlılığı. B.7'deki 0,0265'lik öteleme sapması bu testin doğrudan
   gerekçesidir.
4. Çoklu ızgara orijini desteğinin eklenmesi ve toplama kuralının (minimum
   ve/veya ortalama) yapılandırılabilir kılınması; B.6'daki yayılma
   değerlerinin belirsizlik olarak raporlanması.
5. Bootstrap güven aralığının eklenmesi ve `confidence.py` skoruna dahil
   edilmesi.
6. Otomatik ölçekleme penceresi seçimi (AIC veya R² taraması); `included_in_fit`
   alanının etkin hâle getirilmesi.
7. Çapraz doğrulama: aynı geometrinin GeoPackage'a dönüştürülüp Fractalyse ve
   Multiscale-BC ile analiz edilmesi; D farkının %1'in altında olması hedefi.
8. Başarım karşılaştırması: budama açık/kapalı çalışma süresi ve kesin kesişim
   testi sayısı; ölçek seviyesine göre ölçeklenme eğrisi.

## B.13 Bu bölümün üretim kayıtları

Betikler ve ham çıktılar: `C:\Users\RaşitNarçiçek\rakip_analiz\`
(`gridbias.py`, `gridbias_sonuc.txt`, `koch_t100.svg`, `koch_t103.svg`,
`koch_t150.svg`, klonlanmış rakip depolar).

RASH-HIT proje dizininde hiçbir dosya oluşturulmamış, değiştirilmemiş veya
silinmemiştir. B.7 ve B.8 deneyleri için kullanılan geçici enstrümantasyon,
ölçüm tamamlandıktan sonra geri alınmış ve dosyaların özgün hâlde olduğu
doğrulanmıştır.

---

---

# EK BÖLÜM C — İDDİA–KOD UYUŞMAZLIKLARININ ÖZGÜNLÜK İDDİASINA ETKİSİ (ÖZET)

> **Ayrıntılı yazılım kusuru dökümü bu rapordan çıkarılmış ve şu dosyaya taşınmıştır:**
> `RaşitNarçiçek\rakip_analiz\YAZILIM_SORUNLARI.md`
> (Bölüm C: 34 iddianın kodla karşılaştırılması — 21 doğru, 10 yanlış, 3 kısmen.
>  Bölüm D: depo/sürüm/provenance/test altyapısı — 5 ek bulgu.)
>
> Burada yalnızca **makale ve özgünlük iddiası açısından sonuç doğuran**
> uyuşmazlıklar tutulmuştur.

## C.Ö.1 Yayın kimliği ve öncelik tarihi (özgünlük lehine)

Proje **zaten kamuya açık biçimde yayımlanmıştır** ve bu, özgünlük
tartışmasında en somut dayanaktır:

| Kimlik | Değer | Durum (2026-08-07) |
|:---|:---|:---|
| GitHub | `rasitnarcicek/RASH-HIT-Fractal-Studio` | Açık, Apache-2.0, ilk commit **2026-07-29** |
| Zenodo DOI | `10.5281/zenodo.21704656` | Canlı, v1.0.5, 2026-07-30 |
| Concept DOI | `10.5281/zenodo.21693694` | Canlı |
| ORCID | `0009-0005-3423-255X` | Doğrulandı |

**Sonuç:** Öncelik tarihi olarak **2026-07-29** belgelenebilir. Makalede
"yazılım katkısı" savunulurken arşivlenmiş DOI'ye atıf yapılabilir.

⚠️ Ancak `CITATION.cff` **v1.0.6** ilan ederken DOI **v1.0.5** kaydına
işaret ediyor ve GitHub'da v1.0.6 sürümü yok. Makale gönderiminden önce bu
düzeltilmelidir, aksi hâlde "tam tekrarlanabilirlik" iddiası hakem
tarafından kolayca çürütülür. (Ayrıntı: YAZILIM_SORUNLARI.md § D.2)

## C.Ö.2 Özgünlük iddiasını doğrudan zayıflatan 3 uyuşmazlık

Aşağıdakiler makalede **iddia edilmeden önce düzeltilmesi gereken**
noktalardır; hepsi ölçümle kanıtlanmıştır.

| # | İddia (belge) | Kodun gerçeği | Makaleye etkisi |
|:--|:---|:---|:---|
| 1 | "nonzero → unary_union, evenodd → symmetric_difference" (README) | `fill_rule` değişkeni **kodda hiç tanımlı değil**; her zaman `symmetric_difference` uygulanıyor. Ölçüm: aynı yönlü iç içe kareler → alan **7500** (nonzero'da 10000 olmalıydı) | "SVG dolgu semantiğine tam uyum" iddiası **şu hâliyle savunulamaz** |
| 2 | "Regresyon kalitesi ve güven skoru ile doğrulama" | Dejenere veri (100,100,100,100,100) → **Db=0,000000, R²=1,0, güven 92,0 "Yüksek"**. NaN döndüren güvenli fonksiyon yalnızca testlerde kullanılıyor, üretim yolu `compute_loglog_regression` çağırıyor | "Doğrulanmış sonuç" iddiası **karşı örnekle çürütülebilir** |
| 3 | "Adaptif eğri düzleştirme" | Sabit adımlı örnekleme; `steps=24`'te sarkma **0,2268 birim** → L10'da hücrenin %58'i, L11'de hücreden büyük | Yüksek ölçeklerde **sayısal tavan**; çok ölçekli analiz derinliği iddiası sınırlı |

Ayrıca doyum (saturation) denetimi `regression.py:92-94`'te **boş `pass`**;
tamamen dolu ızgarada hiçbir seviye dışlanmıyor — Koch eğrisindeki sapmanın
(EK B.7) nedeni budur.

## C.Ö.3 Neden fark edilmemiş? — yapısal neden (bağımsız teyitli)

Depodaki **açık PR #10** (2026-08-02) `backend/` test kapsamını **%25**,
`intersection_hierarchical.py` ve `intersection_cpu_area.py`'yi **%0**
olarak ölçmüştür. Sayısal sonucu üreten modüller hiç çalıştırılmıyor;
492 testin yukarıdaki kusurların hiçbirini yakalamaması bununla tutarlıdır.

Kaynak: https://github.com/rasitnarcicek/RASH-HIT-Fractal-Studio/pull/10

**Ek ölçüm (bu çalışma):** Test paketi projenin kopyasında iki kez sonuna
kadar koşturuldu ve iki koşuda da **aynı 15 test başarısız** oldu
(koşu 1: 15 failed / 432 passed / 709 s — koşu 2: 15 failed / 433 passed / 644 s).
Sonuç deterministiktir.

Bu bulgunun **özgünlük açısından iki yönü** vardır:

- *Lehte:* Başarısız testlerin **hiçbiri çekirdek matematikte değildir.**
  Altın örnek testleri (16/16A/16B/16C → Db ∈ [1,5–2,0]) ve Phase 8 motor
  doğruluk testleri geçmektedir. Hatalar arayüz sözleşmesi, i18n, belge
  tutarlılığı ve bir güvenlik kapısındadır.
- *Aleyhte:* DOI ile yayımlanmış sürüm (v1.0.5) **15 kırmızı testle**
  arşivlenmiştir. Hakem depoyu klonlayıp `pytest` çalıştırırsa bunu
  doğrudan görecektir; "tekrarlanabilir araştırma" iddiası için zaaftır.
  Ayrıca `frontend/js/i18n.js` docstring'i "EN is code-authoritative" derken
  kod `const DEFAULT_LANG = 'tr'` tanımlıyor — **belge/kod çelişkisi deseni
  arayüz katmanında da tekrarlanıyor.**

Ayrıntı: YAZILIM_SORUNLARI.md § D.6

## C.Ö.4 Özgünlük iddiası **ayakta kalan** yönler

Kusurlara rağmen aşağıdakiler kodla doğrulanmış ve rakiplerde bulunamamıştır:

1. **Kontur (stroke) kesişiminin mesafe yüklemiyle çözülmesi** —
   `distance(çizgi, hücre) ≤ w/2`, tampon poligonu üretmeden.
   İncelenen 5 rakip sistemde yok; hepsi round cap/join varsayıyor veya
   `stroke-linecap`'i hiç ayrıştırmıyor. **En güçlü yöntemsel ayrışma.**
2. **SHA-256 manifest sistemi** — `academic_exporter.py:204, 1537-1609`'da
   gerçekten uygulanmış; her çıktı dosyası hash'leniyor, `manifest.json`
   yazılıyor, report.html'e gömülüyor. Provenance'ın 4. iddiası **doğrulandı**.
3. **Raster'a hiç düşmeden doğrudan vektör geometrisi üzerinde kutu sayımı** —
   EK B'de incelenen rakiplerin tamamı raster ara adımı kullanıyor.

⚠️ Buna karşılık `intersection_cpu_area.py`, `CODE_PROVENANCE.md`'de
"Exact Vector Geometry Engine" olarak sayılmasına rağmen **üretimde hiç
çağrılmayan 30 satırlık bir adaptördür** (YAZILIM_SORUNLARI.md § D.3).
Mimari anlatımı buna göre düzeltilmelidir.

## C.Ö.5 Makale açısından tavsiye

Özgünlük **"yöntemsel katkı"** olarak değil, öncelikle
**"yazılım katkısı + uygulama katkısı"** olarak savunulmalıdır:
kutu sayma teorisi yeni değildir, ancak *raster'sız vektör hattı +
mesafe yüklemli kontur kesişimi + SHA-256 tekrarlanabilirlik paketi*
birleşimi incelenen kaynaklarda doğrudan eşleşmemiştir.

Bu iddiada bulunulmadan **önce** C.Ö.2'deki 3 kusur giderilmeli, aksi
hâlde hakem "doğrulanmış" ve "SVG semantiğine uyumlu" ifadelerini
karşı örnekle çürütebilir.

---

# EK BÖLÜM D — ÜÇ TEMEL ÖZGÜNLÜK İDDİASININ HEDEFLİ SINANMASI

**Üretim tarihi:** 3. araştırma turu. **Yöntem:** Crossref REST API, OpenAlex REST API, arXiv API, GitHub Search API, PyPI — tamamı `curl` ile doğrudan sorgulanmıştır. Bu bölümdeki tüm DOI'ler ayrıca **bağımsız olarak Crossref'ten tek tek teyit edilmiştir**; teyit edilemeyen tek kayıt (10.25358/openscience-14974) açıkça işaretlenmiştir.

**Amaç:** Raporun önceki turlarında "ayakta kalan" olarak nitelenen üç teknik özgünlük iddiasını, "bu daha önce yapılmış mı?" sorusuyla kanıta dayalı biçimde sınamak.

---

## D.1 İDDİA 1 — "SVG vektör geometrisi üzerinde, rasterizasyon olmadan, kesin kesişim predikatı ile kutu sayma"

### Sonuç: 🔴 ÖNCEKİ SANAT BULUNDU — iddia yöntem düzeyinde SAVUNULAMAZ

**Belirleyici kanıt: Douglass, R. (2025)**, *Fractal and Fractional* 9(10):633, **DOI 10.3390/fractalfract9100633**, yayın **29 Eylül 2025**, MDPI, CC-BY, hakemli, Crossref'te 2 atıf.

Makale özetinden birebir alıntı:

> *"Unlike traditional pixelated approaches that suffer from rasterization artifacts, the method used directly analyzes geometric line segments, providing superior accuracy for mathematical fractals and other computational applications."*

**Tarih karşılaştırması — bu bulgunun ağırlığını belirleyen unsur:**

| Olay | Tarih |
|---|---|
| Douglass preprint (10.20944/preprints202508.1392.v1) | Ağustos 2025 |
| Douglass hakemli yayın (10.3390/fractalfract9100633) | **29 Eylül 2025** |
| RASH-HIT Zenodo öncelik tarihi | **29 Temmuz 2026** |
| **Fark** | **Douglass ~10 ay ÖNCE** |

Yani "rasterizasyonsuz, doğrudan geometri (çizgi segmentleri) üzerinde kutu sayma" fikri, RASH-HIT'in öncelik tarihinden önce hakemli literatürde yayımlanmıştır.

### Douglass ile RASH-HIT arasında AYRIŞAN yönler (RASH-HIT lehine kalanlar)

| Boyut | Douglass 2025 | RASH-HIT |
|---|---|---|
| Girdi | **Kod içinde üretilen segment listesi** — hiçbir tasarım dosya formatı okunmuyor; tam metinde "SVG" 0 kez geçiyor | **SVG dosyası** (CSS/inline stil çözümleme, affine transform yığını, Bézier/arc düzleştirme) |
| Geometri türü | Yalnız **çizgi segmentleri** — yazarın beyanı: *"limited to two-dimensional line segment analysis"* | Çizgi **ve alan poligonları** |
| Kesişim | **Liang–Barsky çizgi kırpma** (tam metinden doğrulandı) — çizgiye özel, poligon yok | **Shapely/GEOS `intersects()`** — çizgi + poligon |
| Uzamsal indeks | **Hiyerarşik uzamsal bölümleme** (doğrulandı) | STRtree + quadtree budama |
| Yazılım dağıtımı | ⚠ **DÜZELTME: kod AÇIK** — github.com/rwdlnk/Fractal-Dimension-Analyzer (Python3). Araştırma betiği, paketlenmiş arayüz yok | Açık kaynak paket: CLI/TUI/web REST |
| Tekrarlanabilirlik altyapısı | R² raporlama | SHA-256 manifest, toplu analiz, i18n |
| Ölçek seçimi | **Otomatik (üç fazlı sliding window)** | Kullanıcı/varsayılan aralık — **Douglass burada RASH-HIT'ten ileride** |

### Diğer ilgili bulgular

- **danielrendall/FractDim** (Java, SVG, 2010–2011, terk edilmiş, lisanssız) — GitHub'da `fractal+dimension+svg` sorgusu yalnızca FractDim ve RASH-HIT'i döndürmüştür. SVG+box-counting fikrinin 2010'da denendiğinin kanıtı.
- **fractopo** — Shapely/geopandas tabanlı çatlak ağı analiz aracı (JOSS yayını var). Geometri kütüphanesi kullanan en yakın jeobilim aracı, ancak SVG/kesin box-counting motoru olarak konumlanmıyor.

### Negatif bulgular (RASH-HIT lehine, iddianın daraltılmış hâlini destekleyen)

GitHub Search API'de şu sorgular **ilgili hiçbir depo döndürmemiştir**: `fractal+dimension+postgis`, `fractal+dimension+gdal`, `qgis+fractal+dimension+plugin`, `fractal+dimension+geopandas`, `jts+fractal`. PyPI'da `fractal-dimension`, `boxcount`, `fractalanalysis` paketleri **mevcut değildir**. `boxcounting language:python` sonuçlarının tamamı (FracStack, spacial-boxcounting-cpu-gpu vb.) **raster** tabanlıdır.

### Temkinli değerlendirme

İddianın **yöntem** kısmı ("rasterizasyonsuz geometrik box-counting yeni bir yaklaşımdır") artık savunulamaz — Douglass 2025 tarafından öncelenmiştir. Savunulabilir kalan **daraltılmış** ifade şudur:

> *"SVG girdisini doğrudan tüketen, kesin GEOS kesişim predikatı ile hem çizgi hem alan geometrilerinde çalışan, paketlenmiş ve tekrarlanabilir bir açık kaynak araç; incelenen kaynaklar içinde bu spesifik kombinasyona doğrudan eşleşme bulunamamıştır."*

**Zorunlu eylem:** Douglass 2025 atıf verilmeli, karşılaştırma matrisine eklenmeli, mümkünse aynı test fraktalleri (Koch, Sierpinski, Minkowski, Hilbert, Dragon) üzerinde sayısal kıyaslama yapılmalıdır. "İlk", "tek", "daha önce yapılmamış" ifadeleri kullanılmamalıdır.

---

## D.2 İDDİA 2 — "STRtree uzamsal indeks + quadtree hiyerarşik negatif alan budaması ile hızlandırma"

### Sonuç: 🟠 KISMEN BULUNDU — algoritmik olarak YENİ DEĞİL, mühendislik katkısı olarak savunulabilir

Hiyerarşik/ağaç tabanlı kutu sayma hızlandırması **35 yıllık, köklü ve yoğun çalışılmış** bir literatürdür. Quadtree özyinelemesi zaten box-counting'in doğal biçimidir.

| Yazar / Yıl | Başlık | DOI | Katkı |
|---|---|---|---|
| Liebovitch & Toth, 1989 | A fast algorithm to determine fractal dimensions by box counting | 10.1016/0375-9601(89)90854-2 | Bit-interleaving, O(N log N), örtük quadtree |
| **Hou, Gilmore, Mindlin, Solari, 1990** | An efficient algorithm for fast box counting | **10.1016/0375-9601(90)90844-E** | İkinci klasik hızlı algoritma |
| **Kruger, 1996** | Implementation of a fast box-counting algorithm | **10.1016/0010-4655(96)00080-X** | Uygulama optimizasyonu |
| Gonzato, 1998 | A practical implementation of the box counting algorithm | 10.1016/S0098-3004(97)00137-4 | Pratik uygulama + ölçek seçimi |
| **Alevizos & Vrahatis, 2010** | Optimal Dynamic Box-Counting Algorithm | **10.1142/S0218127410028197** | Optimal dinamik algoritma |
| **Mukundan, 2015** | Parallel Implementation of the Box Counting Algorithm in OpenCL | **10.1142/S0218348X15500231** | GPU paralelleştirme |
| **Nikolaidis & Nikolaidis, 2016** | The box-merging implementation of the box-counting algorithm | **10.1515/jmbm-2016-0006** | Kutu birleştirme ile verimlilik |

### Ters yönlü ilgili literatür (dikkat: iddiayı desteklemez)

- "Analysis of n-Dimensional Quadtrees using the Hausdorff Fractal Dimension" (DOI 10.1184/R1/6603476, Faloutsos/Gaede çizgisi, VLDB'95 kökenli) — **quadtree'yi hızlandırmak için fraktal boyut** kullanır, tersi değil.
- "Self-spacial join selectivity estimation using fractal concepts" (DOI 10.1145/279339.279342) ve "Estimating the Selectivity of Spatial Queries Using the 'Correlation' Fractal Dimension" (DOI 10.1184/R1/6605282) — R-tree/uzamsal indeks bağlamında fraktal boyutu **maliyet modeli** olarak kullanır.

Bu kayıtlar, "quadtree ↔ box-counting" ve "R-tree ↔ fraktal boyut" ilişkisinin veritabanı literatüründe uzun süredir bilindiğini gösterir.

### Bulunamayan

**STRtree/R-tree uzamsal indeksini box-counting sayımını hızlandırmak için kullanan bir implementasyon doğrudan tespit edilememiştir.** Bu, iddianın tek özgün kalabilecek dilimidir.

### Temkinli değerlendirme

İddia **"algoritmik yenilik" olarak sunulmamalıdır** — hakem bu iddiayı Liebovitch & Toth 1989, Hou 1990, Kruger 1996 ve Alevizos & Vrahatis 2010 zinciriyle kolayca reddeder. Savunulabilir çerçeve:

> *"Kesin vektör geometrisi üzerinde GEOS STRtree ile aday geometri filtreleme ve boş alt-kutuların budanmasının somut, ölçülmüş bir açık kaynak uygulaması — uygulama/entegrasyon katkısı."*

**Kritik uyarı:** Bu çerçeve dahi **ölçülmüş bir benchmark (n vs. süre, budama açık/kapalı karşılaştırması) sunulmazsa zayıf kalır.** Hız iddiası ancak sayısal kanıtla savunulabilir.

---

## D.3 İDDİA 3 — "0–100 birleşik güven skoru ile fraktal boyut güvenilirliğinin otomatik raporlanması"

### Sonuç: 🟢 DOĞRUDAN EŞLEŞME BULUNAMADI — üç iddia içinde EN SAVUNULABİLİR olanı (ancak bileşenleri bilinen)

#### Bileşenlerin tamamı literatürde yerleşiktir

| Bileşen | Önceki sanat | DOI |
|---|---|---|
| Otomatik ölçek aralığı (scaling region) seçimi | Gonzato ve ark., 1998 | 10.1046/j.1365-246x.1998.00461.x |
| En büyük/küçük kutu sınırının nesnel seçimi | Foroutan-pour ve ark., 1999 | 10.1016/s0096-3003(98)10096-6 |
| **Otomatik ölçekleme bölgesi tanımlama (GP ile)** | **Wang Chengdong; Ling Dan; Miao Qiang, 2010** | **10.1109/ICACIA.2010.5709897** |
| **Üç fazlı otomatik ölçek bölgesi + R² raporlama** | **Douglass, 2025** | **10.3390/fractalfract9100633** |
| Çoklu ızgara konumu + ortalama D + std sapma + r² raporlama | **Karperien & Jelinek (FracLac/ImageJ), 2016** | **10.1007/978-1-4939-3995-4_32** (2024 güncelleme: 10.1007/978-3-031-47606-8_40) |
| Log-log EKK regresyonunun yanlılığı/tutarlılığı | Cutler, 1993 | 10.1142/9789814317382_0001 |
| "Tek tık otomatik" fraktal analiz aracı (2025) | **Balel & Sağtaş, 2025** | **10.1186/s12903-025-05932-4** |

**Özellikle kritik:** FracLac (Karperien & Jelinek) zaten **çok metrikli kalite raporlaması** yapmaktadır — ortalama D, standart sapma ve r² birlikte sunulur. Yani "fraktal boyut tahmininin kalitesini raporlamak" fikri yeni değildir.

#### Bulunamayan

OpenAlex ve Crossref'te *"composite quality score"* / *"confidence score for fractal dimension estimate"* kalıbına doğrudan uyan bir başlık **bulunamamıştır**. Yani şu spesifik unsur için doğrudan eşleşme yoktur:

> Birden çok kalite göstergesinin (regresyon R², ölçek aralığı genişliği, doğrusallıktan sapma) **belirlenmiş bir ağırlıklandırma şemasıyla tek, yorumlanabilir 0–100 skalar skora indirgenmesi ve her analizde otomatik raporlanması.**

#### Temkinli değerlendirme

Bu, üç iddia içinde **en savunulabilir** olanıdır — ancak dikkatli formüle edilmelidir:

- Bu bir **istatistiksel yenilik değildir**; kullanılabilirlik/mühendislik katkısıdır.
- Bileşenlerin hiçbiri yeni değildir; yeni olan yalnızca **birleştirme ve tek skalara indirgeme** kararıdır.
- **Skorun kalibrasyonu gösterilmezse hakem eleştirisine tamamen açıktır.** Bilinen teorik D değerine sahip fraktallerle (Koch D=1.2619, Sierpinski D=1.5850, Minkowski D=1.5) skorun gerçek doğrulukla korelasyonu gösterilmelidir. Aksi hâlde skor "keyfi ağırlıklı bir sayı" olarak reddedilir.

**Önerilen dil:** *"Bildiğimiz kadarıyla, mevcut açık kaynak fraktal boyut araçlarında birleşik tek skalar güven skoru raporlaması yaygın değildir."* — "ilk" veya "tek" DEĞİL.

> ⚠ **Bu iddianın önkoşulu:** Raporun YAZILIM_SORUNLARI.md dosyasındaki güven skoru bulguları ile birlikte okunmalıdır. Skorun kod içindeki gerçek hesaplanma biçimi doğrulanmadan bu iddia makaleye taşınmamalıdır.

---

## D.4 ÜÇ İDDİANIN TOPLU DEĞERLENDİRME TABLOSU

| # | İddia | Durum | En kritik önceki sanat | Makalede nasıl sunulmalı |
|---|---|---|---|---|
| 1 | Rasterizasyonsuz vektör box-counting | 🔴 **ÖNCEKİ SANAT BULUNDU** (yöntem öncelenmiş) | **Douglass 2025** — 10.3390/fractalfract9100633 (RASH-HIT'ten 10 ay önce) | Yöntem iddiası **geri çekilmeli**; "SVG + poligon + GEOS + paketlenmiş araç" kombinasyonuna daraltılmalı |
| 2 | STRtree + quadtree budama hızlandırma | 🟠 **KISMEN BULUNDU** (algoritmik olarak yeni değil) | Hou 1990, Kruger 1996, Alevizos & Vrahatis 2010 | "Algoritmik yenilik" değil, **ölçülmüş uygulama katkısı** olarak; benchmark ZORUNLU |
| 3 | 0–100 birleşik güven skoru | 🟢 **DOĞRUDAN EŞLEŞME BULUNAMADI** (bileşenler bilinen) | Douglass 2025; Karperien & Jelinek FracLac 2016 | En güçlü iddia; ancak **kalibrasyon deneyi olmadan sunulmamalı** |

---

## D.5 BU BÖLÜMÜN ÖZGÜNLÜK DEĞERLENDİRMESİNE NET ETKİSİ

**Önceki turlarda "ayakta kalan 3 özgünlük iddiası" olarak nitelenen küme, bu turda daralmıştır:**

- **1 iddia büyük ölçüde düşmüştür** (İddia 1 — Douglass 2025 nedeniyle yöntem düzeyinde).
- **1 iddia mühendislik katkısına indirgenmiştir** (İddia 2 — benchmark şartıyla).
- **1 iddia ayakta kalmıştır ancak kalibrasyon şartına bağlıdır** (İddia 3).

**Buna karşılık, bu turda RASH-HIT lehine GÜÇLENEN yönler:**

1. **Tez literatüründe Kategori A'da hiçbir eşleşme bulunamamıştır** (Bölüm 8.1) — `fractal textile`, `fractal motif`, `fractal carpet design`, `fractal facade` sorgularının tamamı **0 tez** döndürmüştür.
2. **Türkiye kaynaklı hiçbir çalışmada vektör tabanlı rasterizasyonsuz kutu sayma bulunamamıştır** (Bölüm 9.A.6); en yakın yerel muadil Çimen ve ark. 2021 **raster** tabanlıdır.
3. **Çini/tezhip + fraktal boyut ölçümü** için Türkiye kaynaklı eşleşen yayın bulunamamıştır.
4. Douglass 2025 dahi **yalnızca çizgi segmentleriyle** çalışmaktadır; **alan poligonları** ve **SVG semantiği** hâlâ eşleşmemiş kalmaktadır.

**Sonuç olarak katkının ağırlık merkezi, "yeni yöntem"den → "uygulama alanı + yazılım/tekrarlanabilirlik altyapısı"na kaymalıdır.** Bu, Bölüm 15'teki özgün katkı tanımına yansıtılmıştır.

---

## D.6 BU BÖLÜMÜN ÜRETİM KAYITLARI VE SINIRLILIKLARI

**Kullanılan API'ler:** Crossref REST (`api.crossref.org/works/{doi}` ve `query.bibliographic`), OpenAlex REST (`api.openalex.org/works` — `type:dissertation` ve `institutions.country_code:tr` filtreleri), arXiv API, GitHub Search API (repo-search), PyPI.

**Doğrulama yöntemi:** Bu bölümde geçen 18 DOI'nin tamamı, alt araştırmacıların raporundan bağımsız olarak, ana oturumda `curl` ile Crossref'e tek tek sorgulanmış; başlık, yıl, dergi, yazar ve yayın türü karşılaştırılmıştır. **17'si doğrulanmış, 1'i (10.25358/openscience-14974) "Resource not found" döndürmüştür ve raporda kullanılmamıştır.**

**Sınırlılıklar (açık beyan):**
- **GitHub code-search API kimlik doğrulama istemiştir**; yalnızca repo-search kullanılabilmiştir. Depo içeriğinde geçen ancak başlık/açıklamada geçmeyen implementasyonlar gözden kaçmış olabilir.
- **OpenAlex günlük ücretsiz kotası tükenmiştir**; `fractal textile`, `fractal pattern`, `fractal geometry traditional` başlık sorguları çalıştırılamamıştır (**Doğrulanamadı**).
- ✅ **GÜNCELLEME: Douglass 2025'in tam metni indirilmiş ve okunmuştur** (`kaynaklar/Douglass_2025_FractalFract_9_633.md` + `.pdf`, 20 sayfa). Ayrıntılı karşılaştırma: `kaynaklar/ANALIZ_Douglass_2025_vs_RASHHIT.md`. Bu okuma sonucunda yukarıdaki D.1 tablosunda **üç kayıt düzeltilmiştir** (kod açık; kesişim Liang–Barsky; girdi segment listesi).
- **OATD.org ve YÖK Ulusal Tez Merkezi taranamamıştır.**
- Bu bölüm **hiçbir proje dosyasını değiştirmemiştir**; kaynak salt okunur kuralına uyulmuştur.

---

# EK BÖLÜM E — KAPSAMIN YENİDEN TANIMI: "TASARIM FRAKTAL ANALİZİ" ve GİRDİ KATMANININ ASIL KATKI OLMASI

**Not:** Bu bölüm, geliştiricinin kapsam açıklaması üzerine eklenmiştir: *"Biz direkt tüm tasarım alanlarını kapsıyoruz — moda, grafik tasarım ve diğer tasarım alanları. Analiz vektörel tasarımlar üzerinden yapılıyor; yani girdinin vektöre, SVG'den okuyabileceğimiz bir formata dönüşmesi gerekiyor."*

Bu tanım, raporun önceki bölümlerindeki konumlandırmayı **değiştirmektedir** ve Douglass 2025 karşısındaki savunmayı **güçlendirmektedir**.

---

## E.1 KAPSAM: "kültürel motif" değil, "tasarım"

Rapor boyunca RASH-HIT'in uygulama alanı "kültürel motif / tekstil / süsleme" olarak dar tanımlanmıştı. Doğru kapsam daha geniştir:

| Alan | Tipik dosya | Vektör mü? |
|---|---|---|
| Moda / tekstil tasarımı | AI, EPS, PDF, DXF-AAMA, CLO/Optitex/Lectra çıktıları | ✅ Doğası gereği vektör |
| Grafik tasarım / kurumsal kimlik | AI, SVG, EPS, PDF | ✅ Vektör |
| Logo ve marka geometrisi | SVG, AI | ✅ Vektör |
| Mimari cephe / plan | DWG, DXF, PDF | ✅ Vektör |
| Ürün / endüstriyel tasarım | STEP, DXF, AI | ✅ Vektör |
| Tipografi / harf formu | Font outline (TTF/OTF eğrileri), SVG | ✅ Vektör |
| Halı, çini, tezhip, süsleme | Sayısallaştırılmış vektör veya raster | Kısmen |

**Buradaki temel gözlem şudur:** Tasarım disiplinlerinin ürettiği veri **zaten vektördür**. Mevcut fraktal analiz araçlarının tamamına yakını (FracLac, ImageJ, Benoit, HarFA, fractaldim, boxcount) bu veriyi analiz edebilmek için **önce PNG'ye rasterize etmeyi** zorunlu kılar. Bu, tasarımın kendi doğal temsilini bozup ölçüme kuantizasyon hatası enjekte etmek demektir.

Yani problem şudur:

> **Tasarım verisi vektör olarak doğar, ancak mevcut fraktal analiz araçları onu piksel olarak ölçmeye zorlar.**

RASH-HIT'in çözdüğü problem budur. Bu, "yeni bir fraktal boyut algoritması" iddiasından **çok daha savunulabilir** bir problem tanımıdır.

---

## E.2 GİRDİ KATMANI ASIL KATKIDIR — Douglass'ın hiç yapmadığı iş

Douglass 2025 tam metni okunduğunda ortaya çıkan en önemli olgu:

| | Douglass 2025 | RASH-HIT |
|---|---|---|
| Girdi | **Kod içinde üretilen segment listesi** | **Diskteki gerçek tasarım dosyası** |
| Dosya formatı desteği | **Hiçbiri.** Tam metinde SVG/DXF/EPS/AI/PDF **0 kez** geçiyor | SVG (CSS + inline stil, affine transform yığını, Bézier/arc düzleştirme) |
| Kullanıcı ne verir | Bir Python fonksiyonu / nokta dizisi | Bir `.svg` dosyası |
| Tasarımcı kullanabilir mi | ❌ Hayır — programcı gerekir | ✅ Evet |

Douglass'ın aracına bir moda deseni, bir logo veya bir tekstil raporu **veremezsiniz**. Önce onu segment listesine siz çevirmelisiniz. **İşte o çevirme işi, RASH-HIT'in yaptığı iştir** ve makalede "önemsiz mühendislik detayı" değil, **etkinleştirici katkı (enabling contribution)** olarak sunulmalıdır.

Bu ayrımın teknik gerekçesi:

1. **SVG düz bir segment listesi değildir.** `<path d="...">` içindeki Bézier ve arc komutları düzleştirilmeli; `transform` öznitelikleri iç içe affine matris yığını olarak birleştirilmeli; `<use>` referansları çözülmeli; stil CSS kaskadından hesaplanmalı (görünmez/`display:none` öğeler analize girmemeli); `stroke` ile `fill` semantik olarak ayrılmalı.
2. **`stroke` bir çizgidir, `fill` bir alandır.** Douglass yalnızca birincisini işleyebilir. Tasarımın büyük kısmı ikincisidir. Bir logo, bir motif, bir kumaş deseni ağırlıklı olarak **dolu alandır**.
3. **Düzleştirme toleransı ölçümü etkiler.** Bézier'i kaç segmente böldüğünüz, ε_min seçimini ve dolayısıyla D'yi etkiler. Bu, Douglass'ta hiç ortaya çıkmayan, RASH-HIT'e özgü bir metodolojik sorudur — **ve makalede incelenmesi gereken özgün bir deney başlığıdır.**

---

## E.3 REVİZE EDİLMİŞ KATKI TANIMI (Bölüm 15.A'nın yerine geçer)

> Doğrudan geometri üzerinde kutu sayma, matematiksel fraktallerin çizgi segmentleri için daha önce ortaya konmuştur (Douglass, 2025). Bu çalışma, yaklaşımı **tasarım verisine uygulanabilir hâle getirmektedir**. Katkı üç eksende tanımlanır:
>
> **(i) Girdi katmanı.** Tasarım disiplinlerinin ürettiği veri doğası gereği vektöreldir; ancak mevcut fraktal analiz araçları ölçüm için rasterizasyon zorunlu kılar. Bu çalışma, SVG belge semantiğini (CSS kaskadı ve satır içi stil çözümleme, iç içe affine dönüşüm yığını, Bézier ve yay düzleştirme, görünürlük filtreleme) tam olarak ayrıştırıp doğrudan ölçülebilir geometriye dönüştüren bir boru hattı sunar. Böylece tasarım dosyası, ara bir raster temsile uğramadan analiz edilir.
>
> **(ii) Karma geometri desteği.** Mevcut segment tabanlı yaklaşımlar yalnızca çizgi geometrisiyle sınırlıdır (Douglass, 2025: *"limited to two-dimensional line segment analysis"*). Tasarım nesneleri ise ağırlıklı olarak dolu alanlardan oluşur. Bu çalışma, GEOS kesin kesişim predikatlarıyla çizgi ve alan poligonlarını birlikte ele alır.
>
> **(iii) Alan uygulaması ve tekrarlanabilirlik.** Yöntem; moda, grafik tasarım, tekstil ve geleneksel süsleme korpuslarına uygulanmakta, sonuçlar aynı korpusun raster tabanlı ölçümleriyle karşılaştırılmakta ve sağlama toplamlı bir tekrarlanabilirlik paketiyle (SHA-256 manifest, toplu analiz, CLI/TUI/web arayüzleri) dağıtılmaktadır.
>
> İncelenen kaynaklar içinde, tasarım dosyası formatını doğrudan tüketen ve karma çizgi–alan geometrisinde kesin kutu sayımı yapan bir sisteme doğrudan eşleşme bulunamamıştır.

**Konumlandırma:** yöntemsel katkı DEĞİL → **etkinleştirici yazılım katkısı + alan (tasarım) katkısı**.

---

## E.4 BU KAPSAMIN GETİRDİĞİ YENİ ZORUNLULUKLAR

Kapsam "tüm tasarım alanları" olduğunda, raporun önceki bölümlerinde olmayan üç yeni yükümlülük doğar:

### E.4.1 Format zinciri açıkça tanımlanmalı

Tasarım dosyalarının çoğu SVG değildir (AI, EPS, PDF, DXF, CDR). Makalede şu netleştirilmelidir:

- **Kabul edilen tek girdi SVG'dir.** Diğer formatlar için dönüştürme zinciri (ör. Illustrator/Inkscape/CorelDRAW ile SVG dışa aktarımı) **kullanıcı sorumluluğundadır**.
- **Ancak bu dönüşümün ölçümü bozup bozmadığı test edilmelidir.** Aynı tasarımın AI→SVG, PDF→SVG, DXF→SVG yollarından geçirilmiş sürümleri aynı D'yi veriyor mu? Vermiyorsa bu bir sınırlılık olarak beyan edilmelidir.
- **Öneri:** Inkscape CLI (`inkscape --export-type=svg`) veya `pdf2svg` ile standart bir ön-işleme adımı tanımlanıp belgelenmeli; böylece "SVG-only" kısıtı pratikte bir engel olmaktan çıkar.

### E.4.2 Raster karşılaştırması kanıt olarak sunulmalı

Kapsam iddiası ("rasterizasyon tasarım verisini bozar") **ölçülmeden ileri sürülemez**. Yapılması gereken deney:

> Aynı SVG tasarımı → (a) RASH-HIT ile doğrudan vektör analizi, (b) 300/600/1200/2400 DPI'de PNG'ye rasterize edilip FracLac ve ImageJ ile analiz. D değerlerinin DPI ile nasıl kaydığı ve vektör sonucuna yakınsayıp yakınsamadığı grafiklenmeli.

Bu tek deney, projenin varlık gerekçesini kanıtlar. **Şu anda raporda böyle bir ölçüm yoktur ve bu en büyük eksiktir.**

### E.4.3 Tasarım alanında rakip taraması genişletilmeli

Rapor şimdiye kadar "fraktal analiz yazılımı" ekseninde tarandı. Kapsam "tasarım" olduğuna göre şu eksende de taranmalıdır (**bu tur içinde YAPILMAMIŞTIR — açık kalan iştir**):

- Grafik tasarımda görsel karmaşıklık ölçümü (visual complexity metrics, design complexity)
- Logo karmaşıklığı ve marka algısı literatürü (pazarlama/tüketici araştırmaları — burada fraktal boyut kullanan çalışmalar vardır)
- Moda/tekstil desen karmaşıklığı ve estetik tercih çalışmaları
- Mimarlıkta cephe karmaşıklığı — bu alanda fraktal boyut yerleşiktir (Bovill 1996; Ostwald & Vaughan, *The Fractal Dimension of Architecture*, Birkhäuser 2016). **Ostwald & Vaughan mutlaka incelenmelidir**; mimari çizim analizi yaparlar ve girdileri çizgi çizimidir — RASH-HIT'e en yakın "tasarım" uygulaması burada olabilir.
- Tipografi/harf formu karmaşıklığı

**Uyarı:** Mimarlık tarafı, bu raporda henüz yeterince taranmamış en riskli boşluktur. Ostwald & Vaughan çizgisi, "tasarım çizimlerinin kutu sayma ile analizi" konusunda 20 yıllık yerleşik bir literatürdür ve bir kısmı vektör çizim üzerinden çalışır. Özgünlük iddiası kesinleştirilmeden önce bu literatür taranmalıdır.

---

## E.5 SONUÇ

Kapsamın "tasarım" olarak tanımlanması, projenin özgünlük savunmasını **zayıflatmaz, güçlendirir** — çünkü:

- Yöntem yarışından (Douglass'ın kazandığı yarış) çıkar,
- Girdi ve uygulama yarışına girer (Douglass'ın hiç girmediği yarış),
- Ve orada rakip, henüz taranmamış olan mimarlık/tasarım karmaşıklığı literatürüdür.

**Bir sonraki zorunlu adım, Bölüm E.4.3'teki tasarım-ekseni taramasıdır.** O tarama yapılmadan özgünlük değerlendirmesi tamamlanmış sayılamaz.
