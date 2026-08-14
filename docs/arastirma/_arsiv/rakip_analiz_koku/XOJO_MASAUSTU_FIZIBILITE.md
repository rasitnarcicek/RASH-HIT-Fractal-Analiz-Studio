# RASH-HIT FRAKTAL STUDIO → XOJO MASAÜSTÜ UYGULAMASI · FİZİBİLİTE

Tarih: bu oturum. Tüm bilgiler bu makinedeki kurulu Xojo'dan ve resmî
Xojo belgelerinden doğrulanmıştır. Doğrulanamayan noktalar açıkça işaretlendi.

---

## 0. KISA CEVAP

**Yapılabilir, ve mimari olarak doğru yol tek: Xojo = kabuk, Python = motor.**

Motoru Xojo'ya çevirmek gerçekçi değil (aşağıda sebebi). Ama Xojo'yu
kullanıcının gördüğü uygulama hâline getirip Python çekirdeğini içine
gömmek hem gerçekçi hem de senin bugünkü kod tabanını olduğu gibi korur.

**macOS + Windows tek Desktop lisansıyla mümkün** — Xojo lisansı platforma
göre değil, **proje türüne** göre satılır. Bu, kurulu EULA'dan doğrulandı.

**Senin müdahalen:** Xojo tarafı görsel sürükle-bırak. Arayüzü sen
düzenlersin, ben motor köprüsünü yazarım. Bu iş bölümü mantıklı.

---

## 1. MAKİNEDE NE VAR — DOĞRULANDI

| Bulgu | Değer | Kaynak |
|---|---|---|
| Kurulu sürümler | **Xojo 2026r1.2** ve **Xojo 2026r2** | `C:\Program Files\Xojo\` |
| Yapılandırma | `%APPDATA%\Xojo\2026.012.00.67271` | disk |
| Ön derlenmiş eklentiler | **yalnızca** `Plugins*GUIWinx86_64.o` | `%APPDATA%\Xojo\...\Precompiled Plugins` |
| Lisans anahtarı dosyası | **klasör BOŞ** (`Xojo\License Keys\`) | disk |
| Shell (süreç çalıştırma) | `Shellx64.dll` mevcut, API belgeli | disk + docs |
| Gömülü tarayıcı | **CEF/Chromium + WebView2** (`libcef.dll`, `Microsoft.Web.WebView2.Core.dll`) | disk |
| SQLite | `SQLiteDatabasex64.dll` | disk |

### ⚠ Lisansın DOĞRULANAMADI

`License Keys` klasörü boş ve yalnızca **Windows GUI** eklentileri ön
derlenmiş. Bu, şimdiye kadar sadece Windows masaüstü hedefinin
kullanıldığına işaret eder ama hangi lisansa sahip olduğunu **diskten
söyleyemem** — Xojo anahtarları çevrimiçi doğrulanıyor
(EULA md. 18: *"The Xojo IDE will validate your Xojo License Key(s)
... via the Internet"*).

**Sen bakacaksın:** Xojo IDE → menüden lisans/hesap bölümü, ya da
xojo.com hesabın. Bana "Desktop mu, Pro mu, Web var mı" de, planı ona
göre kesinleştireyim.

---

## 2. XOJO LİSANS MODELİ — EULA'DAN BİREBİR

`C:\Program Files\Xojo\Xojo 2026r2\Read Mes\License Agreement.txt` sat. 36:

> *"Desktop projects require a Desktop build key. Web projects require a
> Web Build Key and Mobile projects require a Mobile Build key. Console
> projects require a Console build key."*

sat. 7:

> *"Install Xojo Desktop, Web, Console and Mobile Build license keys you
> purchase on up to two computers. Xojo Pro license keys may be installed
> on 3 computers."*

**Buradan çıkan kritik sonuç:** Lisans **proje türüne** göre. İşletim
sistemine göre DEĞİL. Yani:

> **Tek bir Desktop build key ile hem Windows hem macOS hem Linux
> uygulaması derlersin. Ek ücret yok.**

Bunu resmî belge de doğruluyor — *Application deployment → Desktop*
başlığı altındaki alt sayfalar: **Linux, macOS, Windows.**
(https://documentation.xojo.com/topics/application_deployment/desktop/)

sat. 36'daki diğer önemli nokta:

> *"The Xojo IDE can be used free-of-charge to create projects of any kind
> and run them from the IDE. However, to distribute or deploy a stand-alone,
> compiled version of a project requires the purchase and installation of a
> Xojo Build License key."*

Yani lisansın olmasa bile **prototipi IDE içinde çalıştırarak
geliştirebiliriz**; anahtar sadece dağıtılabilir .exe/.app üretmek için gerekli.
Bu, riski düşürüyor — önce yapalım, sonra lisans durumuna bakarız.

---

## 3. XOJO NELER YAPABİLİYOR — RESMÎ BELGE BAŞLIKLARINDAN

documentation.xojo.com gezinme ağacından doğrulanan yetenek alanları:

**Proje türleri:** Desktop · Web · Console · Mobile (iOS, Android)
**Platformlar (Desktop):** Windows, macOS, Linux, **Raspberry Pi**
**Senin işine yarayacak olanlar:**

| Yetenek | Senin için anlamı |
|---|---|
| **Shell sınıfı** | Python `run_analysis.py`'yi çağırma. Köprünün temeli. |
| **HTMLViewer** (CEF/WebView2 gömülü) | **Mevcut web arayüzünü hiç değiştirmeden uygulamanın içine gömebilirsin.** En kısa yol bu. |
| **SQLiteDatabase** | Analiz geçmişi, toplu iş kuyruğu, motif kütüphanesi. |
| **Graphics / Canvas / Picture** | SVG önizleme, ızgara katmanı çizimi, log-log grafiği yerel çizim. |
| **Declares** | Gerekirse doğrudan C kütüphanesi (GEOS) çağırma. İleri seviye. |
| **XojoScript** | Uygulama içi kullanıcı betikleri (ileride). |
| **Build automation / IDE scripting** | Windows+macOS derlemesini tek komutla otomatikleştirme. |
| **Web projesi** | Ayrı lisans. Mevcut web arayüzün zaten çalışıyor — **buna gerek yok.** |
| **Console projesi** | Ayrı lisans. Mevcut CLI'ın Python'da zaten var — **buna da gerek yok.** |

> **Not:** "Web arayüzünü Xojo'da daha rahat yaparız" fikrine dikkat.
> Xojo Web ayrı bir lisans ve ayrı bir çalışma zamanı. Mevcut web
> arayüzün zaten var ve çalışıyor. Onu Xojo Web'e taşımak **sıfırdan
> yeniden yazmak** demek, düzeltmek değil. **Önermiyorum.**
> Bunun yerine mevcut web arayüzünü HTMLViewer ile masaüstü
> uygulamasının içine göm — hem tek kod tabanı kalır hem bedava.

---

## 4. MOTORU XOJO'YA ÇEVİRMEK — NEDEN HAYIR

RASH-HIT çekirdeğinin dayandığı yığın:

- **Shapely** → C++ **GEOS** (kesişim, mesafe, buffer, STRtree)
- **NumPy** → vektörleştirilmiş `lexsort`, `unique`, `cumsum`, maskeleme
- `intersection_hierarchical.py` toplu Shapely çağrıları (`shapely.box(x0,y0,x1,y1)`
  tek C++ çağrısı, `shapely.distance(dizi, dizi)`)

Xojo'da bunların **hiçbirinin karşılığı yok.** Yapılması gerekenler:
1. GEOS'u Xojo `Declare` ile sarmalamak (yüzlerce fonksiyon, elle),
2. STRtree uzamsal indeksini Xojo'da yeniden yazmak,
3. NumPy'siz döngülerde aynı hızı yakalamaya çalışmak.

**Tahmini süre: aylar. Kazanç: sıfır. Risk: doğrulanmış motorunu bozmak.**
`DOGRULAMA_SONUCLARI.md`'deki %0.00 hata kalibrasyonunu baştan yapman gerekir.

**Karar: motor Python'da kalır.**

---

## 5. ÖNERİLEN MİMARİ

```
┌──────────────────────────────────────────────────────┐
│  Xojo Desktop App  (Windows .exe  +  macOS .app)     │
│                                                       │
│  · Yerel menüler, dosya sürükle-bırak, tercihler     │
│  · SVG kütüphanesi / toplu iş kuyruğu  (SQLite)      │
│  · Sonuç tablosu, karşılaştırma, dışa aktarma        │
│  · HTMLViewer  ─── mevcut web raporunu gömer         │
│                                                       │
│         │  Shell  (stdin/stdout/JSON)                │
│         ▼                                             │
│  ┌────────────────────────────────────────────┐      │
│  │  Gömülü Python  (PyInstaller ile paketli)  │      │
│  │  RASH-HIT motoru — DEĞİŞTİRİLMEDEN         │      │
│  │  Shapely / GEOS / NumPy                    │      │
│  └────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────┘
```

**İki iletişim seçeneği:**

**(A) Shell + JSON** — Xojo `run_analysis.py --json` çağırır, stdout'tan
JSON okur. Basit, hata ayıklaması kolay, en az bağımlılık. **Önerim bu.**

**(B) Yerel HTTP** — Xojo mevcut `backend/web_server.py`'yi arka planda
başlatır, HTMLViewer `127.0.0.1:PORT`'a bakar. **Mevcut web arayüzünü
tek satır değiştirmeden masaüstü uygulaması yapar.** En hızlı sonuç.

**En iyisi ikisi birden:** (B) ile 1 haftada çalışan bir uygulama çıkar,
sonra (A) ile yerel Xojo ekranlarını tek tek ekleyip web'i emekliye ayırırsın.

---

## 6. ÇÖZÜLMESİ GEREKEN TEKNİK NOKTALAR

| Konu | Durum | Not |
|---|---|---|
| Python'u uygulama içine gömme | Çözülebilir | PyInstaller/`python-build-standalone`; Shapely'nin GEOS DLL/dylib'i taşınmalı |
| macOS **kod imzalama + notarization** | **Doğrulanamadı** | Apple Developer hesabı ($99/yıl) gerekir. Gömülü Python ikilisi imzalamayı zorlaştırır — **en büyük riskli kalem, önce bu denenmeli** |
| macOS derlemesini Windows'tan üretme | **Doğrulanamadı** | Xojo Desktop macOS'u hedef gösteriyor; Windows host'tan çapraz derleme yapıp yapamadığını IDE'de Build Settings'ten teyit et |
| Apple Silicon / Intel evrensel ikili | Doğrulanamadı | Xojo Build Settings'te hedef mimari seçimi var, teyit gerekli |
| Uygulama boyutu | ~150-250 MB | Python + NumPy + Shapely + GEOS. Kabul edilebilir. |
| macOS'ta test | **Mac gerekli** | Sende Mac yoksa bu gerçek engeldir — kirala/ödünç al |

---

## 7. YOL HARİTASI

**Faz 0 — Karar (sen, 10 dk)**
Xojo IDE'yi aç, lisans türünü öğren. Bana söyle.

**Faz 1 — Kavram kanıtı (1 gün)**
Boş Xojo Desktop projesi: bir düğme, bir HTMLViewer. Düğme Shell ile
`backend/web_server.py`'yi başlatsın, HTMLViewer localhost'a baksın.
Windows'ta çalıştığını gör. **Buradan sonrası zaten kesin.**

**Faz 2 — Gömme (2-3 gün)**
Python'u PyInstaller ile tek klasöre paketle, Xojo uygulamasının
Resources'ına koy, göreli yoldan çalıştır. Sistemde Python kurulu
olmadan çalışsın.

**Faz 3 — Yerel arayüz (1-2 hafta)**
Sürükle-bırak SVG, toplu kuyruk, SQLite geçmiş, sonuç tablosu,
tercihler ekranı. **Burası senin oynayacağın kısım.**

**Faz 4 — macOS (belirsiz)**
Build Settings'ten macOS hedefi, imzalama, notarization. Mac erişimi
gerekir. Risk buradadır, sonuna bırakılmalı.

---

## 8. SENİN MÜDAHALEN NEREDE

| İş | Kim |
|---|---|
| Lisans türünü öğrenmek | **sen** |
| Arayüz tasarımı, pencere düzeni, sürükle-bırak | **sen** (Xojo görsel editör, kod yazmadan) |
| Türkçe/İngilizce arayüz metinleri | **sen** (Xojo'nun Lingua aracı `Extras/Lingua`'da mevcut) |
| İkon, renk, marka | **sen** |
| Shell köprüsü, JSON protokolü | ben |
| Python gömme ve paketleme | ben |
| Derleme otomasyonu (IDE scripting) | ben |
| macOS imzalama | birlikte, Mac gerekli |

Xojo'nun asıl gücü tam da bu: arayüzü kod yazmadan sürükle-bırakla sen
kurarsın, ben altını bağlarım.

---

## 9. AÇIK SORULAR (doğrulanmalı)

1. Lisans türün ne? (Desktop / Pro / süre dolmuş?)
2. macOS'a erişimin var mı? Yoksa Faz 4 gerçekçi değil.
3. Apple Developer hesabın var mı? Notarization için şart.
4. Xojo Build Settings'te Windows host'tan macOS hedefi seçilebiliyor mu?
   (IDE'de bakılacak, belgeden teyit edilemedi)
5. Bu masaüstü uygulaması dağıtılacak mı, yoksa kişisel/akademik kullanım mı?
   Dağıtılmayacaksa imzalama sorunu büyük ölçüde ortadan kalkar.

---

## 10. KAYNAKLAR

1. Xojo End User License Agreement, Xojo 2026r2 kurulumu,
   `Read Mes/License Agreement.txt`, md. 7, 12, 18, 36, 40.
2. Xojo Documentation — Application deployment → Desktop (Linux/macOS/Windows):
   https://documentation.xojo.com/topics/application_deployment/desktop/index.html
3. Xojo Documentation — Shell sınıfı:
   https://documentation.xojo.com/api/os/shell.html
4. Xojo Documentation — Build automation (IDE scripting, IDE Communicator):
   https://documentation.xojo.com/topics/build_automation/index.html
5. Yerel kurulum denetimi: `C:\Program Files\Xojo\Xojo 2026r2\`,
   `%APPDATA%\Xojo\`
