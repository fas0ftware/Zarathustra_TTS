"""Zarathustra voice engine: text to narrated audio (and optional SRT) with Edge-TTS."""

from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass

import edge_tts

__version__ = "2.0.0"

DEFAULT_VOICE = "en-GB-RyanNeural"  # British English, academic and authoritative

_RATE_RE = re.compile(r"^[+-]\d{1,3}%$")
_PITCH_RE = re.compile(r"^[+-]\d{1,3}Hz$")
_VOICE_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]+){2,3}$")


def validate_settings(voice: str, rate: str, pitch: str, volume: str) -> None:
    """Raise ValueError with a readable message if a setting has the wrong format."""
    if not _VOICE_RE.match(voice):
        raise ValueError(f"Invalid voice name {voice!r} (expected something like 'en-GB-RyanNeural').")
    if not _RATE_RE.match(rate):
        raise ValueError(f"Invalid rate {rate!r} (expected something like '+10%' or '-15%').")
    if not _PITCH_RE.match(pitch):
        raise ValueError(f"Invalid pitch {pitch!r} (expected something like '+2Hz' or '-5Hz').")
    if not _RATE_RE.match(volume):
        raise ValueError(f"Invalid volume {volume!r} (expected something like '+0%' or '-20%').")


@dataclass
class Result:
    audio_file: str
    subtitle_file: str | None
    audio_bytes: int


class VoiceEngine:
    """Turns text into narrated audio with Edge-TTS neural voices."""

    def __init__(self, voice=DEFAULT_VOICE, rate="+0%", pitch="+0Hz", volume="+0%",
                 retries=3, retry_delay=2.0):
        validate_settings(voice, rate, pitch, volume)
        self.voice = voice
        self.rate = rate      # for example "+10%" or "-15%"
        self.pitch = pitch    # for example "+2Hz" or "-5Hz"
        self.volume = volume  # for example "+0%" or "-20%"
        self.retries = max(1, int(retries))
        self.retry_delay = float(retry_delay)

    async def _synthesize_once(self, text: str, want_subs: bool):
        communicate = edge_tts.Communicate(
            text, self.voice, rate=self.rate, pitch=self.pitch, volume=self.volume,
        )
        audio = bytearray()
        submaker = edge_tts.SubMaker() if want_subs else None
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
            elif submaker is not None and chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
        if not audio:
            raise RuntimeError("Edge-TTS returned no audio (check the voice name and your connection).")
        return bytes(audio), (submaker.get_srt() if submaker is not None else None)

    async def synthesize(self, text: str, want_subs: bool = False):
        """Return (audio_bytes, srt_text_or_None), retrying transient failures."""
        if not text or not text.strip():
            raise ValueError("There is no text to convert.")
        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                return await self._synthesize_once(text, want_subs)
            except ValueError:
                raise
            except Exception as exc:  # network / service errors
                last_exc = exc
                if attempt < self.retries:
                    await asyncio.sleep(self.retry_delay * 2 ** (attempt - 1))
        raise RuntimeError(f"Failed after {self.retries} attempt(s): {last_exc}") from last_exc

    async def generate_audio(self, text: str, output_file: str, subtitle_file: str | None = None) -> Result:
        """Convert text to an audio file (and optional .srt). Returns a Result.

        Raises ValueError for empty text and RuntimeError when the service keeps failing.
        Files are written atomically, so a failed run never leaves a half-written mp3.
        """
        audio, srt = await self.synthesize(text, want_subs=subtitle_file is not None)
        _atomic_write(output_file, audio)
        if subtitle_file is not None:
            _atomic_write(subtitle_file, (srt or "").encode("utf-8"))
        return Result(output_file, subtitle_file, len(audio))


async def list_voices(prefix: str = "") -> list[dict]:
    """Return available voices, optionally filtered by locale prefix such as 'en' or 'tr-TR'."""
    voices = await edge_tts.list_voices()
    prefix = prefix.lower()
    return sorted(
        (v for v in voices if v.get("Locale", "").lower().startswith(prefix)),
        key=lambda v: v.get("ShortName", ""),
    )


def _atomic_write(path: str, data: bytes) -> None:
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = f"{path}.part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
