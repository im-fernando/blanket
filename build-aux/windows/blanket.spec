# PyInstaller spec for a native-Windows Blanket bundle.
# Run from an MSYS2 UCRT64 shell:  pyinstaller build-aux/windows/blanket.spec
import glob
import os
import sys

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks.gi import get_gi_typelibs

PREFIX = sys.prefix                       # /ucrt64 when run under UCRT64 python
ROOT = os.path.abspath(os.getcwd())       # repo root (run from there)
WINBUILD = os.path.join(ROOT, "winbuild")

binaries = []
datas = []
hiddenimports = []

# --- GObject-introspection modules with their full transitive closure ---
# (typelibs + shared libs). Adw's hook alone misses Gtk/Gdk, so pull them
# all explicitly.
for _ns, _ver in (
    ("Gtk", "4.0"),
    ("Gdk", "4.0"),
    ("Adw", "1"),
    ("Gst", "1.0"),
    ("GstAudio", "1.0"),
    ("GstPbutils", "1.0"),
    ("GdkPixbuf", "2.0"),
):
    _b, _d, _h = get_gi_typelibs(_ns, _ver)
    binaries += _b
    datas += _d
    hiddenimports += _h

# --- App compiled assets (gresource + app GSettings schema) ---
# Put our merged schema (system + Blanket) in a private dir so PyInstaller's
# own gi hook, which writes the *system* schema into share/glib-2.0/schemas,
# can't overwrite it. The launcher points GSETTINGS_SCHEMA_DIR here.
datas += [
    (os.path.join(WINBUILD, "blanket.gresource"), "."),
    (os.path.join(WINBUILD, "share", "glib-2.0", "schemas", "gschemas.compiled"),
     "blanket_schemas"),
]

# --- GStreamer plugins (bundle all; Blanket decodes ogg/vorbis + mixing) ---
gst_dir = os.path.join(PREFIX, "lib", "gstreamer-1.0")
for dll in glob.glob(os.path.join(gst_dir, "*.dll")):
    binaries.append((dll, os.path.join("lib", "gstreamer-1.0")))
# GStreamer helper exes (plugin scanner)
for exe in ("gst-plugin-scanner.exe",):
    p = os.path.join(PREFIX, "bin", exe)
    if os.path.exists(p):
        binaries.append((p, "bin"))

# --- gdk-pixbuf loaders (needed to render SVG/PNG icons) ---
pb_root = os.path.join(PREFIX, "lib", "gdk-pixbuf-2.0", "2.10.0")
for dll in glob.glob(os.path.join(pb_root, "loaders", "*.dll")):
    binaries.append((dll, os.path.join("lib", "gdk-pixbuf-2.0", "2.10.0", "loaders")))
cache = os.path.join(pb_root, "loaders.cache")
if os.path.exists(cache):
    datas.append((cache, os.path.join("lib", "gdk-pixbuf-2.0", "2.10.0")))

# NOTE: system GSettings schemas (org.gtk.*) are merged into the app's
# gschemas.compiled by build.sh, so we bundle only that single file (above).

# --- Adwaita icon theme (fallback stock icons) ---
for theme in ("Adwaita", "hicolor"):
    tdir = os.path.join(PREFIX, "share", "icons", theme)
    if os.path.isdir(tdir):
        datas.append((tdir, os.path.join("share", "icons", theme)))

# --- GTK4 settings/schemas dir extras ---
glib_share = os.path.join(PREFIX, "share", "glib-2.0")
for sub in ("gettext",):
    d = os.path.join(glib_share, sub)
    # not strictly required; skip if missing

hiddenimports += collect_submodules("gi")

a = Analysis(
    [os.path.join(ROOT, "build-aux", "windows", "blanket-run.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="blanket",
    debug=False,
    strip=False,
    upx=False,
    console=False,               # GUI app: no console window
    icon=os.path.join(ROOT, "build-aux", "windows", "blanket.ico")
        if os.path.exists(os.path.join(ROOT, "build-aux", "windows", "blanket.ico"))
        else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="blanket",
)
