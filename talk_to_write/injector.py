"""
Text injection engine for Wayland / Linux.
Copies formatted text to clipboard and synthesizes Ctrl+V paste into the active window.
"""

import shutil
import subprocess
import time
from typing import Optional

class TextInjector:
    """Injects text into the currently active window via clipboard and ydotool."""

    def __init__(self, restore_clipboard: bool = False):
        self.restore_clipboard = restore_clipboard
        self.has_wl_copy = shutil.which("wl-copy") is not None
        self.has_wl_paste = shutil.which("wl-paste") is not None
        self.has_xclip = shutil.which("xclip") is not None
        self.has_ydotool = shutil.which("ydotool") is not None

    def get_current_clipboard(self) -> Optional[str]:
        """Reads current clipboard text if available."""
        if self.has_wl_paste:
            try:
                res = subprocess.run(["wl-paste", "--no-newline"], capture_output=True, text=True, timeout=1)
                if res.returncode == 0:
                    return res.stdout
            except Exception:
                pass
        return None

    def set_clipboard(self, text: str) -> bool:
        """Sets clipboard content via wl-copy or xclip."""
        if self.has_wl_copy:
            try:
                subprocess.run(
                    ["wl-copy"],
                    input=text.encode("utf-8"),
                    check=True,
                    timeout=2
                )
                return True
            except Exception as e:
                print(f"[Injector] wl-copy error: {e}")

        if self.has_xclip:
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=True,
                    timeout=2
                )
                return True
            except Exception as e:
                print(f"[Injector] xclip error: {e}")

        return False

    def simulate_paste(self) -> bool:
        """Sends Ctrl+V keystroke via ydotool."""
        if not self.has_ydotool:
            print("[Injector] ydotool not found on system.")
            return False

        try:
            # 29 is KEY_LEFTCTRL, 47 is KEY_V
            # Syntax: <keycode>:<1 for press, 0 for release>
            res = subprocess.run(
                ["ydotool", "key", "29:1", "47:1", "47:0", "29:0"],
                capture_output=True,
                timeout=2
            )
            return res.returncode == 0
        except Exception as e:
            print(f"[Injector] ydotool key error: {e}")
            return False

    def inject_text(self, text: str) -> bool:
        """
        Main injection routine:
        1. Optionally captures existing clipboard.
        2. Copies new text to clipboard.
        3. Waits briefly for compositor clipboard synchronization.
        4. Synthesizes Ctrl+V.
        5. Optionally restores previous clipboard.
        """
        if not text:
            return False

        old_clipboard = None
        if self.restore_clipboard:
            old_clipboard = self.get_current_clipboard()

        copied = self.set_clipboard(text)
        if not copied:
            print("[Injector] Failed to copy text to clipboard.")
            return False

        # Brief delay so active app sees updated clipboard
        time.sleep(0.06)

        pasted = self.simulate_paste()

        if self.restore_clipboard and old_clipboard is not None:
            time.sleep(0.3)
            self.set_clipboard(old_clipboard)

        return pasted
