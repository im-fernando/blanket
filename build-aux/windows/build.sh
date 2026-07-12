#!/usr/bin/env bash
#
# Build Blanket's compiled assets (UI, gresource, gschema) for a native
# Windows run. Meant to be run from an MSYS2 UCRT64 shell that has:
#   gtk4, libadwaita, python-gobject, gstreamer + plugins,
#   blueprint-compiler, glib2-devel (glib-compile-resources/-schemas).
#
# Output is staged into ./winbuild so it can be run in place or packaged.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RES="$ROOT/data/resources"
BUILD="$ROOT/winbuild"
UI="$BUILD/ui"
SCHEMADIR="$BUILD/share/glib-2.0/schemas"

echo ">> Cleaning $BUILD"
rm -rf "$BUILD"
mkdir -p "$UI" "$SCHEMADIR"

echo ">> Compiling Blueprint (.blp -> .ui)"
blueprint-compiler batch-compile "$UI" "$RES" \
  "$RES"/about.blp \
  "$RES"/preferences.blp \
  "$RES"/preset-chooser.blp \
  "$RES"/preset-dialog.blp \
  "$RES"/preset-row.blp \
  "$RES"/sound-context-menu.blp \
  "$RES"/shortcuts.blp \
  "$RES"/sound-item.blp \
  "$RES"/volume-row.blp \
  "$RES"/window.blp \
  "$RES"/sound-rename-dialog.blp

echo ">> Bundling gresource"
# .ui come from $UI (generated); css/svg/ogg come from $RES (source tree).
glib-compile-resources "$RES/blanket.gresource.xml" \
  --target="$BUILD/blanket.gresource" \
  --sourcedir="$UI" \
  --sourcedir="$RES"

echo ">> Compiling GSettings schema (app + system, merged into one file)"
# Bundle the system schemas (org.gtk.*, etc.) together with the app schema so
# a single gschemas.compiled satisfies both GTK/Adwaita and Blanket.
PREFIX="${MINGW_PREFIX:-/ucrt64}"
cp "$PREFIX"/share/glib-2.0/schemas/*.gschema.xml "$SCHEMADIR/" 2>/dev/null || true
cp "$PREFIX"/share/glib-2.0/schemas/*.enums.xml "$SCHEMADIR/" 2>/dev/null || true
cp "$ROOT/data/com.rafaelmardojai.Blanket.gschema.xml" "$SCHEMADIR/"
glib-compile-schemas "$SCHEMADIR"

echo ">> Done. Staged in: $BUILD"
