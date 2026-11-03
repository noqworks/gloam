# Sürüm notları

English: [CHANGELOG.md](CHANGELOG.md)

Gloam için bütün değişiklikler, en yenisi üstte. Sürümler ANA.ARA.YAMA biçiminde:

- **Yama (1.0.x)**: düzeltme. Parçalar ve yazılım uyumlu kalır.
- **Ara sürüm (1.x.0)**: yeni özellik ya da parça, önceki yapımlarla uyumlu.
- **Ana sürüm (2.0.0)**: yeni parça ya da yeni kablolama gerektiren değişiklik.

_`releases.json` dosyasından `tools/changelog.py` ile üretilir. Bu dosyayı değil, onu düzenle._

## Sıradaki: 1.3.0

Planlananlar; talep ve sorulardan. Önerin ya da takıldığın bir yer varsa: [konular](https://github.com/noqworks/gloam/issues).

### Yazılım

- Home Assistant'ta güncelleme bildirimi ve sürüm notu bağlantısı. İsteğe bağlı: cihaz onsuz da tamamen çalışır.

### Belgeler

- Her yapım adımı için yakın plan fotoğraf.

## 1.2.1 · 2026-11-03

Kontrol sayfası telefonun ana ekranına uygulama gibi eklenir ve nasıl ekleneceğini kendisi gösterir.

### Yazılım

- Ana ekrana eklenen kontrol sayfası NOQ Open simgesi ve cihazın adıyla görünür, tam ekran açılır (iPhone ve Android).
- Kontrol sayfası ilk açılışta, kullanılan telefona göre ana ekrana eklemeyi adım adım gösterir; gizlenince bir daha çıkmaz.

### Kurulum

- Kurulum ekranının son adımı kontrol sayfasını ana ekrana eklemeyi de anlatır.

**Uyumluluk:** Donanım, bağlantılar ve ayarlar aynı; 1.2.0'dan güncellemede Wi-Fi ve bütün ayarlar korunur.
**Dosyalar:** [kaynak ve baskı dosyaları (zip)](https://open.noq.works/files/gloam/gloam-1.2.1-source.zip) · [GitHub sürümü](https://github.com/noqworks/gloam/releases/tag/v1.2.1)

## 1.2.0 · 2026-11-03

Home Assistant olmadan da çalışır: cihaz kendi kontrol sayfasını açar, duvar anahtarıyla yanar, zamanlama cihazda çalışır. Home Assistant isteğe bağlı kalır ve aynı anda çalışır.

### Yazılım

- Cihazda kontrol sayfası: ev ağında http://gloam-xxxxxx.local adresini aç; iki kanal, parlaklık, efektler, zamanlama ve elektrik gelince davranışı buradan. Uygulama, hesap ya da internet gerekmez; telefonun ana ekranına eklenebilir. (@umut)
- Home Assistant ve kontrol sayfası aynı ışıklar üzerinde aynı anda çalışır; birinde yapılan değişiklik ötekinde hemen görünür.
- Elektrik gelince: son sahneyle yan (varsayılan; sıradan bir duvar anahtarı çalışır), kesintiden önceki gibi ya da kapalı kal.
- Cihazda günlük zamanlama: açılış saatinde son sahne yükseliş süresi boyunca (varsayılan 20 dakika) yükselir, kapanış saatinde söner. Saat internetten alınır; saat dilimi kontrol sayfasında telefondan alınır.

### Kurulum

- Kurulum ekranının son adımı cihazın kendi adresini gösterir; Home Assistant isteğe bağlı ikinci adım.

**Uyumluluk:** Donanım ve bağlantılar aynı. Tarayıcıdan kurulum ya da ESPHome ile güncellenir; Wi-Fi ve ışık ayarları korunur (silme seçeneğini işaretleme). Güncellemeden sonra elektrik gelince son sahne yanar; eski davranış için kontrol sayfasında "Kesintiden önceki gibi"yi seç.
**Teşekkürler:** @umut (öneri: Home Assistant olmadan da çalışsın)
**Dosyalar:** [kaynak ve baskı dosyaları (zip)](https://open.noq.works/files/gloam/gloam-1.2.0-source.zip) · [GitHub sürümü](https://github.com/noqworks/gloam/releases/tag/v1.2.0)

## 1.1.0 · 2026-11-03

Gerçek parçalara göre yeniden tasarlanan denetleyici kutusu ve her baskı parçası için düzenlenebilir CAD kaynakları.

### Donanım

- Denetleyici kutusu parça listesine göre baştan tasarlandı: Mean Well LRS-75-12, 50 × 70 mm pertinaks, aynı uç duvarda PG11 şebeke ve PG7 LED rakoru.
- Bir ayırıcı ve kapağın altındaki kaburga, şebeke klemenslerini ve kablolarını 12 V tarafından ayırır.
- Kapak dört M3 havşa başlı vidayla ısıl insertlere bağlanır; yerine oturtan dudak, güç kaynağının üstünde menfez ve onu bastıran ayaklar var. D1 mini için USB yuvası ve iki montaj kulağı eklendi.
- İç plaka kalktı: pertinaks kutu tabanındaki ayaklara oturur.
- Her baskı parçası için düzenlenebilir CAD kaynakları (CadQuery), her CAD programında açılan STEP dosyaları ve uyumu denetlemek için güç kaynağı, pertinaks ve rakorlarla montaj STEP'i.
- Armatür gövdesi ve difüzör aynı ölçülerle parametrik model olarak yeniden kuruldu; 1.0.0'dan basılmış parçalar uyumlu kalır.

**Uyumluluk:** Armatürler, yazılım ve bağlantılar aynı. Denetleyici yeni iki parçalı bir set (kutu ve kapak); bir PG11 ve bir PG7 rakor, dört M3 ısıl insert, dört M3 × 8 havşa başlı ve dört M2 × 6 vida ister. 1.0.0 ile yapılmış denetleyici çalışmaya devam eder.
**Dosyalar:** [kaynak ve baskı dosyaları (zip)](https://open.noq.works/files/gloam/gloam-1.1.0-source.zip) · [GitHub sürümü](https://github.com/noqworks/gloam/releases/tag/v1.1.0)

## 1.0.0 · 2026-11-02

İlk açık sürüm.

### Donanım

- Oval armatür gövdesi ve düz difüzör; M3 ısıl insertli üç parçalı denetleyici kutusu (kutu, kapak, iç plaka).
- Prototipten bu yana: gövdenin iki ucundaki kablo girişi ~6 mm yuvarlak kablo için 7,5 × 7 mm kemer oldu.
- Prototipten bu yana: denetleyici kutusunda köşe vidasıyla çakışan dört dikme 9 mm aşağı alındı; iç plaka delikleri M3 geçişine (Ø3,4) açıldı.

### Yazılım

- ESPHome yazılımı: amber ve gün ışığı ayrı kısılır, efektler cihazda çalışır, Home Assistant cihazı bulur; API anahtarı ilk bağlantıda belirlenir.
- Kurulum: cihazın kendi ağında Türkçe ve İngilizce NOQ Open kurulum ekranı, 30 dakikalık kurulum penceresi, USB üzerinden Wi-Fi (Improv), gücü beş kez kesip açarak fabrika ayarları.

### Kurulum

- Tarayıcıdan kurulum: yazılımı yükle ve Wi-Fi'yi open.noq.works/tr/kurulum/gloam adresinden ayarla, hiçbir şey kurman gerekmez.

### Belgeler

- Bağlantı şeması, Türkiye'den tedarik bağlantılı parça listesi, kontrollü adım adım yapım.

**Uyumluluk:** İlk sürüm.
**Dosyalar:** [kaynak ve baskı dosyaları (zip)](https://open.noq.works/files/gloam/gloam-1.0.0-source.zip) · [GitHub sürümü](https://github.com/noqworks/gloam/releases/tag/v1.0.0)
