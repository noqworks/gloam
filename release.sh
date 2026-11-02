#!/bin/sh
# Release build: checks versions, writes the changelog, compiles the firmware and writes release artifacts to OUT
# (default ./dist/<version>): factory/ota firmware, web installer manifest, release notes, source zip.
#   sh release.sh            # version from firmware/gloam.yaml
set -eu
cd "$(dirname "$0")"
V=$(sed -n 's/^ *version: "\(.*\)"/\1/p' firmware/gloam.yaml | head -1)
OUT=${OUT:-dist/$V}
ESPHOME=${ESPHOME:-esphome}
python3 tools/changelog.py --check
python3 tools/changelog.py
python3 portal/build.py
TMP=$(mktemp -d)
sed "s#source: github://noqworks/gloam@main#source: { type: local, path: $(pwd)/components }#" firmware/gloam.yaml > "$TMP/gloam.yaml"
"$ESPHOME" compile "$TMP/gloam.yaml"
B="$TMP/.esphome/build/gloam/.pioenvs/gloam"
mkdir -p "$OUT"
cp "$B/firmware.factory.bin" "$OUT/gloam-$V.factory.bin"
cp "$B/firmware.ota.bin" "$OUT/gloam-$V.ota.bin"
cat > "$OUT/manifest.json" <<JSON
{
  "name": "Gloam",
  "version": "$V",
  "home_assistant_domain": "esphome",
  "new_install_prompt_erase": true,
  "builds": [{ "chipFamily": "ESP8266", "parts": [{ "path": "gloam-$V.factory.bin", "offset": 0 }] }]
}
JSON
git archive --format=zip --prefix="gloam-$V/" -o "$OUT/gloam-$V-source.zip" HEAD 2>/dev/null \
  || (cd .. && zip -qr "$OLDPWD/$OUT/gloam-$V-source.zip" "$(basename "$OLDPWD")" -x '*/dist/*' '*/.esphome/*' '*/.git/*')
python3 tools/changelog.py --notes "$V" > "$OUT/release-notes.md"
cp releases.json "$OUT/releases.json"
rm -rf "$TMP"
ls -la "$OUT"
