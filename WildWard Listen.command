#!/bin/bash
# Starts WildWard Listen on macOS in its own window. Close that window to stop it.
cd "$(dirname "$0")"
if [ ! -x ".venv/bin/python" ]; then
  echo "WildWard Listen is not installed yet. Double-click install-mac.command first."
  read -r -p "Press Enter to close."
  exit 1
fi
exec ".venv/bin/python" run.py --app "$@"
