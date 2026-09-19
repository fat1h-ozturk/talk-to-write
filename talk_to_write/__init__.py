"""
Talk-to-Write: High-performance, low-latency dictation and voice-to-text assistant.
Cross-platform support for Linux, Windows, and macOS.
"""

__version__ = "0.2.0"

import sys

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
