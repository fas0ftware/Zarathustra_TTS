# Zarathustra | Voice Engine

> *"Man is a rope, tied between beast and overman—a rope over an abyss."* — F. Nietzsche

## ◼ Overview
**Zarathustra** is an automated content generation ecosystem designed to produce high-quality philosophical and technical content.

This repository hosts the **Voice Engine Module**, the vocal core of the system. It utilizes neural network-based text-to-speech (Edge-TTS) to generate human-like audio narrations without character limits, specifically tuned for deep, storytelling formats.

## ◼ Features
* **Neural Synthesis:** Utilizes Microsoft Edge's advanced neural voice models.
* **Unlimited Stream:** Capable of processing long-form scripts (essays, book summaries) in a single run.
* **Modular Architecture:** Designed to be imported as a class into larger automation pipelines.
* **Default Persona:** Configured to `en-GB-RyanNeural` (British English) for an academic and authoritative tone.

## ◼ Project Structure
```text
Zarathustra/
├── voice_engine.py   # Core TTS logic and voice configuration
├── main.py           # Execution script (Reads file -> Generates Audio)
├── script.txt        # Input text file (Not tracked by git)
└── requirements.txt  # Project dependencies
```
## ◼ Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/fanilk2/Zarathustra_TTS](https://github.com/fanilk2/Zarathustra_TTS)
cd Zarathustra
```

### 1. Environment Setup (Linux/macOS)
# Create virtual environment`
```bash
python3 -m venv venv
```
# Activate virtual environment
```bash
source venv/bin/activate
```
### 3.Install Dependencies
```bash
pip install -r requirements.txt
```
