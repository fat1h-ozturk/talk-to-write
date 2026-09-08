"""
Global hotkey listener and IPC socket server for Wayland / Linux.
Listens to evdev input devices and an IPC socket so external shortcuts or scripts can toggle recording.
"""

import os
import select
import socket
import threading
from typing import Callable, List, Optional, Set
import evdev
from evdev import ecodes

SOCKET_PATH = "/tmp/talk-to-write.sock"

# Map human-readable key names to evdev keycodes
KEY_MAP = {
    "CTRL": {ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL},
    "ALT": {ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT},
    "SHIFT": {ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT},
    "SPACE": {ecodes.KEY_SPACE},
    "F8": {ecodes.KEY_F8},
    "F9": {ecodes.KEY_F9},
    "F10": {ecodes.KEY_F10},
    "F12": {ecodes.KEY_F12},
    "PAUSE": {ecodes.KEY_PAUSE},
    "SCROLLLOCK": {ecodes.KEY_SCROLLLOCK},
}

class HotkeyManager:
    """Manages system-wide hotkeys and IPC socket trigger."""

    def __init__(self, hotkey_str: str = "Ctrl+Alt+Space", on_toggle: Optional[Callable[[], None]] = None):
        self.hotkey_str = hotkey_str
        self.on_toggle = on_toggle
        self.is_running = False
        self._threads: List[threading.Thread] = []
        self._active_keys: Set[int] = set()
        self._lock = threading.Lock()
        self._combo_triggered = False

    def start(self) -> None:
        """Starts evdev listener and IPC socket listener."""
        self.is_running = True

        # 1. Start IPC Socket server
        ipc_thread = threading.Thread(target=self._run_ipc_server, daemon=True)
        ipc_thread.start()
        self._threads.append(ipc_thread)

        # 2. Start Evdev listener
        evdev_thread = threading.Thread(target=self._run_evdev_listener, daemon=True)
        evdev_thread.start()
        self._threads.append(evdev_thread)

    def stop(self) -> None:
        self.is_running = False
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except Exception:
                pass

    def _run_ipc_server(self) -> None:
        """Listens on /tmp/talk-to-write.sock for instant toggle commands."""
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except Exception:
                pass

        try:
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(SOCKET_PATH)
            server.listen(5)
            server.settimeout(1.0)
        except Exception as e:
            print(f"[Hotkey] Failed to start IPC socket: {e}")
            return

        while self.is_running:
            try:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(128).decode("utf-8").strip()
                    if data == "toggle" and self.on_toggle:
                        self.on_toggle()
                    elif data == "ping":
                        conn.sendall(b"pong")
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"[Hotkey] IPC connection error: {e}")

        try:
            server.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
        except Exception:
            pass

    def _run_evdev_listener(self) -> None:
        """Finds keyboards and listens for configured shortcut."""
        keyboards = []
        try:
            for path in evdev.list_devices():
                try:
                    dev = evdev.InputDevice(path)
                    name_lower = dev.name.lower()
                    # Skip virtual ydotool devices to avoid loopback
                    if "ydotool" in name_lower:
                        continue
                    caps = dev.capabilities()
                    if ecodes.EV_KEY in caps:
                        keyboards.append(dev)
                except Exception:
                    pass
        except Exception as e:
            print(f"[Hotkey] Error discovering input devices: {e}")
            return

        if not keyboards:
            print("[Hotkey] No suitable keyboard devices found for evdev.")
            return

        # Simple parse of "Ctrl+Alt+Space"
        parts = [p.strip().upper() for p in self.hotkey_str.split("+")]

        while self.is_running:
            try:
                r, _, _ = select.select(keyboards, [], [], 0.5)
                for dev in r:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY:
                            self._handle_key_event(event.code, event.value, parts)
            except Exception:
                pass

    def _handle_key_event(self, code: int, value: int, combo_parts: List[str]) -> None:
        """value: 1=down, 2=hold, 0=up."""
        with self._lock:
            if value == 1:
                self._active_keys.add(code)
            elif value == 0:
                self._active_keys.discard(code)
                self._combo_triggered = False

            # Check if all required parts of the combination are satisfied
            all_satisfied = True
            for part in combo_parts:
                allowed_codes = KEY_MAP.get(part)
                if allowed_codes:
                    if not any(k in self._active_keys for k in allowed_codes):
                        all_satisfied = False
                        break
                else:
                    # Try matching direct ecodes attribute
                    attr_name = f"KEY_{part}"
                    if hasattr(ecodes, attr_name):
                        target_code = getattr(ecodes, attr_name)
                        if target_code not in self._active_keys:
                            all_satisfied = False
                            break
                    else:
                        all_satisfied = False
                        break

            if all_satisfied and not self._combo_triggered:
                self._combo_triggered = True
                if self.on_toggle:
                    self.on_toggle()


def send_ipc_toggle() -> bool:
    """Sends a toggle trigger to a running Talk-to-Write instance."""
    if not os.path.exists(SOCKET_PATH):
        return False

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.sendall(b"toggle")
        client.close()
        return True
    except Exception:
        return False
