# Native-Windows launcher for Blanket.
#
# Sets the GSettings schema dir, registers the compiled gresource bundle,
# then hands off to blanket.main. Works both when running from the source
# tree (winbuild/ staged next to the repo) and when frozen into an .exe.

import os
import sys

if getattr(sys, "frozen", False):
    # Packaged by PyInstaller: bundled data lives under sys._MEIPASS.
    STAGE = sys._MEIPASS  # type: ignore[attr-defined]
    REPO = STAGE
    # Our merged schema (system + Blanket) is in a private dir (see spec).
    schema_dir = os.path.join(STAGE, "blanket_schemas")
else:
    # Source run: this file lives in build-aux/windows/, assets in winbuild/.
    HERE = os.path.dirname(os.path.abspath(__file__))
    REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
    STAGE = os.path.join(REPO, "winbuild")
    sys.path.insert(0, REPO)
    schema_dir = os.path.join(STAGE, "share", "glib-2.0", "schemas")

# GSettings needs the compiled schema; prepend before GLib is first used so
# our dir wins over any bundled system-only schema source.
if os.path.isdir(schema_dir):
    existing = os.environ.get("GSETTINGS_SCHEMA_DIR", "")
    os.environ["GSETTINGS_SCHEMA_DIR"] = (
        schema_dir + os.pathsep + existing if existing else schema_dir
    )

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")
from gi.repository import Gio  # noqa: E402

resource = Gio.Resource.load(os.path.join(STAGE, "blanket.gresource"))
resource._register()

from blanket import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main.main("0.8.0"))
