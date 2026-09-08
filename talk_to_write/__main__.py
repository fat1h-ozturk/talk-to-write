"""
CLI and Desktop entry point for Talk-to-Write.
"""

import argparse
import sys
from PySide6.QtWidgets import QApplication

from . import __version__
from .app import TalkToWriteApp
from .hotkey import send_ipc_toggle

def main():
    parser = argparse.ArgumentParser(
        prog="talk-to-write",
        description="Talk-to-Write: Ultra-fast dictation assistant for Linux."
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Send toggle trigger to running Talk-to-Write instance."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Talk-to-Write {__version__}"
    )

    args = parser.parse_args()

    # If --toggle was passed, trigger running instance via IPC and exit
    if args.toggle:
        success = send_ipc_toggle()
        if success:
            print("[Talk-to-Write] Kayıt durumu değiştirildi (Toggle sinyali iletildi).")
            sys.exit(0)
        else:
            print("[Talk-to-Write] Çalışan bir Talk-to-Write uygulaması bulunamadı. Lütfen önce uygulamayı başlatın.")
            sys.exit(1)

    # Launch GUI Application
    q_app = QApplication(sys.argv)
    q_app.setApplicationName("Talk-to-Write")
    q_app.setApplicationDisplayName("Talk-to-Write")
    q_app.setQuitOnLastWindowClosed(False)

    app = TalkToWriteApp(q_app)

    print("=" * 60)
    print(f"🎙️  Talk-to-Write v{__version__} Başlatıldı!")
    print("📌  Kısayol: Ctrl+Alt+Space (veya 'talk-to-write --toggle')")
    print("⚙️  Sistem çekmecesi (System Tray) üzerinden ayarlara ulaşabilirsiniz.")
    print("=" * 60)

    sys.exit(q_app.exec())

if __name__ == "__main__":
    main()
