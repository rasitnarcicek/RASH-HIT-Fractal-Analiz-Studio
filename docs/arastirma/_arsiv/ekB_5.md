
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
