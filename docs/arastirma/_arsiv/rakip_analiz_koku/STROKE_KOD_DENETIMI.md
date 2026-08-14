# ÇİZGİ KALINLIĞI (STROKE) ÖLÇÜM MOTORU — KOD DENETİMİ

Tarih: bu oturum · Denetlenen sürüm: çalışma kopyası v1.0.6
Yöntem: kaynak kod satır düzeyinde okuma + bağımsız Shapely deneyleriyle sınama
**Proje dosyalarında hiçbir değişiklik yapılmadı.** Deney betikleri:
`~/rakip_analiz/_arsiv/deneyler/stroke_model_audit.py`

---

## ÖZET HÜKÜM

**Çekirdek matematik DOĞRU ve aslında zekice.** Ama modellediği şey SVG'nin
varsayılanı değil, ve bu hiçbir yerde yazmıyor. Ayrıca kodun kendi yorumu
ile kullanıcıya gösterilen uyarı birbiriyle çelişiyor.

| # | Bulgu | Ağırlık | Durum |
|---|---|---|---|
| S1 | `distance <= hw` testi round-cap/round-join varsayıyor; SVG varsayılanı butt/miter | ORTA | ölçüldü, %0.7–3.5 sapma |
| S2 | `fill-rule` — kod even-odd yapıyor, uyarı "nonzero kullanıldı" diyor, yorum "ikisi de" diyor | **YÜKSEK** | üçlü çelişki |
| S3 | `stroke-width` hiçbir rapora/manifest'e yazılmıyor | **YÜKSEK** | tekrarlanabilirlik açığı |
| S4 | `vector-effect="non-scaling-stroke"` desteklenmiyor, sessizce yanlış | ORTA | kodda hiç geçmiyor |
| S5 | Anizotropik dönüşümde `sqrt(det M)` yaklaşımı | DÜŞÜK | belgelenmemiş |
| S6 | `stroke-dasharray` yok sayılıyor, kesikli çizgi dolu sayılıyor | DÜŞÜK | kodda hiç geçmiyor |

---

## 1. ÇEKİRDEK MATEMATİK — DOĞRU

`backend/intersection_hierarchical.py` sat. 162-184:

```python
hw = stroke_widths[gi] / 2.0
zw = hw <= 0.0
if zw.any():
    hits_z = shapely.intersects(g_arr[zw], c_arr[zw])
    filled[ci[zw][hits_z]] = True
if (~zw).any():
    dists  = shapely.distance(g_arr[~zw], c_arr[~zw])
    hits_d = dists <= hw[~zw]
    filled[ci[~zw][hits_d]] = True
```

Motor stroke'u **poligona çevirmiyor.** Merkez çizgiyi (`LineString`) tutuyor
ve hücreyle arasındaki mesafeyi yarı kalınlıkla karşılaştırıyor.

Bu matematiksel olarak **tam doğru**: `distance(L, C) <= hw` ⟺
`C ∩ (L ⊕ D_hw) ≠ ∅`, yani merkez çizginin hw yarıçaplı diskle Minkowski
toplamı. Buffer poligonu hiç üretilmediği için hem hızlı hem de
poligonlaştırma yaklaşım hatası yok. **Bu iyi bir mühendislik kararıdır ve
FractDim'in özyinelemeli eğri bölme yaklaşımından daha temizdir.**

Doğru yapılan diğer şeyler:
- Fill önce test ediliyor, stroke yalnızca dolmamış hücreler için (sat. 163
  `not filled.all()`, sat. 170 `unfilled`). Doğru ve verimli.
- `hw <= 0` ayrı dalda saf kesişimle işleniyor — sıfır kalınlıkta
  `distance<=0` kayan nokta tuzağına düşmüyor. Doğru.
- STRtree ön eleme (sat. 316) — doğru uzamsal indeks kullanımı.
- `svg_loader.py:143` stroke-width yokken varsayılan `1.0` — SVG spesifikasyonuna uygun.
- `svg_loader.py:160-163` has_stroke; `stroke:none` ve `stroke-opacity:0`
  durumlarını eliyor — doğru.

---

## 2. BULGU S1 — MODELLENEN ŞEY SVG'NİN VARSAYILANI DEĞİL

`distance <= hw` testi **yuvarlak uç (round cap) + yuvarlak köşe (round join)**
demektir. SVG spesifikasyonunun varsayılanı ise `stroke-linecap: butt` ve
`stroke-linejoin: miter`.

Kodda `linecap`, `linejoin`, `miter` kelimeleri **backend mantığında hiç
geçmiyor** (yalnızca HTML tema CSS'inde dekoratif ikonlarda var).

### Ölçüm (Koch L4, 257 nokta, 255 adet 60° köşe)

Alan karşılaştırması — motorun ölçtüğü (ROUND) vs tarayıcının çizdiği (MITER+BUTT):

| stroke | ROUND alan (motor) | MITER alan (gerçek SVG) | fark |
|---|---|---|---|
| 0.25 | 789.12 | 790.12 | +0.13% |
| 1.00 | 3144.42 | 3160.49 | +0.51% |
| 3.00 | 9336.85 | 9481.48 | +1.55% |
| 8.00 | 24255.44 | 25283.95 | +4.24% |

Kutu sayımına yansıması:

| stroke | seviye | N (motor/round) | N (gerçek/miter) | fark |
|---|---|---|---|---|
| 1.00 | L05 | 100 | 100 | 0.00% |
| 1.00 | L06 | 220 | 222 | +0.91% |
| 1.00 | L07 | 538 | 542 | +0.74% |
| 3.00 | L05 | 102 | 104 | +1.96% |
| 3.00 | L06 | 232 | 240 | +3.45% |
| 3.00 | L07 | 594 | 610 | +2.69% |

**Yorum — dürüst olmak gerekirse bu küçük bir etki.** %0.7–3.5 hücre farkı,
regresyon eğimine bundan da az yansır. Kalınlık yanlılığının kendisi (%22)
yanında ihmal edilebilir.

**Ama bir hata değil, bir eksik belgelemedir ve hakem sorar.** 60°'lik Koch
köşesinde gerçek miter uzantısı `hw / sin(30°) = 2·hw`, yani motorun
yuvarladığı köşe gerçekte iki katı dışarı taşıyor. Sivri köşeli motiflerde
(çini, geometrik bordür) fark büyür.

**Yapılacak:** Ya (a) belgeye "stroke modeli: yuvarlak uç/köşe yaklaşımı"
diye yazılsın, ya (b) `stroke-linejoin` okunup miter olduğunda gerçek
buffer kullanılsın. (a) 10 dakikalık iş ve yayın için yeterli.

---

## 3. BULGU S2 — FILL-RULE ÜÇLÜ ÇELİŞKİ [YÜKSEK]

Üç yer, üç farklı şey söylüyor:

**(a) Kod ne yapıyor** — `geometry_engine.py` sat. 527-533:
```python
polygons.sort(key=lambda p: p.area, reverse=True)
fill_obj = polygons[0]
for p in polygons[1:]:
    fill_obj = fill_obj.symmetric_difference(p)
```
`symmetric_difference` = **saf EVEN-ODD.** Koşulsuz, her zaman.

**(b) Kodun kendi yorumu** — `geometry_engine.py` sat. 510:
```python
# Build Fill Geometry (Preserves fill-rule evenodd/nonzero and inner compound path holes)
```
"İkisini de destekliyor" diyor. **Yanlış.**

**(c) Kullanıcıya gösterilen uyarı** — `svg_loader.py` sat. 249-250:
```python
if elem.attrib.get('fill-rule') == 'evenodd':
    self.warnings.append("fill-rule='evenodd' detected. Default non-zero winding rule used in core v1.0.")
```
"Nonzero kullanıldı" diyor. **Bu da yanlış — hem de tam tersi yönde.**

Yani kullanıcı even-odd bir SVG yüklediğinde yazılım ona *"senin even-odd'unu
yok saydım, nonzero kullandım"* diyor; oysa gerçekte tam istediği şeyi,
even-odd'u uygulamış. Ve `fill-rule: nonzero` (SVG'nin gerçek varsayılanı)
olan bir dosyada da sessizce even-odd uyguluyor — uyarı bile vermiyor.

**Neden önemli:** Aynı yönde dolanan iki iç içe alt yol, nonzero'da dolu
kalır, even-odd'da delik açar. Motif SVG'lerinde (özellikle Illustrator
çıkışlı compound path'lerde) bu doğrudan yanlış alan, yanlış N(ε),
yanlış Db demektir. Ve `area` ölçüm modu tamamen dolguya dayandığı için
bu bulgu doğrudan senin ana katkını etkiler.

**Bu üç ifadeden ikisi yanlış. Yayından önce düzeltilmesi zorunlu.**

---

## 4. BULGU S3 — STROKE-WIDTH RAPORA HİÇ YAZILMIYOR [YÜKSEK]

`academic_exporter.py` ve `regression.py` içinde `stroke_width` araması:
**sıfır sonuç.**

Değer `intersection_cpu.py` sat. 49'da `to_dict()` içinde var
(`'stroke_width': float(round(self.stroke_width, 4))`) ama akademik pakete,
HTML rapora veya manifest'e ulaşmıyor.

Bunun sonucu, `DOGRULAMA_SONUCLARI.md` Tablo 3 ile birleştiğinde ciddidir:
çizgi kalınlığı sonucu 0.26 boyut birimi kaydırıyor, **ve o kalınlık
çıktının hiçbir yerinde yazmıyor.** Yani üretilen "tekrarlanabilirlik
manifesti" tekrarlanabilirlik için gereken en kritik parametreyi içermiyor.

Bu, `DOGRULAMA_SONUCLARI.md` Y3 maddesinin kod düzeyinde doğrulanmasıdır.

---

## 5. BULGU S4 — non-scaling-stroke DESTEKLENMİYOR [ORTA]

`geometry_engine.py` sat. 505-508:
```python
det_m = abs(M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0])
scale_factor = math.sqrt(det_m) if det_m > 0 else 1.0
effective_stroke_width = node.stroke_width * scale_factor
```

Kalınlık her zaman dönüşümle ölçekleniyor. Ama SVG'de
`vector-effect="non-scaling-stroke"` varsa kalınlık ölçeklenmemelidir.
Bu öznitelik kod tabanında **hiç geçmiyor** — ne desteklenmiş ne de
uyarı verilmiş. Böyle bir dosyada sonuç sessizce yanlış çıkar.

En az bir uyarı eklenmeli (`svg_loader.py` zaten clipPath/mask için
uyarı üretiyor, aynı mekanizma kullanılabilir).

---

## 6. BULGU S5 — ANİZOTROPİK DÖNÜŞÜM YAKLAŞIMI [DÜŞÜK]

`sqrt(|det M|)` yalnızca **eşyönlü (uniform)** ölçeklemede doğrudur.
`transform="scale(4,1)"` gibi bir dönüşümde gerçek SVG stroke'u eliptik
kesitli olur; motor onu dairesel varsayar. Yatay kalınlık olduğundan ince,
dikey kalınlık olduğundan kalın ölçülür.

Yalnızca alan koruyan ortalamayı verdiği için toplamda makul bir yaklaşımdır,
ama belgelenmemiştir. Ayrıca `det_m == 0` (yozlaşmış dönüşüm) durumunda
sessizce `1.0`'a düşüyor — burada uyarı üretilmeli.

---

## 7. BULGU S6 — stroke-dasharray YOK SAYILIYOR [DÜŞÜK]

Kod tabanında backend mantığı olarak geçmiyor. Kesikli çizgili bir motif
kesintisiz sayılır; N(ε) olduğundan büyük çıkar. Nadir ama teknik çizim
kökenli SVG'lerde görülür. En azından uyarı verilmeli.

---

## 8. SONUÇ — "DOĞRU ÇALIŞIYOR MU?"

**Sayma motoru doğru çalışıyor.** `distance <= hw` yaklaşımı matematiksel
olarak sağlam, hızlı ve `DOGRULAMA_SONUCLARI.md`'deki kontrol şekilleriyle
(düz çizgi 1.0000, dolu kare 2.0000) uçtan uca kanıtlanmış durumda.

**Sorun sayma değil, beyan.** Motor neyi ölçtüğünü söylemiyor, bir yerde
de yanlış söylüyor:

- Yuvarlak köşe/uç modeli kullanıyor, SVG varsayılanı sanılıyor → sessiz
- Even-odd uyguluyor, "nonzero uyguladım" diyor → **açıkça yanlış beyan**
- Kullandığı stroke kalınlığını rapora yazmıyor → tekrarlanamaz
- Desteklemediği öznitelikleri (non-scaling-stroke, dasharray) uyarmıyor → sessiz

Bunların hepsi düzeltilebilir ve hiçbiri çekirdek algoritmayı yeniden
yazmayı gerektirmiyor. **S2 ve S3 yayın öncesi zorunlu.**

---

## 9. ÖNCELİKLİ DÜZELTME LİSTESİ

| Sıra | İş | Dosya | Tahmini |
|---|---|---|---|
| 1 | `fill-rule` uyarı metnini gerçeğe uydur (even-odd deniyor) veya nonzero'yu gerçekten uygula | `svg_loader.py:250`, `geometry_engine.py:527` | 1-3 saat |
| 2 | `stroke_width` (ort. + maks. + kullanılan) manifest ve HTML rapora yazılsın | `academic_exporter.py` | 1 saat |
| 3 | En küçük hücre < stroke_width olduğunda ölçek tabanı uyarısı | `intersection_hierarchical.py` | 2 saat |
| 4 | Güven skoruna ölçek geçerliliği bileşeni | güven skoru modülü | 3 saat |
| 5 | `vector-effect`, `stroke-dasharray`, yozlaşmış dönüşüm uyarıları | `svg_loader.py` | 1 saat |
| 6 | Stroke modelinin (round cap/join) belgeye yazılması | README / docs | 15 dk |
| 7 | `stroke-linejoin: miter` gerçek desteği (isteğe bağlı) | `intersection_hierarchical.py` | 1 gün |
