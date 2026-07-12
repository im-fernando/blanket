# Blanket on Windows (native)

Blanket is a GTK4 / libadwaita app. On Windows it runs **natively** using the
GTK4 Windows backend (no WSL, no X server) with a bundled GStreamer runtime.

## What was ported

The codebase is Linux-first; these Linux-only integrations are guarded so the
app runs on Windows (see `blanket/main.py`, `blanket/preferences.py`):

- **MPRIS** (D-Bus session bus) is skipped when no bus is available.
- **`Gio.PowerProfileMonitor`** may be `None`; the signal connect is guarded.
- **Autostart** uses the `HKCU\...\Run` registry key instead of the
  freedesktop background portal.

A `desert` symbolic icon was added (the sound had none, showing a broken tile).

## Build requirements (MSYS2 UCRT64)

Install [MSYS2](https://www.msys2.org/), then from a **UCRT64** shell:

```bash
pacman -S --needed \
  mingw-w64-ucrt-x86_64-gtk4 \
  mingw-w64-ucrt-x86_64-libadwaita \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-gstreamer \
  mingw-w64-ucrt-x86_64-gst-plugins-base \
  mingw-w64-ucrt-x86_64-gst-plugins-good \
  mingw-w64-ucrt-x86_64-gst-plugins-bad \
  mingw-w64-ucrt-x86_64-blueprint-compiler \
  mingw-w64-ucrt-x86_64-pyinstaller \
  mingw-w64-ucrt-x86_64-pyinstaller-hooks-contrib \
  mingw-w64-ucrt-x86_64-nsis \
  mingw-w64-ucrt-x86_64-librsvg \
  mingw-w64-ucrt-x86_64-imagemagick
```

## Run from source (dev)

```bash
bash build-aux/windows/build.sh      # compile blueprint -> ui, gresource, gschema
bash build-aux/windows/run.sh        # launch with the UCRT64 python
```

## Build the installer

```bash
bash build-aux/windows/package.sh
```

Outputs:

- `dist-win/blanket/` — the frozen, self-contained app folder
- `dist-win/Blanket-0.8.0-Setup.exe` — NSIS installer (Start-menu + desktop
  shortcuts, uninstaller, Add/Remove Programs entry)

The installed app runs with no dependency on MSYS2.

## Files

| File | Purpose |
|------|---------|
| `build.sh` | Compile Blueprint → `.ui`, bundle `.gresource`, compile the (merged system + app) GSettings schema into `winbuild/`. |
| `blanket-run.py` | Entry point: sets `GSETTINGS_SCHEMA_DIR`, registers the gresource, calls `blanket.main`. Works from source and when frozen. |
| `blanket.spec` | PyInstaller spec: collects GI typelibs (Gtk/Gdk/Adw/Gst…), GStreamer plugins, gdk-pixbuf loaders, icons, and the app assets. |
| `installer.nsi` | NSIS installer script. |
| `package.sh` | One-shot: assets → icon → PyInstaller → installer. |
| `run.sh` | Convenience wrapper to run from source. |

## Notes / gotchas

- The merged GSettings schema is bundled into a **private** `blanket_schemas/`
  dir (not `share/glib-2.0/schemas`) so PyInstaller's own hook — which drops the
  *system* schema there — can't overwrite it.
- PyInstaller under an MSYS2 login shell needs a resolvable Windows home dir:
  `export USERPROFILE=...` before running (handled by `package.sh`).
