"""
Transcriber Service - Speech-to-text using Groq Whisper.
Sanitizes browser audio (WebM) via FFmpeg to 16 kHz mono WAV before sending to Groq.
"""

import os
import tempfile
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
import ffmpeg

load_dotenv()

MIN_AUDIO_BYTES = 2048

_GHOST_PHRASES = frozenset({
    "",
    "you",
    "thank you for watching",
    "thanks for watching",
    "mbc news",
})

_CONTEXT_PROMPT = (
    "Conversation with an IoT robot assistant named Gus. "
    "Engineering, electronics, M3."
)


class Transcriber:
    """Transcribe audio bytes to text using Groq Whisper after FFmpeg sanitization."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
        self.model = "whisper-large-v3"

    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Save audio_data to temp_input.webm, convert to 16 kHz mono WAV with FFmpeg,
        send the WAV to Groq, apply ghost filter. Returns None on short audio,
        conversion error, API error, or hallucination.
        """
        if not audio_data or len(audio_data) < MIN_AUDIO_BYTES:
            print("⚠️ Audio too short/empty")
            return None

        tmpdir = tempfile.mktemp(prefix="transcriber_")
        os.mkdir(tmpdir)
        temp_input = os.path.join(tmpdir, "temp_input.webm")
        temp_clean = os.path.join(tmpdir, "temp_clean.wav")

        try:
            with open(temp_input, "wb") as f:
                f.write(audio_data)

            try:
                (
                    ffmpeg
                    .input(temp_input)
                    .output(temp_clean, ac=1, ar="16000")
                    .overwrite_output()
                    .run(quiet=True)
                )
            except Exception as e:
                print("⚠️ FFmpeg conversion error", e)
                return None

            if not os.path.exists(temp_clean) or os.path.getsize(temp_clean) < 100:
                print("⚠️ FFmpeg did not produce a valid WAV")
                return None

            raw: Optional[str] = None
            try:
                with open(temp_clean, "rb") as f:
                    transcription = self.client.audio.transcriptions.create(
                        file=f,
                        model=self.model,
                        response_format="text",
                        language="en",
                        temperature=0.0,
                        prompt=_CONTEXT_PROMPT,
                    )
                raw = (
                    transcription
                    if isinstance(transcription, str)
                    else getattr(transcription, "text", "") or ""
                )
            except Exception as e:
                print("⚠️ Groq API Error", e)
                return None

            text = (raw or "").strip()
            if not text:
                return None
            if text.lower() in _GHOST_PHRASES:
                return None
            return text
        finally:
            for path in (temp_input, temp_clean):
                try:
                    if path and os.path.exists(path):
                        os.unlink(path)
                except OSError:
                    pass
            try:
                if os.path.exists(tmpdir):
                    os.rmdir(tmpdir)
            except OSError:
                pass
