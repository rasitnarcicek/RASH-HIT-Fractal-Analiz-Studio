# RASH-HIT Fractal Studio — KATKI İFADESİ ve KONUMLANDIRMA

Hazırlayan: Hermes Agent · Tarih: 2026-08-08
Amaç: Makale/tez için *savunulabilir* özgün katkı ifadesini sabitlemek.
Bağlam: Douglass (2025), Fractal and Fractional 9(10):633, DOI 10.3390/fractalfract9100633
— "rasterizasyonsuz doğrudan geometrik line-segment analizi" iddiası bizim
Zenodo öncelik tarihimizden (~29 Tem 2026) ~10 ay ÖNCE, hakemli ve kodlu.
Dolayısıyla "yöntemsel ilk / dünyada ilk rastersız vektör box-counting" iddiası
KULLANILAMAZ.

---

## 0. TEK CÜMLELİK CONTRIBUTION STATEMENT (abstract'a yapıştırılabilir)

> "RASH-HIT Fractal Studio is a reproducible analysis pipeline that ingests
> general-purpose **SVG design documents** — faithfully reconstructing their
> full vector semantics (CSS and inline styling, affine transform stacks,
> Bézier/arc flattening, fill and stroke geometry) — and performs exact
> box-counting on the resulting **mixed polygon-and-line geometry** using
> precise GEOS intersection predicates with STRtree and quadtree
> negative-space pruning, emitting a **SHA-256 reproducibility manifest**.
> While rasterization-free segment-based box-counting is already established
> in the literature (e.g. Douglass, 2025), the document-level vector input
> layer, exact filled-area measurement, and cultural/design-motif
> application addressed here remain unaddressed."

Türkçe karşılık (giriş için):

> "RASH-HIT, genel amaçlı SVG tasarım belgelerini (tam vektör semantiği:
> CSS+inline stil, affine dönüşüm yığını, Bézier/arc düzleştirme, dolu alan
> ve çizgi geometrisi) sadık biçimde ayrıştırıp, kesin GEOS kesişim
> predikatları ve STRtree + quadtree negatif-alan budamasıyla, çizgi+poligon
> karma geometri üzerinde exact box-counting yapan ve SHA-256 tekrarlanabilirlik
> manifesti üreten tekrarlanabilir bir analiz hattıdır. Raster'sız segment
> tabanlı kutu sayım literatürde zaten yer almakta olup (ör. Douglass 2025),
> buradaki katkı belge-düzeyi vektör girdi katmanı, exact dolu-alan ölçümü ve
> kültürel/tasarımsal motif uygulamasıdır."

---

## 1. KATKININ DÖRT AYAĞI (savunulabilir)

| # | Katkı | Neden savunulabilir | Dayanak |
|---|---|---|---|
| 1 | **Belge-düzeyi vektör girdi katmanı** (SVG → exact geometri) | Douglass bir DOSYA okumaz; girdisi kod içi segment listesidir. Gerçek tasarım dosyasından sadık geometri çıkarma işini yapan ikinci sistem taramada bulunamadı. | KAYNAK_DEPOSU A1; ANALIZ_Douglass_2025_vs_RASHHIT §1 |
| 2 | **Exact dolu-alan (fill) + çizgi karma geometri** | Douglass "limited to two-dimensional line segment analysis" der — poligon/alan YOK. Tasarımın baskın kısmı dolu alandır. | STROKE_KOD_DENETIMI (çekirdek matematik doğru); Douglass §4.2 |
| 3 | **SHA-256 tekrarlanabilirlik manifesti** | İncelenen rakiplerde (FracLac, Fractalyse, Douglass, FractDim) böyle bir manifest bulunamadı. | KAYNAK_DEPOSU F; README "EN ÖNEMLİ 5" |
| 4 | **Tasarım / kültürel motif uygulama alanı** | Douglass = matematiksel fraktaller + akışkan mekaniği. Moda, tekstil, grafik, kültürel miras motifleri hiç geçmez. | ANALIZ §3; KAYNAK_DEPOSU B/D |

---

## 2. AÇIKÇA İDDİA EDİLEMEYECEK ŞEYLER (hakem tuzağı)

- ❌ "Dünyada ilk raster'sız vektör box-counting" → Douglass 2025 çürütür.
- ❌ "Yeni bir box-counting yöntemi bulduk" → yöntemLieBovitch&Toth (1989) + Douglass (2025) öncesi.
- ❌ "İlk SVG fraktal analiz sistemi" → FractDim (2009) bunu yapar (ölü ve lisanssız olsa da).
- ✅ "İncelenen kaynaklar içinde, GENEL AMAÇLI SVG geometrisini tam ayrıştırıp
  poligon+çizgi karma geometride KESİN GEOS kesişimiyle, tekrarlanabilirlik
  manifestiyle ve motif odaklı raporlamayla kutu sayan ikinci bir sistem
  bulunamadı." → Bu ölçülü ifade defansif.

---

## 3. DOUGLASS İLE İLİŞKİ — "FARKLI BAĞLAM" NASIL LEHİMİZE ÇEVRİLİR

Douglass'ın hikâyesi, BİZİM SVG ayrıştırmamız BİTTİKTEN SONRA başlar
(segment listesi hazır). İki sistem farklı sorulara cevap verir:

- Douglass: "Verilen ham segment kümesi üzerinde en doğru ölçek aralığını
  otomatik nasıl seçerim?" (yöntem/optimalizasyon katmanı)
- RASH-HIT: "Gerçek bir tasarım belgesinden sadık vektör geometriyi nasıl
  çıkarırım ve exact predikatla, tekrarlanabilir biçimde ölçerim?" (girdi +
  uygulama katmanı)

Bu, "o farklı alanda, biz farklı alandayız, karışmayalım" DEĞİL; tam tersi
en güçlü konumlandırmadır: **box-counting ham segmentler üzerinde çözülmüş
bir problemdir; çözülmemiş ve pratikte önemli olan, gerçek tasarım
belgesi→sadık geometri→exact ölçüm→manifest zinciridir.**

---

## 4. DÜRÜST ÖN KOŞULLAR (bunlar düzeltilmeden #1 ve #2 iddiaları BOŞ)

Katkı ifadesi şu an kodda TAM OLARAK KARŞILANMIYOR. Yayına GÖNDERMEDEN
önce zorunlu:

| Kod | Bulgu | Etkilediği iddia | Durum |
|---|---|---|---|
| S2 | fill-rule: kod her zaman even-odd uygular, uyarı "nonzero" der | #2 (exact dolu-alan) | PROJEDE DÜZELTİLECEK |
| S3 | stroke_width hiçbir rapor/manifest'e yazılmıyor | #3 (tekrarlanabilirlik) | PROJEDE DÜZELTİLECEK |

Ayrıca Douglass'ın üstün olduğu 3 nokta dürüstçe kabul edilmeli ve ya
kapatılmalı ya "future work" yazılmalı:
- Otomatik ölçek aralığı seçimi (sliding window) — RASH-HIT'te YOK
- Grid offset optimizasyonu — RASH-HIT'te YOK
- Doğrulama titizliği (5 fraktal + teorik D) — RASH-HIT'te zayıf

---

## 5. ATIF STRATEJİSİ (Douglass nasıl atıf verilir)

ZORUNLU: Douglass (2025) ilgili çalışma olarak atıf verilir ve yöntemi
açıkça karşılaştırılır. Kullanılabilir doğrudan alıntılar:

- "Unlike traditional pixelated approaches that suffer from rasterization
  artifacts, the method used directly analyzes geometric line segments"
  (Abstract) — *bizim yöntem-yeniliği iddiamızı geçersiz kılan cümle;
  bu yüzden katkıyı girdi+uygulama olarak kuruyoruz.*
- "Current implementation is limited to two-dimensional line segment
  analysis" (§4.2) — *bizim dolu-alan farkımızı meşrulaştıran cümle.*
- "may require adjustment for significantly different geometric patterns
  or applications beyond the tested range" (§4.2) — *tasarım verisine
  genellenebilirliğinin yazarca sorgulandığı cümle; uygulama boşluğumuzu
  pekiştirir.*

---

## 6. SONUÇ

Katkı = **yazılım/mühendislik + uygulama (kültürel motif) katkısı**.
Katkı ≠ box-counting yöntemi. "Farklı bağlam" bir zayıflık değil, savunulabilir
konumlandırmanın kendisidir — Douglass yöntem katmanında öndedir, RASH-HIT
girdi + dolu-alan + manifest + tasarım uygulaması katmanlarında öndedir.
