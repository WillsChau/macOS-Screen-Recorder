
Gemini

即時通訊

Spark
Beta 版
新對話
搜尋對話
影片
媒體庫
Gem
新增筆記本
Gotcha
ESP32
Drafting a Project README File
Surface Laptop 4 Upgrade Decision
汽車12V電池壽命與更換時機
WebSocket 與 HTTP 的關係
Flutter 是真正的 Native App 吗？
補血湯的種類與食用指南
常見南瓜品種大比拼
軟件架構模式解析
POS 系統部署與點檢規劃
建立文檔整理與審閱 Gem
澳洲PayTo實體POS整合與效益
尋求意見與分析
Rewriting a Help Request
Gaming Setup Listing Feedback
PlayStation Portable: Hardware and Games
ESP32 創新產品設計方向
電子時鐘 Layout 設計指南
ESP32 PTV 火車班次提醒器
Bixolon 印表機問題排除指南
GTFS Realtime Metro Train Data
Cybersecurity Success: Career or Organization
ESP32 製作捷運到站顯示器
ESP32-S3 vs. ESP32-32E Comparison
Gmail MCP 服務介紹與設定
ClickUp MCP 官方伺服器介紹
Gemini 網頁搜尋與瀏覽器 AI
Edge AI 追蹤技術解析
根據日曆總結今日活動
Spark 整合 ClickUp 指南
Accessing ClickUp Data with AI
和 Gemini 的對話
draft README.md

Ubuntu / Debian:

Bash
sudo apt update && sudo apt install ffmpeg
Windows (Chocolatey / Scoop):

PowerShell
choco install ffmpeg
📦 Installation
Clone the repository:

Bash
git clone [https://github.com/your-username/screen-recorder-studio.git](https://github.com/your-username/screen-recorder-studio.git)
cd screen-recorder-studio
Create and activate a virtual environment (recommended):

Bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate
Install Python dependencies:

Bash
pip install PyQt6 opencv-python numpy mss edge-tts
🚀 Usage
Run the application:

Bash
python main.py
1. Record Screen
Click the 📐 (Area Selector) icon on the left panel.

Click and drag across the screen to define the capture boundary.

Click the 🔴 (Record) button to begin recording.

Click the ⏹️ (Stop) button when finished.

Choose where to save your MP4 recording.

2. Add AI Voiceover
Once a recording is completed or an existing video is loaded via 📂 (Open File):

Click the 🗣️ (Voiceover) icon.

Enter your timeline script in the dialog following the format:

Plaintext
0 | Welcome to this demonstration video.
3 | Here we select the target region on the screen.
8 | Once finished, the video is saved and synchronized with audio.
Click Generate & Merge Voiceover.

The processed video will be saved in the same directory with the voiced_ prefix.

⚙️ Configuration & Customization
Change Voice: Change the VOICE constant in main.py (e.g., "en-US-GuyNeural", "en-GB-SoniaNeural", "zh-CN-YunxiNeural").

To view all available voices:

Bash
edge-tts --list-voices
Frame Rate: Default recording frame rate is configured at ~25 FPS (timer.start(40)).

🔒 Permissions Notice (macOS)
If running on macOS, ensure your terminal or Python executable has Screen Recording permissions:

Open System Settings > Privacy & Security > Screen Recording.

Enable permission for your Terminal / IDE (e.g., iTerm, VS Code, or Python).

📄 License
This project is licensed under the MIT License.
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(readme_content)

print("README.md created successfully.")


```text?code_stdout&code_event_index=1
README.md created successfully.

Your Markdown file is ready:
  
PY
「MD」圖示
README
 MD 
開啟

Overview of README.md
Key Highlights & Features: Area selection, virtual cursor overlay, high-DPI scaling, Edge-TTS audio timeline synthesis, and FFmpeg audio multiplexing.  
PY

Prerequisites: FFmpeg installation commands for macOS, Linux, and Windows.

Quickstart Guide: Step-by-step installation, dependency requirements (PyQt6, opencv-python, numpy, mss, edge-tts), and application execution instructions.  
PY

Voiceover Format & Scripting Guide: Clear timeline documentation for formatting timestamps (Second | Voiceover Text).  
PY

macOS Permissions Note: Screen recording authorization guidance in System Settings.  
PY




Gemini 是 AI，有時可能會出錯。

正在分析
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
README.md
目前顯示的是「README.md」。
