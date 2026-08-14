
---

# EK BÖLÜM C — PROJE BELGELERİNDEKİ İDDİALARIN KAYNAK KODLA BİREBİR DOĞRULANMASI

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
