<p align="center"><img src="docs/noqopen.svg" alt="NOQ Open" height="40"></p>

# Gloam

Amber and warm white light line for ceiling beams. Small 3D-printed fixtures, two dimmable 12 V COB channels, one ESP8266. Works on its own from a phone or a wall switch; Home Assistant is optional. No cloud, no account.

**Project page, photos and browser installer:** https://open.noq.works/projects/gloam/ · [Türkçe](README.tr.md)

## What it does

- **Amber (~1800 K) and warm white (3000 K)** in every fixture, dimmed separately or together.
- **Effects** on the device: candle, fireplace, breathe, flicker (amber) and candle, cloud, breathe (warm white).
- **Works on its own.** On your home network the device serves its own control page at `http://gloam-xxxxxx.local`: both channels, brightness, effects, a daily schedule and what happens when power comes on. No app, account or internet needed.
- **Wall switch.** By default power coming on lights the last scene, so a plain switch on the mains side works (or choose *as before the power cut* / *stay off*).
- **Home Assistant, optional and at the same time.** Home Assistant discovers it over ESPHome; the API key is set by Home Assistant on first connection, so no secret is baked into the firmware. The control page keeps working next to it; both see each other's changes at once.
- **Its own setup screen.** On first boot it opens a `gloam-xxxxxx` network with the NOQ Open Wi-Fi setup page. Once it has joined your network it never opens that network again.

## Repository

| Path | Contents |
|---|---|
| `firmware/gloam.yaml` | ESPHome configuration (pins, effects, provisioning) |
| `components/noqopen_portal/` | ESPHome external component: the NOQ Open setup page on the captive portal and the control page on the home network |
| `portal/` | Page sources: `tokens.css` → `components.css` → setup page `index.html` + `app.js`, control page `panel.html` + `panel.css` + `panel.js`; `build.py` inlines and gzips them into `components/noqopen_portal/portal_page.h` and `panel_page.h` |
| `hardware/3mf/` | Bambu Studio print projects for the Bambu Lab A1 (0.4 mm nozzle), sliced and ready to print: `gloam-fixture-a1.3mf` (16 bodies and 16 diffusers on four plates), `gloam-controller-a1.3mf` (box and lid). Bambu Studio converts them for other printers |
| `hardware/stl/` | Print files, ready to slice |
| `hardware/step/` | STEP files for any CAD program, plus a controller assembly with the power supply and perfboard |
| `hardware/cad/` | Editable CadQuery sources for every printed part; parameters, hardware and print settings in [its README](hardware/cad/README.md) |
| `releases.json` | Versions and release notes; `tools/changelog.py` writes `CHANGELOG.md` / `CHANGELOG.tr.md` from it |
| `docs/wiring.svg` | Wiring diagram |

## Build

Parts, tools, print settings and step-by-step build with photos are on the [project page](https://open.noq.works/projects/gloam/). In short:

1. Print one body and one diffuser per fixture (PETG; body white, diffuser clear) and the two-part controller box (box and lid).
2. Fit 5 cm of amber and 5 cm of warm white COB strip into each body, plus ends joined.
3. Run 3-core 0.5 mm² cable through the fixtures: +12 V shared, amber − and warm white − separate.
4. Wire the controller as in `docs/wiring.svg`: D1 → ULN2003A IN1+IN2 (amber), D2 → IN3+IN4 (warm white), COM to +12 V, 12 → 5 V step-down for the D1 mini.
5. Close the controller: Mean Well LRS-75-12 in its corner stops, perfboard on the four standoffs, PG11 gland for mains and PG7 for the LED line, lid with four M3 screws in heat-set inserts. Full hardware list in [hardware/cad](hardware/cad/README.md).

The ULN2003A carries about 1 m of COB strip per colour. For longer lines use one logic-level MOSFET per colour; the firmware is the same.

## Firmware

**Browser:** open https://open.noq.works/install/gloam/ in Chrome or Edge on a desktop. The setup wizard flashes the board over USB and joins Wi-Fi; then open `http://gloam-xxxxxx.local` (or add it to Home Assistant).

**ESPHome:** adopt the device in ESPHome Builder (it is announced with `dashboard_import`), or build it yourself:

```bash
esphome run firmware/gloam.yaml
```

Change pins or PWM frequency with the `substitutions` at the top of the file.

**Setup and control pages:** edit files in `portal/` (`index.html` + `app.js` setup page, `panel.html` + `panel.js` + `panel.css` control page), then run `python3 portal/build.py` and rebuild the firmware. The control page talks to the stock ESPHome web server API (`/events`, `/light/Amber/turn_on`, …).

### Setup and reset

- Unconfigured: the device opens `gloam-xxxxxx` and keeps it open for 30 minutes (provisioning window). Power-cycle to reopen.
- Configured: no setup network, ever. Wi-Fi can still be changed over USB (Improv serial).
- Factory reset: cut and restore power 5 times, each within 10 seconds, or use *Reset to factory settings* on the control page (or *Factory reset* in Home Assistant).

## Versions

Versions are MAJOR.MINOR.PATCH: patch = fixes, minor = compatible new features or parts, major = needs new parts or wiring. What changed in each version and what is planned next: [CHANGELOG.md](CHANGELOG.md).

## Licence

- Firmware, setup page and component: [MIT](LICENSE)
- Print files, wiring diagram and documentation: [CC BY 4.0](LICENSE-HARDWARE)

Attribution: *Gloam, NOQ Open · open.noq.works/projects/gloam*

Made one or improved it? Open an [issue](https://github.com/noqworks/gloam/issues) or write to hello@noq.works.
