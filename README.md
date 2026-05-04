# SubtitleSmith

SubtitleSmith is a local, AI-powered desktop application that extracts audio from video files and converts it to synchronised `.srt` subtitles using the NVIDIA CUDA engine and `faster-whisper`. 

Featuring drag-and-drop file support and an intelligent hardware scanner that automatically recommends the best AI model for your system's VRAM. All processing runs locally on your machine—no internet connection or API keys required!

## Features

* **Hardware Auto-Profiling:** A built-in scanner analyses your CPU, RAM (speed/slots), and GPU VRAM to automatically recommend the optimal `faster-whisper` AI model for your specific machine.
* **Universal Media Support:** Drag-and-drop your favorite Video (MP4, MKV, AVI, MOV) or Audio (MP3, WAV, FLAC) files directly into the UI.
* **Expanded Language Support:** Transcribe or translate 20 major global languages—including Arabic, Chinese, Japanese, Spanish, and Urdu—or just use Auto-Detect.
* **Multimodal Output:** Choose to transcribe the original audio into text, or translate it directly into English subtitles.
* **Sleek & Interactive UI:** Dark mode interface featuring drag-and-drop targets, double-click file browsing, live progress bars, and safe process cancellation.
* **Smart Auto-Namer:** Automatically generates and saves the `.srt` file in the same directory as your source media.

## Requirements

* **OS:** Windows 10 or Windows 11 (Required for the hardware auto-profiler).
* **GPU:** NVIDIA GPU (8GB+ VRAM highly recommended for `large-v3` models).
* **Toolkit:** CUDA 12 Toolkit installed on your machine.
* **Python:** Python 3.12 or higher.
* **FFmpeg:** Must be installed and added to your Windows System PATH (Required for audio extraction).

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gingermuaz/SubtitleSmith.git
   cd SubtitleSmith

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate

3. **Install dependencies:**
   ```bash
   python -m pip install faster-whisper ctranslate2 customtkinter nvidia-cublas-cu12 nvidia-cudnn-cu12 psutil tkinterdnd2

4. **Run the Application:**
   ```bash
   python GUI.py

## Usage
Click Browse to select your .mp4 video file (the save location automatically appears next to it).

Choose your Source Language and AI Model Size.

Select your desired Action (Translate to English or Transcribe in the original language).

Click Start Processing and monitor the progress.


---
