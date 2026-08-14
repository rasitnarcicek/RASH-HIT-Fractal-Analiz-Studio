
## C.13 İddia–kod uyum tablosu

| # | Belgedeki iddia | Kaynak | Kod durumu | Kanıt |
|---|---|---|---|---|
| 1 | Rasterleştirme yok | README | ✅ Doğru | raster kütüphanesi yok |
| 2 | Kesin GEOS kesişimi | README | ✅ Doğru | ih.py:153 |
| 3 | STRtree toplu sorgu | README | ✅ Doğru | ih.py:166 |
| 4 | Boş ebeveyn budama, FULL yok | README | ✅ Doğru | ih.py:381 |
| 5 | Kesin 2^i katlama | README | ✅ Doğru | gp.py:132-136 |
| 6 | AR tabanlı taban ızgara | README | ✅ Doğru | gp.py:120-125 |
| 7 | Analiz kutusu önceliği | README | ✅ Doğru | gp.py:76-85 |
| 8 | Tamamlayıcı boş sayım | README | ✅ Doğru | — |
| 9 | 7 SVG öğesi | README | ✅ Doğru | sl.py:282 |
| 10 | 6 dönüşüm fonksiyonu | README | ✅ Doğru | ge.py:25-79 |
| 11 | Kontur ölçeği √&#124;det&#124; | README | ✅ Doğru | ge.py:506-508 |
| 12 | defusedxml XXE | README | ✅ Doğru | sl.py |
| 13 | Tolerans 24/12/6 | README | ✅ Doğru | ge.py:435 |
| 14 | Yay merkez parameterizasyonu | README | ✅ Doğru | ge.py:133+ |
| 15 | 20 iş parçacığı → 17 işçi | README | ✅ Doğru | ih.py:190-192 |
| 16 | Güven: R² %40 / ölçek %30 / sağlık %30 | kod | ✅ Doğru | conf.py:65-86 |
| 17 | Ezme koruması / sürümleme | README | ✅ Doğru | — |
| 18 | OLS eğim hesabı | README | ✅ Doğru | D=2,000000 / D=1,000000 |
| 19 | RLE + yüksek seviye kısıtlama | README | ✅ Doğru | op.py |
| 20 | Kontur mesafe yüklemi | kod | ✅ Doğru (nitelikli) | ih.py:176-184 |
| 21 | Çok çekirdekli yürütme | README | ✅ Doğru | ih.py:220-233 |
| 22 | **nonzero → unary_union, evenodd → sym.diff** | README | ❌ **Yanlış** — her zaman even-odd | ge.py:510-531; ölçüm 7500/7500 |
| 23 | **"Varsayılan non-zero kullanıldı" uyarısı** | sl.py:250 | ❌ **Yanlış** — even-odd uygulanıyor | aynı |
| 24 | **Sıfır varyansta R² = NaN** | README | ❌ **Yanlış** — üretimde R² = 1,0 | reg.py:145-146; ölçüm |
| 25 | **Doyum denetimi** | reg.py:92-94 | ❌ **Boş `pass`** | ölçüm: dışlanan yok |
| 26 | **mm / cm / in / pc / % birimleri** | README | ❌ **Uygulanmamış** | ölçüm: tümü default |
| 27 | **rem birimi** | README | ❌ **Bozuk** (`[:-2]` → `"1r"`) | ölçüm: default |
| 28 | **Eğriler "adaptif" örnekleniyor** | README | ❌ **Yanlış** — sabit adım | ölçüm: 1000 br = 1 br |
| 29 | **summary_only_after_level = 9** | README | ❌ Kod: 8 | op.py:42 |
| 30 | **svg_only_after_level = 10** | README | ❌ Kod: 9 | op.py:43 |
| 31 | **Paralellik "L04+"** | README | ❌ Kapı `n ≥ 4000` | ih.py:211 |
| 32 | **"%100 mükemmel kare hücre"** | gp.py docstring | ❌ Yuvarlama var | gp.py:122 |
| 33 | ε tanımı (maks / normalize / ln) | README+gp.py | ⚠️ Kısmen — regresyon farklı eksen kullanıyor (eğim etkilenmez) | reg.py:80-84 |
| 34 | "Seviye sayısında sınır yok" | README | ⚠️ Kısmen — hesaplama evet, ölçüm geçerliliği ≈L9'da tükeniyor | ölçüm: sarkma/hücre |

(Kısaltmalar: ge = geometry_engine.py, gp = grid_planner.py,
ih = intersection_hierarchical.py, sl = svg_loader.py, reg = regression.py,
op = output_profiles.py, conf = confidence.py.)

## C.14 Bu bulguların EK BÖLÜM A ve B'deki değerlendirmeye etkisi

**Geri çekilmesi gereken.**

- EK BÖLÜM B.11'de "güçlenen yön" olarak sıraladığım **"dolgu semantiğinin
  doğru ele alınması"** maddesi geçerliliğini yitirmiştir (C.3). FractDim'in
  dolguyu kontura indirgemesini eleştirmiştim; bu proje ise dolguyu SVG
  standardının varsayılanının aksine even-odd olarak çözmektedir. Farklı bir
  hata, ama yine bir hata. Düzeltilene kadar üstünlük iddiası olarak
  kullanılmamalıdır.
- EK BÖLÜM A ve B'de vurgulanan **"L10 / 8,4 milyon kutuya ölçeklenme"**
  ifadesi, C.7'deki düzleştirme tavanı nedeniyle bir *başarım* iddiası olarak
  korunmalı, bir *çözünürlük/doğruluk* iddiası olarak kullanılmamalıdır.

**Güçlenen.**

- **Hiyerarşik negatif-uzay budaması** (B.4) kod düzeyinde doğrulanmıştır ve
  incelenen beş rakipte bulunmamaktadır. Projenin en savunulabilir teknik
  katkısı olmayı sürdürmektedir.
- **Kontur mesafe yüklemi** (C.12) beklenmedik bir ikinci özgün katkıdır;
  önceki bölümlerde fark edilmemişti. Rakiplerin hiçbiri kontur kalınlığını
  bu biçimde kesin ve tamponsuz ele almamaktadır. Makalede ayrı bir teknik
  katkı olarak sunulabilir.
- **Regresyon çekirdeğinin doğruluğu** sentetik olarak kanıtlanmıştır (C.2/18).
  Bu, B.7'deki Koch sapmasının bir kodlama hatasından değil, ölçek penceresi ve
  ızgara hizası eksikliğinden kaynaklandığını göstermektedir — yani sorun
  düzeltilebilir niteliktedir.

**Değişmeyen.** B.9'daki eksiklikler (çoklu ızgara orijini, bootstrap güven
aralığı, otomatik ölçek penceresi, multifraktal, bilinen-değer doğrulaması)
aynen geçerlidir; C.4 ve C.5 bunların ikisini kod düzeyinde kanıtlamıştır.

**Genel değerlendirme.** Projenin **mimarisi ve çekirdek geometri motoru
sağlamdır**; bulunan on kusurun hiçbiri mimari değildir. Sekizi yerel
düzeltmelerle (tek fonksiyon veya tek koşul) giderilebilir. Buna karşılık
bulguların üçü (C.3 dolgu kuralı, C.4 dejenere R², C.5 doyum denetimi)
**bildirilen sayısal sonucu doğrudan etkilemektedir** ve düzeltilmeden
yayımlanacak herhangi bir ölçüm tablosu savunulamaz.

## C.15 Öncelikli düzeltme listesi (C bulguları)

Etki × düzeltme maliyeti sırasına göre:

| Sıra | Bulgu | Düzeltme | Tahmini kapsam |
|---|---|---|---|
| 1 | C.4 dejenere R² = 1,0 | `ss_tot <= 1e-12` dalını `float("nan")` yap; `abs(slope)` kaldır; `slope = 1.0` yedeğine uyarı ekle | 3 satır |
| 2 | C.3 dolgu kuralı | `SVGNode`'a `fill_rule` ekle; nonzero'da `unary_union`, evenodd'da mevcut yol; loader uyarısını düzelt | ~15 satır |
| 3 | C.5 doyum denetimi | `pass` yerine `included = False` + gerekçe; alt-uç seyreklik filtresi ekle | ~8 satır |
| 4 | C.6 CSS birimleri | `parse_length`'e mm/cm/in/pc/% ekle; `rem` kırpmasını `[:-3]` yap | ~12 satır |
| 5 | B.8 `square_bbox` etkisiz | `ih.py:491`'deki ikinci `create_grid_plan` çağrısına `grid_mode` + `geometry_bounds` ilet | 2 satır |
| 6 | C.7 düzleştirme tavanı | Toleransı eğri yay uzunluğu / hedef hücre boyutuna bağla; `--tolerance` bayrağı ekle | ~25 satır |
| 7 | C.9 ε tanımı | Regresyonu `grid_planner`'ın `log_inv_epsilon` alanından besle | ~5 satır |
| 8 | C.8 Phase 8 sabitleri | README'yi koda göre düzelt (veya tersi) | belge |
| 9 | C.10 paralellik açıklaması | README'yi `n ≥ 4000` ve %85 olarak düzelt | belge |
| 10 | C.11 "%100 kare" | docstring'leri "as square as possible" yap | belge |

1–5 arası maddeler toplam ~40 satırdır ve bildirilen sayısal sonucu etkileyen
kusurların tamamını kapatır.

## C.16 Makale açısından sonuç

C bölümündeki doğrulama, projenin özgünlük iddiasını **zayıflatmamakta**,
tersine onu savunulabilir bir zemine oturtmaktadır. Ayırt edici iki teknik
unsur — hiyerarşik negatif-uzay budaması ve tamponsuz kontur mesafe yüklemi —
kaynak kodla doğrulanmış ve incelenen beş rakipte bulunamamıştır. Buna karşılık
bu unsurların çevresindeki ölçüm katmanı (dolgu kuralı, dejenere durum
raporlaması, ölçek penceresi, birim ayrıştırma) hâlihazırda yayımlanabilir
olgunlukta değildir.

Bu nedenle önerilen sıralama şudur: önce C.15'teki 1–5 maddeleri düzeltilmeli,
ardından EK BÖLÜM B.12'deki bilinen-değer ve değişmezlik testleri
çalıştırılmalı, sonuçlar bu düzeltmelerden **önce ve sonra** raporlanmalıdır.
Bu "önce/sonra" tablosu, makalenin doğrulama (validation) bölümünü tek başına
taşıyabilecek güçte bir kanıt oluşturur ve yazılım katkısının ciddiyetini
gösterir.

Kesin bir "ilk" veya "benzersiz" ifadesi bu bölümden de türetilmemektedir;
tespitler "incelenen kaynaklar ve okunan kaynak kodlar içinde doğrudan eşleşme
bulunamadı" düzeyinde tutulmuştur.

## C.17 Üretim kayıtları

Doğrulama betikleri: `C:\Users\RaşitNarçiçek\rakip_analiz\verify1.py` …
`verify6.py`. Her biri proje köküne geçici adla (`_v1_tmp.py` … `_v6_tmp.py`)
kopyalanıp çalıştırılmış ve aynı komut içinde silinmiştir.

Proje dizini denetimi: kalıcı olarak oluşturulan, değiştirilen veya silinen
dosya yoktur; `outputs/` altına hiçbir analiz paketi yazılmamıştır.
`backend/` dosyalarının değişiklik zamanları bu oturumdan öncedir.
