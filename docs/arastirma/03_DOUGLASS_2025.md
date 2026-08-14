# Douglass (2025) — TAM METİN ANALİZİ ve RASH-HIT KARŞILAŞTIRMASI

Kaynak: Douglass, R.W. (2025). *Automated Box-Counting Fractal Dimension
Analysis: Sliding Window Optimization and Multi-Fractal Validation.*
Fractal and Fractional, 9(10), 633. DOI: 10.3390/fractalfract9100633
(CC BY 4.0, yayın 29 Eyl 2025, kod: github.com/rwdlnk/Fractal-Dimension-Analyzer)
Tam metin: `kanit/Douglass_2025_FractalFract_9_633.md`

> Douglass'ın "rasterizasyonsuz doğrudan geometrik analiz" iddiası, RASH-HIT'in
> Zenodo öncelik tarihinden (~29 Tem 2026) ~10 ay ÖNCE. Bu yüzden "dünyada ilk
> rastersız vektör box-counting" iddiası ÇÖKMÜŞ — katkı girdi+uygulama olarak
> kurgulanmalı (bkz. `00_OZGUNLUK_VE_KATKI.md` §4-5).

---

## 1. DOUGLASS NE YAPIYOR

**Girdi:** Bir DOSYA OKUMAZ. Girdi = kod içi düz çizgi-segment listesi
("x1 y1 x2 y2"). Tam metinde "SVG" kelimesi 0 kez. Test verisi: kendi
ürettiği matematiksel fraktaller (Koch 16.384 seg [D=1.2619], Sierpinski 6561 seg [D=1.5850], Hilbert
16.383 seg [D=2.0000], Dragon 1023 seg [D=1.5236], Minkowski 262.144 seg [D=1.5000])
+ 1 fiziksel (Rayleigh–Taylor akışkan arayüzü, D=1.835).

**Çekirdek:** Segment tabanlı geometrik box-counting, rastersiz. Çizgi–kutu
Çizgi–kutu kesişimi Liang–Barsky line clipping (O(1), parametrik; Douglass 2025 §2.3 [20]) + hiyerarşik uzamsal bölümleme.
Shapely/GEOS DEĞİL, poligon DEĞİL.

**Kutu boyutu:** ε_min = 2× ortalama segment uzunluğu; ε_max = sınırlayıcı
kutunun 1/8'i; logaritmik ilerleme ε_i = ε_min·2^i (10-20 boyut).

---

## 2. ASIL KATKISI (yöntem DEĞİL, ölçek aralığı seçimi)

"Core innovation" = 3 FAZLI OPTİMİZASYON:
1. **Grid offset:** Izgarayı kaydırıp MINIMUM kutu sayısını alır → kuantizasyon
   yanlılığını azaltır.
2. **Sınır artefaktı:** İstatistiksel eşikler (eğim sapması 0.12, R² 0.95/0.99)
   bozuk uç noktaları otomatik atar.
3. **Sliding window:** Tüm regresyon pencerelerini dener; teorik D biliniyorsa
   |D−D_teo|'yi minimize eden, bilinmiyorsa R²'yi maksimize eden pencereyi seçer
   → öznel ölçek aralığı seçimini ortadan kaldırır.

**Sonuçlar (Tablo 2, optimize 3-faz):** ortalama mutlak hata %2.3, tüm sonuçlar
R²≥0.9996. Bireysel: Koch D=1.2605 (%0.11), Minkowski D=1.5037 (%0.25,
R²=0.9988), Hilbert D=1.9923 (%0.39), Sierpinski (%3.4), Dragon D=1.6362
(%7.4). Fiziksel örnek: Rayleigh–Taylor arayüzü D=1.835±0.0037 (R²=0.999988).

---

## 3. YAZARIN KENDİ SINIRLILIKLARI (bizim için altın)
1. "limited to two-dimensional line segment analysis" — poligon/alan YOK.
2. Yalnız matematiksel fraktallerle doğrulanmış; gerçek dünya verisi tek örnek.
3. Eşikler (0.12, 0.99) "different geometric patterns" için ayar gerektirebilir.
4. Yöntemi evrensel DEĞİL — Dragon en yüksek hata (%7.4), Sierpinski %3.4;
doğruluk fraktal tipine göre değişir, eşikler farklı desenlerde ayar
gerektirebilir (makale §5.2).

---

## 4. RASH-HIT vs DOUGLASS — KARŞILAŞTIRMA MATRİSİ

| Boyut | Douglass 2025 | RASH-HIT | Kim önde |
|---|---|---|---|
| Raster'sız geometrik sayım | var | var | BERABERE — özgünlük iddiası yok |
| **Gerçek tasarım dosyası (SVG) girdisi** | yok (kod içi segment) | **var** (CSS+stil, transform, Bézier) | **RASH-HIT** |
| **Alan poligonu (dolu şekil)** | yok ("2D line segment") | **var** | **RASH-HIT** |
| Kesişim motoru | Liang–Barsky (çizgi-özel) | Shapely/GEOS (genel, poligon) | Farklı; GEOS daha genel |
| **Otomatik ölçek aralığı seçimi** | **var** (ana katkısı) | yok | **DOUGLASS** |
| Grid offset optimizasyonu | var | yok | **DOUGLASS** |
| Sınır artefaktı otomatik temizleme | var | yok | **DOUGLASS** |
| Birleşik 0–100 güven skoru | yok | var | **RASH-HIT** |
| Paketlenmiş arayüz (CLI/web) | yok (betik) | var | **RASH-HIT** |
| Toplu analiz | yok | var | **RASH-HIT** |
| SHA-256 manifest | yok | var | **RASH-HIT** |
| Doğrulama titizliği | 5 fraktal + teorik D | zayıf | **DOUGLASS** |
| Uygulama alanı | matematiksel + akışkan | **tasarım/motif** | **RASH-HIT** (örtüşme yok) |

---

## 5. NET SONUÇ

- **Örtüşen (iddia edilemez):** "rasterize etmeden doğrudan geometri üzerinde
  kutu sayma" — Douglass 10 ay önce, hakemli, kodlu.
- **Douglass'ın BİZDEN ÜSTÜN olduğu 3 nokta (kapatılmalı):** otomatik ölçek
  aralığı seçimi, grid offset optimizasyonu, doğrulama titizliği.
- **Douglass'ın KAPSAMADIĞI boşluk:** (1) gerçek tasarım dosyası girdisi,
  (2) alan poligonları, (3) tasarım/motif uygulaması.

---

## 6. KULLANILABİLİR DOĞRUDAN ALINTILAR
- "Unlike traditional pixelated approaches that suffer from rasterization
  artifacts, the method used directly analyzes geometric line segments"
  (Abstract) — *yöntem-yeniliği iddiamızı geçersiz kılan.*
- "Current implementation is limited to two-dimensional line segment
  analysis" (§4.2) — *dolu-alan farkımızı meşrulaştıran.*
- "may require adjustment for significantly different geometric patterns or
  applications beyond the tested range" (§4.2) — *tasarım verisine
  genellenebilirliğinin yazarca sorgulandığı.*

---

## 7. DENEY PLANI (DOUGLASS ENTEGRASYONU)

1. Douglass 2025 atıf verilecek, ilgili çalışma olarak tartışılacak.
2. "Raster'sız geometrik sayım yeni yöntemdir" iddiası GERİ ÇEKİLECEK.
3. Aynı 5 fraktal (Koch 1.2619, Sierpinski 1.5850, Minkowski 1.5, Hilbert,
   Dragon) RASH-HIT'ten geçirilecek; Douglass'ın raporladığı değerler benchmark
   olarak alınır (Koch %0.11, R²≥0.9988, ort. %2.3 — Tablo 2), RASH-HIT kendi
   yöntemiyle (fill+stroke) kıyaslanır.
4. (Güçlü öneri) Sliding-window + grid offset RASH-HIT'e eklenir (CC-BY,
   GitHub'da; yöntem uyarlanabilir) — aksi hâlde matriste açık kalır.
5. Douglass kodu indirilip **aynı SVG girdisi** üzerinde yan yana koşturulur
   — o SVG okuyamadığı için ayrım görünür olur.
