# KAYNAK DEPOSU — RASH-HIT Fraktal Studio
Amaç: ileride makale/tez yazımında kullanılacak tüm doğrulanmış kaynakların
tek dosyada, DOI/link + kısa açıklama + "bizim için önemi" ile saklanması.
Kural: Buradaki her DOI Crossref veya yayıncı sayfası üzerinden doğrulanmıştır.
Doğrulanamayan hiçbir kayıt eklenmemiştir. Son güncelleme: bu oturum.

---------------------------------------------------------------------------
## A. EN KRİTİK RAKİP — DOĞRUDAN BENZER (Kategori A)
---------------------------------------------------------------------------

### A1. Douglass, R.W. (2025)
"Advanced Box-Counting Methods for Fractal Dimension Analysis: Grid
Optimization and Boundary Artifact Detection"
- Dergi: Fractal and Fractional 9(10):633
- DOI: 10.3390/fractalfract9100633
- Link: https://www.mdpi.com/2504-3110/9/10/633
- Yayın: 29 Eylül 2025 · Lisans: CC BY 4.0 · Açık erişim
- Kod: https://github.com/rwdlnk/Fractal-Dimension-Analyzer (Python 3, 6757 satır)
- Yerel kopya: kaynaklar/Douglass_2025_FractalFract_9_633.pdf + .md (tam metin)
- Yöntem: Çizgi PARÇALARI (line segments) üzerinde doğrudan kutu sayımı;
  rasterizasyon YOK. Kesişim testi = Liang-Barsky çizgi kırpma. Uzamsal
  indeks = düzgün hücre ızgarası (uniform grid hash), quadtree/STRtree değil.
  3 fazlı iyileştirme: (1) grid offset optimizasyonu, (2) sınır artefaktı
  tespiti, (3) kayan pencere ile ölçek aralığı seçimi.
- Doğrulama: Koch, Sierpinski, Minkowski, Hilbert, Dragon; R^2 >= 0.9988;
  Koch hata %0.11.
- BİZE BENZERLİĞİ: "rasterizasyonsuz vektör box-counting" iddiamızın
  ÖNCELİĞİNİ elinde tutuyor (~10 ay önce, bizim Zenodo 29 Tem 2026'ya karşı).
- BİZDEN FARKI: girdisi DOSYA DEĞİL, kod içi/ham 4-sütunlu koordinat metni
  (read_line_segments: "x1 y1 x2 y2" satırları). Tam metinde "SVG" 0 kez
  geçiyor. Poligon/alan desteği yok — yazarın kendi ifadesi:
  "limited to two-dimensional line segment analysis". Bezier, CSS,
  transform, clip-path, fill-rule yok. Toplu (batch) analiz yok, web arayüzü
  yok, güven skoru yok. Uygulama alanı akışkanlar dinamiği (Rayleigh-Taylor).
- ÖNEMİ: Makalede MUTLAKA atıf verilmeli ve fark açıkça yazılmalı. "İlk"
  iddiası kullanılamaz; "belge-düzeyi vektör girdi katmanı" iddiası kullanılır.

---------------------------------------------------------------------------
## B. MİMARLIK / TASARIM EKSENİ (Kategori D — alan benzerliği, BİZİM BOŞLUĞUMUZUN KANITI)
---------------------------------------------------------------------------

### B1. Ostwald, M.J. & Vaughan, J. (2016)
"The Fractal Dimension of Architecture" (Birkhauser, Mathematics and the
Built Environment vol.1)
- DOI: 10.1007/978-3-319-32426-5
- Tür: Kitap · Kapalı erişim (bölüm özetleri açık)
- Yöntem: Mimari çizimleri (CAD kökenli, yani VEKTÖR doğan veri) box-counting
  ile ölçer — ama önce RASTER görüntüye çevirerek. Kitabın büyük bölümü
  rasterizasyon kaynaklı hata kaynaklarının (çizgi kalınlığı, görüntü
  çözünürlüğü, beyaz alan oranı, kutu sayısı) kalibrasyonuna ayrılmıştır.
- BİZİM İÇİN ÖNEMİ: EN GÜÇLÜ GEREKÇEMİZ. Alanın standart referansı, vektör
  doğan veriyi rasterleştirmek zorunda kaldığı için sayfalarca hata
  kalibrasyonu yapıyor. RASH-HIT bu hata sınıfını tanım gereği ortadan
  kaldırıyor. Makalede "problem statement" bu kitaptan alıntılanmalı.

### B2. Ostwald, M.J. (2013)
"The fractal analysis of architecture: calibrating the box-counting method
using scaling coefficient and grid disposition variables"
- Dergi: Environment and Planning B: Planning and Design 40(4):644-663
- DOI: 10.1068/b38124
- BİZİM İÇİN ÖNEMİ: "Grid disposition" (ızgara konumu) değişkeninin sonucu
  nasıl değiştirdiğini mimarlık verisinde gösteriyor. Douglass'ın grid offset
  optimizasyonuyla AYNI problem, 12 yıl önce, farklı alanda. Yani grid offset
  algoritmik olarak yeni değil — bizim de bunu "yenilik" diye sunmamamız
  gerektiğinin kanıtı, ama uygulamamız için zorunlu bir özellik.

### B3. Bovill, C. (1996)
"Fractal Geometry in Architecture and Design" (Birkhauser Boston)
- ISBN: 978-1-4612-0843-3 · DOI: 10.1007/978-1-4612-0843-3
- BİZİM İÇİN ÖNEMİ: Mimarlık/tasarımda box-counting kullanımının kurucu
  metni. Elle ızgara sayımı yapıyor. Tarihsel arka plan bölümü için.

---------------------------------------------------------------------------
## C. SANAT / GÖRSEL KARMAŞIKLIK / ESTETİK
---------------------------------------------------------------------------

### C1. Taylor, R.P., Micolich, A.P., Jonas, D. (1999)
"Fractal analysis of Pollock's drip paintings"
- Dergi: Nature 399:422 · DOI: 10.1038/20833
- Yöntem: Pollock tablolarının fotoğrafları (RASTER) üzerinde box-counting.
- ÖNEMİ: Sanat eserine fraktal boyut uygulamasının en çok atıf alan örneği.
  Girdi raster fotoğraf — bizim vektör yaklaşımımızın karşıt kutbu.

### C2. Jones-Smith, K., Mathur, H., Krauss, L.M. (2009)
"Drip paintings and fractal analysis"
- Dergi: Physical Review E 79:046111 · DOI: 10.1103/PhysRevE.79.046111
- ÖNEMİ: Taylor'ın sonuçlarını ÇÜRÜTÜYOR — basit çocuk çizimlerinin de aynı
  "fraktal" imzayı verdiğini gösteriyor. UYARI KAYNAĞI: fraktal boyutun tek
  başına ayırt edici olmadığının kanıtı. Bizim "güven skoru" bileşenimizin
  gerekçesi tam olarak budur; makalede bu tartışmaya bağlanmalı.

### C3. Taylor, R.P. et al. (2007)
"Authenticating Pollock paintings using fractal geometry"
- Dergi: Pattern Recognition Letters 28(6):695-702
- DOI: 10.1016/j.patrec.2006.08.012
- ÖNEMİ: C1-C2 tartışmasının yazarın cevabı; metodolojik hassasiyet tartışması.

### C4. Forsythe, A. et al. (2011)
"Predicting beauty: fractal dimension and visual complexity in art"
- Dergi: British Journal of Psychology 102(1):49-70
- DOI: 10.1348/000712610X498958
- ÖNEMİ: Fraktal boyut <-> algılanan görsel karmaşıklık ilişkisi. Tasarım
  uygulamamızın "neden işe yarar" gerekçesi.

### C5. Machado, P. et al. (2015)
"Computerized measures of visual complexity"
- Dergi: Acta Psychologica 160:43-57
- DOI: 10.1016/j.actpsy.2015.06.005
- ÖNEMİ: Görsel karmaşıklığın hesaplamalı ölçütleri; fraktal boyut bunlardan
  yalnızca biri. Karşılaştırma bölümü için.

### C6. Donderi, D.C. (2006)
"Visual complexity: a review"
- Dergi: Psychological Bulletin 132(1):73-97
- DOI: 10.1037/0033-2909.132.1.73
- ÖNEMİ: Alanın derleme referansı; giriş bölümü için.

---------------------------------------------------------------------------
## D. LOGO / MARKA / TİPOGRAFİ KARMAŞIKLIĞI (vektör doğan veri, ama ölçüm ÖZNEL)
---------------------------------------------------------------------------

### D1. van Grinsven, B. & Das, E. (2016)
"Logo design in marketing communications: brand logo complexity..."
- Journal of Marketing Communications 22(3):256-270
- DOI: 10.1080/13527266.2013.866593
- ÖNEMİ: Logo karmaşıklığı ÖZNEL ölçekle (katılımcı anketi) ölçülüyor.
  BOŞLUK KANITI: vektör logo dosyası varken bile nesnel geometrik ölçüm
  kullanılmıyor. RASH-HIT tam bu boşluğa oturuyor.

### D2. Kosaka, H. & Ikeguchi, T. (2024)
"Evaluation of Logo Design Using Fractal Dimension"
- AHFE International Conference · DOI: 10.54941/ahfe1004810
- ÖNEMİ: BULUNAN EN YAKIN TASARIM UYGULAMASI. Logolara fraktal boyut
  uyguluyor. Girdi tipinin vektör mü raster mı olduğu makale tam metninden
  DOĞRULANMALI (henüz doğrulanamadı — TAKİP GEREKLİ).

### D3. Trehan, S. & Kalro, A.D. (2024) / Tang (2025) — logo karmaşıklığı
      pazarlama literatürü
- Durum: Crossref'te doğrulandı, tam metin erişimi sınırlı.
- ÖNEMİ: D1 ile aynı argüman (öznel ölçüm hakimiyeti). İkincil kaynak.

---------------------------------------------------------------------------
## E. KLASİK YÖNTEM KAYNAKLARI (öncelik iddiasını sınırlayan temel metinler)
---------------------------------------------------------------------------

### E1. Liebovitch, L.S. & Toth, T. (1989)
"A fast algorithm to determine fractal dimensions by box counting"
- Physics Letters A 141(8-9):386-390 · DOI: 10.1016/0375-9601(89)90854-2
- ÖNEMİ: Box-counting hızlandırmanın klasik referansı. "Hızlı algoritma"
  iddiası bu makaleye kadar geri gider — bizim STRtree/quadtree budamamız
  algoritmik olarak YENİ DEĞİL, mühendislik katkısıdır.

### E2. Karperien, A. — FracLac for ImageJ (1999-2013)
- Link: https://imagej.net/ij/plugins/fraclac/fraclac.html
- Kılavuz: https://imagej.net/ij/plugins/fraclac/FLHelp/Introduction.htm
- Tür: Açık kaynak ImageJ eklentisi (Java) · Hâlâ dağıtımda, aktif geliştirme
  durmuş sayılır.
- ÖNEMİ: Alanın DE FACTO standardı. RASTER giriş. Grid offset ("num grids"),
  çoklu ölçek, toplu analiz zaten var. Karşılaştırma matrisinde ana rakip.
  Raster-vs-vektör DPI deneyinde referans araç olarak kullanılacak.

### E3. Watson, R. (2012)
"Computing the Fractal Dimension of ..." Mathematica Journal 14
- DOI: 10.3888/tmj.14-5
- ÖNEMİ: Wolfram ekosisteminde box-counting uygulaması; ticari/kapalı
  ekosistem karşılaştırması için.

---------------------------------------------------------------------------
## F. YAZILIM / PAKET KAYNAKLARI (karşılaştırma matrisi girdileri)
---------------------------------------------------------------------------

| Ad | Link | Dil | Giriş | Not |
|---|---|---|---|---|
| FracLac (ImageJ) | https://imagej.net/ij/plugins/fraclac/fraclac.html | Java | Raster | De facto standart |
| Fractal-Dimension-Analyzer (Douglass) | https://github.com/rwdlnk/Fractal-Dimension-Analyzer | Python | Çizgi parçası metni | En yakın rakip |
| Fiji / ImageJ Fractal Box Count | https://imagej.net/ij/docs/menus/analyze.html | Java | Raster | Yerleşik basit araç |
| PyFracVAL / fractal-dimension PyPI paketleri | https://pypi.org/ | Python | Raster/nokta | Kütüphane düzeyi, uygulama değil |

NOT: PyPI/CRAN taramasında SVG'yi doğrudan (rasterleştirmeden) box-counting
ile analiz eden paketleme düzeyinde bir araç doğrulanamadı. Bu bir
"bulunamadı" ifadesidir, "yoktur" ifadesi DEĞİLDİR.

---------------------------------------------------------------------------
## G. TAKİP EDİLECEK / DOĞRULANAMAYAN KAYNAKLAR
---------------------------------------------------------------------------
- Kosaka & Ikeguchi 2024 (D2) tam metni: girdi vektör mü raster mı?
- YÖK Ulusal Tez Merkezi: "fraktal boyut + motif/tekstil/mimari" taraması
  bu oturumda tamamlanamadı (erişim kısıtı). YAPILACAK.
- DergiPark / TR Dizin taraması: YAPILACAK.
- OpenAlex günlük kota doldu, Semantic Scholar 429 verdi — doğrulama
  Crossref üzerinden yapıldı. Bu iki kaynak tekrar denenmeli.
- Patent taraması (Espacenet/Google Patents): HENÜZ YAPILMADI.
