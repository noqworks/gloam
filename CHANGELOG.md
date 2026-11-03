# Changelog

Türkçe: [CHANGELOG.tr.md](CHANGELOG.tr.md)

All changes to Gloam, newest first. Versions are MAJOR.MINOR.PATCH:

- **Patch (1.0.x)**: fixes. Parts and firmware stay compatible.
- **Minor (1.x.0)**: new features or parts, compatible with earlier builds.
- **Major (2.0.0)**: changes that need new parts or new wiring.

_Generated from `releases.json` by `tools/changelog.py`. Edit that file, not this one._

## Next: 1.3.0

Planned, from requests and questions. Suggest something or tell us what you hit: [issues](https://github.com/noqworks/gloam/issues).

### Firmware

- Update notice in Home Assistant with a link to the release notes. Optional: the device works fully without it.

### Documentation

- A close-up photo for every build step.

## 1.2.0 · 2026-11-03

Works without Home Assistant: the device serves its own control page, a wall switch lights it and the schedule runs on the device. Home Assistant stays optional and works at the same time.

### Firmware

- Control page on the device: open http://gloam-xxxxxx.local on the home network for both channels, brightness, effects, schedule and power-on behaviour. No app, account or internet needed; it can be added to the phone's home screen. (@umut)
- Home Assistant and the control page work at the same time on the same lights; a change on one shows up on the other at once.
- Power on: light up with the last scene (default, so a plain wall switch works), as before the power cut, or stay off.
- Daily schedule on the device: at the on time the last scene rises over the fade-in time (20 minutes by default), at the off time it fades out. The clock comes from the internet; the time zone is taken from the phone on the control page.

### Setup

- The last step of the setup page shows the device's own address, with Home Assistant as the optional second step.

**Compatibility:** Hardware and wiring unchanged. Update with the browser installer or ESPHome; Wi-Fi and light settings are kept (do not choose erase). After the update power coming back lights the last scene; choose "As before the power cut" on the control page for the old behaviour.
**Thanks:** @umut (öneri: Home Assistant olmadan da çalışsın)
**Files:** [source and print files (zip)](https://open.noq.works/files/gloam/gloam-1.2.0-source.zip) · [GitHub release](https://github.com/noqworks/gloam/releases/tag/v1.2.0)

## 1.1.0 · 2026-11-03

A new controller enclosure built around the real parts, and editable CAD sources for every printed part.

### Hardware

- Controller enclosure redesigned around the parts in the list: Mean Well LRS-75-12, a 50 × 70 mm perfboard, a PG11 mains gland and a PG7 LED gland on the same end wall.
- A divider and a rib under the lid keep the mains terminals and wiring apart from the 12 V side.
- Lid with four M3 countersunk screws in heat-set inserts, a locating lip, vents above the power supply and pads that hold it down; a USB slot for the D1 mini; two mounting ears.
- The inner plate is gone: the perfboard sits on standoffs in the box floor.
- Editable CAD sources (CadQuery) for every printed part, STEP files that open in any CAD program, and an assembly STEP with the power supply, perfboard and glands for checking the fit.
- Fixture body and diffuser rebuilt as parametric models with the same dimensions; parts printed from 1.0.0 still fit.

**Compatibility:** Fixtures, firmware and wiring are unchanged. The controller is a new two-part set (box and lid) that needs a PG11 and a PG7 gland, four M3 heat-set inserts, four M3 × 8 countersunk screws and four M2 × 6 screws; a controller built from 1.0.0 keeps working.
**Files:** [source and print files (zip)](https://open.noq.works/files/gloam/gloam-1.1.0-source.zip) · [GitHub release](https://github.com/noqworks/gloam/releases/tag/v1.1.0)

## 1.0.0 · 2026-11-02

First open release.

### Hardware

- Oval fixture body and plain diffuser; three-part controller box (box, lid, inner plate) for M3 heat-set inserts.
- Since the prototype: the cable entry at both ends of the body is a 7.5 × 7 mm arch for ~6 mm round cable.
- Since the prototype: in the controller box, the four standoffs that overlapped the corner screw moved 9 mm down; inner plate holes are M3 clearance (Ø3.4).

### Firmware

- ESPHome firmware: amber and warm white dimmed separately, effects on the device, Home Assistant discovery with the API key set on first connection.
- Setup: NOQ Open setup page in Turkish and English on the device's own network, 30-minute setup window, Wi-Fi over USB (Improv), factory reset with five power cycles.

### Setup

- Browser installer: write the firmware and set Wi-Fi from open.noq.works/install/gloam, nothing to install.

### Documentation

- Wiring diagram, parts list with suppliers in Turkey, step-by-step build with checks.

**Compatibility:** First release.
**Files:** [source and print files (zip)](https://open.noq.works/files/gloam/gloam-1.0.0-source.zip) · [GitHub release](https://github.com/noqworks/gloam/releases/tag/v1.0.0)
