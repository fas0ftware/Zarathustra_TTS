import asyncio
import os
import sys
import tempfile
import types
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import edge_tts  # noqa: F401
except ImportError:  # allow the tests to run without the real package
    sys.modules["edge_tts"] = types.ModuleType("edge_tts")

import main  # noqa: E402
import voice_engine  # noqa: E402


class FakeCommunicate:
    calls = []

    def __init__(self, text, voice, rate="+0%", pitch="+0Hz"):
        FakeCommunicate.calls.append((text, voice, rate, pitch))

    async def save(self, path):
        with open(path, "wb") as f:
            f.write(b"fake-audio")


FAKE_EDGE = types.SimpleNamespace(Communicate=FakeCommunicate)


def patched_edge():
    FakeCommunicate.calls = []
    return mock.patch.object(voice_engine, "edge_tts", FAKE_EDGE)


def test_generate_audio_passes_settings_and_creates_folder():
    with tempfile.TemporaryDirectory() as tmp, patched_edge():
        out = os.path.join(tmp, "audio", "part1.mp3")
        engine = voice_engine.VoiceEngine(voice="en-US-GuyNeural", rate="+10%", pitch="-5Hz")
        result = asyncio.run(engine.generate_audio("Hello there", out))
        assert result == out and os.path.exists(out)
        assert FakeCommunicate.calls == [("Hello there", "en-US-GuyNeural", "+10%", "-5Hz")]


def test_generate_audio_rejects_empty_text():
    with patched_edge():
        try:
            asyncio.run(voice_engine.VoiceEngine().generate_audio("   ", "x.mp3"))
        except ValueError:
            return
    raise AssertionError("expected ValueError")


def test_read_script_handles_missing_empty_and_utf8():
    with tempfile.TemporaryDirectory() as tmp:
        missing = os.path.join(tmp, "nope.txt")
        try:
            main.read_script(missing)
            raise AssertionError("expected FileNotFoundError")
        except FileNotFoundError:
            pass

        empty = os.path.join(tmp, "empty.txt")
        open(empty, "w").close()
        try:
            main.read_script(empty)
            raise AssertionError("expected ValueError")
        except ValueError:
            pass

        turkish = os.path.join(tmp, "tr.txt")
        with open(turkish, "w", encoding="utf-8") as f:
            f.write("  Übermensch ve şiir  \n")
        assert main.read_script(turkish) == "Übermensch ve şiir"


def test_parser_defaults():
    args = main.build_parser().parse_args([])
    assert args.script == "script.txt"
    assert args.output == "narration.mp3"
    assert args.voice == voice_engine.DEFAULT_VOICE
    assert args.rate == "+0%" and args.pitch == "+0Hz"


def test_main_exit_codes():
    with tempfile.TemporaryDirectory() as tmp, patched_edge():
        script = os.path.join(tmp, "s.txt")
        out = os.path.join(tmp, "o.mp3")
        with open(script, "w", encoding="utf-8") as f:
            f.write("Some text")
        assert main.main([script, "-o", out]) == 0 and os.path.exists(out)
        assert main.main([os.path.join(tmp, "missing.txt"), "-o", out]) == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
