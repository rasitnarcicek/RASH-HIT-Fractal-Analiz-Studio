# RASH-HIT — DOĞRULAMA VE DENEYLER (birleştirilmiş)

Kapsam: Motorun temel doğruluğu, çizgi kalınlığı duyarlılığı, ızgara yanlılığı,
dolgu-çizgi sağlamlık karşılaştırması ve tek rakip araç (FractDim) sınaması.
Tüm deneyler proje dosyasına dokunmadan, ayrı betiklerle (`deneyler/`) yapıldı.

---

## 1. KONTROL ŞEKİLLERİ — MOTOR DOĞRU (kanıtlandı)

Ayar: v1.0.6, `--levels 8 --profile lean --grid-mode canvas_aspect`.
Test SVG'leri: `~/rakip_analiz/dogrulama/svg/`

| Şekil | Teorik D | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|---|
| Düz çizgi | 1.000000 | 1.0000 | %0.00 | 1.0000 | 92.5 |
| Dolu kare | 2.000000 | 2.0000 | %0.00 | 1.0000 | 92.5 |
| Sierpinski (L6, dolgulu) | 1.584963 | 1.6137 | %1.81 | 1.0000 | 100.0 |
| Minkowski (L4, stroke 1.0) | 1.500000 | 1.4518 | %3.21 | 1.0000 | 92.5 |

**Sonuç:** Boyutun iki ucu (1.0 ve 2.0) tam isabet. Ölçüm zinciri sağlam.
Bu, hakeme gösterilecek en temel kanıttır.

---

## 2. ÇİZGİ KALINLIĞI DUYARLILIĞI (Koch L6, tuval 1000px, teorik D=1.261859)

| stroke-width | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|
| 3.00 px | 1.5408 | %22.11 | 0.9970 | 92.5 |
| 1.00 px | 1.4091 | %11.67 | 0.9986 | 92.5 |
| 0.25 px | 1.3100 | %3.82 | 0.9995 | 92.5 |
| 0.10 px | 1.2806 | %1.49 | 0.9992 | 92.5 |

**Bulgu:** Aynı geometri, tek değişken çizgi kalınlığı → **0.26 boyut birimi
kayma** (Koch 1.26 ile Sierpinski 1.58 arasındaki farkın yarısından fazla).
Kalın çizgi ince çizgiye göre daha çok hücre doldurur; ızgara çizgi
kalınlığının altına inince geometriyi değil kalınlığı ölçer. Bu bir HATA
değil, bir OLGUDUR — sorulan soru belirsiz ("geometri mi, kaplanan alan mı?").

**Güven skoru doğruluğu ölçmüyor:** stroke 3.0 (%22 yanlış) ve stroke 0.10
(%1.5 doğru) AYNI güven notunu (92.5) alır; çünkü skor R² tabanlı ve her
ikisinde de R²>0.997. Yazılım %22 yanlış cevaba "yüksek güven" diyor.

---

## 3. IZGARA YANLILIĞI (kaydırma + döndürme)

Betik: `deneyler/grid_bias_audit.py`. Aynı şekil, ızgara kaydırılıp
döndürülerek yeniden ölçülür; Db yayılımı ölçülür.

### Koch L5 (çizgi) · teorik 1.261859
| koşul | Db | hata % |
|---|---|---|
| referans (0,0,0°) | 1.1825 | −6.29 |
| döndür 45° | 1.2659 | +0.32 |
| **YAYILIM (maks−min)** | **0.0868** | std 0.0347 |

### Sierpinski L5 (dolgu) · teorik 1.584963
| koşul | Db | hata % |
|---|---|---|
| referans | 1.6007 | +0.99 |
| döndür 30° | 1.6123 | +1.73 |
| **YAYILIM (maks−min)** | **0.0185** | std 0.0064 |

**Bulgu 1:** Dolgu ölçümü ızgara yanlılığına KARŞI SAĞLAM (yayılım 0.019).
**Bulgu 2:** Çizgi ölçümü ızgaraya 4.7 kat daha duyarlı (0.087); eksene
hizalı ızgara (0°) en kötü sonucu veriyor (rezonans) — sistematik/yönlü hata.
**Bulgu 3:** Altı koşulun hepsinde R²≥0.9988 — R² bu hatayı GÖREMİYOR (§2 ile
bağımsız doğrulama).

---

## 4. DOLGU vs ÇİZGİ — NET SONUÇ

Birbirinden bağımsız üç deney aynı yere varıyor:

| Deney | Bulgu | Etki (Db) |
|---|---|---|
| Çizgi kalınlığı | stroke genişliği sonucu kaydırıyor | **0.26** |
| Izgara yanlılığı (çizgi) | ızgara açısı sonucu kaydırıyor | **0.087** |
| Izgara yanlılığı (dolgu) | dolguda etki çok küçük | **0.019** |

**Ortak sonuç:** RASH-HIT'in **dolgu (fill) tabanlı ölçümü SAĞLAM**; **çizgi
(stroke) tabanlı ölçümü KIRILGAN** ve yazılım bunu kullanıcıya bildirmiyor.
Makale omurgası önerisi:
> *Vektör uzayında kutu sayımı, dolu düzlemsel biçimler için ızgara
> yerleşimine karşı kararlıdır (yayılım 0.019); konturlu eğriler için ise
> hem ızgara açısına (0.087) hem çizgi kalınlığına (0.26) duyarlıdır.
> Motif/tasarım analizinde dolgu tabanlı ölçüm yeğlenmeli, çizgi kalınlığı
> zorunlu olarak raporlanmalıdır.*

---

## 5. TEK RAKİP ARACIN SINANMASI — FractDim (Rendall, 2009-2011)

Amaç: "FractDim dolgu ölçemiyor" iddiasını kod okumayla değil, aracı
**derleyip çalıştırarak** sınamak. (`deneyler/build_fractdim*.sh`,
`run_fractdim*.sh`; araç ayrı klasörde derlendi, projeye dokunulmadı.)

| Soru | Cevap |
|---|---|
| Derlenebiliyor mu? | Evet — ama 4 onarım gerekli (ölü Maven eklentileri, Central'da olmayan kendi kütüphanesi, Türkçe karakterli classpath) |
| CLI çalışıyor mu? | **Hayır** — her girdide `NullPointerException` |
| Dolgu ölçebiliyor mu? | Kanıt: kaynak kod `FDGraphics2D.java:80-85` `// ignore for now - treat as draw` → `fill()` çağrısı `draw()`'a yönlenir. Dolu kare teorik 2.0 yerine ~1.0 döner. |
| Karşılaştırmalı kıyas? | Mevcut hâliyle HAYIR (CLI çöktüğü için) |

**NPE kök nedeni:** `cmd/FractDim.java:94-98` `getMetadata()` null döner;
metadata üreten `generateMetaData()` `private` ve yalnız Swing arayüz iş
parçacığından tetiklenir. **CLI, GUI'ye yapısal olarak bağımlı** — bu bir
yapılandırma hatası değil, mimari kusur.

**Dürüst makale ifadesi:** "Karşılaştırma için erişilebilen tek önceki
vektör-tabanlı araç FractDim (Rendall, 2009-2011), 2026'da kaynaktan
derlenebilmiş ancak CLI'ı GUI iş parçacığına bağlı olduğundan her girdide
NPE vermiştir; sayısal kıyas yapılamamış, karşılaştırma kaynak kodun
anlamsal incelemesiyle sınırlı kalmıştır."

---

## 6. YAPILACAKLAR (yayın öncesi zorunlu + önerilen)

### ZORUNLU (kod düzeyinde kanıtlandı)
| # | İş | Kaynak |
|---|---|---|
| S2 | `fill-rule` özniteliği yok sayılıyor: `geometry_engine.py:510-531` dallanma yok, çok-yollu yollarda daima `symmetric_difference` (even-odd) uygular; `verify2.py` kodun HER ZAMAN even-odd çalıştığını ölçtü (iç içe kare 7500/7500). `svg_loader.py:250` "Default non-zero winding rule used" diyor — YANLIŞ. SVG varsayılanı nonzero → fill-rule'sız dosyalar standardın aksine çözülür; bu bir HATA, üstünlük iddiası olarak kullanılmamalı | `geometry_engine.py:510-531`, `verify2.py` |
| S3 | `stroke_width` (ort.+maks.) manifest ve HTML rapora yazılsın | `STROKE_KOD_DENETIMI.md` |

### YÜKSEK ÖNCELİK (önerilen)
- **Y1** Ölçek tabanı uyarısı: en ince ızgara hücresi çizgi kalınlığının
  altındaysa kullanıcıyı uyar. (DOGRULAMA §Bulgu 3)
- **Y2** Güven skoruna ızgara kararlılığı + ölçek geçerliliği bileşeni ekle
  (R² tek başına yetersiz — §2 ve §3'te 3 kez kanıtlandı).
- **Y3** Raporda kalınlık bilgisi zorunlu yazılsın (tekrarlanabilirlik).
- **Y4** Bu 5 şekil (çizgi, dolu kare, Koch, Sierpinski, Minkowski) her
  sürümde otomatik doğrulama paketine girsin.
- **Y5** Çok açılı ızgara taraması (0/15/30/45°) ekle, yayılımı belirsizlik
  payı olarak raporla (FractDim 2011'de vardı; eksikliğimiz).

### DÜŞÜNÜLECEK
- "Ölçüm modu" seçeneği: çizgisel şekiller için kalınlığı yok sayan mod.
