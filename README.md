# Zarathustra | Voice Engine

> *"Man is a rope, tied between beast and overman - a rope over an abyss."* - F. Nietzsche

A text-to-speech voice engine that turns long scripts into narrated audio. Built on Edge-TTS, designed to be dropped into larger content pipelines.

## ◼ Overview

**Zarathustra** is an automated content generation ecosystem for philosophical and technical content. This repository holds its **Voice Engine module**, the vocal core of the system.

It uses neural text-to-speech (Edge-TTS) to produce natural-sounding narration from plain text, tuned for deep, storytelling-style formats such as essays and book summaries.

## ◼ Features

- **Neural synthesis:** Microsoft Edge's neural voice models through the `edge-tts` library, no API key required.
- **Long-form input:** Processes full scripts (essays, summaries) in a single run, without a manual character limit.
- **Modular design:** The engine is a class in `voice_engine.py`, so other scripts can import and reuse it.
- **Default persona:** `en-GB-RyanNeural` (British English), an academic and authoritative tone. Easy to swap.
- **Command-line options:** Choose the input file, output file, voice, speed and pitch without editing code.
- **Clear failures:** A missing or empty script, or a network problem, prints an error and exits with a non-zero code, so pipelines can detect it.

## ◼ Project structure

```
Zarathustra_TTS/
├── voice_engine.py   # Core TTS logic (VoiceEngine class)
├── main.py           # Command-line entry point
├── script.txt        # Sample input text, replace it with your own
├── tests/
│   └── test_engine.py
└── requirements.txt  # Dependencies
```

## ◼ Requirements

- Python 3.8+
- An internet connection (Edge-TTS calls Microsoft's online voice service)

## ◼ Installation

```bash
git clone https://github.com/fas0ftware/Zarathustra_TTS.git
cd Zarathustra_TTS
```

Create and activate a virtual environment.

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ◼ Usage

1. Put your text in `script.txt` (plain UTF-8 text). The repository ships a short sample there; replace it with your own script.
2. Run:

```bash
python main.py
```

The narration is saved as `narration.mp3` in the current folder. Options:

```bash
python main.py my_essay.txt -o audio/essay.mp3 --voice en-US-GuyNeural --rate "+10%" --pitch "-5Hz"
python main.py --help
```

### Changing the voice

The default voice is `en-GB-RyanNeural`. To see every available voice:

```bash
edge-tts --list-voices
```

Pass the name you want with `--voice` (for example `en-US-GuyNeural`), or change `DEFAULT_VOICE` in `voice_engine.py`.

### Using it as a module

```python
import asyncio
from voice_engine import VoiceEngine

engine = VoiceEngine(voice="en-GB-RyanNeural", rate="+0%", pitch="+0Hz")
asyncio.run(engine.generate_audio("Hello from Zarathustra.", "hello.mp3"))
```

`generate_audio` creates the output folder if needed, returns the file path, and raises an exception on failure instead of hiding it.

### Tests

The tests use a stand-in for Edge-TTS, so they need neither internet nor the `edge-tts` package:

```bash
python tests/test_engine.py
```

## ◼ Notes and limitations

- Edge-TTS is an unofficial client for Microsoft's online voices. It needs internet access, and the service can change or limit access at any time.
- Generated audio does not belong in the repository: `*.mp3` is listed in `.gitignore`. `script.txt` is tracked because it holds the sample text, so keep private scripts under another name (for example `my_essay.txt`).
- Voice quality depends on the chosen neural voice and the punctuation of the input text.

## ◼ Roadmap

- [ ] Voice-over integration for the FA Software video montage pipeline

---

Part of the **FA Software** projects.
