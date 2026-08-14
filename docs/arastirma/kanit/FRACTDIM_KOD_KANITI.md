# FractDim (Daniel Rendall, 2011) — Kod Düzeyinde Kanıt Dosyası

Amaç: "FractDim bozuk" ifadesini iddia olmaktan çıkarıp, doğrulanabilir kaynak
kodu satırlarına dayandırmak. Aşağıdaki her bulgu, üst projenin kendi deposundan
alınmış satır numaralı alıntıdır.

Kaynak ağaç (salt okunur inceleme):
`rakip_analiz/kaynaklar/FractDim/code/modules/src/main/java/uk/co/danielrendall/fractdim/`

---

## Terminoloji uyarısı

"Bozuk" (broken) kelimesi, yazılımın tamamının çalışmadığı anlamına gelmez.
Ölçülü ve savunulabilir ifade şudur:

> FractDim'in GUI yolu tasarlandığı gibi çalışır; ancak **komut satırı (CLI)
> arayüzü, toplu/başsız (headless) analiz için kullanılamaz durumdadır.**

Aşağıdaki iki bulgu bu ifadeyi doğrular.

---

## Bulgu 1 — CLI, hesapladığı sonucu hiçbir yere yazmıyor

Dosya: `cmd/FractDim.java`, satır 101–112

```java
switch (action) {
    case Count:
        SquareCounterBuilder squareCounterBuilder = new SquareCounterBuilder();
        squareCounterBuilder.maxDepth(maxDepth).
                angleIterator(getAngleIterator()).
                resolutionIterator(getResolutionIterator()).
                displacementIterator(getDisplacementIterator()).
                fractalDocument(document);
        SquareCounter calc = squareCounterBuilder.build();
        SquareCountingResult result = calc.process();
        break;
```

`result` değişkeni atanıyor, ardından hemen `break` geliyor. Değişken hiçbir
yerde okunmuyor, yazdırılmıyor, dosyaya aktarılmıyor.

Karşılaştırma: aynı `switch` içindeki `case Stats:` dalı (satır 113–122)
sonuçlarını düzgün biçimde `System.out.println` ile basar. Yani bu bir tasarım
tercihi değil, `Count` dalındaki bir eksikliktir.

**Sonuç:** `-do Count` ile çalıştırıldığında CLI, yalnızca dosya adı, kaba
sınırlayıcı kutu ve eğri sayısını basar. Kutu sayma sonucu ve fraktal boyut
çıktısı üretilmez.

---

## Bulgu 2 — CLI, Swing GUI bileşenine zorunlu bağımlı

Çağrı zinciri:

1. `cmd/FractDim.java:94` → `FractalController.fromFile(svgFile)`
2. `app/controller/FractalController.java:129-133` → `fromDocument(...)`
3. `app/controller/FractalController.java:141-144` → `new FractalController(document)`
4. `app/controller/FractalController.java:146-148`:

```java
private FractalController(FractalDocument document) {
    this.document = document;
    panel = new FractalPanel();
```

`FractalPanel` bir Swing bileşenidir (`app/gui/FractalPanel.java`). Yapıcı
devamında (satır 151–185) `panel.getMinimumSquareSizeSlider()`,
`panel.getResolutionSlider()`, `panel.getResolutionIteratorList()` gibi
doğrudan GUI widget çağrıları yapılır.

**Sonuç:** Komut satırı yolu, grafik ortamı olmayan bir makinede
(`-Djava.awt.headless=true`, konteyner, CI, sunucu) `HeadlessException`
riski taşır ve her durumda gereksiz yere tüm Swing arayüz nesne ağacını kurar.
Mimari olarak hesaplama çekirdeği ile sunum katmanı ayrılmamıştır.

---

## Bulgu 3 — Analiz, SVG'yi Graphics2D üzerinden tüketiyor

Dosyalar:
- `svgbridge/FDGraphics2D.java:35` → `extends org.apache.batik.ext.awt.g2d.DefaultGraphics2D`
- `calculation/AbstractNotifyingGraphics.java:37` → `extends FDGraphics2D`
- `calculation/FractalMetadataUtil.java:37` → `extends FDGraphics2D`

Yani geometri, Batik'in `Graphics2D` çizim çağrıları (`draw`/`fill` akışı)
yakalanarak elde edilir. Bu, saf analitik yol geometrisi üzerinde çalışmak
yerine, bir çizim ardışık düzenine takılıp kalmak demektir.

**Bunun pratik anlamı:** çizim odaklı bir akışta bir şeklin dolgusu (`fill`)
ile konturu (`draw`) farklı çağrılara düşer; ölçülen şeyin hangisi olduğu
kullanıcıya açıkça sunulmaz. RASH-HIT tarafında bu ayrım (stroke/fill) açık bir
karar noktası olarak ele alınmaktadır — bkz. `../STROKE_KOD_DENETIMI.md`.

**Not (dürüstlük payı):** Bulgu 3, Bulgu 1 ve 2 kadar kesin değildir.
"Dolgu ölçülemiyor" biçiminde kategorik bir iddia için, aracın çalıştırılıp
bilinen dolgulu bir test şekliyle sınanması gerekir. Şu an için doğrulanabilir
olan tek şey, analizin bir `Graphics2D` alt sınıfı üzerinden yürüdüğüdür.

---

## Nasıl ifade edilmeli

Kullanılabilir (kanıtlı):
- "FractDim'in CLI `Count` dalı hesapladığı sonucu yazdırmaz (`cmd/FractDim.java:111`)."
- "FractDim'in CLI yolu Swing `FractalPanel` örneklemesine bağımlıdır
  (`FractalController.java:148`), bu nedenle başsız toplu analiz için elverişli değildir."
- "FractDim son olarak 2011'de güncellenmiştir; bakımı sürdürülmemektedir."

Kaçınılmalı (kanıtsız / abartılı):
- "FractDim tamamen bozuk."
- "FractDim yanlış sonuç üretir." (Sayısal doğruluğu test edilmedi.)
- "Dünyada ilk / benzeri yok." (Bkz. proje genel kuralı.)

---

## Eksik kalan doğrulama adımları

1. FractDim'i derleyip `-do Count` ile çalıştırarak Bulgu 1'i çalışma zamanında teyit et.
2. `-Djava.awt.headless=true` ile çalıştırıp Bulgu 2'nin `HeadlessException`
   ürettiğini kaydet (stack trace ekle).
3. Bilinen fraktal boyutlu referans şekiller (Koch eğrisi, Sierpinski üçgeni)
   ile RASH-HIT ve FractDim'in GUI yolunu karşılaştır.

Bu üç adım tamamlanmadan, karşılaştırma matrisindeki ilgili hücreler
"doğrulanamadı" olarak işaretlenmelidir.
