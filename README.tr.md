<p align="center"><img src="docs/noqopen.svg" alt="NOQ Open" height="40"></p>

# Gloam

Tavan kirişleri için amber ve gün ışığı aydınlatma hattı. 3D baskı küçük armatürler, iki kanal kısılabilir 12 V COB LED, tek ESP8266 ve Home Assistant. Bulut yok, hesap yok.

**Proje sayfası, fotoğraflar ve tarayıcıdan yükleme:** https://open.noq.works/tr/projeler/gloam/ · [English](README.md)

## Ne yapar

- Her armatürde **amber (~1800 K) ve gün ışığı (3000 K)**; ayrı ayrı ya da birlikte kısılır.
- Cihazın içinde çalışan **efektler**: mum, şömine, nefes, titreşim (amber); mum, bulut, nefes (gün ışığı).
- **Yerel çalışır.** Home Assistant cihazı ESPHome ile bulur; şifreleme anahtarını ilk bağlantıda Home Assistant kurar, yazılımın içinde sır yoktur.
- **Kendi kurulum ekranı.** İlk açılışta `gloam-xxxxxx` ağını ve NOQ Open Wi-Fi kurulum ekranını açar. Ev ağına bağlandıktan sonra bu ağı bir daha açmaz.

## Depo

| Yol | İçerik |
|---|---|
| `firmware/gloam.yaml` | ESPHome yapılandırması (pinler, efektler, kurulum penceresi) |
| `components/noqopen_portal/` | Kurulum ağında NOQ Open kurulum ekranını sunan ESPHome bileşeni |
| `portal/` | Kurulum ekranı kaynağı: `tokens.css` → `components.css` → `index.html` + `app.js`; `build.py` hepsini tek sayfada birleştirip `components/noqopen_portal/portal_page.h` dosyasına sıkıştırır |
| `hardware/stl/` | Baskı dosyaları |
| `releases.json` | Sürümler ve sürüm notları; `tools/changelog.py` bundan `CHANGELOG.md` / `CHANGELOG.tr.md` üretir |
| `docs/wiring.svg` | Bağlantı şeması |

## Yapım

Bileşenler, araçlar, baskı ayarları ve fotoğraflı adımlar [proje sayfasında](https://open.noq.works/tr/projeler/gloam/). Kısaca:

1. Her armatür için bir gövde ve bir difüzör bas (PETG; gövde beyaz, difüzör şeffaf) ve üç parçalı denetleyici kutusu.
2. Her gövdeye 5 cm amber ve 5 cm gün ışığı COB şerit yerleştir, artı uçları birleştir.
3. 3 × 0,5 mm² kabloyu armatürlerden geçir: +12 V ortak, amber − ve gün ışığı − ayrı.
4. Denetleyiciyi `docs/wiring.svg` şemasına göre kablola: D1 → ULN2003A IN1+IN2 (amber), D2 → IN3+IN4 (gün ışığı), COM → +12 V, D1 mini için 12 → 5 V düşürücü.

ULN2003A renk başına yaklaşık 1 m COB şerit taşır. Daha uzun hatlarda her renk için bir mantık seviyeli MOSFET kullan; yazılım aynı kalır.

## Yazılım

**Tarayıcı:** https://open.noq.works/tr/kurulum/gloam/ adresini masaüstünde Chrome ya da Edge ile aç. Kurulum sihirbazı kartı USB ile yükler, Wi-Fi'ye bağlar ve Home Assistant'a devreder.

**ESPHome:** cihazı ESPHome Builder'da benimse (`dashboard_import` ile duyurulur) ya da kendin derle:

```bash
esphome run firmware/gloam.yaml
```

Pinleri ve PWM frekansını dosyanın başındaki `substitutions` ile değiştir.

**Kurulum ekranı:** `portal/` altındaki dosyaları düzenle, `python3 portal/build.py` çalıştır, yazılımı yeniden derle.

### Kurulum ve sıfırlama

- Kurulmamış cihaz `gloam-xxxxxx` ağını açar ve 30 dakika açık tutar. Kaçırırsan gücünü kesip aç.
- Kurulmuş cihaz kurulum ağını hiç açmaz. Wi-Fi USB üzerinden (Improv) yine değiştirilebilir.
- Fabrika ayarları: gücü 10 saniyeden kısa aralıklarla 5 kez kesip aç ya da Home Assistant'ta *Factory reset*'e bas.

## Sürümler

Sürümler ANA.ARA.YAMA biçiminde: yama = düzeltme, ara sürüm = uyumlu yeni özellik ya da parça, ana sürüm = yeni parça ya da kablolama gerektirir. Her sürümde ne değişti, sıradakinde ne var: [CHANGELOG.tr.md](CHANGELOG.tr.md).

## Lisans

- Yazılım, kurulum ekranı ve bileşen: [MIT](LICENSE)
- Baskı dosyaları, bağlantı şeması ve belgeler: [CC BY 4.0](LICENSE-HARDWARE)

Kaynak gösterme: *Gloam, NOQ Open · open.noq.works/projects/gloam*

Ürettin ya da geliştirdin mi? GitHub'da bir [konu](https://github.com/noqworks/gloam/issues) aç ya da hello@noq.works adresine yaz.
