#!/bin/bash
# WildWard Listen installer for macOS. Double-click this file in Finder (first time: right-click > Open).
#
# Everything goes into this folder: a private Python (via uv) and the app's packages, nothing
# system-wide, no admin password. Needs internet once (about 1 GB including the Perch 2.0 model).
set -e
cd "$(dirname "$0")"
APP="$(pwd)"
TOOLS="$APP/.tools"
UV_VERSION="0.12.19"
export UV_PYTHON_INSTALL_DIR="$TOOLS/python" UV_CACHE_DIR="$TOOLS/cache"
mkdir -p "$TOOLS"

step() { printf "\n==> %s\n" "$1"; }

echo "WildWard Listen setup"
echo "Installing into $APP"

if [ ! -x "$TOOLS/uv" ]; then
  step "Downloading the uv package manager $UV_VERSION"
  if [ "$(uname -m)" != "arm64" ]; then
    # TensorFlow, which runs the Perch model, only ships Mac builds for Apple Silicon
    echo "Sorry: WildWard Listen needs a Mac with Apple Silicon (M1 or newer). On this Mac, please use a Windows PC instead."
    read -r -p "Press Enter to close."
    exit 1
  fi
  ARCH="aarch64-apple-darwin"
  curl -fsSL "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$ARCH.tar.gz" | tar -xz -C "$TOOLS" --strip-components 1
fi

if [ ! -x "$APP/.venv/bin/python" ]; then
  step "Setting up a private Python 3.12"
  "$TOOLS/uv" venv "$APP/.venv" --python 3.12
fi

step "Installing WildWard Listen's packages (the biggest step, a few minutes)"
"$TOOLS/uv" pip install --python "$APP/.venv/bin/python" -r "$APP/requirements.txt"

step "Downloading the Perch 2.0 sound model (about 400 MB, once) so Listen works offline in the field"
"$APP/.venv/bin/python" -c "from listen import embed; embed._load(); print('Perch 2.0 ready')" \
  || echo "The model download didn't finish. Listen will try again on its first scan (needs internet then)."

chmod +x "$APP/WildWard Listen.command"
echo
echo "Done. Double-click 'WildWard Listen.command' in this folder to start."
read -r -p "Press Enter to close."
