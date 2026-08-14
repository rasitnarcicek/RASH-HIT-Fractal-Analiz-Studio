
## B.6 Doğrulama Deneyi 1 — Izgara konumu duyarlılığının ölçülmesi

**Amaç.** Rakiplerin tamamında bulunan "çoklu ızgara orijini" mekanizmasının
RASH-HIT'te bulunmamasının sayısal sonucunu ölçmek.

**Yöntem.** Koch eğrisi (5. yineleme), matematiksel kesin değeri
D = log4/log3 = 1.261860. Sayım yöntemi RASH-HIT ile aynı sınıfta:
`shapely` + `STRtree` + kesin `intersects`. Tek değişken ızgara orijinidir;
16 farklı orijin (4×4 kesirli kaydırma) denenmiştir. Ölçek seviyeleri:
8, 16, 32, 64, 128, 256. Betik: `rakip_analiz/gridbias.py`.

**Sonuçlar — ölçek başına dolu kutu sayısı:**

| Izgara bölmesi | Sabit orijin | 16 orijin min. | Ortalama | Maks. | Yayılma % |
|---|---|---|---|---|---|
| 8 | 16 | 12 | 16,9 | 20 | 66,7 |
| 16 | 32 | 32 | 39,5 | 49 | 53,1 |
| 32 | 91 | 81 | 89,2 | 101 | 24,7 |
| 64 | 227 | 191 | 208,7 | 227 | 18,8 |
| 128 | 494 | 489 | 501,0 | 516 | 5,5 |
| 256 | 1112 | 1088 | 1135,4 | 1185 | 8,9 |

**Elde edilen fraktal boyutlar:**

| Toplama kuralı | D | Mutlak hata | R² |
|---|---|---|---|
| Sabit tek ızgara (RASH-HIT'in bugünkü davranışı) | 1,250245 | 0,011615 | 0,997519 |
| 16 orijin üzerinden minimum (Fractalyse/FractDim kuralı) | 1,301461 | 0,039601 | 0,999195 |
| 16 orijin üzerinden ortalama (QGIS tabanlı iki depo) | 1,215872 | 0,045988 | 0,999913 |

**Yalnızca ızgara orijini değiştirilerek elde edilen D dağılımı:**
en küçük 1,182981 — en büyük 1,271940 — yayılma 0,088960 — standart sapma 0,023323.

**Yorum (temkinli).** Bu koşuda çoklu orijin toplama kuralları, sabit ızgaradan
**daha doğru** bir D üretmemiştir; sabit ızgaranın hatası (0,0116) minimum
(0,0396) ve ortalama (0,0460) kurallarından düşüktür. Dolayısıyla çoklu orijin
mekanizması "doğruluğu artırır" gerekçesiyle savunulamaz. Ancak bulgular üç
ayrı gerekçeyi desteklemektedir:

1. **Belirsizliğin nicelenmesi.** Aynı geometri, aynı algoritma ve aynı kesin
   kesişim ile yalnızca ızgara konumu değiştirildiğinde bildirilen D değeri
   1,18–1,27 aralığında değişmektedir (σ = 0,023). Tek bir nokta tahmin
   bildiren bir sistem, bu belirsizliği kullanıcıya aktaramaz. Motifler arası
   0,02 düzeyindeki farkların anlamlı olup olmadığı bu bilgi olmadan
   değerlendirilemez.
2. **Keyfiliğin giderilmesi.** Tek bir ızgara hizasının seçimi metodolojik
   olarak gerekçelendirilemez; buna karşılık "N konum denenip minimum alındı"
   kuralı literatürde yerleşiktir (Fractalyse, FractDim).
3. **Regresyon kalitesi.** Çoklu orijin ortalaması R²'yi 0,997519'dan
   0,999913'e yükseltmektedir. RASH-HIT'in `backend/confidence.py` modülü
   güven skorunda R²'ye %40 ağırlık verdiğinden, bu doğrudan bildirilen güven
   düzeyini etkiler.

## B.7 Doğrulama Deneyi 2 — RASH-HIT'in öteleme duyarlılığı

**Amaç.** "Sistem ızgarayı tasarımın en-boy oranına göre kurduğu için tasarımın
kanvas içinde kaydırılması sonucu etkilemez" varsayımını RASH-HIT'in kendi
üretim hattıyla sınamak.

**Yöntem.** Aynı Koch geometrisi (4. yineleme), aynı 800×800 viewBox içinde
yalnızca `transform="translate(T,100)"` değeri değiştirilerek üç SVG üretildi
(T = 100, 103, 150). Analiz RASH-HIT'in kendi komut satırı arayüzüyle
çalıştırıldı:

```
python run_analysis.py -i koch_tT.svg -l 7 --grid-mode <mod> --profile reproducible
```

**Sonuçlar:**

| Öteleme | grid-mode | D | R² | Güven skoru |
|---|---|---|---|---|
| translate(100,100) | canvas_aspect | 1,1690 | 0,9951 | 92,5 (Yüksek) |
| translate(103,100) | canvas_aspect | 1,1955 | 0,9992 | 92,5 (Yüksek) |
| translate(150,100) | canvas_aspect | 1,1986 | 0,9982 | 92,5 (Yüksek) |
| translate(100,100) | square_bbox | 1,1690 | 0,9951 | 92,5 (Yüksek) |
| translate(103,100) | square_bbox | 1,1955 | 0,9992 | 92,5 (Yüksek) |
| translate(150,100) | square_bbox | 1,1986 | 0,9982 | 92,5 (Yüksek) |

Seviye bazında dolu kutu sayıları da değişmektedir (T=100 → T=103):
L2: 20→16, L3: 40→35, L4: 82→76, L5: 172→169, L6: 410→400.

**Bulgu 1 — öteleme duyarlılığı doğrulanmıştır.** Tasarımın yalnızca 3 birim
sağa kaydırılması bildirilen fraktal boyutu 1,1690'dan 1,1955'e taşımaktadır
(Δ = 0,0265). Bunun nedeni, ızgaranın **tasarım sınır kutusuna değil, SVG
viewBox'ına (kanvasa) demirlenmiş olmasıdır**: `backend/grid_planner.py`
içindeki `create_grid_plan` fonksiyonu varsayılan `canvas_aspect` modunda
`raw_bounds` değerini viewBox'tan türetir. Sistemin en-boy oranını algılayıp
kareye yakın hücreler üretmesi doğrudur; ancak bu, ızgaranın *hizasını* değil
yalnızca *hücre biçimini* belirler.

**Bulgu 2 — güven skoru bu değişkenliği yansıtmamaktadır.** Her üç çalıştırmada
da güven skoru 92,5 ("Yüksek") ve akademik yorum "Sonuç doğrudan akademik
yayına dahil edilebilir" olarak üretilmiştir. Yani sistem, aynı motif için
birbirinden farklı üç sonucu eşit ve yüksek güvenle bildirmektedir.

**Bulgu 3 — doğruluk sapması.** Kesin değeri 1,261860 olan Koch eğrisi için
üretilen değerler 1,169–1,199 aralığındadır; mutlak hata yaklaşık 0,06–0,09
düzeyindedir. Bu, B.9'da açıklanan ölçekleme penceresi seçiminin
bulunmamasıyla tutarlıdır ve bilinen-değer doğrulamasının neden zorunlu
olduğunu göstermektedir.
