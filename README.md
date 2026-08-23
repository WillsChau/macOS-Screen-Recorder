# Screen Recorder Studio (Mac Native + Edge-TTS Voiceover)

A lightweight, modern desktop screen recording application built with **PyQt6**, **OpenCV**, **MSS**, and **Edge-TTS**. It supports high-DPI custom region recording, virtual cursor capture, and timeline-based AI text-to-speech voiceover generation and video multiplexing with **FFmpeg**.

---

## 🌟 Key Features

- **Custom Region & Full-Screen Capture**: Interactive drag-to-select bounding box with DPI scaling awareness (Retina/macOS optimized).
- **High-Performance Screen Grabber**: Ultra-fast frame capture powered by `mss` and encoded via `cv2.VideoWriter` (H.264/avc1 or mp4v).
- **Virtual Cursor Overlay**: Injects mouse cursor rendering directly into frames during recording.
- **AI-Powered Voiceover Generator**: Synchronized Text-to-Speech (Edge-TTS) with natural neural voices (default: `en-AU-WilliamNeural`).
- **Timeline-Based Voiceover Merging**: Define multi-segment voiceover scripts by second offsets (e.g. `0 | Intro text`, `5 | Step one...`) and mix directly into video tracks via FFmpeg filters (`adelay` + `amix`).
- **Standalone Video Audio Insertion**: Import pre-existing videos (`.mp4`, `.mov`, `.avi`, `.mkv`) and inject synchronized AI voiceovers.
- **Dark Theme UI**: Clean, responsive PyQt6 graphical interface with custom hover tooltips.

---

## 🛠️ Prerequisites & Requirements

### 1. System Requirements
- **OS**: macOS, Linux, or Windows (macOS requires Screen Recording permissions).
- **Python**: `3.9+`
- **FFmpeg**: Must be installed and accessible in your system `PATH`.

#### Install FFmpeg:
- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
- **Windows (Chocolatey / Scoop)**:
  ```powershell
  choco install ffmpeg
  ```

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/screen-recorder-studio.git
   cd screen-recorder-studio
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install PyQt6 opencv-python numpy mss edge-tts
   ```

---

## 🚀 Usage

Run the application:
```bash
python main.py
```

### 1. Record Screen
1. Click the **📐 (Area Selector)** icon on the left panel.
2. Click and drag across the screen to define the capture boundary.
3. Click the **🔴 (Record)** button to begin recording.
4. Click the **⏹️ (Stop)** button when finished.
5. Choose where to save your MP4 recording.

### 2. Add AI Voiceover
1. Once a recording is completed or an existing video is loaded via **📂 (Open File)**:
2. Click the **🗣️ (Voiceover)** icon.
3. Enter your timeline script in the dialog following the format:
   ```text
   0 | Welcome to this demonstration video.
   3 | Here we select the target region on the screen.
   8 | Once finished, the video is saved and synchronized with audio.
   ```
4. Click **Generate & Merge Voiceover**.
5. The processed video will be saved in the same directory with the `voiced_` prefix.

---

## ⚙️ Configuration & Customization

- **Change Voice**: Change the `VOICE` constant in `main.py` (e.g., `"en-US-GuyNeural"`, `"en-GB-SoniaNeural"`, `"zh-CN-YunxiNeural"`).
  - To view all available voices:
    ```bash
    edge-tts --list-voices
    ```
- **Frame Rate**: Default recording frame rate is configured at ~25 FPS (`timer.start(40)`).

---

## 🔒 Permissions Notice (macOS)

If running on macOS, ensure your terminal or Python executable has **Screen Recording** permissions:
1. Open **System Settings > Privacy & Security > Screen Recording**.
2. Enable permission for your Terminal / IDE (e.g., iTerm, VS Code, or Python).

---

## 📄 License

This project is licensed under the MIT License.
