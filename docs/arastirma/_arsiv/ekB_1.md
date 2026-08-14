
---

# EK BÖLÜM B — RAKİP KAYNAK KODLARININ İNDİRİLİP OKUNMASI VE RASH-HIT ÜZERİNDE YAPILAN DOĞRULAMA DENEYLERİ

Bu bölüm, EK BÖLÜM A'daki belge/kılavuz temelli incelemenin ötesine geçerek
rakip yazılımların **kaynak kodlarının indirilip satır düzeyinde okunmasına**
ve bu iddiaların **RASH-HIT'in kendi motoru üzerinde çalıştırılan ölçümlerle**
sınanmasına dayanır. Bu bölümdeki tüm sayısal sonuçlar bu makinede üretilmiştir
ve tekrar üretilebilir; betikler `C:\Users\RaşitNarçiçek\rakip_analiz\` altındadır.

Analiz sırasında RASH-HIT proje dizinine hiçbir dosya yazılmamış, değiştirilmemiş
veya silinmemiştir; tüm incelemeler salt-okunur yapılmıştır.

## B.1 İndirilen ve okunan rakip kaynak kodları

| Yazılım | Dil | Satır | Lisans | Son sürüm/commit | Kaynak |
|---|---|---|---|---|---|
| FracPaQ | MATLAB | 20.512 | MIT | v2.8.0, Mart 2021 | github.com/DaveHealy-github/FracPaQ |
| Fractalyse 3 | Java | 16.380 | GPLv3 | v0.9.1, 5 Nisan 2022 | git.renater.fr/anonscm/git/fractalyse/fractalyse.git |
| FractDim | Java | 7.823 | GPLv3+ | 2009–2011 | github.com/danielrendall/FractDim |
| GeoFractalLines | Python | 1.476 | MIT | 2026 | github.com/roko-gis/GeoFractalLines |
| Multiscale Box-Counting Framework | Python | 742 | MIT | 2026 | github.com/roko-gis/Multiscale-Box-Counting-Framework-for-Fractal-Dimension-Analysis-of-Vector-Lines |

Karşılaştırma için RASH-HIT Fractal Studio: Python, 18.376 satır, Apache-2.0.

**Yöntem notu:** Bu bölümdeki her iddia, EK BÖLÜM A'daki gibi README veya
kılavuz metnine değil, doğrudan kaynak dosya yoluna ve kod satırına
dayandırılmıştır. Pazarlama ifadeleri kanıt olarak kullanılmamıştır.

## B.2 Temel yöntem ayrımı: kutu doluluğu nasıl belirleniyor?

Bu, projenin özgünlük iddiasının döndüğü teknik eksendir. Beş rakip
sistemin çekirdek sayım döngüsü okunmuştur.

**(a) Nokta örnekleme — FractDim**

`calculation/SquareCounter.java`, `doHandleCurve` → `evaluateBetween(curve, 0, 0.0, 1.0)`
metodu eğri üzerinde yalnızca **nokta** değerlendirir; kutu doluluğu
`Grid.java:263` içindeki tamsayı bölme ile belirlenir:

```java
int SquareelX = (int) Math.floor(p.x() / resolution);   // "todo - some serious testing!"
```

Segment ile kutu kenarı arasında geometrik kesişim testi hiçbir yerde
hesaplanmaz. Adaptif ikiye bölme (bisection) örnekleme sıklığını artırır ancak
yöntemi kesin kesişime dönüştürmez; `maxDepth` aşıldığında
`Log.app.warn("Max iteration depth reached - bailing out")` ile sessizce
eksik sayım yapılır.

Ayrıca dolgu (fill) semantiği tamamen devre dışıdır — `svgbridge/FDGraphics2D.java:81-86`:

```java
// ignore for now - treat as draw
@Override
public void fill(Shape s) {
    Log.misc.debug("Filling shape " + s.toString());
    draw(s);
}
```

Yani dolu bir şekil yalnızca konturundan sayılır. Bu, dolu alanların
boyutunun sistematik olarak düşük kestirilmesine yol açar.

**(b) Vertex binning — GeoFractalLines**

`_count_boxes_single` fonksiyonu geometriyi önce noktalara örnekler,
sonra bu noktaları tamsayı hücre indekslerine eşler:

```python
gx = np.floor((pts_array[:, 0] - min_xy[0]) / scale).astype(np.int32)
gy = np.floor((pts_array[:, 1] - min_xy[1]) / scale).astype(np.int32)
flat = np.ravel_multi_index((gx, gy), (nx, ny))
return np.unique(flat).size, flat
```

Kutu içinde çizgi bulunup bulunmadığı geometrik olarak sınanmaz; yalnızca
örneklenmiş köşe noktalarının düştüğü kutular sayılır. Doğruluk, örnekleme
yoğunluğuna (`ADAPTIVE_SAMPLING_FACTOR = 0.8`) bağlıdır ve seyrek örneklenmiş
uzun segmentlerde ara kutular kaçırılabilir.

**(c) Box-counting bulunmaması — FracPaQ**

Depo genelinde box-counting veya fraktal boyut hesabı **yoktur**;
`grep -ric "boxcount|box-count|fractal" --include=*.m .` sıfır eşleşme verir.
Mekânsal örüntü niceliği bunun yerine tek ölçekli **dairesel tarama
pencereleri** ile yapılır (`guiFracPaQ2Dpattern.m`, analitik segment-daire
sekant testi). Blok alanı analizi ise geometriyi diske BMP olarak basıp
geri okuyarak, yani fiilen rasterleştirerek yapılır
(`guiFracPaQ2Dlength.m:486-495`): `print(...,'-dbmp256')` → `imread` →
`imbinarize` → `bwconncomp`.

Bu nedenle FracPaQ, isim benzerliğine rağmen RASH-HIT'in **yöntemsel rakibi
değildir**; Kategori D/E'ye (alan/kısmi ilişki) aittir.

**(d) Kesin geometrik kesişim — Multiscale Box-Counting Framework**

```python
cell_orig = QgsRectangle(min(xs), min(ys), max(xs), max(ys))
candidates = spatial_index.intersects(cell_orig)      # bbox ön-eleme
if candidates:
    cell_geom = QgsGeometry.fromRect(cell_orig)
    for fid in candidates:
        if feature_geoms[fid].intersects(cell_geom):  # gerçek GEOS kesişimi
            count += 1
            break
```

**(e) Kesin geometrik kesişim — Fractalyse 3**

`method/vector/mono/BoxCountingMethod.java`, `BoxCountingTask.execute` (satır 74-94):

```java
Polygon cellGeom = grid.getCellGeom(x, y);
for(Feature f : coverage.getFeatures(cellGeom.getEnvelopeInternal())) {
    if(f.getGeometry().intersects(cellGeom)) { nb++; break; }
}
```

LocationTech JTS kullanılır (eski vividsolutions değil). Rasterleştirme
veya vertex binning yoktur.

**Sonuç:** İncelenen beş sistemin üçü (FractDim, GeoFractalLines, FracPaQ)
kesin geometrik kesişim yapmamaktadır. Kesin kesişim yapan iki sistem
(Fractalyse, Multiscale-BC) ise **SVG değil, coğrafi vektör formatları**
(GeoPackage/GeoJSON/Shapefile veya QGIS katmanı) okumaktadır.
