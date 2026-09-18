"""
Cross-Platform Global Hotkey Listener and IPC Server for Linux, Windows, and macOS.
Listens to global shortcuts (evdev on Linux / pynput on Windows & macOS) and provides
an IPC trigger so CLI commands, scripts, or OS shortcuts can toggle recording.
"""

import os
import select
import socket
import sys
import threading
from typing import Callable, List, Optional, Set

SOCKET_PATH = "/tmp/talk-to-write.sock"
TCP_PORT = 49215

# Safe optional imports
HAS_EVDEV = False
try:
    import evdev
    from evdev import ecodes
    HAS_EVDEV = True
except ImportError:
    evdev = None
    ecodes = None

HAS_PYNPUT = False
try:
    from pynput import keyboard as pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    pynput_keyboard = None


class HotkeyManager:
    """Manages system-wide hotkeys and IPC socket trigger across OS platforms."""

    def __init__(self, hotkey_str: str = "Ctrl+Alt+Space", on_toggle: Optional[Callable[[], None]] = None):
        self.hotkey_str = hotkey_str
        self.on_toggle = on_toggle
        self.is_running = False
        self._threads: List[threading.Thread] = []
        self._active_keys: Set[int] = set()
        self._lock = threading.Lock()
        self._combo_triggered = False
        self._pynput_listener = None

    def start(self) -> None:
        """Starts the platform IPC server and background hotkey listener."""
        self.is_running = True

        # 1. Start IPC Server (TCP on Windows, Unix domain socket on Linux/macOS)
        ipc_thread = threading.Thread(target=self._run_ipc_server, daemon=True)
        ipc_thread.start()
        self._threads.append(ipc_thread)

        # 2. Start Global Hotkey Listener
        if sys.platform.startswith("linux") and HAS_EVDEV:
            evdev_thread = threading.Thread(target=self._run_evdev_listener, daemon=True)
            evdev_thread.start()
            self._threads.append(evdev_thread)
        elif HAS_PYNPUT:
            self._start_pynput_listener()
        else:
            print("[Hotkey] Notice: Neither evdev nor pynput is available. Global shortcuts will rely on CLI IPC (--toggle).")

    def stop(self) -> None:
        self.is_running = False
        if self._pynput_listener:
            try:
                self._pynput_listener.stop()
            except Exception:
                pass
            self._pynput_listener = None

        if not sys.platform.startswith("win") and os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except Exception:
                pass

    # --- IPC SERVER (TCP on Windows, Unix Domain Socket on POSIX) ---
    def _run_ipc_server(self) -> None:
        server = None
        try:
            if sys.platform.startswith("win"):
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("127.0.0.1", TCP_PORT))
            else:
                if os.path.exists(SOCKET_PATH):
                    try:
                        os.remove(SOCKET_PATH)
                    except Exception:
                        pass
                server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server.bind(SOCKET_PATH)

            server.listen(5)
            server.settimeout(1.0)
        except Exception as e:
            print(f"[Hotkey] Failed to start IPC server: {e}")
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
            if server:
                server.close()
            if not sys.platform.startswith("win") and os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)
        except Exception:
            pass

    # --- PYNPUT LISTENER (Windows & macOS) ---
    def _start_pynput_listener(self) -> None:
        """Sets up cross-platform hotkey listener using pynput."""
        if not HAS_PYNPUT:
            return

        # Format "Ctrl+Alt+Space" into pynput syntax: "<ctrl>+<alt>+<space>"
        parts = [p.strip().lower() for p in self.hotkey_str.split("+")]
        pynput_parts = []
        for p in parts:
            if p in ("ctrl", "control"):
                pynput_parts.append("<ctrl>")
            elif p in ("alt", "option"):
                pynput_parts.append("<alt>")
            elif p in ("shift",):
                pynput_parts.append("<shift>")
            elif p in ("cmd", "command", "super", "win"):
                pynput_parts.append("<cmd>")
            elif p == "space":
                pynput_parts.append("<space>")
            else:
                pynput_parts.append(p)

        hotkey_combo = "+".join(pynput_parts)

        def on_activate():
            if self.on_toggle:
                self.on_toggle()

        try:
            self._pynput_listener = pynput_keyboard.GlobalHotKeys({
                hotkey_combo: on_activate
            })
            self._pynput_listener.start()
        except Exception as e:
            print(f"[Hotkey] Failed to start pynput listener ({hotkey_combo}): {e}")

    # --- EVDEV LISTENER (Linux) ---
    def _run_evdev_listener(self) -> None:
        """Finds keyboards and listens for configured shortcut via evdev."""
        if not HAS_EVDEV:
            return

        key_map = {
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

        keyboards = []
        try:
            for path in evdev.list_devices():
                try:
                    dev = evdev.InputDevice(path)
                    name_lower = dev.name.lower()
                    if "ydotool" in name_lower:
                        continue
                    caps = dev.capabilities()
                    if ecodes.EV_KEY in caps:
                        keyboards.append(dev)
                except Exception:
                    pass
        except Exception as e:
            print(f"[Hotkey] Error discovering evdev devices: {e}")
            return

        if not keyboards:
            print("[Hotkey] No suitable keyboard devices found for evdev.")
            return

        parts = [p.strip().upper() for p in self.hotkey_str.split("+")]

        while self.is_running:
            try:
                r, _, _ = select.select(keyboards, [], [], 0.5)
                for dev in r:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY:
                            self._handle_evdev_key(event.code, event.value, parts, key_map)
            except Exception:
                pass

    def _handle_evdev_key(self, code: int, value: int, combo_parts: List[str], key_map: dict) -> None:
        with self._lock:
            if value == 1:
                self._active_keys.add(code)
            elif value == 0:
                self._active_keys.discard(code)
                self._combo_triggered = False

            all_satisfied = True
            for part in combo_parts:
                allowed_codes = key_map.get(part)
                if allowed_codes:
                    if not any(k in self._active_keys for k in allowed_codes):
                        all_satisfied = False
                        break
                else:
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
    """Sends a toggle trigger to a running Talk-to-Write instance across OS platforms."""
    if sys.platform.startswith("win"):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
            client.connect(("127.0.0.1", TCP_PORT))
            client.sendall(b"toggle")
            client.close()
            return True
        except Exception:
            return False
    else:
        if not os.path.exists(SOCKET_PATH):
            return False
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(1.0)
            client.connect(SOCKET_PATH)
            client.sendall(b"toggle")
            client.close()
            return True
        except Exception:
            return False
