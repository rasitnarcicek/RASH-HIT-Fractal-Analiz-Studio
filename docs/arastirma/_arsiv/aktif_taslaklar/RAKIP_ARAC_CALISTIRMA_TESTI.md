# RAKİP ARACIN DERLENMESİ VE ÇALIŞTIRILMASI — FractDim

Tarih: bu oturum
Amaç: "FractDim dolgu ölçemiyor" iddiasını **kod okumayla değil, aracı
gerçekten derleyip çalıştırarak** sınamak.
Ortam: Windows, JDK 21 (derleme hedefi 1.8), Maven 3.9.9, Java 8 çalışma zamanı.
Betikler: `deneyler/build_fractdim*.sh`, `deneyler/run_fractdim*.sh`

**Bu çalışma RASH-HIT proje dosyalarına dokunmaz.** FractDim ayrı bir
klasörde (`~/rakip_analiz/_arsiv/fd_build`, çalıştırma `C:\fdrun`) derlenmiştir.

---

## SONUÇ ÖZETİ

| Soru | Cevap |
|---|---|
| FractDim derlenebiliyor mu? | **Evet** — ama 4 ayrı onarım gerekti |
| Komut satırı çalışıyor mu? | **Hayır** — her girdide `NullPointerException` |
| Dolgu ölçebiliyor mu? | **Hayır** — kaynak kodda kanıtlı, çalıştırılarak sınanamadı |
| Karşılaştırmalı kıyas (benchmark) yapılabilir mi? | **Mevcut hâliyle hayır** |

---

## 1. DERLEME — 4 ENGEL, HEPSİ AŞILDI

Depo 2011'den beri güncellenmemiş (son commit 2011-09-12). Derlemek için
aşılan engeller:

| # | Engel | Çözüm |
|---|---|---|
| 1 | `onejar-maven-plugin:1.2.1` — googlecode'da barındırılıyordu, **depo ölü** | Paketleme eklentisi pom kopyasından çıkarıldı (derleme için gereksiz) |
| 2 | `launch4j-maven-plugin` — `9stmaryrd.com` HTTP deposu, Maven'ın varsayılan güvenlik engeli | Aynı şekilde çıkarıldı |
| 3 | `uk.co.danielrendall:javamathlib:1.0` — **Maven Central'da yok**, geliştiricinin kendi kütüphanesi | `danielrendall/JavaMathLib` klonlandı, yerel olarak kuruldu (mevcut sürüm **1.2-SNAPSHOT**), bağımlılık sürümü yükseltildi |
| 4 | Java classpath'i `C:\Users\RaşitNarçiçek\...` yolundaki Türkçe karakterleri çözemedi | Derlenmiş sınıflar + 40 jar saf ASCII yola (`C:\fdrun`) kopyalandı |

**Derleme sonucu:** `BUILD SUCCESS` — 76 kaynak dosya, 132 sınıf,
hedef Java 1.8.

> Not: `javamathlib` 1.0 yerine 2021 tarihli 1.2-SNAPSHOT kullanıldı.
> Derleme hatasız geçtiği için API uyumlu görünüyor, ancak bu **birebir
> 2011 yapılandırması değildir** ve raporlanmalıdır.

---

## 2. ÇALIŞTIRMA — CLI HER GİRDİDE ÇÖKÜYOR

Dört ayrı test SVG'si denendi:

| Dosya | İçerik | Sonuç |
|---|---|---|
| `dolu_kare.svg` | `<rect fill="black">` | `NullPointerException` |
| `bos_kare.svg` | `<rect fill="none" stroke="black">` | `NullPointerException` |
| `p_dolu.svg` | `<path ... Z fill="black">` | `NullPointerException` |
| `p_bos.svg` | `<path ... Z fill="none" stroke>` | `NullPointerException` |

Hem `-do Count` hem `-do Stats` eylemlerinde aynı sonuç:

```
File: p_dolu.svg
Exception in thread "main" java.lang.NullPointerException
    at uk.co.danielrendall.fractdim.cmd.FractDim.process(FractDim.java:98)
    at uk.co.danielrendall.fractdim.cmd.FractDim.doMain(FractDim.java:78)
    at uk.co.danielrendall.fractdim.cmd.FractDim.main(FractDim.java:67)
```

### Kök neden — kaynak kodda bulundu

`cmd/FractDim.java` sat. 94-98:
```java
FractalController controller = FractalController.fromFile(svgFile);
FractalDocument document = controller.getDocument();
System.out.println("File: " + svgFile.getName());
System.out.println("Approximate bounding box: " + document.getMetadata().getBoundingBox());
```

`getMetadata()` **null** dönüyor. Çünkü metadata'yı üreten tek yer
`FractalController.java` sat. 249-254:

```java
private void generateMetaData() {
    controllerThread.checkControllerThread();
    ...
    panel.updateProgressBar(33);          // <-- Swing arayüz bileşeni
    FractalDocumentMetadata metadata = FractalMetadataUtil.getMetadata(document.getSvgDoc());
    document.setMetadata(metadata);
```

Bu metot `private` ve yalnızca **grafik arayüzün** denetleyici iş
parçacığı geri çağrımından tetikleniyor; üstelik içinde ilerleme
çubuğuna (`panel`) dokunuyor.

**Yani komut satırı arayüzü, grafik arayüze yapısal olarak bağımlı ve
tek başına hiçbir zaman çalışmıyor.** Bu bir yapılandırma hatası değil,
kodun kendi mimarisinden gelen bir kusur.

---

## 3. BUNUN ANLAMI

### 3.1 Karşılaştırmalı kıyas mümkün değil

Literatürde bulunan **tek** karşılaştırılabilir önceki araç FractDim'di
(bkz. `TASARIM_SVG_FARKIMIZ.md`). Mevcut hâliyle:

- Komut satırından ölçüm alınamıyor
- Toplu test yapılamıyor
- Sayısal karşılaştırma üretilemiyor

Grafik arayüz üzerinden tek tek elle ölçüm teorik olarak denenebilir
(`app.FractDim` sınıfı, Swing) ama bu tekrarlanabilir bir kıyas
oluşturmaz ve makalede sunulamaz.

**Makalede dürüst ifade şu olmalı:**

> "Karşılaştırma için erişilebilen tek önceki vektör-tabanlı araç olan
> FractDim (Rendall, 2009-2011), 2026 itibarıyla kaynaktan derlenebilmiş
> ancak komut satırı arayüzü metadata üretiminin grafik arayüz iş
> parçacığına bağlı olması nedeniyle her girdide `NullPointerException`
> vermiştir. Bu nedenle sayısal karşılaştırmalı kıyas yapılamamış,
> karşılaştırma kaynak kodun anlamsal incelemesiyle sınırlı kalmıştır."

### 3.2 Dolgu iddiası hâlâ geçerli — ama dayanağı kod, deney değil

`TASARIM_SVG_FARKIMIZ.md`'deki iddia `FDGraphics2D.java` sat. 80-85'e
dayanıyor:
```java
// ignore for now - treat as draw
public void fill(Shape s) { draw(s); }
```

Bu kanıt **hâlâ sağlam ve tek anlamlı** — dolgu, kontur gibi işleniyor.
Ancak artık şunu da net söyleyebiliyoruz: bu davranışı çalışma anında
gösteremedik, çünkü **araç hiç çalışmıyor.** Raporda bu ayrım
korunmalıdır: *kaynak kod kanıtı* ≠ *çalıştırma kanıtı*.

### 3.3 "Terk edilmiş" nitelemesi artık kanıtlı

Önceki raporda FractDim "terk edilmiş" deniyordu; gerekçe son commit
tarihiydi. Artık daha güçlü bir gerekçe var: **bağımlılıklarının
barındırıldığı depolar ölü, kendi kütüphanesi Central'da yok ve
komut satırı arayüzü çalışmıyor.** Bu, tarih argümanından çok daha
sağlam bir dayanaktır.

---

## 4. TEKRARLANABİLİRLİK

```
deneyler/build_fractdim.sh    Maven kurulumu + ilk deneme (paketleme hatası)
deneyler/build_fractdim2.sh   compile'a geçiş (bağımlılık hatası)
deneyler/build_fractdim3.sh   ölü eklentilerin pom kopyasından çıkarılması
deneyler/build_fractdim4.sh   javamathlib 1.2-SNAPSHOT'a yükseltme -> BUILD SUCCESS
deneyler/run_fractdim.sh      ilk çalıştırma (classpath sorunu)
deneyler/run_fractdim2.sh     ASCII yola taşıma -> araç açılıyor
deneyler/run_fractdim3.sh     <path> tabanlı testler -> NPE onaylandı
```

Kaynak: https://github.com/danielrendall/FractDim (son commit 2011-09-12)
Yardımcı kütüphane: https://github.com/danielrendall/JavaMathLib (2021-09-22)
Lisans: GPL-3.0
