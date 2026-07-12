#!/usr/bin/env bash
#
# One-shot native-Windows packaging for Blanket.
# Run from an MSYS2 UCRT64 shell (MSYSTEM=UCRT64) at the repo root:
#   bash build-aux/windows/package.sh
#
# Produces:
#   dist-win/blanket/                     frozen app (folder)
#   dist-win/Blanket-<version>-Setup.exe  NSIS installer
#
# Requires (pacman -S, ucrt64): gtk4 libadwaita python-gobject gstreamer
#   gst-plugins-{base,good,bad} blueprint-compiler pyinstaller
#   pyinstaller-hooks-contrib nsis librsvg imagemagick
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# PyInstaller (native python) needs a resolvable Windows home dir.
: "${USERPROFILE:=C:\\Users\\$USER}"
export USERPROFILE

echo "==> [1/4] Compiling assets (blueprint + gresource + gschema)"
bash build-aux/windows/build.sh

echo "==> [2/4] Generating app icon (.ico)"
if command -v rsvg-convert >/dev/null && command -v magick >/dev/null; then
  tmp="$(mktemp -d)"
  for s in 16 24 32 48 64 128 256; do
    rsvg-convert -w "$s" -h "$s" brand/logo.svg -o "$tmp/icon-$s.png"
  done
  magick "$tmp"/icon-16.png "$tmp"/icon-24.png "$tmp"/icon-32.png \
         "$tmp"/icon-48.png "$tmp"/icon-64.png "$tmp"/icon-128.png \
         "$tmp"/icon-256.png build-aux/windows/blanket.ico
  rm -rf "$tmp"
fi

echo "==> [3/4] Freezing app with PyInstaller"
rm -rf build-win dist-win
pyinstaller --noconfirm --distpath dist-win --workpath build-win \
  build-aux/windows/blanket.spec

echo "==> [4/4] Building NSIS installer"
if command -v makensis >/dev/null; then
  ( cd build-aux/windows && makensis installer.nsi )
else
  echo "makensis not found; skipping installer (frozen app is in dist-win/blanket)"
fi

echo "==> Done."
ls -la dist-win/*.exe 2>/dev/null || true
