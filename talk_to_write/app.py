"""
Main Application Coordinator for Talk-to-Write.
Connects Audio, AI Services, Text Injector, System Tray, Floating Pill, and Hotkeys.
"""

import sys
import threading
from typing import Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from .audio import AudioRecorder
from .config import ConfigManager
from .hotkey import HotkeyManager
from .injector import TextInjector
from .services.gemini import GeminiService
from .services.groq import GroqService
from .sound import SoundPlayer
from .ui.pill import FloatingPill
from .ui.settings import SettingsDialog
from .ui.tray import TrayIcon

class WorkerSignals(QObject):
    """Thread-safe signals for background transcription and injection."""
    level_changed = Signal(float)
    processing_done = Signal(str, float)
    processing_error = Signal(str)
    toggle_received = Signal()

class TalkToWriteApp:
    """The central Talk-to-Write application."""

    def __init__(self, q_app: QApplication):
        self.q_app = q_app
        self.config = ConfigManager()

        # Thread-safe Qt signal bridge
        self.signals = WorkerSignals()
        self.signals.level_changed.connect(self._on_audio_level)
        self.signals.processing_done.connect(self._on_processing_success)
        self.signals.processing_error.connect(self._on_processing_error)
        self.signals.toggle_received.connect(self.toggle_recording)

        # Core Engines
        self.sound = SoundPlayer(enabled=self.config.get("sound_effects", True))
        self.injector = TextInjector(restore_clipboard=self.config.get("restore_clipboard", False))
        self.recorder = AudioRecorder(
            on_level_callback=lambda lvl: self.signals.level_changed.emit(lvl)
        )

        # UI Components
        self.pill = FloatingPill()
        self.pill.clicked.connect(self.toggle_recording)
        self.pill.set_mode(self.config.get("mode", "dictation"))

        self.tray = TrayIcon()
        self.tray.set_active_mode(self.config.get("mode", "dictation"))
        self.tray.mode_changed.connect(self._on_mode_changed)
        self.tray.toggle_requested.connect(self.toggle_recording)
        self.tray.settings_requested.connect(self.open_settings)
        self.tray.quit_requested.connect(self.quit)
        self.tray.show()

        self.settings_dialog: Optional[SettingsDialog] = None

        # Hotkey & IPC listener
        self.hotkey_mgr = HotkeyManager(
            hotkey_str=self.config.get("hotkey", "Ctrl+Alt+Space"),
            on_toggle=lambda: self.signals.toggle_received.emit()
        )
        self.hotkey_mgr.start()

        self.is_busy_processing = False

    def toggle_recording(self) -> None:
        """Toggles between starting audio capture and sending to AI."""
        if self.is_busy_processing:
            print("[App] Henüz önceki işlem devam ediyor, bekleniyor...")
            return

        if not self.recorder.is_recording:
            # START RECORDING
            current_mode = self.config.get("mode", "dictation")
            print(f"[App] Kayıt başladı (Mod: {current_mode})")
            self.sound.play("start")
            self.pill.show_recording(mode=current_mode)
            self.tray.set_recording(True)
            self.recorder.start_recording()
        else:
            # STOP RECORDING & PROCESS
            print("[App] Kayıt durduruldu, ses işleniyor...")
            self.sound.play("stop")
            self.pill.show_processing()
            self.tray.set_recording(False)
            audio_bytes = self.recorder.stop_recording()

            if not audio_bytes or len(audio_bytes) < 3200:  # < 0.1s
                print("[App] Çok kısa ses veya ses algılanamadı.")
                self.sound.play("error")
                self.pill.show_error("Ses algılanamadı.")
                return

            self.is_busy_processing = True
            threading.Thread(target=self._process_audio_worker, args=(audio_bytes,), daemon=True).start()

    def _process_audio_worker(self, audio_bytes: bytes) -> None:
        """Runs in background thread to query AI and inject text."""
        provider = self.config.get("provider", "gemini")
        mode = self.config.get("mode", "dictation")
        custom_vocab = self.config.get("custom_vocabulary", [])

        try:
            print(f"[App] {provider.upper()} API isteği gönderiliyor ({len(audio_bytes)} bayt)...")
            if provider == "gemini":
                api_key = self.config.get("gemini_api_key", "")
                model = self.config.get("gemini_model", "gemini-2.0-flash")
                service = GeminiService(api_key=api_key, model=model)
                text, latency = service.transcribe_and_format(
                    audio_bytes, mode=mode, custom_vocabulary=custom_vocab
                )
            else:
                api_key = self.config.get("groq_api_key", "")
                stt_model = self.config.get("groq_stt_model", "whisper-large-v3-turbo")
                llm_model = self.config.get("groq_llm_model", "llama-3.3-70b-versatile")
                service = GroqService(api_key=api_key, stt_model=stt_model, llm_model=llm_model)
                text, latency = service.transcribe_and_format(
                    audio_bytes, mode=mode, custom_vocabulary=custom_vocab
                )

            if not text.strip():
                print("[App] AI boş yanıt döndürdü.")
                self.signals.processing_error.emit("Boş yanıt veya ses anlaşılmadı.")
                return

            print(f"[App] Metin alındı ({latency}s): {text[:60]}...")

            # Inject text into active window
            success = self.injector.inject_text(text)
            if success:
                print("[App] Metin aktif pencereye başarıyla yapıştırıldı!")
            else:
                print(f"[App] Metin panoya kopyalandı (Ctrl+V ydotool gönderilemedi)")

            self.signals.processing_done.emit(text, latency)

        except Exception as e:
            print(f"[App] Hata oluştu: {e}")
            self.signals.processing_error.emit(str(e))
        finally:
            self.is_busy_processing = False

    def _on_audio_level(self, level: float) -> None:
        if self.recorder.is_recording:
            self.pill.set_audio_level(level)

    def _on_processing_success(self, text: str, latency: float) -> None:
        self.is_busy_processing = False
        self.sound.play("success")
        self.pill.show_success(latency=latency)

    def _on_processing_error(self, error_message: str) -> None:
        self.is_busy_processing = False
        self.sound.play("error")
        self.pill.show_error(error_message)

    def _on_mode_changed(self, new_mode: str) -> None:
        self.config.set("mode", new_mode)
        self.pill.set_mode(new_mode)

    def open_settings(self) -> None:
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.config)
            self.settings_dialog.config_updated.connect(self._on_config_updated)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_config_updated(self) -> None:
        self.sound.enabled = self.config.get("sound_effects", True)
        self.injector.restore_clipboard = self.config.get("restore_clipboard", False)
        # Refresh hotkey manager
        self.hotkey_mgr.stop()
        self.hotkey_mgr = HotkeyManager(
            hotkey_str=self.config.get("hotkey", "Ctrl+Alt+Space"),
            on_toggle=lambda: self.signals.toggle_received.emit()
        )
        self.hotkey_mgr.start()

    def quit(self) -> None:
        self.hotkey_mgr.stop()
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.q_app.quit()
