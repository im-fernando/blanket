#!/usr/bin/env bash
# Run Blanket from the staged winbuild assets using the UCRT64 Python.
# Invoke from an MSYS2 UCRT64 shell (MSYSTEM=UCRT64) after build.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python "$ROOT/build-aux/windows/blanket-run.py" "$@"
