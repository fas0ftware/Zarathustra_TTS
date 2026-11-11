"""Command-line entry point for the Zarathustra voice engine."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from voice_engine import DEFAULT_VOICE, VoiceEngine, __version__, list_voices


def build_parser():
    parser = argparse.ArgumentParser(
        prog="zarathustra",
        description="Zarathustra | turn a text script into narrated audio (Edge-TTS).",
    )
    parser.add_argument("script", nargs="?", default="script.txt",
                        help="text file to read, a folder of .txt files (batch mode), "
                             "or '-' for stdin (default: script.txt)")
    parser.add_argument("-o", "--output", default=None,
                        help="audio file to write (default: narration.mp3; in batch mode, "
                             "the output folder, default: the input folder)")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help=f"Edge-TTS voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="+0%",
                        help='speaking speed, for example "+10%%" or "-15%%" (default: +0%%)')
    parser.add_argument("--pitch", default="+0Hz",
                        help='pitch, for example "+2Hz" or "-5Hz" (default: +0Hz)')
    parser.add_argument("--volume", default="+0%",
                        help='volume, for example "-20%%" (default: +0%%)')
    parser.add_argument("--srt", action="store_true",
                        help="also write an .srt subtitle file next to each audio file")
    parser.add_argument("--retries", type=int, default=3,
                        help="attempts per file when the service fails (default: 3)")
    parser.add_argument("--list-voices", nargs="?", const="", metavar="LOCALE",
                        help="list available voices (optionally only a locale, e.g. 'en' or 'tr-TR') and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def read_script(path):
    """Read a UTF-8 text file (or stdin for '-') and return its stripped content."""
    if path == "-":
        text = sys.stdin.read().strip()
    else:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"'{path}' was not found. Create it or pass another file name.")
        except UnicodeDecodeError:
            raise ValueError(f"'{path}' is not valid UTF-8 text.")

    if not text:
        raise ValueError(f"'{path}' is empty.")
    return text


def plan_jobs(script, output):
    """Return a list of (input_path, output_mp3) pairs."""
    if script != "-" and os.path.isdir(script):
        out_dir = output or script
        names = sorted(n for n in os.listdir(script) if n.lower().endswith(".txt"))
        if not names:
            raise FileNotFoundError(f"No .txt files in folder '{script}'.")
        return [(os.path.join(script, n), os.path.join(out_dir, os.path.splitext(n)[0] + ".mp3"))
                for n in names]
    return [(script, output or "narration.mp3")]


def srt_path_for(audio_path):
    return os.path.splitext(audio_path)[0] + ".srt"


async def run(args):
    if args.list_voices is not None:
        voices = await list_voices(args.list_voices)
        for v in voices:
            print(f"{v['ShortName']:<36} {v.get('Gender', ''):<7} {v.get('Locale', '')}")
        print(f"{len(voices)} voice(s)")
        return 0

    engine = VoiceEngine(voice=args.voice, rate=args.rate, pitch=args.pitch,
                         volume=args.volume, retries=args.retries)
    jobs = plan_jobs(args.script, args.output)
    print(f"Voice: {args.voice} | rate {args.rate} | pitch {args.pitch} | volume {args.volume}")
    failures = 0
    for i, (src, dst) in enumerate(jobs, 1):
        prefix = f"[{i}/{len(jobs)}] " if len(jobs) > 1 else ""
        try:
            text = read_script(src)
            print(f"{prefix}Reading {src}: {text[:60]!r}{'...' if len(text) > 60 else ''}")
            result = await engine.generate_audio(text, dst, srt_path_for(dst) if args.srt else None)
            extra = f" + {result.subtitle_file}" if result.subtitle_file else ""
            print(f"{prefix}Saved {result.audio_file} ({result.audio_bytes / 1024:.0f} KiB){extra}")
        except (ValueError, FileNotFoundError, RuntimeError) as exc:
            failures += 1
            print(f"{prefix}Error: {exc}", file=sys.stderr)
    return 1 if failures else 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(run(args))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:  # network or Edge-TTS service problems
        print(f"Could not generate audio: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
