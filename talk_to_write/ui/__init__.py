"""
UI components for Talk-to-Write (Floating Pill, System Tray, Settings).
"""

from .pill import FloatingPill
from .tray import TrayIcon
from .settings import SettingsDialog

__all__ = ["FloatingPill", "TrayIcon", "SettingsDialog"]
