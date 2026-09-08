"""
Audio capture engine for Talk-to-Write.
Captures 16kHz 16-bit mono PCM audio in memory and reports real-time audio volume levels.
"""

import contextlib
import ctypes
import io
import math
import os
import struct
import threading
import time
import wave
from typing import Callable, Optional
import pyaudio

# Suppress ALSA C-level error spam on Linux
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextlib.contextmanager
def no_alsa_err():
    try:
        asound = ctypes.cdll.LoadLibrary('libasound.so.2')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except Exception:
        yield


class AudioRecorder:
    """Manages audio capture with real-time level metering."""

    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16

    def __init__(self, on_level_callback: Optional[Callable[[float], None]] = None):
        self.on_level_callback = on_level_callback
        self.is_recording = False
        self._thread: Optional[threading.Thread] = None
        self._frames = []
        self._lock = threading.Lock()
        self._pyaudio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None

    def start_recording(self) -> None:
        """Starts capturing audio in a background thread."""
        with self._lock:
            if self.is_recording:
                return
            self.is_recording = True
            self._frames = []

        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop_recording(self) -> bytes:
        """Stops capturing audio and returns the recorded WAV bytes."""
        with self._lock:
            if not self.is_recording:
                return b""
            self.is_recording = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        with self._lock:
            frames = list(self._frames)
            self._frames = []

        return self._encode_wav(frames)

    def _record_loop(self) -> None:
        try:
            with no_alsa_err():
                self._pyaudio = pyaudio.PyAudio()
                self._stream = self._pyaudio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK_SIZE
                )

            while True:
                with self._lock:
                    if not self.is_recording:
                        break

                try:
                    data = self._stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    with self._lock:
                        self._frames.append(data)

                    # Compute RMS audio level
                    if self.on_level_callback and data:
                        shorts = struct.unpack(f"{len(data) // 2}h", data)
                        if shorts:
                            sum_sq = sum(s * s for s in shorts)
                            rms = math.sqrt(sum_sq / len(shorts)) / 32768.0
                            # Amplify dynamic range slightly for visual punch
                            normalized = min(1.0, rms * 4.0)
                            self.on_level_callback(normalized)

                except Exception as e:
                    print(f"[Audio] Error reading chunk: {e}")
                    break

        except Exception as e:
            print(f"[Audio] Stream initialization error: {e}")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None
        except Exception:
            pass

        try:
            if self._pyaudio:
                self._pyaudio.terminate()
                self._pyaudio = None
        except Exception:
            pass

    def _normalize_pcm(self, raw_bytes: bytes, target_peak: int = 24000) -> bytes:
        """Normalizes audio volume so quiet microphones are loud and clear for STT models."""
        if not raw_bytes:
            return raw_bytes
        count = len(raw_bytes) // 2
        try:
            samples = struct.unpack(f"<{count}h", raw_bytes)
            peak = max(abs(s) for s in samples) if samples else 0
            if peak > 80 and peak < target_peak:
                gain = min(8.0, target_peak / peak)
                norm_samples = [max(-32768, min(32767, int(s * gain))) for s in samples]
                return struct.pack(f"<{count}h", *norm_samples)
        except Exception:
            pass
        return raw_bytes

    def _encode_wav(self, frames: list) -> bytes:
        """Encodes raw PCM frames into a valid RIFF WAV container with volume normalization."""
        if not frames:
            return b""

        raw_pcm = b"".join(frames)
        normalized_pcm = self._normalize_pcm(raw_pcm)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(normalized_pcm)

        return buf.getvalue()
