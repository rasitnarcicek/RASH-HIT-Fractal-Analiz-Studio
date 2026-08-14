
## C.6 BULGU 4 (Yüksek) — CSS birim dönüşüm tablosunun yarısı uygulanmamış

README, dokuz satırlık bir birim dönüşüm tablosu sunar (px, pt, pc, mm, cm, in,
em, rem, %) ve her biri için bir çarpan verir.

**Kod (svg_loader.py:109-129).** `parse_length` yalnızca üç ek duruma bakar:
`px` (sonek atılır), `pt` (×1,33333) ve `em`/`rem` (×16,0). Diğerleri için
`float(val_str)` çağrısı `ValueError` fırlatır ve fonksiyon **sessizce
`default` değerini döndürür**.

**Deney (verify1.py), `default = −999,0`:**

| Girdi | README'ye göre | **Ölçülen** | Durum |
|---|---|---|---|
| `10px` | 10,0 | 10,0 | ✅ |
| `12pt` | 16,0 | 15,99996 | ✅ |
| `1em` | 16,0 | 16,0 | ✅ |
| `3` (birimsiz) | 3,0 | 3,0 | ✅ |
| `1rem` | 16,0 | **−999,0** | ❌ |
| `10.5mm` | 39,69 | **−999,0** | ❌ |
| `5cm` | 188,98 | **−999,0** | ❌ |
| `1in` | 96,0 | **−999,0** | ❌ |
| `2pc` | 32,0 | **−999,0** | ❌ |
| `50%` | ViewBox oranı | **−999,0** | ❌ |

`rem` hatasının nedeni ayrıca ilginçtir: `'1rem'.endswith('em')` doğru olduğu
için ilk dal yakalar, ardından `val_str[:-2]` yalnızca `"em"` kırpar ve geriye
`"1r"` kalır → `ValueError` → varsayılan. Yani `rem` desteği eklenmiş
görünmekte ama işlememektedir.

Fonksiyonun kendi docstring'i de yanıltıcıdır: örnek olarak `'10.5mm'` verir,
oysa bu değeri ayrıştıramaz.

**Neden önemli.** `mm` ve `cm`, Adobe Illustrator ve Inkscape'in **baskı amaçlı
SVG dışa aktarımlarında varsayılan birimlerdir**. Projenin hedef veri türü olan
motif, tekstil ve süsleme çizimleri tam olarak bu araçlardan gelmektedir.
Somut sonuçları:

- `stroke-width="0.5mm"` → varsayılan `1.0` px'e düşer; kontur kalınlığı
  yanlış, dolayısıyla C.12'deki mesafe yüklemi yanlış eşikle çalışır.
- `width="210mm" height="297mm"` (A4) → her ikisi de `0.0` döner. Bu durumda
  `grid_planner` width/height dalını atlar; viewBox varsa kurtarır, yoksa
  analiz kutusu 100×100 yedeğine düşer ve tüm ölçek ekseni bozulur.

Hata sessizdir: kullanıcıya hiçbir uyarı verilmez.

## C.7 BULGU 5 (Orta-Yüksek) — Eğri düzleştirme "adaptif" değil, sabit adımlı; yüksek seviyelerde sayısal tavan oluşturuyor

**İddia (README):** "SVG paths contain parametric curves that are **adaptively
sampled** into linear segments based on tolerance configuration."

**Kod.** `sample_cubic_bezier`, `sample_quadratic_bezier` ve
`sample_elliptical_arc` fonksiyonlarının tamamı `for i in range(1, num_steps+1):
t = i / num_steps` biçiminde **düzgün (uniform) t adımlarıyla** örnekler.
Eğrilik, kiriş hatası veya yay uzunluğu hiçbir yerde değerlendirilmez.

**Deney (verify2.py).** 1000 birimlik bir eğri ile 1 birimlik bir eğri, aynı
tolerans ayarında **aynı sayıda** noktaya indirgenir:

| Eğri | steps=6 | steps=12 | steps=24 |
|---|---|---|---|
| Büyük eğri (1000 birim) | 7 nokta | 13 nokta | 25 nokta |
| Küçük eğri (1 birim) | 7 nokta | 13 nokta | 25 nokta |

Örnekleme yoğunluğu geometrik ölçekten tümüyle bağımsızdır. Bu tanım gereği
adaptif değildir. (Karşılaştırma: EK BÖLÜM B.2'de incelenen FractDim, bu sorunu
tam olarak önlemek için adaptif ikiye bölme kullanmaktadır — bu tek eksende
rakip yaklaşım üstündür.)

**Deney (verify4.py) — sayısal sonucun ölçülmesi.** R = 400 yarıçaplı çeyrek
daireyi temsil eden standart kübik Bézier (kontrol noktası katsayısı
K = 0,5522847498), 800 birimlik bir analiz kutusu içinde:

| tolerance_steps | Üretilen nokta | Düğüm hatası | **Kiriş sarkması** |
|---|---|---|---|
| 6 | 7 | 0,100938 | 3,562725 birim |
| 12 | 13 | 0,103477 | 0,901970 birim |
| **24 (üretimde kullanılan)** | **25** | **0,108977** | **0,226823 birim** |
| 48 | 49 | 0,108977 | 0,056865 birim |

Üretim ayarındaki kiriş sarkması **0,2268 birimdir**. Bunu ızgara hücre
boyutuyla karşılaştırdığımızda:

| Seviye | Hücre boyutu | Sarkma / hücre |
|---|---|---|
| L07 | 3,1250 | 0,073 |
| L08 | 1,5625 | 0,145 |
| L09 | 0,7813 | 0,290 |
| L10 | 0,3906 | **0,581** |
| L11 | 0,1953 | **1,161** ← sarkma hücreden büyük |

**Sonuç.** README'nin "**seviye sayısında kesin bir sınır yoktur**" (`no hard
limit`) iddiası hesaplama açısından doğrudur, ancak **ölçüm açısından
yanıltıcıdır**. Yaklaşık L9'dan itibaren düzleştirme hatası hücre boyutunun
anlamlı bir kesrine ulaşır; L11'de hücreyi tamamen aşar. Bu seviyelerde sistem
artık SVG eğrisini değil, onun 24 kirişlik çokgen yaklaşımını ölçmektedir.

Bu, EK BÖLÜM A ve B'de projenin güçlü yönü olarak sunduğum
"≈8,4 milyon kutu / L10'a ölçeklenme" ifadesinin **niteliklendirilmesini**
gerektirir: ölçeklenme başarımsal olarak gerçektir, ancak ölçüm geçerliliği
düzleştirme toleransıyla sınırlıdır. Makalede bu sınır açıkça belirtilmeli veya
tolerans eğri uzunluğuna/hücre boyutuna bağlı hâle getirilmelidir.

Ek olarak `--tolerance` bayrağı komut satırında **hiç sunulmamaktadır**
(mevcut bayraklar: `--batch`, `--batch-profile`, `--engine`, `--grid-mode`,
`--input`, `--lang`, `--levels`, `--measure`, `--output`, `--overwrite`,
`--profile`, `--show-technical`). Tolerans üretimde `'high'` değerine sabitlidir
ve kullanıcı bunu değiştiremez.
