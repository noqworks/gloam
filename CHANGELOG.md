# Changelog

Türkçe: [CHANGELOG.tr.md](CHANGELOG.tr.md)

All changes to Gloam, newest first. Versions are MAJOR.MINOR.PATCH:

- **Patch (1.0.x)**: fixes. Parts and firmware stay compatible.
- **Minor (1.x.0)**: new features or parts, compatible with earlier builds.
- **Major (2.0.0)**: changes that need new parts or new wiring.

_Generated from `releases.json` by `tools/changelog.py`. Edit that file, not this one._

## Next: 1.1.0

Planned, from requests and questions. Suggest something or tell us what you hit: [issues](https://github.com/noqworks/gloam/issues).

### Hardware

- Editable CAD sources next to the print files.

### Firmware

- Update notice in Home Assistant with a link to the release notes. Optional: the device works fully without it.

### Documentation

- A close-up photo for every build step.

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
