# RASH-HIT FRAKTAL STUDIO — DOĞRULAMA TESTİ SONUÇLARI
Tarih: bu oturum · Sürüm: v1.0.6 · Motor: CPU Hassas Vektör
Ayarlar: --levels 8, --profile lean, --grid-mode canvas_aspect (varsayılan)
Test SVG'leri: C:\Users\RaşitNarçiçek\rakip_analiz\dogrulama\svg\
Çıktı paketleri: C:\Users\RaşitNarçiçek\rakip_analiz\dogrulama\out\
NOT: Proje klasöründe HİÇBİR değişiklik yapılmadı.

## TABLO 1 — KONTROL ŞEKİLLERİ (motorun temel doğruluğu)

| Şekil | Teorik D | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|---|
| Düz çizgi | 1.000000 | 1.0000 | %0.00 | 1.0000 | 92.5 |
| Dolu kare | 2.000000 | 2.0000 | %0.00 | 1.0000 | 92.5 |

SONUÇ: Motor, boyutun iki ucunu da TAM ISABETLE veriyor. Kutu sayma,
ızgara kurulumu ve regresyon zinciri doğru çalışıyor. Bu, hakeme
gösterilecek en temel kanıttır.

## TABLO 2 — DOLGULU FRAKTAL (area ölçümü)

| Şekil | Teorik D | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|---|
| Sierpinski üçgeni (L6, dolgulu) | 1.584963 | 1.6137 | %1.81 | 1.0000 | 100.0 |

SONUÇ: Dolgu tabanlı ölçüm çok temiz. %1.81 sapma, sonlu iterasyon
(L6) ve sonlu ızgara derinliğinden (8 seviye) beklenen düzeyde.
R²=1.0000 mükemmel doğrusallık.

## TABLO 3 — ÇİZGİSEL FRAKTAL VE ÇİZGİ KALINLIĞI DUYARLILIĞI
(Koch eğrisi, iterasyon 6, tuval 1000 px, teorik D = 1.261859)

| stroke-width | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|
| 3.00 px | 1.5408 | %22.11 | 0.9970 | 92.5 |
| 1.00 px | 1.4091 | %11.67 | 0.9986 | 92.5 |
| 0.25 px | 1.3100 | %3.82 | 0.9995 | 92.5 |
| 0.10 px | 1.2806 | %1.49 | 0.9992 | 92.5 |

## TABLO 4 — MINKOWSKI

| Şekil | Teorik D | Ölçülen Db | Hata | R² | Güven |
|---|---|---|---|---|---|
| Minkowski eğrisi (L4, stroke 1.0) | 1.500000 | 1.4518 | %3.21 | 1.0000 | 92.5 |

===========================================================================
## BULGU 1 — MOTOR DOĞRU (kanıtlandı)
===========================================================================
Düz çizgi 1.0000 ve dolu kare 2.0000 tam isabet. Dolgulu Sierpinski
%1.81 sapma. Ölçüm zinciri sağlam.

===========================================================================
## BULGU 2 — ÇİZGİ KALINLIĞI ÖLÇÜMÜ SİSTEMATİK OLARAK ŞİŞİRİYOR
===========================================================================
Aynı Koch eğrisi, aynı geometri, TEK değişen çizgi kalınlığı:
3.00 px -> 1.5408 · 0.10 px -> 1.2806
Fark: 0.26 boyut birimi. Bu, Koch ile Sierpinski arasındaki farkın
yarısından fazla. Yani çizgi kalınlığı, motifin kimliğini değiştirecek
kadar sonucu kaydırıyor.

NEDEN OLUYOR: Kalın çizgi, ince çizgiye göre daha çok hücreyi doldurur.
Izgara inceldikçe (L07, L08) hücre boyu çizgi kalınlığının ALTINA
düşüyor; o noktadan sonra sayım geometriyi değil, çizginin kendi
kalınlığını ölçmeye başlıyor. Boyut 2'ye doğru itiliyor.

BU BİR HATA DEĞİL, BİR OLGUDUR. Yazılım doğru sayıyor; sorulan soru
belirsiz. "Bu çizginin karmaşıklığı" mı, "bu çizgi kalınlığıyla
kaplanan alanın karmaşıklığı" mı?

===========================================================================
## BULGU 3 — GÜVEN SKORU DOĞRULUĞU DEĞİL, UYUMU ÖLÇÜYOR
===========================================================================
En kritik bulgu:
  stroke 3.00 px -> Db 1.5408 (%22 YANLIŞ) -> Güven skoru 92.5/100
  stroke 0.10 px -> Db 1.2806 (%1.5 doğru)  -> Güven skoru 92.5/100

Aynı güven notu. Çünkü skor R² tabanlı ve her ikisinde de R² > 0.997.
Yani yazılım, %22 yanlış bir cevaba "yüksek güven" diyor.

Bu, güven skorunun sahte olduğu anlamına gelmez — doğru şeyi ölçüyor
(regresyonun doğrusallığı). Ama kullanıcı bunu "cevap doğru" diye
okuyor. Skorun ne ölçtüğü açıkça yazılmalı, ve içine ölçek-geçerliliği
bileşeni eklenmeli.

===========================================================================
## YAPILACAKLAR (bu testten çıkan, gerçek liste)
===========================================================================

Y1. ÖLÇEK TABANI UYARISI [YÜKSEK]
    Yazılım, en ince ızgara hücresinin boyutunu geometrideki en ince
    yapıyla (çizgi kalınlığı) karşılaştırsın. Hücre, çizgiden inceyse
    kullanıcıyı uyarsın: "L07 ve L08 seviyelerinde ızgara çizgi
    kalınlığının altına indi; bu seviyeler kalınlığı ölçüyor."
    Neden: Sessizce yanlış sonuç vermek yerine, neyin ölçüldüğünü
    söylemek. Bu tek başına yazılımı rakiplerinden ayırır.

Y2. GÜVEN SKORUNA ÖLÇEK GEÇERLİLİĞİ EKLE [YÜKSEK]
    Skor sadece R²'ye değil, "kaç seviye çizgi kalınlığının üstünde
    kaldı" bilgisine de baksın. stroke 3.0 vakası 92.5 değil, 55 gibi
    bir not almalıydı.
    Neden: Bulgu 3 doğrudan bunu gösteriyor. Bir hakem bu testi yapar
    ve aynı şeyi görür.

Y3. RAPORDA KALINLIK BİLGİSİNİ ZORUNLU YAZ [ORTA]
    report.html ve manifest.json her zaman ortalama ve en büyük
    effective stroke width ile en küçük hücre boyutunu göstersin.
    Neden: Tekrarlanabilirlik. Aynı motifi başka biri farklı
    kalınlıkla çizip farklı sonuç bulunca kaynağı görebilsin.

Y4. DOĞRULAMA PAKETİNİ PROJEYE EKLE [YÜKSEK]
    Bu 5 şekil (çizgi, dolu kare, Koch, Sierpinski, Minkowski) test
    klasörüne girsin, her sürümde otomatik çalışsın.
    Neden: Yayın şartı. Ayrıca ileride bir değişiklik doğruluğu
    bozarsa anında yakalanır.

Y5. "ÖLÇÜM MODU" SEÇENEĞİ [DÜŞÜNÜLECEK]
    Çizgisel şekiller için kalınlığı yok sayan bir mod (çizgiyi
    kalınlıksız eğri olarak sayma). O modda Koch'un kalınlıktan
    bağımsız tek bir Db değeri çıkar.
    Neden: Şu an --measure sadece "area". Çizgisel motifler için
    ikinci bir mod, aracın kapsamını gerçekten genişletir.

===========================================================================
## MAKALE İÇİN DEĞERİ
===========================================================================
Tablo 3 tek başına bir makale şeklidir. Söylediği:
"Vektör geometriden doğrudan ölçüm yaparken bile, çizgi kalınlığı bir
serbestlik derecesidir ve raporlanmadığı sürece sonuç tekrarlanamaz."

Literatürde raster tarafında bu tartışılıyor (Ostwald 2013, çizgi
kalınlığı kalibrasyonu). Vektör tarafında aynı olgunun ölçülüp
sayısallaştırıldığı bir çalışma taramamızda bulunamadı. Bu, iddia
edilebilir somut bir katkıdır — ve dürüsttür, çünkü kendi aracımızın
sınırını gösteriyoruz.
