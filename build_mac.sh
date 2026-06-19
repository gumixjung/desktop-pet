#!/bin/bash
# Build Desktop Pet → DesktopPet.app (macOS)

set -e
cd "$(dirname "$0")"

source venv/bin/activate
pip install pyinstaller --quiet

pyinstaller \
  --noconfirm \
  --windowed \
  --name "DesktopPet" \
  --add-data "sprites:sprites" \
  --hidden-import "webview.platforms.cocoa" \
  --hidden-import "PIL._tkinter_finder" \
  desktop_pet.py

echo ""
echo "✅  Done! App is at: dist/DesktopPet.app"
echo "    Double-click to run, or: open dist/DesktopPet.app"
