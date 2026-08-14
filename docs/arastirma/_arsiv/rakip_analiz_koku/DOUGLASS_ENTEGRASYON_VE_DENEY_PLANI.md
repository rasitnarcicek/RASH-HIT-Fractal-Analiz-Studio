# DOUGLASS'TAN ÖĞRENİLECEKLER + DENEY PLANI
(Kaynak kodu satır satır incelenerek çıkarıldı:
 kaynaklar/Fractal-Dimension-Analyzer/fractal_analyzer.py — 2361 satır)

===========================================================================
BÖLÜM 1 — DOUGLASS'IN BİZDEN ÜSTÜN OLDUĞU 3 NOKTA (kod referanslı)
===========================================================================

## ÜSTÜNLÜK 1 — Otomatik ölçek aralığı seçimi (kayan pencere)
Kod: analyze_linear_region(), satır 1194-1305
Ne yapıyor:
  - Tüm kutu boyutları için log-log noktalarını çıkarıyor.
  - min_window=3'ten tüm veri uzunluğuna kadar HER pencere boyutu için,
    HER başlangıç indeksinde regresyon yapıyor (O(n^2) tarama).
  - Her pencere boyutu için en yüksek R^2'li konumu saklıyor.
  - Sonra "fiziksel kısıt" filtresi uyguluyor (satır 1275-1292):
        1.0 <= D <= 2.0  VE  pencere >= 4 nokta  VE  R^2 >= 0.99
    Bu filtreden geçenler arasında R^2'ye, eşitlikte pencere boyutuna göre
    sıralayıp en iyisini seçiyor.
  - Hiçbiri geçmezse en yüksek R^2'ye düşüyor ve UYARI basıyor.
Ne işe yarıyor:
  Box-counting'in en büyük öznel kararı "hangi ölçek aralığında regresyon
  yapacağım" sorusudur. Elle seçim = sonucu istediğin yere çekebilme =
  bilimsel itiraz konusu. Bu algoritma kararı veriden türetiyor.
Bize katkısı:
  RASH-HIT'te ölçek aralığı hâlâ parametre/varsayılan. Bunu eklersek
  "kullanıcıdan bağımsız, tekrarlanabilir sonuç" iddiamız gerçekten
  savunulabilir hale gelir. Hakem bunu SORAR.

## ÜSTÜNLÜK 2 — Grid offset (ızgara konumu) optimizasyonu
Kod: box_counting_with_grid_optimization(), satır 560-652 + _count_boxes_with_offset() 654-688
Ne yapıyor:
  - Aynı kutu boyutu için ızgarayı kaydırarak birden çok kez sayıyor,
    EN KÜÇÜK sayımı alıyor (satır 627, 636-638).
  - Kaydırma yoğunluğu kutu boyutuna göre uyarlanıyor (satır 594-606):
        kutu < 5*min  -> 4x4 = 16 deneme  ("fine")
        kutu < 20*min -> 3x3 = 9 deneme   ("medium")
        aksi halde    -> 2x2 = 4 deneme   ("coarse")
    Mantık: küçük kutularda kuantalama hatası en büyük, orada çok dene;
    büyük kutularda az dene -> hız/doğruluk dengesi.
  - "improvement" metriği basıyor: (max-min)/max*100, yani ızgara konumunun
    sonucu ne kadar değiştirdiğini raporluyor.
Ne işe yarıyor:
  Sabit ızgarayla sayarsan, ızgaranın nereye denk geldiğine bağlı olarak
  kutu sayısı şişer. Bu D'yi sistematik olarak YUKARI kaydırır. Makale
  0.01-0.05 tipik iyileşme bildiriyor — bu, D=1.26 için %1-4 hata demek.
Bize katkısı:
  RASH-HIT tek ızgara konumu kullanıyorsa, ölçtüğümüz her D bir miktar
  şişkindir. Bu, Ostwald 2013'ün (DOI 10.1068/b38124) mimarlıkta gösterdiği
  "grid disposition" problemiyle aynı şey. Eklenmesi ZORUNLU, çünkü
  literatürde bilinen bir hata kaynağını görmezden gelmiş oluruz.
  UYARI: Bu algoritmik bir YENİLİK DEĞİL (1989'dan beri biliniyor) —
  bizim için "eksik kapatma", "katkı" değil.

## ÜSTÜNLÜK 3 — Doğrulama titizliği (validation suite)
Kod: examples/ altında 6 ayrı çalışma:
  koch_validation/ (doğruluk), minkowski_grid_optimization/ (grid etkisi),
  sierpinski_boundary_effects/ (sınır artefaktı), hilbert_scaling/ (ölçekleme),
  dragon_robustness/ (gürültü dayanıklılığı), rt_interface_analysis/ (gerçek veri)
  + enhanced_boundary_removal(), satır 490-558:
      veriyi çeyreklere bölüp baş/orta/son eğimleri karşılaştırıyor;
      eğim sapması > 0.12 VEYA R^2 < 0.95 ise uçtan nokta kırpıyor,
      kırpma sonrası R^2'yi tekrar raporluyor.
Ne yapıyor:
  Bilinen teorik fraktalların (Koch 1.2619, Sierpinski 1.5850,
  Minkowski 1.5) tam değerine karşı ölçüyor, hatayı yüzde olarak veriyor.
  Bildirilen: tüm optimize sonuçlarda R^2 >= 0.9988, Koch hatası %0.11.
Ne işe yarıyor:
  Hakem "bu yazılımın çıktısı doğru mu?" diye sorduğunda gösterilecek tek
  şey budur. Yazılım makalesinin (JOSS/SoftwareX) ZORUNLU bileşeni.
Bize katkısı:
  RASH-HIT'in yayımlanabilmesi için AYNI doğrulama takımını, hatta aynı
  fraktalları çalıştırıp sayısal olarak yan yana koymamız gerekiyor.
  Bu bizim en acil eksiğimiz.

===========================================================================
BÖLÜM 2 — DOUGLASS'IN ZAYIF NOKTALARI (bizim savunma hattımız)
===========================================================================

Z1. GİRDİ KATMANI YOK.
    read_line_segments(), satır 373-392: dosyadan sadece "x1 y1 x2 y2"
    biçiminde 4 sayı okuyor. Virgül/boşluk ayırıyor, # yorum atlıyor.
    Yani "dosya formatı desteği" = düz metin koordinat listesi.
    SVG, DXF, AI, PDF, EPS -> HİÇBİRİ YOK. Tam metinde "SVG" 0 kez geçiyor.
    Bir tasarımcının elindeki logo/motif dosyasını bu araca sokmanın yolu
    yok; kullanıcı önce kendi dönüştürücüsünü yazmak zorunda.
    >>> BİZİM ASIL KATKIMIZ TAM BURASI: belge-düzeyi vektör girdi katmanı
        (Bezier düzleştirme, transform zinciri, CSS/stil çözümleme,
         clip-path, fill-rule, grup hiyerarşisi).

Z2. ALAN (POLİGON) DESTEĞİ YOK.
    Tüm kesişim mantığı Liang-Barsky ÇİZGİ-kutu kırpması üzerine kurulu
    (satır 405-436). Kapalı dolgulu şekil (filled polygon) kavramı yok.
    Yazarın kendi ifadesi: "limited to two-dimensional line segment analysis".
    Bir motifin/logonun DOLGUSU varsa, Douglass sadece konturunu ölçer.
    >>> Tasarım verisinin çoğu dolgudur. Karma geometri (çizgi + poligon)
        desteği bizim ikinci ayrım noktamız.

Z3. ÖLÇEK SEÇİMİNDE DÖNGÜSELLİK RİSKİ.
    satır 1267-1268: theoretical_dimension verilmişse, pencereyi
    "teorik değere EN YAKIN D'yi veren pencere" olarak seçiyor.
    Bu, doğrulama testlerinde sonucu bilerek en iyi pencereyi seçmek
    demektir — Koch %0.11 hatası bu modda üretilmişse rakam iyimserdir.
    >>> Dürüst karşılaştırma için biz kör (blind) modda ölçmeli ve bunu
        açıkça yazmalıyız. Bu, makalede yapıcı bir metodolojik eleştiri
        olarak sunulabilir (kişisel değil, teknik).

Z4. ÖLÇEKLENEBİLİRLİK.
    _count_boxes_with_offset() her ızgara konumu için TÜM kutuları
    (num_boxes_x * num_boxes_y) döngüyle geziyor (satır 664-665) — boş
    kutular dahil. Küçük kutu boyutlarında bu kuadratik patlar.
    Bizim yaklaşımımız (sadece dolu bölgeleri hiyerarşik gezme) burada
    ÖLÇÜLEBİLİR bir hız avantajı verebilir — ama BENCHMARK ŞART,
    iddia edilmeden ölçülmeli.

Z5. Toplu (batch) analiz, web arayüzü, güven skoru, dışa aktarma
    formatları yok. Tek dosya, tek çalıştırma, CLI.

===========================================================================
BÖLÜM 3 — RASH-HIT'E EKLEME PLANI (öncelik sırasıyla)
===========================================================================

P1 [ZORUNLU] Doğrulama takımı: Koch(1.2619), Sierpinski(1.5850),
   Minkowski(1.5), Hilbert, Dragon -> SVG olarak üret, RASH-HIT ile ölç,
   hata yüzdesi + R^2 tablosu çıkar. Douglass'ın rakamlarıyla yan yana koy.
   Çıktı: DOGRULAMA_TABLOSU.md

P2 [ZORUNLU] Grid offset optimizasyonu ekle (Douglass'ın uyarlamalı
   4x4/3x3/2x2 şemasını referans alarak, atıfla). Öncesi/sonrası D farkını
   raporla — bu farkın kendisi bir bulgudur.

P3 [ZORUNLU] Otomatik ölçek aralığı seçimi (kayan pencere + fiziksel kısıt
   1<=D<=2, pencere>=4, R^2>=0.99). AMA theoretical_dimension ile seçim
   yapma — kör modda çalıştır.

P4 [YÜKSEK] Sınır artefaktı tespiti (çeyrek eğim karşılaştırma,
   eşikler 0.12 / 0.95). Douglass'ın eşiklerini başlangıç değeri al,
   kendi verimizde duyarlılık analizi yap.

P5 [KATKI] Karma geometri: dolgulu poligon + çizgi birlikte. Douglass'ta
   yok. fill-rule (nonzero/evenodd) ve clip-path doğru işlenmeli.

P6 [KATKI] Girdi katmanı testleri: aynı motifin SVG / DXF / PDF
   sürümlerinden aynı D'nin çıktığını göster (format bağımsızlığı).

===========================================================================
BÖLÜM 4 — RASTER-vs-VEKTÖR DPI DENEYİ (varlık gerekçemizin kanıtı)
===========================================================================

HİPOTEZ:
  Vektör doğan bir tasarımı raster'a çevirip ölçtüğünüzde bulunan fraktal
  boyut D, rasterizasyon parametrelerine (DPI, çizgi kalınlığı, eşikleme)
  sistematik olarak bağlıdır ve tek bir "doğru" değer vermez. Doğrudan
  vektör ölçümü bu bağımlılığı ortadan kaldırır.

TASARIM:
  Girdi kümesi (hepsi VEKTÖR doğan):
    G1. Koch eğrisi (teorik D = 1.261859...) — yer gerçeği var
    G2. Sierpinski üçgeni (D = 1.5849625) — yer gerçeği var
    G3. Minkowski sosisi (D = 1.5) — yer gerçeği var
    G4. Gerçek tasarım: 3 logo + 3 geleneksel motif (SVG)
    G5. Kontrol: düz çizgi (D=1) ve dolu kare (D=2)

  Manipüle edilen değişkenler:
    DPI: 75, 150, 300, 600, 1200, 2400
    Çizgi kalınlığı (stroke-width): 0.25pt, 0.5pt, 1pt, 2pt
    (İkincil) İkileştirme eşiği: 128 sabit + Otsu

  Ölçüm kolları:
    Kol A: SVG -> PNG (DPI/kalınlık kombinasyonu) -> FracLac/ImageJ ile
           box-counting -> D_raster(DPI, kalınlık)
    Kol B: SVG -> PNG -> RASH-HIT'in (varsa) raster yolu -> iç tutarlılık
    Kol C: SVG -> RASH-HIT doğrudan vektör -> D_vektor (TEK değer, DPI yok)
    Kol D: (varsa) segment listesi -> Douglass aracı -> D_douglass
           [sadece çizgisel G1-G3 için; poligonlarda çalışmaz -> bu da bulgu]

  Ölçütler:
    M1. Doğruluk: |D_olculen - D_teorik| (G1-G3 için)
    M2. DPI kararlılığı: D'nin DPI aralığındaki standart sapması ve
        yayılımı (max-min). Kol C için tanım gereği 0.
    M3. Kalınlık duyarlılığı: stroke-width değişiminin D'ye etkisi.
    M4. Yakınsama: D_raster(DPI) -> D_vektor'e yakınsıyor mu, hangi DPI'da
        fark < 0.01 oluyor? ("Vektörle aynı sonuç için kaç DPI gerekiyor
        ve bu ne kadar bellek/süre maliyeti?")
    M5. Süre ve bellek: her kol için.

  BEKLENEN BULGU (hipotez, sonuç değil):
    Düşük DPI'da ince çizgiler kopar -> D düşer; yüksek DPI'da çizgi
    kalınlığı göreli incelir -> D teorik değere yaklaşır ama maliyet
    kareyle artar. İnce detaylı motiflerde 2400 DPI'da bile yakınsama
    tamamlanmayabilir. Bu grafik (x=DPI, y=D, yatay çizgi=D_vektor)
    makalenin AÇILIŞ ŞEKLİ olur.

  GEREKLİ ARAÇLAR:
    - rsvg-convert veya Inkscape CLI (SVG->PNG, DPI kontrollü)
    - ImageJ/Fiji + FracLac eklentisi (bağımsız referans ölçüm — kendi
      kodumuzla ölçersek hakem "kendi kendini doğrulama" der)
    - RASH-HIT CLI

  DÜRÜSTLÜK KURALI:
    Kol A'da FracLac'ın kendi grid offset ayarı ("num grids") AÇIK
    olmalı; kapalı bırakıp rakip aracı zayıf göstermek geçersiz karşılaştırma
    olur. Tüm parametreler raporlanmalı.

DURUM: Tasarlandı. Uygulama için ImageJ/FracLac kurulumu ve test SVG
       kümesinin üretilmesi gerekiyor — henüz yapılmadı.
