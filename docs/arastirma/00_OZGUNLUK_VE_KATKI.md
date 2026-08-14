# RASH-HIT Fractal Studio — ÖZGÜNLÜK VE KATKI (odaklı ana belge)

Hazırlayan: Hermes Agent · Son güncelleme: 2026-08-08
Amaç: Projenin ne yaptığı, hangi bağlamda benzersiz olduğu ve makale için
savunulabilir katkı ifadesi — GÜRÜLTÜSÜZ, odaklı tek belge.
Tüm deney/kanıt detayları `01_DOGRULAMA_VE_DENEYLER.md`, `03_DOUGLASS_2025.md`,
`02_YAZILIM_SORUNLARI.md`, `04_KAYNAK_DEPOSU.md` içindedir.

> Proje kaynak kodu SALT OKUNUR — hiçbir değişiklik yapılmamıştır.

---

## 1. YÖNETİCİ ÖZETİ

RASH-HIT Fractal Studio, **vektörel tasarım çıktılarını (SVG) rasterize
etmeden** kutu sayma (box-counting) fraktal boyutu hesaplayan, Python
tabanlı, akademik çıktı paketi üreten bir araştırma yazılımıdır.

Çalışma akışı: tasarım aracında üretilen vektörel form → SVG dışa aktarım →
**SVG içindeki geometri kodu ayrıştırılır** (CSS+inline stil, affine dönüşüm
yığını, Bézier/arc düzleştirme, dolu alan + çizgi geometrisi) → kesin GEOS
kesişim predikatlarıyla (Shapely) kutu sayımı → SHA-256 tekrarlanabilirlik
manifesti + HTML/JSON rapor.

**Çekirdek iddia (ölçülü):** İncelenen kaynaklar içinde, *genel amaçlı SVG
tasarım belgesini tam vektör semantiğiyle ayrıştırıp, çizgi+poligon karma
geometride exact kesişimle, tekrarlanabilirlik manifestiyle ve motif odaklı
raporlamayla kutu sayan ikinci bir sistem bulunamamıştır.*

---

## 2. ÇEKİRDEK İDDİANIN TAZE KANITI (GitHub, 2026-08-08)

Yanlış/yön sapmasını önlemek için çekirdek iddia doğrudan GitHub aramasıyla
yeniden doğrulandı (`api.github.com/search/repositories`):

| Sorgu | Toplam depo | Not |
|---|---|---|
| `svg fractal dimension` | **2** | `danielrendall/FractDim` + `rasitnarcicek/RASH-HIT-Fractal-Studio` |
| `vector design fractal dimension` | **0** | — |
| `fractal dimension motif` | **0** | — |
| `fractal analysis ornament` | **0** | — |
| `box-counting svg` | **2** | RASH-HIT + alakasız bir repo (`ncasias/fb`) |

**Sonuç:** "SVG dosyası üzerinden fraktal analiz" yapan GitHub'daki İKİ
depodan biri biziz; "vektör tasarım / motif / süsleme + fraktal boyut"
kesişiminde hiçbir depo yok. Bu, çekirdek tezin en temiz kanıtıdır.

---

## 3. NE YENİ, NE DEĞİL (dürüst ayrım)

### ✗ Yenilik DEĞİL (iddia edilmez)
- "SVG'den doğrudan kutu sayımı" → FractDim (2009-2011) yaptı.
- "Rasterleştirmeden analiz" → aynı, 2009.
- "log N(ε) vs log(1/ε) regresyonu + R²" → 1980'lerden standart.
- "Quadtree/STRtree ile hızlandırma" → hesaplamalı geometride bilinen.
- "Web arayüzü / HTML rapor / CLI" → yazılım konforu, akademik katkı değil.

### ~ Kısmen yeni (yazılım katkısı — savunulabilir)
Vektör-yerel motor + dolu-alan ölçümü + toplu analiz + CLI/web + tekrarlanabilir
paket çıktısının **tek sistemde birleşimi**. Taramada bütünsel eşleşme
bulunamadı; ama bu "yöntemsel katkı" değil, **yazılım/mühendislik katkısı**dır.

### ✓ Gerçekten yeni / savunulabilir (makale omurgası)
**(A) Vektör uzayında DOLGU-FARKINDALIKLI kutu sayımı.**
Bilinen tek vektör-yerel SVG uygulaması (FractDim) dolguyu koda düşülmüş
`// ignore for now - treat as draw` notuyla atlar (`FDGraphics2D.java:80-85`).
RASH-HIT Shapely/GEOS ile iç alanı gerçekten hesaplar ve **dolu kare üzerinde
%0.00 hata** ile kalibre edilmiştir (bkz. `01_DOGRULAMA_VE_DENEYLER.md` §1).

**(B) Çizgi kalınlığının vektör kutu sayımındaki sistematik yanlılığı.**
Aynı Koch eğrisi, tek değişken çizgi kalınlığı: stroke 3.0 px → Db 1.5408
(%22 yanlış), stroke 0.10 px → Db 1.2806 (%1.5). **0.26 boyut birimi kayma.**
Üstelik dört durumda da güven skoru 92.5 (R²>0.997) — yani yazılım %22 yanlış
sonuca "yüksek güven" diyor. Bu, raster tabanlı fraktal analizde de bilinen (çizgi kalınlığı/çözünürlük
etkisi) bir olgunun **vektör tarafında ölçülüp sayısallaştırıldığı** bir çalışma
taramada bulunamadı. (Not: spesifik kaynak atfı bu belgede doğrulanmadı; makalede ayrıca taranmalı.) Kendi aracının sınırını gösterdiği için hakem önünde
güçlü VE dürüst bir bulgudur.

---

## 4. KATKI İFADESİ (contribution statement)

### Tek cümle (abstract'a)
> "RASH-HIT Fractal Studio is a reproducible analysis pipeline that ingests
> general-purpose SVG design documents — faithfully reconstructing their full
> vector semantics (CSS and inline styling, affine transform stacks,
> Bézier/arc flattening, fill and stroke geometry) — and performs exact
> box-counting on the resulting mixed polygon-and-line geometry using precise
> GEOS intersection predicates with STRtree and quadtree negative-space
> pruning, emitting a SHA-256 reproducibility manifest. While rasterization-
> free segment-based box-counting is already established in the literature
> (e.g. Douglass, 2025), the document-level vector input layer, exact
> filled-area measurement, and cultural/design-motif application addressed
> here remain unaddressed."

### Dört ayak
1. **Belge-düzeyi vektör girdi katmanı** (SVG → exact geometri) — Douglass bir
   DOSYA okumaz, girdisi kod içi segment listesidir.
2. **Exact dolu-alan (fill) + çizgi karma geometri** — Douglass "limited to
   two-dimensional line segment analysis" der; poligon/alan yok.
3. **SHA-256 tekrarlanabilirlik manifesti** — incelenen rakiplerde bulunamadı.
4. **Tasarım / kültürel motif uygulama alanı** — Douglass = matematiksel
   fraktaller + akışkan mekaniği; moda/tekstil/motif hiç geçmez.

### Katkı türü
**Yazılım/mühendislik katkısı + uygulama (kültürel motif) katkısı.**
Katkı ≠ box-counting yöntemi.

---

## 5. DOUGLASS (2025) İLE İLİŞKİ — "FARKLI BAĞLAM" NASIL LEHİMİZE ÇEVRİLİR

Douglass'ın hikâyesi, BİZİM SVG ayrıştırmamız BİTTİKTEN SONRA başlar (segment
listesi hazır). İki sistem farklı sorulara cevap verir:

- Douglass: "Verilen ham segment kümesi üzerinde en doğru ölçek aralığını
  otomatik nasıl seçerim?" (yöntem/optimalizasyon katmanı)
- RASH-HIT: "Gerçek bir tasarım belgesinden sadık vektör geometriyi nasıl
  çıkarırım ve exact predikatla, tekrarlanabilir biçimde ölçerim?" (girdi +
  uygulama katmanı)

Bu, "o farklı alanda, biz farklı alandayız" DEĞİL; tam tersi en güçlü
konumlandırmadır: **box-counting ham segmentler üzerinde çözülmüş bir
problemdir; çözülmemiş ve pratikte önemli olan, gerçek tasarım belgesi → sadık
geometri → exact ölçüm → manifest zinciridir.** (Ayrıntı: `03_DOUGLASS_2025.md`)

---

## 6. DÜRÜST ÖN KOŞULLAR (yayına göndermeden ZORUNLU)

Katkı ifadesi şu an kodda TAM OLARAK KARŞILANMIYOR. Düzeltilmeden (A) ve (B)
iddiaları BOŞ:

| Kod | Bulgu | Etkilediği iddia |
|---|---|---|
| S2 | `fill-rule` özniteliği YOK SAYILIYOR: `geometry_engine.py:510-531` dallanma yok, çok-yollu yollar için daima `symmetric_difference` (yani even-odd) uygular; `verify2.py` bunu ölçtü (iç içe kare 7500/7500). Oysa `svg_loader.py:250` "Default non-zero winding rule used" uyarısı VERİYOR — uyarı YANLIŞ. SVG varsayılanı nonzero olduğundan fill-rule'sız dosyalar standardın aksine çözülür | (A) exact dolu-alan — düzeltilene kadar üstünlük iddiası KULLANILMAMALI |
| S3 | stroke_width hiçbir rapor/manifest'e yazılmıyor | (3) tekrarlanabilirlik |

Ayrıca Douglass'ın üstün olduğu 3 nokta dürüstçe kabul edilmeli:
otomatik ölçek aralığı seçimi (sliding window), grid offset optimizasyonu,
doğrulama titizliği (5 fraktal). Ya kapatılmalı ya "future work" yazılmalı.

---

## 7. ATIF STRATEJİSİ

ZORUNLU: Douglass (2025) ilgili çalışma olarak atıf verilir, yöntemi açıkça
karşılaştırılır. Kullanılabilir doğrudan alıntılar (`03_DOUGLASS_2025.md` §6):
- "Unlike traditional pixelated approaches... the method used directly
  analyzes geometric line segments" (Abstract) — *yöntem-yeniliği iddiamızı
  geçersiz kılan; bu yüzden katkıyı girdi+uygulama kuruyoruz.*
- "Current implementation is limited to two-dimensional line segment
  analysis" (§4.2) — *dolu-alan farkımızı meşrulaştıran.*
- "may require adjustment for significantly different geometric patterns or
  applications beyond the tested range" (§4.2) — *tasarım verisine
  genellenebilirliğinin yazarca sorgulandığı; uygulama boşluğumuzu pekiştiren.*

---

## 8. DİL KURALI (hakem tuzağı önlemi)

❌ "dünyada ilk", "tamamen benzersiz", "daha önce hiç yapılmadı"
✅ "incelenen kaynaklar içinde doğrudan eşleşme bulunamadı"
Gerekçe: FractDim ve Douglass'in varlığı her "ilk" iddiasını çürütür.
