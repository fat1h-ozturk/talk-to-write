#!/bin/bash
# ==============================================================================
# Talk-to-Write: Double-Click Installer for macOS Finder
# ==============================================================================

cd "$(dirname "$0")"
chmod +x install.sh update.sh bin/talk-to-write 2>/dev/null || true
./install.sh

echo ""
echo "Pencereyi kapatmak icin Enter'a basin..."
read -r
