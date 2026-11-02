# Sürüm notları

English: [CHANGELOG.md](CHANGELOG.md)

Gloam için bütün değişiklikler, en yenisi üstte. Sürümler ANA.ARA.YAMA biçiminde:

- **Yama (1.0.x)**: düzeltme. Parçalar ve yazılım uyumlu kalır.
- **Ara sürüm (1.x.0)**: yeni özellik ya da parça, önceki yapımlarla uyumlu.
- **Ana sürüm (2.0.0)**: yeni parça ya da yeni kablolama gerektiren değişiklik.

_`releases.json` dosyasından `tools/changelog.py` ile üretilir. Bu dosyayı değil, onu düzenle._

## Sıradaki: 1.1.0

Planlananlar; talep ve sorulardan. Önerin ya da takıldığın bir yer varsa: [konular](https://github.com/noqworks/gloam/issues).

### Donanım

- Baskı dosyalarının yanında düzenlenebilir CAD kaynakları.

### Yazılım

- Home Assistant'ta güncelleme bildirimi ve sürüm notu bağlantısı. İsteğe bağlı: cihaz onsuz da tamamen çalışır.

### Belgeler

- Her yapım adımı için yakın plan fotoğraf.

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
