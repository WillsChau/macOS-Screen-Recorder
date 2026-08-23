
# macOS Screen Recorder

A lightweight, functional, and minimalist desktop screen recording application for macOS built with **Python**, **PyQt6**, **mss**, and **OpenCV**.

---

## Features

* **Custom Region Selection**: Draw a precise bounding box on your screen or record the entire desktop.
* **Persistent Region Memory**: Selected recording areas remain locked across multiple recording sessions until changed.
* **Auto Cursor Rendering**: Manually calculates and paints a high-resolution macOS-style mouse cursor onto every captured frame.
* **Even-Dimension Formatting**: Automatically adjusts selection boundaries to even-pixel dimensions to satisfy macOS `AVFoundation` / `AVAssetWriter` requirements.
* **Custom Save Dialog**: Prompts native macOS `QFileDialog` upon stopping a recording to allow custom naming and folder destination.
* **Apple Silicon & Intel Compatible**: Built using a single-threaded `QTimer` frame-capture loop to avoid thread-safety crashes on Apple Silicon (M1/M2/M3) chips under Rosetta or native Python environments.

---

## Tech Stack

* **GUI Framework**: PyQt6
* **Screen Capture**: `mss`
* **Video Processing & Encoder**: `opencv-python` (`cv2`)
* **Array Processing**: `numpy`

---

## Installation

1. **Clone or download this repository** containing `studio_recorder.py`.
2. **Install dependencies** using your terminal:

```bash
/Library/Developer/CommandLineTools/usr/bin/python3 -m pip install PyQt6 mss opencv-python numpy

```

*(Note: Adjust the Python path above if you are using a virtual environment or Homebrew Python).*

---

## macOS Permissions Setup

Before running the application, grant screen recording permissions to your terminal or IDE:

1. Open **System Settings** -> **Privacy & Security** -> **Screen & System Audio Recording**.
2. Ensure **Terminal**, **iTerm**, or **VS Code** (depending on where you execute the script) is enabled.

---

## Usage

Run the script from your terminal:

```bash
/Library/Developer/CommandLineTools/usr/bin/python3 studio_recorder.py

```

### Controls

| Button Icon | Action | Description |
| --- | --- | --- |
| **📐** | **Select Region** | Darkens the screen to let you drag and select a custom capture area. |
| **🔴 / ⏹️** | **Record / Stop** | Click **🔴** to begin capturing. Click **⏹️** to stop recording. |

### Recording Workflow

1. Click **📐** to select a custom recording area (optional; defaults to full screen if skipped).
2. Click **🔴** to start recording. The window remains visible on screen.
3. Perform your screen actions.
4. Click **⏹️** to end the recording.
5. Enter your preferred filename in the native Mac **Save File** prompt.
6. The selection region stays locked so you can immediately click **🔴** again for the next take!
