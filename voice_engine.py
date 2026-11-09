import os

import edge_tts

DEFAULT_VOICE = "en-GB-RyanNeural"  # British English, academic and authoritative


class VoiceEngine:
    """Turns text into narrated audio with Edge-TTS neural voices."""

    def __init__(self, voice=DEFAULT_VOICE, rate="+0%", pitch="+0Hz"):
        self.voice = voice
        self.rate = rate    # for example "+10%" or "-15%"
        self.pitch = pitch  # for example "+2Hz" or "-5Hz"

    async def generate_audio(self, text, output_file):
        """Convert text to an audio file and return the file path.

        Raises ValueError for empty text. Network and service errors from
        edge-tts are not swallowed, so callers can decide how to handle them.
        """
        if not text or not text.strip():
            raise ValueError("There is no text to convert.")

        # Make sure the output folder exists (for example "audio/part1.mp3").
        folder = os.path.dirname(output_file)
        if folder:
            os.makedirs(folder, exist_ok=True)

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch,
        )
        await communicate.save(output_file)
        return output_file
