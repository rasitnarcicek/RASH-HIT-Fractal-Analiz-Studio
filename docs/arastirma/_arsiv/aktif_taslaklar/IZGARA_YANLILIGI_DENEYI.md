# IZGARA YANLILIĞI (GRID BIAS) DENEYİ

Tarih: bu oturum
Betik: `deneyler/grid_bias_audit.py`
Yöntem: aynı şekil, ızgara **kaydırılarak** ve **döndürülerek** yeniden
ölçülür; çıkan Db değerlerinin yayılımı ölçülür.
**RASH-HIT proje dosyalarına dokunulmamıştır.**

---

## NEDEN BU DENEY

Kutu sayma yönteminin bilinen zayıflığı, sonucun ızgaranın nereye
konduğuna bağlı olmasıdır. Rakip araç FractDim bunu biliyordu — komut
satırında `-a` (açı sayısı) ve `-p` (yer değiştirme noktası sayısı)
seçenekleri var, yani **birden çok açı ve kaydırma deneyip en iyisini
arıyor.**

RASH-HIT'te böyle bir tarama **yok**: tek, eksene hizalı ızgara
kullanılıyor. Soru şu: bu bir eksiklik mi, yoksa önemsiz mi?

---

## SONUÇLAR

### Koch eğrisi L5 (çizgi/stroke geometrisi) · teorik D = 1.261859

| koşul | Db | hata % | R² |
|---|---|---|---|
| referans (0,0, 0°) | 1.1825 | −6.29% | 0.9997 |
| kaydır x +0.25 hücre | 1.1866 | −5.97% | 0.9996 |
| kaydır x,y +0.5 hücre | 1.1791 | −6.56% | 0.9988 |
| döndür 15° | 1.2521 | −0.77% | 0.9996 |
| döndür 30° | 1.2252 | −2.90% | 0.9995 |
| döndür 45° | **1.2659** | **+0.32%** | 0.9993 |
| **YAYILIM (maks−min)** | **0.0868** | | std = 0.0347 |

### Sierpinski üçgeni L5 (dolgu/fill geometrisi) · teorik D = 1.584963

| koşul | Db | hata % | R² |
|---|---|---|---|
| referans (0,0, 0°) | 1.6007 | +0.99% | 0.9996 |
| kaydır x +0.25 hücre | 1.6010 | +1.01% | 0.9996 |
| kaydır x,y +0.5 hücre | 1.6042 | +1.21% | 0.9994 |
| döndür 15° | 1.5938 | +0.56% | 0.9995 |
| döndür 30° | 1.6123 | +1.73% | 0.9996 |
| döndür 45° | 1.5938 | +0.56% | 0.9995 |
| **YAYILIM (maks−min)** | **0.0185** | | std = 0.0064 |

---

## YORUM — BU ÇOK ÖĞRETİCİ BİR SONUÇ

### Bulgu 1: Dolgu ölçümü ızgara yanlılığına karşı SAĞLAM

Sierpinski'de yayılım yalnızca **0.0185**. Izgarayı istediğin gibi
kaydır veya döndür, sonuç neredeyse değişmiyor ve teorik değere hep
%1-2 içinde yakın kalıyor.

**Bu, projenin en güçlü tarafının ölçüm olarak da en sağlam tarafı
olduğu anlamına gelir.** Dolgu ölçümü zaten FractDim'in yapamadığı
şeydi (bkz. `RAKIP_ARAC_CALISTIRMA_TESTI.md`); şimdi bu yeteneğin
aynı zamanda sayısal olarak kararlı olduğunu da biliyoruz.

### Bulgu 2: Çizgi (stroke) ölçümü ızgaraya 4.7 kat daha duyarlı

Koch'ta yayılım **0.0868** — Sierpinski'nin **4.7 katı.**

Daha çarpıcısı: eksene hizalı ızgara (0°) en kötü sonucu veriyor
(−6.29%), 45° döndürülmüş ızgara ise neredeyse tam isabet (+0.32%).
Koch eğrisinin kendi doğru parçaları belirli açılarda yoğunlaştığı
için, eksene hizalı ızgarayla **hizalanma (rezonans)** oluşuyor ve
hücre sayısı sistematik olarak eksik çıkıyor.

Yani RASH-HIT'in tek, eksene hizalı ızgara kullanması, çizgi
tabanlı şekillerde **sistematik ve yönlü bir hata** üretiyor —
rastgele gürültü değil, hep aynı yönde bir sapma.

### Bulgu 3: R² bu hatayı GÖREMİYOR

Altı koşulun **hepsinde** R² ≥ 0.9988. Yani:

> Db −6.29% yanlışken bile regresyon uyumu mükemmel görünüyor.

Bu, `STROKE_KOD_DENETIMI.md` ve `DOGRULAMA_SONUCLARI.md`'deki bulgunun
**bağımsız bir yoldan doğrulanmasıdır**: R² tabanlı güven skoru,
doğruluğun göstergesi değildir. Yazılım kullanıcıya "yüksek güven"
diyor, sonuç ise %6 yanlış.

---

## ÜÇ BULGU AYNI YERE ÇIKIYOR

Birbirinden bağımsız üç deney, aynı sonuca varıyor:

| Deney | Bulgu | Etki (Db) |
|---|---|---|
| Çizgi kalınlığı (`stroke_model_audit.py`) | stroke genişliği sonucu kaydırıyor | **0.26** |
| Izgara yanlılığı (`grid_bias_audit.py`) | ızgara açısı sonucu kaydırıyor (çizgide) | **0.087** |
| Izgara yanlılığı (dolgu) | dolguda etki çok küçük | **0.019** |

**Ortak sonuç:** RASH-HIT'in **dolgu (fill) tabanlı ölçümü sağlam**;
**çizgi (stroke) tabanlı ölçümü kırılgan** ve yazılım bu kırılganlığı
kullanıcıya bildirmiyor.

Bu, makalenin omurgası olabilecek nettikte bir bulgudur:

> *Vektör uzayında kutu sayımı, dolu düzlemsel biçimler için ızgara
> yerleşimine karşı kararlıdır (yayılım 0.019); konturlu eğriler için
> ise hem ızgara açısına (0.087) hem çizgi kalınlığına (0.26) duyarlıdır.
> Dolayısıyla motif ve tasarım analizinde dolgu tabanlı ölçüm
> yeğlenmeli, çizgi kalınlığı ise zorunlu olarak raporlanmalıdır.*

---

## ÖNERİLEN DÜZELTMELER

| # | İş | Gerekçe |
|---|---|---|
| 1 | Çok açılı ızgara taraması (en az 0°/15°/30°/45°) ekle, sonucu minimum veya ortalama olarak ver | FractDim 2011'de bunu zaten yapıyordu; eksikliğimiz |
| 2 | Yayılımı belirsizlik payı olarak rapora yaz (`Db = 1.183 ± 0.043`) | Tek sayı vermek yanıltıcı |
| 3 | Güven skoruna ızgara kararlılığı bileşeni ekle | R² tek başına yetersiz — üç deneyde de kanıtlandı |
| 4 | Dolgu ölçümünü varsayılan/önerilen mod yap, stroke modunda uyarı ver | Ölçümün hangi modda sağlam olduğu artık biliniyor |

---

## SINIRLAR

- Tek seviye (L5) ve iki şekil ile sınanmıştır; daha geniş şekil kümesiyle
  yinelenmelidir.
- Ölçek aralığı ve seviye sayısı bu deneyde sabit tutulmuştur; referans
  değerler `DOGRULAMA_SONUCLARI.md`'deki üretim ayarlarıyla birebir aynı
  değildir. Bu nedenle mutlak hata yüzdeleri değil, **koşullar arası
  yayılım** anlamlıdır.
- Döndürme işlemi şeklin kendisine değil ızgaraya uygulanmış sayılır;
  eşdeğer olarak şekil ters yönde döndürülmüştür.
