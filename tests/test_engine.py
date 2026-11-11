import asyncio
import io
import os
import sys
import types

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import edge_tts  # noqa: F401
except ImportError:  # allow the tests to run without the real package
    sys.modules["edge_tts"] = types.ModuleType("edge_tts")

import main  # noqa: E402
import voice_engine  # noqa: E402


class FakeSubMaker:
    def __init__(self):
        self.cues = []

    def feed(self, chunk):
        self.cues.append(chunk["text"])

    def get_srt(self):
        return "".join(f"{i}\n00:00:0{i},000 --> 00:00:0{i},500\n{t}\n\n"
                       for i, t in enumerate(self.cues, 1))


class FakeCommunicate:
    calls = []
    fail_times = 0
    empty = False

    def __init__(self, text, voice, rate="+0%", pitch="+0Hz", volume="+0%"):
        FakeCommunicate.calls.append((text, voice, rate, pitch, volume))

    async def stream(self):
        if FakeCommunicate.fail_times > 0:
            FakeCommunicate.fail_times -= 1
            raise ConnectionError("network down")
        if FakeCommunicate.empty:
            return
        for word in self.__class__.calls[-1][0].split():
            yield {"type": "SentenceBoundary", "text": word, "offset": 0, "duration": 1}
            yield {"type": "audio", "data": b"\xff\xfb" + word.encode()}


async def fake_list_voices():
    return [
        {"ShortName": "tr-TR-AhmetNeural", "Gender": "Male", "Locale": "tr-TR"},
        {"ShortName": "en-US-GuyNeural", "Gender": "Male", "Locale": "en-US"},
        {"ShortName": "en-GB-RyanNeural", "Gender": "Male", "Locale": "en-GB"},
    ]


@pytest.fixture(autouse=True)
def fake_edge(monkeypatch):
    FakeCommunicate.calls, FakeCommunicate.fail_times, FakeCommunicate.empty = [], 0, False
    fake = types.SimpleNamespace(Communicate=FakeCommunicate, SubMaker=FakeSubMaker,
                                 list_voices=fake_list_voices)
    monkeypatch.setattr(voice_engine, "edge_tts", fake)
    return fake


def run(coro):
    return asyncio.run(coro)


# --- engine -----------------------------------------------------------------

def test_generate_audio_passes_settings_and_creates_folder(tmp_path):
    out = tmp_path / "audio" / "part1.mp3"
    engine = voice_engine.VoiceEngine(voice="en-US-GuyNeural", rate="+10%", pitch="-5Hz", volume="-20%")
    result = run(engine.generate_audio("Hello there", str(out)))
    assert result.audio_file == str(out) and out.exists()
    assert result.audio_bytes == out.stat().st_size > 0
    assert FakeCommunicate.calls == [("Hello there", "en-US-GuyNeural", "+10%", "-5Hz", "-20%")]


def test_generate_audio_writes_srt(tmp_path):
    out, srt = tmp_path / "a.mp3", tmp_path / "a.srt"
    result = run(voice_engine.VoiceEngine().generate_audio("one two", str(out), str(srt)))
    assert result.subtitle_file == str(srt)
    text = srt.read_text(encoding="utf-8")
    assert "one" in text and "two" in text and "-->" in text


def test_generate_audio_rejects_empty_text():
    with pytest.raises(ValueError):
        run(voice_engine.VoiceEngine().generate_audio("   ", "x.mp3"))


def test_no_partial_file_left_on_failure(tmp_path):
    FakeCommunicate.fail_times = 99
    out = tmp_path / "a.mp3"
    engine = voice_engine.VoiceEngine(retries=2, retry_delay=0)
    with pytest.raises(RuntimeError, match="2 attempt"):
        run(engine.generate_audio("text", str(out)))
    assert not out.exists() and not (tmp_path / "a.mp3.part").exists()


def test_retry_recovers_from_transient_error(tmp_path):
    FakeCommunicate.fail_times = 2
    out = tmp_path / "a.mp3"
    run(voice_engine.VoiceEngine(retries=3, retry_delay=0).generate_audio("hi", str(out)))
    assert out.exists() and len(FakeCommunicate.calls) == 3


def test_empty_audio_from_service_is_an_error(tmp_path):
    FakeCommunicate.empty = True
    with pytest.raises(RuntimeError, match="no audio"):
        run(voice_engine.VoiceEngine(retries=1).generate_audio("hi", str(tmp_path / "a.mp3")))


@pytest.mark.parametrize("kwargs", [
    {"rate": "10%"}, {"rate": "+10"}, {"pitch": "+5"}, {"pitch": "5Hz"},
    {"volume": "loud"}, {"voice": "Ryan"}, {"voice": "en-GB-Ryan Neural; rm"},
])
def test_invalid_settings_are_rejected(kwargs):
    with pytest.raises(ValueError):
        voice_engine.VoiceEngine(**kwargs)


@pytest.mark.parametrize("voice", ["en-GB-RyanNeural", "en-US-AvaMultilingualNeural",
                                   "zh-CN-liaoning-XiaobeiNeural", "tr-TR-AhmetNeural"])
def test_real_voice_names_are_accepted(voice):
    assert voice_engine.VoiceEngine(voice=voice).voice == voice


def test_list_voices_filters_and_sorts():
    names = [v["ShortName"] for v in run(voice_engine.list_voices("en"))]
    assert names == ["en-GB-RyanNeural", "en-US-GuyNeural"]
    assert len(run(voice_engine.list_voices())) == 3


# --- CLI --------------------------------------------------------------------

def test_read_script_handles_missing_empty_bom_and_utf8(tmp_path):
    with pytest.raises(FileNotFoundError):
        main.read_script(str(tmp_path / "nope.txt"))
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    with pytest.raises(ValueError):
        main.read_script(str(empty))
    tr = tmp_path / "tr.txt"
    tr.write_bytes("﻿  Übermensch ve şiir  \n".encode("utf-8"))
    assert main.read_script(str(tr)) == "Übermensch ve şiir"
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(ValueError, match="UTF-8"):
        main.read_script(str(bad))


def test_read_script_from_stdin(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("  piped text \n"))
    assert main.read_script("-") == "piped text"


def test_parser_defaults():
    args = main.build_parser().parse_args([])
    assert args.script == "script.txt" and args.output is None
    assert args.voice == voice_engine.DEFAULT_VOICE
    assert (args.rate, args.pitch, args.volume) == ("+0%", "+0Hz", "+0%")
    assert args.srt is False and args.list_voices is None


def test_plan_jobs_single_and_batch(tmp_path):
    assert main.plan_jobs("s.txt", None) == [("s.txt", "narration.mp3")]
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "a.TXT").write_text("a")
    (tmp_path / "skip.md").write_text("x")
    jobs = main.plan_jobs(str(tmp_path), str(tmp_path / "out"))
    assert [os.path.basename(j[1]) for j in jobs] == ["a.mp3", "b.mp3"]
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        main.plan_jobs(str(empty), None)


def test_main_exit_codes(tmp_path):
    script = tmp_path / "s.txt"
    script.write_text("Some text", encoding="utf-8")
    out = tmp_path / "o.mp3"
    assert main.main([str(script), "-o", str(out), "--srt"]) == 0
    assert out.exists() and (tmp_path / "o.srt").exists()
    assert main.main([str(tmp_path / "missing.txt"), "-o", str(out)]) == 1
    assert main.main([str(script), "--rate", "fast"]) == 1


def test_batch_mode_continues_after_a_bad_file(tmp_path, capsys):
    (tmp_path / "1.txt").write_text("first")
    (tmp_path / "2.txt").write_text("")
    (tmp_path / "3.txt").write_text("third")
    assert main.main([str(tmp_path)]) == 1  # one file failed
    assert (tmp_path / "1.mp3").exists() and (tmp_path / "3.mp3").exists()
    assert not (tmp_path / "2.mp3").exists()
    assert "[2/3] Error" in capsys.readouterr().err


def test_list_voices_command(capsys):
    assert main.main(["--list-voices", "tr"]) == 0
    out = capsys.readouterr().out
    assert "tr-TR-AhmetNeural" in out and "1 voice(s)" in out
