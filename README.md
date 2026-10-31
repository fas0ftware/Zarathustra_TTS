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

## ◼ Project structure

```
Zarathustra_TTS/
├── voice_engine.py   # Core TTS logic and voice configuration
├── main.py           # Entry point: reads script.txt, generates audio
├── script.txt        # Your input text (local file, not tracked by git)
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

1. Put your text in `script.txt` (plain text, one file).
2. Run:

```bash
python main.py
```

The narration is saved as an MP3 file. The output name and location are set in `main.py`.

### Changing the voice

The default voice is set in `voice_engine.py`. To see every available voice:

```bash
edge-tts --list-voices
```

Copy the name of the voice you want (for example `en-US-GuyNeural`) into the voice setting in `voice_engine.py`.

### Using it as a module

```python
from voice_engine import *  # import the engine class and use it in your own pipeline
```

Check `voice_engine.py` for the class name and its methods.

## ◼ Notes and limitations

- Edge-TTS is an unofficial client for Microsoft's online voices. It needs internet access, and the service can change or limit access at any time.
- Generated audio and your private scripts are not meant to live in the repository. `script.txt` and `*.mp3` are listed in `.gitignore`.
- Voice quality depends on the chosen neural voice and the punctuation of the input text.

## ◼ Roadmap

- [ ] Voice-over integration for the FA Software video montage pipeline

---

Part of the **FA Software** projects.
