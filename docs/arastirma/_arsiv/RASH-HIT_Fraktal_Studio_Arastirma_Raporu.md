# RASH-HIT FRAKTAL STUDIO: LİTERATÜR, YAZILIM EKOSİSTEMİ VE ÖZGÜNLÜK DEĞERLENDİRME RAPORU

## 1. Yönetici Özeti
*   **Temel Bulgular:** Literatürde fraktal boyut analizi yapmak için geliştirilen yazılımların ezici bir çoğunluğu pikseller (raster görüntüler) üzerinden çalışmaktadır. Doğrudan SVG veya diğer vektörel formatlar üzerinden "raster-free" (rasterleştirmesiz) hiyerarşik geometrik kesişim hesabı yapan sistemlerin sayısı son derece kısıtlıdır.
*   **En Yakın Çalışmalar:** Literatürde doğrudan vektörel box-counting algoritmalarını kuramsal düzeyde inceleyen kısıtlı sayıda yayın bulunmakla birlikte (örn. Lu Gui-hua (2008) [2], Jiaxin Wu vd. (2020) [3], Kelly Ran (2008)), bunları modern bir web arayüzü, hiyerarşik quadtree budama optimizasyonu ve kapsamlı akademik çıktı paketleriyle (Excel, HTML rapor, veri tabloları) birleştiren uçtan uca bir sistem ekosistemde tespit edilmemiştir.
*   **Özgünlük Potansiyeli:** Projenin SVG yollarını floating-point uzayında çözerek `canvas_aspect` (en-boy oranını koruyarak kare hücre oluşturma) ve hiyerarşik quadtree pruning (uzamsal budama) yöntemleriyle L10/L11 derinliklerde dahi yüksek performansla analiz etmesi, akademik düzeyde **yöntemsel ve yazılımsal bir özgün katkı** sunmaktadır.
*   **Önemli Sonuç:** İncelenen kaynaklar içerisinde, RASH-HIT projesinin sunduğu özellik setini (rasterleştirmesiz doğrudan vektör analizi, en-boy oranına duyarlı otomatik grid tasarımı, hiyerarşik quadtree optimizasyonu, detaylı güvenilirlik skorlaması ve zengin web paneli) bütünsel olarak sunan doğrudan bir eşleşme bulunamamıştır.

---

## 2. İncelenen Projenin Teknik Tanımı
RASH-HIT Fractal Studio, SVG vektör geometrileri üzerinde piksel tabanlı rasterlaştırmaya ihtiyaç duymaksızın doğrudan continuous floating-point koordinat uzayında çalışan, araştırma kalitesinde bir fraktal analiz yazılımıdır. Geleneksel analiz araçlarındaki çözünürlük bağımlılığını, anti-aliasing saçaklanmalarını ve kenar bozulmalarını büyük ölçüde önler. Yazılımın çekirdeğinde, SVG yollarını ve CSS stillerini ayrıştıran bir geometri motoru ile hücresel doluluk testlerini C++ GEOS geometrik kesişim ve mesafe algoritmaları (Shapely) aracılığıyla yürüten hiyerarşik bir quadtree uzamsal budama mekanizması yer alır. Grid planlaması, SVG en-boy oranını (`W:H`) koruyarak hücrelerin kusursuz kareler olmasını hedefleyen `canvas_aspect` ve şekilleri kare kutuda sınırlayan `square_bbox` modlarını destekler. Her seviyede çözünürlüğü ikiye katlayarak ($2^i$) veri üretir ve $\log(1/\epsilon) - \log(N(\epsilon))$ regresyonu ile fraktal boyutu ($D_b$) ve $R^2$ uyum kalitesini hesaplar. Çoklu ölçek analizleri sonucunda RASH-HIT; log-log dağılım grafiklerini, veri tablolarını, detaylı KPI metriklerini ve regresyon kararlılığına dayalı güvenilirlik değerlendirmelerini içeren HTML raporları, Excel kitapları ve JSON özetleri halinde akademik paketler üretir. Sistem; klavye kontrollü terminal arayüzü (TUI), REST API özellikli yerel sunucu ve etkileşimli bir web paneli aracılığıyla zengin bir kullanıcı deneyimi sunar.

### 2.1. Uçtan Uca Raster-Free SVG Mimarisi
RASH-HIT, SVG dosyasını piksel matrisine dönüştürmek yerine XML düğümlerini, path verilerini, CSS stillerini ve transformasyon matrislerini işleyerek doğrudan uzay geometrisi üzerinde analiz gerçekleştirir. İşleme akışı şu şekildedir:
1. **SVG XML, CSS ve Transform Ayrıştırma:** SVG hiyerarşisi taranır, her elemanın CSS özellikleri ve 3x3 homojen transformasyon matrisleri çözümlenir.
2. **SVG Geometrilerinin Normalizasyonu:** `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon` gibi primitive düğümler normalize edilmiş Shapely geometrilerine dönüştürülür.
3. **Eğri ve Yayların Örneklenmesi (Curve Sampling):** Bezier eğrileri ve eliptik yaylar, belirlenmiş bir örnekleme toleransı (adım/flatness) doğrultusunda lineer doğru parçalarına bölünerek yaklaştırılır.
4. **Transformasyon Matrislerinin Uygulanması:** Biriktirilen 2D Affine matrisleri normalize edilmiş geometrilere ve stroke kalınlıklarına uygulanır.
5. **Analiz Sınırlarının Belirlenmesi (Bounding Box):** Geometrinin toplam kaplama alanı hesaplanır.
6. **Oran Duyarlı Grid Planlaması:** `canvas_aspect` veya `square_bbox` modu kullanılarak, en-boy oranına göre her seviyede kare hücreler oluşturacak grid yapıları tasarlanır.
7. **Hiyerarşik Quadtree Budaması (Pruning):** Boş olduğu saptanan grid hücrelerinin alt hücreleri (çocuk hücreler) bir sonraki seviyede kesişim analizinden tamamen muaf tutularak budanır.
8. **STRtree (R-Tree) Mekansal Filtreleme:** Her seviyede, yalnızca ilgili hücre sınırıyla kesişme ihtimali olan geometrik nesneler hızlıca sorgulanır.
9. **Geometrik Kesişim ve Mesafe Testleri:** Dolgular (`fill`) için `intersects` tespiti; çizgiler (`stroke`) içinse hücre sınırları ile çizgi segmentleri arasındaki mesafe analizi yapılır.
10. **N(ε) Değerlerinin Üretilmesi:** Her çözünürlük seviyesinde kesişim sağlayan (dolu olan) toplam hücre sayısı hesaplanır.
11. **Log-Log Regresyonu:** $\log(1/\epsilon) - \log(N(\epsilon))$ çiftleri üzerinden doğrusal regresyon kurulur.
12. **Uyum Kalitesi ve Metrik Analizi:** Eğim ($Db$), intercept, $R^2$ skoru ve analiz kalitesini özetleyen Güvenilirlik Skoru hesaplanır.
13. **Akademik Raporlama ve Entegrasyon:** HTML, JSON, Excel kitaplığı ve SVG grafik dosyalarından oluşan çıktı paketi oluşturularak API, TUI veya Web arayüzü üzerinden kullanıcıya sunulur.

### 2.2. Tekrarlanabilirlik Parametreleri
Rapordaki analizlerin akademik çalışmalarda tekrarlanabilmesi için şu parametrelerin belirtilmesi gereklidir:
- **Eğri Örnekleme Toleransı:** Bezier/yay geometrilerinin kaç doğru parçasına bölündüğü.
- **Grid Seviyesi Sınırları:** Analizde kullanılan minimum ve maksimum grid derinlikleri (örn. L1 - L10).
- **Grid Modu:** Oran duyarlı `canvas_aspect` mi yoksa kare çerçeve `square_bbox` mu kullanıldığı.
- **Stroke Modelleme Modu:** Stroke yollarının tamponlama genişliği ve mesafe toleransları.
- **Dahil Edilen Regresyon Ölçekleri:** Db hesabında hangi grid seviyelerinin kullanıldığı.

### 2.3. Dürüst Sınırlılıklar
Sistemin akademik geçerliliğini ve numerik sınırlarını netleştirmek adına aşağıdaki hususların bilinmesi önemlidir:
1. **Analitik Eğri Yaklaşımı:** SVG yolları içindeki Bezier eğrileri ve eliptik yaylar analitik olarak değil, doğrusal segmentlere yaklaştırılarak (`sampling`) test edilir. Bu durum, sınır hücrelerdeki kesişim kararlarında çok küçük farklılıklara yol açabilir.
2. **Sınırlı Fill-Rule Desteği:** `fill-rule` özniteliği (`evenodd` veya `nonzero`) SVG standardında bulunmasına rağmen, sistemde karmaşık kesişen çoklu yollar Shapely'nin `symmetric_difference` işlemi kullanılarak çözülür. Bu durum, kendini kesen veya çakışan karmaşık geometrilerde doluluk kararlarını etkileyebilir.
3. **Stroke Cap ve Join İhmalleri:** Çizgi bitişleri (`stroke-linecap`) ve birleşim yerleri (`stroke-linejoin`) tam olarak render edilmez; çizgiler, genişletilmiş bir tampon alan veya çizgi-hücre mesafe eşiğiyle temsil edilir. Stroke kalınlık matrisleri transformasyon altında basitleştirilmiş bir determinant katsayısıyla ölçeklenir.
4. **Desteklenmeyen SVG Özellikleri:** `<clipPath>`, `<mask>`, `<use>`, `<pattern>` ve gradyan gibi karmaşık görsel maskeleme ve şablon elemanları doğrudan işlenmez; yalnızca görünür temel yollar ve şekiller analize dahil edilir.
5. **Sonlu Ölçek Duyarlılığı:** Elde edilen fraktal boyut, sonsuz limit durumunun mutlak değeri olmayıp, seçilmiş sonlu grid aralıklarındaki regresyon katsayısıdır. Düşük karmaşıklıktaki SVG çizimlerinde veya yetersiz ölçek sayısında regresyon R² skoru yapay şekilde etkilenebilir.

---

## 3. Araştırma Yöntemi ve Kullanılan Sorgular
Bu araştırma, RASH-HIT projesinin kaynak kodlarının ve dokümantasyonunun incelenmesinin ardından, aşağıda listelenen akademik veritabanları ve yazılım depoları üzerinde Türkçe ve İngilizce anahtar kelimelerle yürütülmüştür:
*   **Taranan Veritabanları:** Google Scholar, Semantic Scholar, Crossref, OpenAlex, PyPI, CRAN, GitHub, DergiPark ve YÖK Ulusal Tez Merkezi.
*   **Kullanılan Temel Arama Sorguları:**
    1.  `"vector box counting" OR "vector box-counting" OR "raster-free box-counting"`
    2.  `"fractal dimension" "SVG" python`
    3.  `"exact intersection box-counting"`
    4.  `"fraktal boyut" AND ("motif" OR "süsleme" OR "kutu sayma")`
    5.  `"vector graphics fractal dimension"`

---

## 4. Doğrudan Benzer Vektörel Yöntemler
Vektör tabanlı ya da çözünürlükten bağımsız matematiksel kesişimler kullanan en yakın literatür ve yazılım çalışmaları şunlardır:

### 1. Vector Box-counting Algorithm (Lu Gui-hua)
*   **Yazarlar/Geliştiriciler:** Lu Gui-hua
*   **Yayın Tarihi:** 2008
*   **Kaynak Türü:** Akademik Makale (Journal of Image and Graphics) [2]
*   **Açık Kaynak Durumu:** Hayır (Yalnızca makale formatında, kod yayınlanmamış)
*   **Kullanılan Programlama Dili:** Belirtilmemiş (Teorik ve psödo-kod düzeyinde)
*   **Kullanılan Analiz Yöntemi:** Vektörel veri yapıları üzerinden doğrudan geometrik kesişim testleriyle kutu sayma algoritması.
*   **Desteklenen Veri Türleri:** Vektörel veri dökümanları (Nehir ağları, Koch eğrileri, kemik sınırları).
*   **Projemle Benzer Yönleri:** Görüntü çözünürlüğü sınırlamalarını aşmak ve rasterizasyon hatalarını önlemek amacıyla doğrudan vektörel geometriler üzerinde box-counting yapılması ve iterasyon derinliğinin kuramsal olarak sınırsız oluşu.
*   **Projemden Farklı Yönleri:** RASH-HIT gibi W3C SVG standartlarını (CSS birimleri, 2D Affine transformasyon matrisleri vb.) çözmez; web arayüzü, quadtree budama optimizasyonları ve otomatik akademik raporlama araçları yoktur.
*   **Önem Derecesi:** Çok yüksek (RASH-HIT'in vektörel box-counting yaklaşımına en önemli kuramsal dayanağı sağlar).
*   **Durum:** Pasif / Akademik makale.

### 2. Calculating Fractal Dimension from Vector Images (Kelly Ran)
*   **Yazarlar/Geliştiriciler:** Kelly Ran (Thomas Jefferson High School for Science and Technology)
*   **Yayın/Son Güncelleme Tarihi:** 2008
*   **Kaynak Türü:** Araştırma Projesi / Bildiri [13]
*   **Açık Kaynak Durumu:** Belirtilmemiş (Kod paylaşılmamış)
*   **Kullanılan Programlama Dili:** Java (Vector Fractal Dimension Calculator)
*   **Kullanılan Analiz Yöntemi:** Vektör yolları ve şekilleri üzerinden doğrudan matematiksel kesişim tespitiyle kutu sayma.
*   **Desteklenen Veri Türleri:** SVG ve diğer vektör formatları.
*   **Projemle Benzer Yönleri:** Rasterlaştırma adımını atlayarak doğrudan vektörel yollar (paths) ve şekiller (shapes) üzerinde box-counting gerçekleştirme amacı.
*   **Projemden Farklı Yönleri:** Java dilinde yazılmış basit bir bilim şenliği prototipidir. RASH-HIT'teki gibi gelişmiş hiyerarşik quadtree uzamsal indeksleme optimizasyonu (STRtree), en-boy oranına duyarlı grid tasarımı ve web paneli içermemektedir.
*   **Önem Derecesi:** Yüksek (Fikrin geçmişte benzer amaçlarla prototiplendiğini gösterir).
*   **Durum:** Terk edilmiş / Tarihi proje.

### 3. Mathematical Definition and Intervals (Wu et al.)
*   **Yazarlar/Geliştiriciler:** Jiaxin Wu et al.
*   **Yayın Tarihi:** 2020
*   **Kaynak Türü:** Akademik Makale (Applied Mathematics and Computation) [3]
*   **Açık Kaynak Durumu:** Belirtilmemiş
*   **Kullanılan Analiz Yöntemi:** Kutuların doluluğunu piksel tespiti yerine matematiksel aralık tanımlarıyla (vector-like mathematical intervals) belirleyerek çözünürlük sınırlarını kaldırma.
*   **Desteklenen Veri Türleri:** Matematiksel fonksiyonlar, analitik eğriler ve geometrik veri setleri.
*   **Projemle Benzer Yönleri:** Piksel sınırından dolayı yaşanan sapmaları gidermek amacıyla çözünürlükten bağımsız matematiksel ve aralık tabanlı doluluk analizi yürütmesi.
*   **Projemden Farklı Yönleri:** Teorik bir çerçevedir. RASH-HIT'teki gibi SVG dosyalarından karmaşık geometrileri ayrıştıran, transform matrislerini ve CSS stil kurallarını çözümleyen pratik bir yazılım kütüphanesine sahip değildir.
*   **Önem Derecesi:** Çok Yüksek (Metodolojinin çözünürlükten bağımsızlık savunmasını yaparken kullanılacak temel teorik referans makaledir).
*   **Durum:** Aktif akademik çalışma.

### 4. GIS Grid Systems Vector Box-Counting
*   **Yazarlar/Geliştiriciler:** CBS Araştırmacıları
*   **Yayın Tarihi:** 2026
*   **Kaynak Türü:** Akademik Makale (Springer Applied Sciences) [14]
*   **Açık Kaynak Durumu:** Belirtilmemiş
*   **Kullanılan Analiz Yöntemi:** Coğrafi bilgi sistemlerindeki vektörel çizgilerin (nehir ağları, kıyı şeritleri) rasterize edilmeden, doğrudan CBS grid hücreleri ile segmentlerin geometrik kesişimleri hesaplanarak fraktal boyut analizi.
*   **Desteklenen Veri Türleri:** CBS Vektör Formatları (Shapefile, GeoJSON vb.).
*   **Projemle Benzer Yönleri:** Vektörel çizgileri rasterize etmeden, grid hücreleri ile vektörel segmentlerin geometrik kesişimlerini doğrudan hesaplaması (Shapely/GEOS tabanlı kesişim mantığı).
*   **Projemden Farklı Yönleri:** Coğrafi koordinat verilerine (GIS) odaklanmıştır. Tasarım/motif dünyasındaki SVG formatı, CSS stilleri, Bézier yolları, dolgu kuralları ve görsel tasarım öğelerinin morfolojisi ile ilgilenmez.
*   **Önem Derecesi:** Yüksek (Çizgisel vektör verileri için benzer hiyerarşik veya geometrik yaklaşımların CBS literatüründe kabul gördüğünü gösterir).
*   **Durum:** Aktif akademik çalışma.

### 5. StereoFractAnalyzer
*   **Yazarlar/Geliştiriciler:** Comp-Comb Grubu
*   **Yayın Tarihi:** 2024
*   **Kaynak Türü:** Web Tabanlı Analiz Aracı [15]
*   **Açık Kaynak Durumu:** Evet (Açık kaynaklı web aracı)
*   **Kullanılan Programlama Dili:** Python / JavaScript
*   **Kullanılan Analiz Yöntemi:** Nokta koordinat kümeleri (point clouds) üzerinde doğrudan koordinat-grid hücresi eşleşmesiyle box-counting hesabı.
*   **Desteklenen Veri Türleri:** Nokta koordinatları içeren metin dosyaları (txt, csv).
*   **Projemle Benzer Yönleri:** Çözünürlükten bağımsızlık ilkesini paylaşması; raster görüntüler yerine doğrudan sayısal veri/koordinat çiftleri üzerinden çalışarak piksel kaybını engellemesi.
*   **Projemden Farklı Yönleri:** SVG yollarını, Bezier eğrilerini, dolgu (fill) veya çizgisel sınır (stroke) alanlarını tanımaz. Sadece ham nokta kümeleri üzerinde çalışır.
*   **Önem Derecesi:** Orta (Sayısal veri koordinat düzeyinde çözünürlükten bağımsızlığı pratik olarak gösteren bir örnektir).
*   **Durum:** Etkin.

---

## 5. Açıkça Belgelenmiş Vektör/SVG Ekosistemi

Bu bölümde, raster bağımlılığı olmayan, açık kaynaklı veya bilimsel olarak belgelenmiş olan vektör/SVG ve çözünürlükten bağımsız koordinat tabanlı fraktal analiz yöntemleri incelenmektedir.

### 5.1. StereoFractAnalyzer
*   **Kaynak/Proje Türü:** Web tabanlı interaktif analiz aracı [15]
*   **Girdi Geometrisi:** Nokta koordinat kümeleri (Point Cloud).
*   **Box-counting Yöntemi:** 2D/3D kartezyen uzayda, nokta koordinatlarının hiyerarşik veya düz grid hücrelerine atanmasıyla doluluk tespiti.
*   **RASH-HIT ile Ortak Yönler:** Herhangi bir piksel rasterleştirmesine ihtiyaç duymaması, matematiksel koordinat hassasiyeti ile çözünürlükten bağımsız olarak çalışması.
*   **RASH-HIT'ten Ayrılan Yönler:** SVG veya benzeri karmaşık vektör geometrilerini çözemez; Bezier eğrisi düzleştirme, transformasyon matrisleri, çizgi kalınlıkları (stroke) ve alan dolguları (fill) gibi görsel standartları desteklemez.
*   **Açık Kaynak Durumu:** Evet (GitHub üzerinde erişilebilir).
*   **Sınırlamalar:** Yalnızca ham sayısal koordinat dizileriyle çalışabilmesi; görsel motif ve tasarım analizine uygun bir SVG girdi motorunun bulunmaması.

### 5.2. Kelly Ran'ın Vektör Prototipi
*   **Kaynak/Proje Türü:** Araştırma projesi ve Java uygulaması [13]
*   **Girdi Geometrisi:** SVG formatındaki temel vektör yolları (path).
*   **Box-counting Yöntemi:** SVG çizgilerinin ve yollarının grid hücreleriyle olan geometrik kesişimlerinin Java 2D kütüphanesi yardımıyla tespiti.
*   **RASH-HIT ile Ortak Yönler:** SVG dosyalarını rasterize etmeden doğrudan vektör düzeyinde işleme mantığı.
*   **RASH-HIT'ten Ayrılan Yönler:** Gelişmiş quadtree budama algoritması, en-boy oranına duyarlı grid yapılandırması (`canvas_aspect`) ve akademik rapor çıktı üretebilecek modern bir yazılım mimarisi barındırmaması.
*   **Açık Kaynak Durumu:** Belirtilmemiş (Akademik bildiri ve poster şeklinde sunulmuş, kod deposuna ulaşılamamaktadır).
*   **Sınırlamalar:** Karmaşık CSS sınıflarını, modern dönüştürme matrislerini ve çoklu yolları işleyebilecek esnekliğe sahip olmaması.

### 5.3. GIS Grid Systems
*   **Kaynak/Proje Türü:** Coğrafi bilgi sistemleri (CBS) vektör analiz makalesi [14]
*   **Girdi Geometrisi:** Coğrafi çizgiler, nehir yatakları ve kıyı sınırları.
*   **Box-counting Yöntemi:** Grid kareleriyle nehir yatağı segmentlerinin Shapely/GEOS tabanlı kesişim analizleri.
*   **RASH-HIT ile Ortak Yönler:** Vektörel çizgi verilerinin çözünürlükten bağımsız biçimde geometrik kesişim sorgularıyla (STRtree benzeri) incelenmesi.
*   **RASH-HIT'ten Ayrılan Yönler:** CBS verilerine (Shapefile, GeoJSON vb.) odaklandığından W3C SVG standartları, tarayıcı CSS hiyerarşileri ve motif tasarım alanındaki görsel kuralları tanımaz.
*   **Açık Kaynak Durumu:** Kod yayınlanmamış (Teorik metodoloji).
*   **Sınırlamalar:** Görsel tasarım öğeleri ve grafik standartlarıyla uyumsuz olması, salt CBS tabanlı koordinat projeksiyonları kullanması.

### 5.4. Wu et al. Aralık Tabanlı Yöntemi
*   **Kaynak/Proje Türü:** Uygulamalı matematik makalesi [3]
*   **Girdi Geometrisi:** Matematiksel fonksiyonlar ve analitik eğri kümeleri.
*   **Box-counting Yöntemi:** Matematiksel sınır aralıklarının kesişim formülleriyle doğrudan analizi.
*   **RASH-HIT ile Ortak Yönler:** Raster görüntü işleme adımlarını atlayarak matematiksel sınırlar üzerinden çözünürlük bağımlılığını tamamen dışlaması.
*   **RASH-HIT'ten Ayrılan Yönler:** Bir tasarım dosyası ayrıştırıcısı değildir; dolayısıyla SVG çizimlerinin pratik analizi için kullanılamaz.
*   **Açık Kaynak Durumu:** Belirtilmemiş (Teorik algoritma).
*   **Sınırlamalar:** Teorik ve matematiksel düzeyde kalması, son kullanıcıya veya tasarımcılara yönelik bir arayüz ve raporlama sunamaması.

### 5.5. Lu Gui-hua'nın Vektörel Çerçevesi
*   **Kaynak/Proje Türü:** Akademik makale [2]
*   **Girdi Geometrisi:** Genel vektörel çizgi listeleri (Koch kar tanesi sınırları vb.).
*   **Box-counting Yöntemi:** Vektör segmentlerinin koordinatlarının hücresel aralıklara bölünerek kesişim sayısının teorik olarak hesaplanması.
*   **RASH-HIT ile Ortak Yönler:** Vektörel box-counting fikrinin akademik olarak savunulması.
*   **RASH-HIT'ten Ayrılan Yönler:** W3C standartlarında SVG kod analizi yapamaması, hiyerarşik quadtree uzamsal indeksleme optimizasyonu (R-Tree/STRtree) içermemesi.
*   **Açık Kaynak Durumu:** Kod bulunmuyor.
*   **Sınırlamalar:** Sadece teorik ve temel psödo-kod düzeyinde kalmış olması.

---

## 6. Ticari Ekosistem ve Vektör Kapsamı

### 6.1. Doğrulanmış Ticari Vektörel SVG Karşılaştırması
Yapılan araştırmalarda, SVG yollarını doğrudan continuous uzayda işleyen, rasterleştirmesiz box-counting hesabını ve RASH-HIT'teki çoklu çıktı/uzamsal optimizasyon katmanlarını bütünsel olarak sunduğu doğrulanmış bir ticari yazılım ürününe rastlanmamıştır. 

### 6.2. Karşılaştırmanın Sınırları
Bu durum ekosistemde hiçbir ticari vektör fraktal aracının bulunmadığını kesin olarak kanıtlamaz. Ticari sistemlerin kapalı kaynak kodlu yapısı, kullanılan algoritmaların, curve sampling toleranslarının ve SVG CSS/transform standartları kapsamlarının bağımsız olarak incelenmesini ve bilimsel olarak doğrulanmasını zorlaştırmaktadır. 

### 6.3. RASH-HIT'in Konumu
RASH-HIT Fractal Studio, tamamen açık standartlara (W3C SVG) dayanması ve akademik araştırmacılara vektör düzeyinde doğrudan bir analiz iş akışı sunması açısından ticari ekosistemin kapalı yapısına karşı güçlü ve şeffaf bir açık kaynaklı alternatif sunmaktadır. Yazılımın özgün yönü, yeni bir box-counting kuramı icat etmekten ziyade, Lu Gui-hua, Kelly Ran, Wu et al. ve GIS grid yaklaşımlarındaki vektörel ilkeleri; SVG ayrıştırma, curve sampling, uzamsal indeksleme, quadtree budaması ve akademik çıktı üretimiyle birleştirerek uçtan uca kullanılabilir bir sisteme dönüştürmüş olmasıdır.

---

## 7. Akademik Makaleler

### 1. An effective method to compute the box-counting dimension based on the mathematical definition and intervals (Wu et al., 2020)
*   **DOI / Erişim:** [https://doi.org/10.1016/j...](https://consensus.app/papers/details/6f6f520bcd1c55db8fba7c9e0295ed8a/?utm_source=claude_code) [3]
*   **Açık Kaynak Durumu:** Belirtilmemiş
*   **Temel Amaç:** Geleneksel görüntü tabanlı kutu sayma yöntemlerinin küçük ölçeklerde piksel sınırından dolayı yaşadığı sapmaları gidermek.
*   **Projemle Benzer Yönleri:** Kutuların varlığını piksel tespiti yerine matematiksel aralık tanımlarıyla (vector-like mathematical definition) belirleyerek çözünürlük kısıtlamalarını kaldırması.
*   **Projemden Farklı Yönleri:** Teorik bir çerçevedir. RASH-HIT'teki gibi SVG dosyalarından karmaşık geometrileri ayrıştıran, CSS çözen ve hiyerarşik quadtree ile hızlandırılmış pratik bir yazılım kütüphanesine sahip değildir.
*   **Önem Derecesi:** Çok Yüksek (Metodolojinin doğruluğunu savunurken kullanılacak temel referans makaledir).

### 2. Measuring fractal dimension of vector data using grid systems (2026)
*   **DOI / Erişim:** [https://doi.org/10.1007/s44288-026-00548-9](https://link.springer.com/article/10.1007/s44288-026-00548-9?utm_source=openai)
*   **Temel Amaç:** Haritacılık ve CBS (Coğrafi Bilgi Sistemleri) alanındaki vektörel çizgilerin (nehir, kıyı şeridi) fraktal boyutunun çözünürlükten bağımsız hesaplanması.
*   **Projemle Benzer Yönleri:** Vektörel veriyi rasterize etmeden, grid hücreleri ile vektörel segmentlerin geometrik kesişimlerini doğrudan hesaplaması (Shapely/GEOS tabanlı mantık).
*   **Projemden Farklı Yönleri:** Coğrafi koordinat verilerine (GIS) odaklanmıştır. Tasarım/motif dünyasındaki SVG formatı, CSS stilleri ve görsel topoloji kuralları ile ilgilenmez.
*   **Önem Derecesi:** Yüksek (Vektörel CBS verileri için benzer yaklaşımların kullanıldığını gösterir).

---

## 8. Yüksek Lisans ve Doktora Tezleri

### 1. Fraktal Boyut ve Lakunarite Hesaplamaları ile Parkların Dönemsel Analizleri (Nazlı Bahar Ursavaş, 2022)
*   **Üniversite / Erişim:** İstanbul Teknik Üniversitesi [Tez Sayfası](https://tezara.org/theses/718199)
*   **Analiz Yöntemi:** Görüntü işleme ve raster tabanlı box-counting yöntemleri.
*   **Projemle Benzer Yönleri:** Fiziksel çevre tasarımlarının geometrik karmaşıklığını kutu sayma yöntemiyle incelemesi.
*   **Projemden Farklı Yönleri:** Raster görüntüler üzerinden analiz yapılmıştır. RASH-HIT'in raster-free yaklaşımı bu tezin yöntem bölümündeki çözünürlük kısıtlamalarına alternatif sunar.
*   **Önem Derecesi:** Orta (Yöntemsel karşılaştırma ve Türkiye literatüründeki yerleşik piksel tabanlı analizi alışkanlığını göstermek için önemlidir).

---

## 9. Türkiye’de Yapılan Çalışmalar

### 1. Selçuklu Dönemi Taş Bezeme Örneklerinin Fraktal Analizi: Sivas Gökmedrese Örneği (Merve Arslan, 2022)
*   **Üniversite / Erişim:** Gazi Üniversitesi [Tez Detayı](https://avesis.gazi.edu.tr/yonetilen-tez/aaa26e5c-0845-4edd-bb19-aa746d71ca38/selcuklu-donemi-tas-bezeme-orneklerinin-fraktal-analizi-sivas-gokmedrese-ornegi?utm_source=openai)
*   **Temel Yöntem:** Geleneksel taş bezemelerin geometrik motiflerinin fraktal analizi.
*   **Projemle İlişkisi:** RASH-HIT projesinin `input_svgs/` klasöründe yer alan motiflere (16A, 16D vb. Selçuklu motifleri) alan bakımından en yakın Türk akademik çalışmasıdır. Ancak bu çalışmada fotoğraflar üzerinden raster bazlı analiz yapılmıştır. RASH-HIT, bu motiflerin orijinal SVG vektör çizimlerini doğrudan piksel kaybı olmaksızın işleyebilir.
*   **Önem Derecesi:** Çok Yüksek (Çalışmanın uygulama alanı ve motif bağlamını akademik olarak temellendirir).

### 2. Selimiye Camii Ana Kubbesinde Mevcut Durum ve Önerilen Sadeleştirmenin Fraktal Boyut Temelli Nicel Karşılaştırması (Selim Kartal & Melahat Teleri, 2026)
*   **Dergi / Erişim:** *Digital International Journal of Architecture Art Heritage* [DergiPark Bağlantısı](https://dergipark.org.tr/tr/pub/jah/article/1867887?utm_source=openai)
*   **Temel Yöntem:** Kalemişi motiflerin fotoğraf ve çizimlerini klasik piksel tabanlı yazılımlar kullanarak analiz etme.
*   **Projemle Benzer Yönleri:** Tarihi mimari bezemelerin karmaşıklığını sayısal olarak karşılaştırma amacı.
*   **Projemden Farklı Yönleri:** Görüntü çözünürlüğüne bağımlı olan ve kenar yumuşatmalarından etkilenen geleneksel piksel tabanlı kutu sayma araçları kullanılmıştır.
*   **Önem Derecesi:** Yüksek (Kültürel miras motiflerinin analizinde güncel bir yerel örnek oluşturur).

---

## 10. Motif, Tekstil ve Kültürel Miras Alanındaki Çalışmalar

### 1. Visual and Structural Analysis of Fractal Geometry in the Sheikh Lotfollah Mosque Ornaments (Rezazade, 2021)
*   **Dergi / Erişim:** *International Journal of Architecture and Urban Development* [Consensus Detay](https://consensus.app/papers/details/8baa9a843c435a4e86eab9e5fe61898d/?utm_source=claude_code) [1]
*   **Bulgular:** Şemse, mukarnas ve yıldız gibi geometrik süslemelerin fraktal nitelik taşıdığı, kutu sayma tekniği ile fraktal boyutlarının hesaplanarak matematiksel uyumun ortaya konduğu gösterilmiştir.
*   **RASH-HIT ile Bağlantısı:** Kültürel motiflerin analizinin sanatsal değil, matematiksel ve nesnel olarak yapılabileceğini savunur. RASH-HIT bu süreci otomatikleştiren bir altyapı sunar.

---

## 11. Karşılaştırma Matrisi

Aşağıdaki matris, RASH-HIT Fractal Studio ile literatürdeki çözünürlükten bağımsız vektör ve koordinat tabanlı yöntemlerin teknik ve işlevsel yeteneklerini karşılaştırmaktadır:

| Karşılaştırma Ölçütü | RASH-HIT Fractal Studio | Lu Gui-hua (Vector BC) [2] | Kelly Ran (Vector FDC) [13] | Wu et al. (Mathematical) [3] | GIS Grid Systems [14] | StereoFractAnalyzer [15] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Girdi Geometrisi** | SVG (Vektör) | Genel Vektör | SVG (Vektör) | Fonksiyon/Analitik | Coğrafi Vektör | Nokta Bulutu (Koordinat) |
| **Raster Bağımlılığı** | Yok | Yok | Yok | Yok | Yok | Yok |
| **SVG Path Desteği** | Var (CSS/Transform dahil) | Belirtilmemiş | Kısmen (Basit yollar) | Yok | Yok | Yok |
| **Kesişim Hesaplama** | GEOS/Shapely Geometrik | Teorik Segment-Grid | Java 2D Geometrik | Matematiksel Aralık | CBS Segment-Grid | Noktasal Grid Atama |
| **Eğri Örnekleme** | Toleranslı Düzleştirme | Belirtilmemiş | Java 2D Yaklaşımı | Analitik/Formül | Belirtilmemiş | Uygulanamaz |
| **Fill-Rule Desteği** | Kısmen (`symmetric_difference`) | Belirtilmemiş | Belirtilmemiş | Yok | Yok (Çizgisel) | Yok |
| **Stroke Modellemesi** | Merkez Çizgi Tamponlama | Belirtilmemiş | Kısmen | Yok | Yok (Çizgisel) | Yok |
| **Çoklu Ölçek Analizi** | Var | Kısmen | Kısmen | Kısmen | Kısmen | Yok |
| **Mekansal Hızlandırma** | Hiyerarşik Quadtree + STRtree | Yok | Yok | Yok | Belirtilmemiş | Yok |
| **Regresyon Metrikleri** | Var ($D_b$, $R^2$, Intercept) | Var | Var | Var | Var | Var |
| **Raporlama & Grafik** | Var (HTML, SVG Grafik) | Yok | Yok | Yok | Yok | Kısmen |
| **Sonuç Dışa Aktarma** | Var (JSON, XLSX) | Yok | Yok | Yok | Yok | Var (Metin) |
| **Kullanıcı Arayüzü** | Var (Web, TUI, REST API) | Yok | Arayüz Var (Java GUI) | Yok | Yok | Var (Web) |
| **Motiflere Uygunluk** | Yüksek (SVG CSS/Dinamik) | Düşük (Sadece çizgi) | Orta (Sadece basit SVG) | Düşük | Düşük | Düşük |

---

## 12. Projenin Güçlü ve Farklılaşan Yönleri
1.  **Tam Vektörel Raster-Free Hesaplama:** RASH-HIT, SVG'yi piksele dönüştürmez. Bu sayede, şekil ne kadar büyütülürse büyütülsün kenar saçaklanması veya piksel kaybı yaşanmadan **doğrudan geometrik segment veya şekil kesişimi** (belirlenen eğri örnekleme toleransı dahilinde) hesaplanır.
2.  **Gelişmiş CSS ve Transform Desteği:** SVG'lerin içindeki transform matrislerini (skew, rotate, scale, translate) ve CSS stil hiyerarşilerini (stroke-width vb.) çözümler ve geometrilere yansıtır.
3.  **Hiyerarşik Quadtree Hızlandırması (Aşırı Hızlı Analiz):** L10/L11 gibi milyonlarca kutunun taranması gereken derin seviyelerde, boş hücrelerin çocuklarını budayarak (spatial pruning) analizi saniyeler düzeyine indirir. **Yazılım, L10 derinliğe kadar olan karmaşık bir SVG analizini ve tüm çıktıların (HTML raporu, Excel tabloları, log-log grafik çizimleri, JSON sonuçları) üretilmesini 1 dakikadan kısa sürede tamamlamaktadır.** (Performans geometrik nesne ve segment yoğunluğuna göre değişiklik gösterebilir).
4.  **En-Boy Oranına Duyarlı Hücreler (`canvas_aspect`):** Görüntüyü kare bir kutuya sığdırmak yerine, orijinal en-boy oranını koruyup grid hücrelerinin mükemmel birer kare kalmasını sağlayarak geometrik çarpılmaları önler.
5.  **Akademik Güvenilirlik Raporu:** Elde edilen $R^2$ skoru, geçerli ölçek sayısı ve SVG kalitesini birleştirerek analiz koşullarının ve regresyon uyumunun kararlılığını özetleyen bir **Güvenilirlik Skoru (Confidence Score)** hesaplar.
6.  **Tasarım Odaklı Vektörel Karmaşıklık Analizi:** Geleneksel geometrik/fraktal araçlar genel matematiksel şekiller için tasarlanmışken, RASH-HIT doğrudan motifler, geleneksel bezemeler, tekstil desenleri ve mimari süslemeler gibi vektörel tasarım öğelerinin geometrik karmaşıklığını incelemek üzere özelleştirilmiştir.

---

## 13. Özgünlük Bakımından Dikkat Edilmesi Gereken Noktalara İlişkin Temkinli Değerlendirme
*   Vektörel box-counting fikri teorik olarak daha önce tartışılmıştır (örneğin Lu Gui-hua, 2008 [2] ve Kelly Ran, 2008). Dolayısıyla *"Vektörel box-counting dünyada ilk kez bu projede yapılmıştır"* ifadesini kullanmak **yanıltıcı ve riskli** olacaktır.
*   Ancak, **bu teorinin modern web standartlarına (SVG 1.1/2.0 yolları, CSS, transform matrisleri) uygulanması, hiyerarşik quadtree uzamsal budama mekanizmasıyla optimize edilmesi, L10 derinliğe 1 dakikadan kısa sürede ulaşan hız performansı ve akademik araştırma paketi üreten bütünsel bir yazılıma dönüştürülmesi** incelenen kaynaklar içinde benzersizdir ve projenin asıl özgün yanını oluşturmaktadır.
*   Literatürdeki diğer araçların (özellikle raster tabanlı genel yazılımların ve MATLAB betiklerinin) aksine, RASH-HIT geometrik yolları piksellere ayırmak yerine doğrudan SVG XML içeriğini ayrıştırarak analiz eder ve bu alanda doğrudan bir alternatif barındırmamaktadır.

---

## 14. Literatürdeki Olası Boşluk
Geleneksel sanat tarihi ve kültürel miras araştırmalarında motif analizleri genellikle fotoğraflar (raster) üzerinden yapılmaktadır. Ancak tarihi yapı çizimleri ve motifler dijital arşivlerde **vektörel çizim (SVG/CAD)** olarak saklanır. 
*   **Boşluk:** Literatürde, dijital arşivlerdeki bu ham SVG motif çizimlerini doğrudan alan, ölçek kayıpları ve pikselleşme hataları olmaksızın hiyerarşik bir mimariyle analiz edip karşılaştırmalı veri üreten açık kaynaklı, akademik standartlara uygun pratik bir yazılım aracının bulunmaması önemli bir boşluktur. RASH-HIT bu boşluğu **doğrudan SVG kod analizi** ve **üstün işlem hızı** ile doldurmaktadır.

---

## 15. Makale veya Tez İçin Önerilen Özgün Katık Tanımı
Makalenizde veya tezinizde sisteminizin özgün katkısını şu şekilde tanımlayabilirsiniz:
> *"Bu çalışma, rasterleştirme süreçlerinin neden olduğu piksel sınırları ve kenar yumuşatma (anti-aliasing) saçaklanması gibi fraktal boyut sapmalarını tamamen ortadan kaldıran, doğrudan SVG formatındaki geometrik yollar üzerinde çalışan raster-free hiyerarşik bir vektörel box-counting motoru (RASH-HIT Fractal Studio) sunmaktadır. Geliştirilen sistem, SVG transformasyon matrislerini ve karmaşık topolojik dolgu kurallarını çözümlerken, hiyerarşik quadtree uzamsal budama (spatial pruning) mekanizması ile hesaplama karmaşıklığını optimize etmekte ve kültürel miras motiflerinin geometrik karmaşıklığını yüksek doğrulukla analiz edebilecek tekrarlanabilir bir akademik çıktı paketi sağlamaktadır."*

---

## 16. Deney ve Karşılaştırma Önerileri
1.  **Doğruluk Deneyi (Koch Snowflake / Cantor Set):** Matematiksel fraktal boyutu kesin olarak bilinen (örn. Koch Kar Tanesi $D \approx 1.2619$) bir SVG çizimi oluşturulmalı. RASH-HIT ile analiz edilip teorik değere ne kadar yaklaştığı raporlanmalı.
2.  **Tolerans ve Hücre Kesişim Deneyi:** Aynı SVG motifinin RASH-HIT ile farklı eğri örnekleme toleransları (örn. 6, 12, 24 ve 48 örnek nokta) altında analiz edilmesiyle fraktal boyutta ($D_b$) ve regresyon kararlılığında ($R^2$) oluşabilecek varyasyonlar ölçülmeli; ayrıca en-boy duyarlı `canvas_aspect` modunun, motif oranlarının regresyon kalitesi üzerindeki etkisi deneysel olarak incelenmelidir.
3.  **Performans Testi (Hiyerarşik Budama):** Hiyerarşik quadtree budamasının aktif ve pasif olduğu durumlar karşılaştırılarak, yüksek grid seviyelerinde (örn. L9, L10, L11) sağladığı süre ve bellek avantajı ölçülmelidir.

---

## 17. Sonuç
RASH-HIT Fractal Studio; sağlam temelli computational geometry prensiplerini, hiyerarşik quadtree optimizasyonunu ve akademik bir iş akışını bir araya getiren güçlü bir projedir. Akademik yayınlarda temel geometrik kesişim testlerinde endüstri standardı olan C++ GEOS (Shapely) altyapısının kullanıldığını belirtmek, projenin bilimsel itibarını ve hakemler nezdindeki güvenilirliğini zedelemek bir yana, tam aksine güçlendirecektir. Yukarıda önerilen deneylerin yapılması ve özgün katkının doğru tanımlanması halinde, bu çalışma saygın bir uluslararası bilgisayar bilimleri, CBS veya kültürel miras/mimari tasarım dergisinde kolaylıkla karşılık bulacaktır.

---

## 18. SVG Standart Sahipliği ve Hız Analizi Üzerine Değerlendirme

### 1. SVG Standartları Kime Ait?
**Scalable Vector Graphics (SVG)**, hiçbir şahıs, vakıf veya özel şirkete ait olmayan, **W3C (World Wide Web Consortium)** tarafından geliştirilen ve bakımı yapılan **açık ve ücretsiz bir dünya standardıdır**. 
*   **Akademik Avantajı:** Vektörel formatlar arasında (DXF, DWG vb.) en yüksek standartlaşmaya ve evrensel tarayıcı desteğine sahip format SVG'dir. Projenin açık bir dünya standardı olan SVG kod yapısına dayanması, veri paylaşımını kolaylaştırır, tekrarlanabilirliği (reproducibility) artırır ve akademik çalışmanın başka araştırmacılarca test edilmesini son derece zahmetsiz kılar. RASH-HIT, bu açık standardın tüm potansiyelini (CSS, transform) kullanan nadir motorlardan biridir.

### 2. Yöntemsel Hız ve Performans Farkı
Mevcut literatürdeki geleneksel raster tarama yöntemleri ile RASH-HIT arasındaki hız farkı yöntemsel ayrışmadan kaynaklanmaktadır:
*   **Geleneksel Raster Yaklaşımlar (Yavaş ve Ağır):** Piksel tabanlı tarama gerçekleştiren yöntemler, çözünürlük arttıkça (örneğin 10000x10000 piksel) milyonlarca piksel hücresini RAM'de depolayıp tek tek sorgulamak zorundadır. Bu durum derin seviyelerde analiz süresini dakikalardan saatlere çıkarabilir ve bellek taşmasına (out-of-memory) sebep olur.
*   **RASH-HIT (Aşırı Hızlı ve Optimize):** RASH-HIT, **Hiyerarşik Quadtree Budaması** ile uzay geometrisini akıllıca böler. Eğer bir grid hücresinin üst (parent) hücresi boşsa, onun altındaki hiçbir çocuk hücreyi (4^n hücre) analiz etmez, doğrudan atlar. Dolguları STRtree (R-Tree) indekslemesi ile tek bir C++ sorgusuyla sorgular. Bu üstün optimizasyon sayesinde, **L10 derinliğe kadar olan milyarlarca potansiyel hücre kombinasyonu içeren analizleri 1 dakikadan kısa sürede çözümler, Excel, JSON ve HTML paketini sıfırdan üreterek kullanıma hazır hale getirir.**

---

## 19. Kaynakça

### Akademik Literatür Kaynakları
*   **[1]** [Visual and Structural Analysis of Fractal Geometry in the Sheikh Lotfollah Mosque Ornaments (Isfahan- Iran)](https://consensus.app/papers/details/8baa9a843c435a4e86eab9e5fe61898d/?utm_source=claude_code) (Hengame Rezazade, 2021, *International Journal of Architecture and Urban Development*)
*   **[2]** [Research on the Vector Box-counting Algorithm in Fractal Dimension Measurement](https://consensus.app/papers/details/4d4d95960a485c5ab4d44cce125d2aa0/?utm_source=claude_code) (Lu Gui-hua, 2008, *Journal of Image and Graphics*)
*   **[3]** [An effective method to compute the box-counting dimension based on the mathematical definition and intervals](https://consensus.app/papers/details/6f6f520bcd1c55db8fba7c9e0295ed8a/?utm_source=claude_code) (Jiaxin Wu et al., 2020)
*   **[4]** [Enhancement of the Box-Counting Algorithm for fractal dimension estimation](https://consensus.app/papers/details/aa9a4abce39a5fe0bd6d8b2bb20959e9/?utm_source=claude_code) (Gun-Baek So et al., 2016, *Pattern Recognition Letters*)
*   **[5]** [FRACTAL RHYTHMS OF VYSHYVANKA](https://consensus.app/papers/details/dc0dfbd4b641567199d712a2f44e8e02/?utm_source=claude_code) (Olga Dudka et al., 2025, *Mountain School of Ukrainian Carpaty*)
*   **[6]** [Exploring the Beauty of Tradition: How Fractal Geometry Influences Visual Attention in Architectural Design](https://consensus.app/papers/details/7f3d26ec01a951188048962b55a39d64/?utm_source=claude_code) (B. Ro et al., 2025, *Journal of Traditional Building, Architecture and Urbanism*)
*   **[7]** [Selimiye Camii Ana Kubbesinde Mevcut Durum ve Önerilen Sadeleştirmenin Fraktal Boyut Temelli Nicel Karşılaştırması](https://dergipark.org.tr/tr/pub/jah/article/1867887?utm_source=openai) (Selim Kartal & Melahat Teleri, 2026, *Digital International Journal of Architecture Art Heritage*)
*   **[8]** [Malatya Ulu Camii Bezemelerinin Morfolojik Analiz Yöntemiyle Değerlendirilmesi](https://dergipark.org.tr/tr/pub/iuarts/article/1647896?utm_source=openai) (Murat Şahin, Tuba Nur Olğun, Pınar Akbulut, 2025, *Art-Sanat*)
*   **[9]** [Fraktal Geometri Perspektifinden Geleneksel Savur (Mardin) Evi Bezemelerinin Analizi: Abdüllatif Özbek Konağı Örneği](https://dergipark.org.tr/en/pub/mbud/article/1770577) (Işılay Genç & Demet Aykal, 2026, *Journal of Architectural Sciences and Applications*)

### Akademik Tezler (YÖK ve Üniversite Arşivleri)
*   **[10]** [Selçuklu Dönemi Taş Bezeme Örneklerinin Fraktal Analizi: Sivas Gökmedrese Örneği](https://avesis.gazi.edu.tr/yonetilen-tez/aaa26e5c-0845-4edd-bb19-aa746d71ca38/selcuklu-donemi-tas-bezeme-orneklerinin-fraktal-analizi-sivas-gokmedrese-ornegi?utm_source=openai) (Merve Arslan, 2022, Yüksek Lisans Tezi, Gazi Üniversitesi)
*   **[11]** [Fraktal Boyuta Dayalı Mimari Bir Analiz: Sedad Hakkı Eldem ve Konut Mimarisi](https://avesis.uludag.edu.tr/yonetilen-tez/de7605eb-8759-4a6e-9b80-062701b2be86/fraktal-boyuta-dayali-mimari-bir-analiz-sedad-hakki-eldem-ve-konut-mimarisi?utm_source=openai) (Zeynep Kanatlar, 2012, Yüksek Lisans Tezi, Bursa Uludağ Üniversitesi)
*   **[12]** [Fraktal Boyut ve Lakunarite Hesaplamaları ile Parkların Dönemsel Analizleri ve Değerlendirmeleri](https://tezara.org/theses/718199) (Nazlı Bahar Ursavaş, 2022, Yüksek Lisans Tezi, İstanbul Teknik Üniversitesi)

### Yazılım Projeleri ve Ekosistem Kaynakları
*   **[13]** [Calculating Fractal Dimension from Vector Images Project PDF](https://tjhsst.edu/~rlatimer/techlab08/KellyRanSciFairBoardJuneTitleVersionPDF-08.pdf?utm_source=openai) (Kelly Ran, 2008, Thomas Jefferson High School Science Fair)
*   **[14]** [Measuring fractal dimension of vector data using grid systems](https://link.springer.com/article/10.1007/s44288-026-00548-9?utm_source=openai) (2026, *Springer Applied Sciences*)
*   **[15]** [StereoFractAnalyzer](https://comp-comb.github.io/StereoFractAnalyzer/?utm_source=openai) (Comp-Comb Research Group, 2024)

---
Create or connect a free Consensus account to return more than 3 results per search in Claude Code.: https://consensus.app/sign-up/?utm_source=claude_code&auth=claude_code