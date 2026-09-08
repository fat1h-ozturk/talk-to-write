"""
Groq Whisper STT + Llama 3 LLM Formatter Service.
"""

import time
from typing import List, Optional, Tuple
import requests

from ..prompts import build_system_prompt

GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

class GroqService:
    """Service utilizing Groq Whisper for ultra-fast STT and Llama 3 for formatting."""

    def __init__(
        self,
        api_key: str,
        stt_model: str = "whisper-large-v3-turbo",
        llm_model: str = "qwen/qwen3.8-27b"
    ):
        self.api_key = api_key.strip() if api_key else ""
        self.stt_model = stt_model or "whisper-large-v3-turbo"
        self.llm_model = llm_model or "qwen/qwen3.8-27b"

    def transcribe_and_format(
        self,
        audio_bytes: bytes,
        mode: str = "dictation",
        custom_vocabulary: Optional[List[str]] = None,
        language: str = "tr",
        timeout: int = 25
    ) -> Tuple[str, float]:
        """
        Transcribes audio with Groq Whisper and polishes text with Groq LLM.
        Returns (formatted_text, total_latency_seconds).
        """
        if not self.api_key:
            raise ValueError(
                "Groq API anahtarı bulunamadı!\n"
                "Lütfen Ayarlar'dan API anahtarınızı girin veya GROQ_API_KEY tanımlayın."
            )

        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # 1. Step: Groq Whisper Transcription with Turkish Priming & Greedy Decoding
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        data = {
            "model": self.stt_model,
            "response_format": "json",
            "temperature": "0.0",
        }
        if language and language.lower() not in ("auto", ""):
            data["language"] = language.lower()
        else:
            data["language"] = "tr"

        # Prime Whisper context for proper capitalization, Turkish punctuation & vocab
        whisper_priming = "Merhaba. Bu bir Türkçe konuşma diktesidir; noktalama işaretleri ve büyük harfler içerir."
        if custom_vocabulary:
            whisper_priming += " Terimler: " + ", ".join(custom_vocabulary)
        data["prompt"] = whisper_priming

        try:
            stt_resp = requests.post(GROQ_AUDIO_URL, headers=headers, files=files, data=data, timeout=timeout)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Groq Whisper bağlantı hatası: {e}")

        if stt_resp.status_code != 200:
            raise RuntimeError(f"Groq Whisper Hatası ({stt_resp.status_code}): {stt_resp.text[:200]}")

        raw_transcript = stt_resp.json().get("text", "").strip()
        print(f"[STT Ham Çıktı]: {raw_transcript}")
        if not raw_transcript:
            return ("", round(time.time() - start_time, 2))

        # 2. Step: Groq LLM Formatting (with fallback to raw transcript)
        system_prompt = build_system_prompt(mode=mode, custom_vocabulary=custom_vocabulary)
        chat_payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Ham konuşma metni:\n{raw_transcript}"}
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
        }

        try:
            chat_resp = requests.post(GROQ_CHAT_URL, headers=headers, json=chat_payload, timeout=timeout)
            if chat_resp.status_code == 200:
                formatted_text = chat_resp.json()["choices"][0]["message"]["content"].strip()
                if formatted_text.startswith("```") and formatted_text.endswith("```"):
                    lines = formatted_text.splitlines()
                    if len(lines) >= 2:
                        formatted_text = "\n".join(lines[1:-1]).strip()
            else:
                print(f"[Groq] LLM formatting HTTP {chat_resp.status_code}, using raw transcript.")
                formatted_text = raw_transcript
        except Exception as e:
            print(f"[Groq] LLM formatting error ({e}), using raw transcript.")
            formatted_text = raw_transcript

        total_latency = round(time.time() - start_time, 2)
        return (formatted_text, total_latency)
