import argparse
import asyncio
import sys

from voice_engine import DEFAULT_VOICE, VoiceEngine


def build_parser():
    parser = argparse.ArgumentParser(
        description="Zarathustra | turn a text script into narrated audio (Edge-TTS)."
    )
    parser.add_argument("script", nargs="?", default="script.txt",
                        help="text file to read (default: script.txt)")
    parser.add_argument("-o", "--output", default="narration.mp3",
                        help="audio file to write (default: narration.mp3)")
    parser.add_argument("--voice", default=DEFAULT_VOICE,
                        help=f"Edge-TTS voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("--rate", default="+0%",
                        help='speaking speed, for example "+10%%" or "-15%%" (default: +0%%)')
    parser.add_argument("--pitch", default="+0Hz",
                        help='pitch, for example "+2Hz" or "-5Hz" (default: +0Hz)')
    return parser


def read_script(path):
    """Read a UTF-8 text file and return its stripped content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"'{path}' was not found. Create it or pass another file name.")

    if not text:
        raise ValueError(f"'{path}' is empty.")
    return text


async def run(args):
    text = read_script(args.script)
    engine = VoiceEngine(voice=args.voice, rate=args.rate, pitch=args.pitch)

    print(f"Reading: {text[:60]}...")
    print(f"Voice: {args.voice} | rate {args.rate} | pitch {args.pitch}")
    await engine.generate_audio(text, args.output)
    print(f"Done. Saved to {args.output}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        asyncio.run(run(args))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # network or Edge-TTS service problems
        print(f"Could not generate audio: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
