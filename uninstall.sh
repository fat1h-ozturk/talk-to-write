#!/usr/bin/env bash
# ==============================================================================
# Talk-to-Write: Cross-Platform Uninstaller (Linux & macOS)
# Completely removes desktop entries, autostart, icons, config, and virtualenv.
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================"
echo "🗑️  Talk-to-Write Kaldırma Aracı (Uninstaller)"
echo "======================================================"
echo ""
echo "Bu işlem Talk-to-Write uygulamasını sisteminizden kaldıracaktır:"
echo "  - Çalışan uygulama süreçleri kapatılacak"
echo "  - Uygulama menüsü ve otomatik başlatma kayıtları silinecek"
echo "  - Simgeler ve yapılandırma/veri dizinleri temizlenecek"
echo "  - Sanal ortam (.venv) silinecek"
echo ""
read -p "Devam etmek istiyor musunuz? [e/H]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[eEyY]$ ]]; then
    echo "Kaldırma işlemi iptal edildi."
    exit 0
fi

echo ""
echo "1/4 Çalışan Talk-to-Write süreçleri durduruluyor..."
pkill -f "talk_to_write" 2>/dev/null || true

echo "2/4 Sistem entegrasyonu ve ayarlar temizleniyor..."
if [ -f ".venv/bin/python" ]; then
    .venv/bin/python -m talk_to_write --purge 2>/dev/null || true
fi

# Platform-specific manual cleanup fallback
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    rm -rf "$HOME/Applications/Talk-to-Write.app" 2>/dev/null || true
    if [ -f "$HOME/Library/LaunchAgents/com.talktowrite.app.plist" ]; then
        launchctl unload "$HOME/Library/LaunchAgents/com.talktowrite.app.plist" 2>/dev/null || true
        rm -f "$HOME/Library/LaunchAgents/com.talktowrite.app.plist" 2>/dev/null || true
    fi
    rm -rf "$HOME/Library/Application Support/talk-to-write" 2>/dev/null || true
else
    # Linux
    DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
    CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

    rm -f "$DATA_HOME/applications/talk-to-write.desktop" 2>/dev/null || true
    rm -f "$CONFIG_HOME/autostart/talk-to-write.desktop" 2>/dev/null || true
    rm -f "$DATA_HOME/icons/hicolor/scalable/apps/talk-to-write.svg" 2>/dev/null || true
    rm -f "$DATA_HOME/icons/hicolor/"*x*/apps/talk-to-write.png 2>/dev/null || true
    rm -rf "$CONFIG_HOME/talk-to-write" 2>/dev/null || true
    rm -f "/tmp/talk-to-write.sock" 2>/dev/null || true

    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$DATA_HOME/applications" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -q -t -f "$DATA_HOME/icons/hicolor" 2>/dev/null || true
    fi
fi

echo "3/4 Sanal ortam ve derleme artıkları siliniyor..."
rm -rf .venv .pytest_cache talk_to_write.egg-info build dist __pycache__ 2>/dev/null || true

echo "4/4 Sistem temizliği tamamlandı!"
echo ""
read -p "Proje klasörünün kendisini de ($DIR) tamamen silmek istiyor musunuz? [e/H]: " DEL_FOLDER
if [[ "$DEL_FOLDER" =~ ^[eEyY]$ ]]; then
    echo "Proje klasörü siliniyor..."
    cd ..
    rm -rf "$DIR"
    echo "✓ Talk-to-Write ve tüm dosyaları sistemden tamamen kaldırıldı."
else
    echo "======================================================"
    echo "✓ Talk-to-Write sistemden başarıyla kaldırıldı."
    echo "  Proje kaynak kodları korundu."
    echo "======================================================"
fi
