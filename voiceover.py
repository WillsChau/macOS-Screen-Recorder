import sys
import os
import cv2
import numpy as np
import mss
import asyncio
import subprocess
import threading
import edge_tts

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QFrame, QMessageBox,
                             QFileDialog, QTextEdit, QDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal, QPoint, QThread
from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QColor, QCursor

VOICE = "en-AU-WilliamNeural"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------
# Custom White ToolTip Label (Fixed Font Alias Warning)
# --------------------------------------------------
class CustomToolTip(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # Using native macOS font alias '.AppleSystemUIFont' to avoid Qt font population warnings
        self.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                color: #111111;
                border: 1px solid #999999;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-family: .AppleSystemUIFont, Helvetica, Arial, sans-serif;
            }
        """)

    def show_text(self, text, pos):
        self.setText(text)
        self.adjustSize()
        self.move(pos.x() + 15, pos.y() + 10)
        self.show()


class CustomButton(QPushButton):
    def __init__(self, icon_text, tooltip_text, parent=None):
        super().__init__(icon_text, parent)
        self.tooltip_text = tooltip_text
        self.custom_tooltip = None

    def enterEvent(self, event):
        if self.isEnabled() and self.tooltip_text:
            if not self.custom_tooltip:
                self.custom_tooltip = CustomToolTip()
            self.custom_tooltip.show_text(self.tooltip_text, QCursor.pos())
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.custom_tooltip:
            self.custom_tooltip.hide()
        super().leaveEvent(event)


# --------------------------------------------------
# Background Voiceover Thread (Fixed Async Event Loop)
# --------------------------------------------------
class VoiceoverWorker(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, input_video, segments):
        super().__init__()
        self.input_video = input_video
        self.segments = segments

    def run(self):
        # Create and set a dedicated event loop for this thread context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._process_voiceover())
            self.finished_signal.emit(True, "")
        except Exception as e:
            self.finished_signal.emit(False, str(e))
        finally:
            loop.close()

    async def _process_voiceover(self):
        output_video = os.path.join(
            os.path.dirname(self.input_video), 
            f"voiced_{os.path.basename(self.input_video)}"
        )
        inputs = []
        filter_complex = []
        temp_files = []
        
        for idx, (timestamp_sec, text) in enumerate(self.segments):
            audio_file = os.path.join(SCRIPT_DIR, f"temp_{idx}.mp3")
            temp_files.append(audio_file)
            
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(audio_file)
            
            inputs.extend(["-i", audio_file])
            filter_complex.append(f"[{idx}:a]adelay={timestamp_sec*1000}|{timestamp_sec*1000}[a{idx}]")
        
        concat_inputs = "".join(f"[a{i}]" for i in range(len(self.segments)))
        filter_complex.append(f"{concat_inputs}amix=inputs={len(self.segments)}:normalize=0[aout]")
        
        combined_audio = os.path.join(SCRIPT_DIR, "temp_combined.mp3")
        temp_files.append(combined_audio)
        
        cmd_audio = ["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(filter_complex), "-map", "[aout]", combined_audio]
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        cmd_merge = [
            "ffmpeg", "-y",
            "-i", self.input_video,
            "-i", combined_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_video
        ]
        subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)


class AreaSelector(QWidget):
    area_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        screen_geom = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen_geom)
        
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selecting = False
            rect = QRect(self.start_point, self.end_point).normalized()
            self.area_selected.emit(rect)
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if not self.start_point.isNull() and not self.end_point.isNull():
            rect = QRect(self.start_point, self.end_point).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 255, 120), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)


class VoiceoverDialog(QDialog):
    def __init__(self, current_script="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voiceover Script Settings")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Enter script timeline (Format: Seconds | Voiceover Text):")
        label.setStyleSheet("font-size: 14px; color: #CCC;")
        layout.addWidget(label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("background-color: #2D2D2D; color: white; font-size: 13px; font-family: Menlo, Courier, monospace;")
        
        if current_script:
            self.text_edit.setPlainText(current_script)
        else:
            default_script = "0 | Welcome to the demonstration video."
            self.text_edit.setPlainText(default_script)
            
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        self.btn_submit = QPushButton("Generate & Merge Voiceover")
        self.btn_submit.setStyleSheet("background-color: #007ACC; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.btn_submit.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #444; color: white; padding: 8px; border-radius: 5px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_submit)
        layout.addLayout(btn_layout)

    def get_raw_text(self):
        return self.text_edit.toPlainText().strip()

    def get_segments(self):
        segments = []
        raw_text = self.get_raw_text()
        for line in raw_text.split("\n"):
            if "|" in line:
                parts = line.split("|", 1)
                try:
                    sec = int(parts[0].strip())
                    text = parts[1].strip()
                    if text:
                        segments.append((sec, text))
                except ValueError:
                    continue
        return segments


class ScreenRecorderStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder (Mac Native + Voiceover)")
        self.resize(600, 350)
        
        self.is_recording = False
        self.temp_video_path = os.path.join(SCRIPT_DIR, "temp_recording.mp4")
        self.target_video_path = None
        self.saved_script_text = ""
        self.voice_worker = None
        self.progress_dialog = None
        
        self.sct = None
        self.record_region = None
        self.video_writer = None
        self.selector = None
        self.frame_count = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.record_frame)
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QFrame()
        left_panel.setFixedWidth(70)
        left_panel.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #333;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 20, 10, 20)
        left_layout.setSpacing(20)

        self.btn_select_area = CustomButton("📐", "Select Recording Area")
        self.btn_record = CustomButton("🔴", "Start/Stop Recording")
        self.btn_open_file = CustomButton("📂", "Open Existing Video File")
        self.btn_voiceover = CustomButton("🗣️", "Add Voiceover")
        
        for btn in (self.btn_select_area, self.btn_record, self.btn_open_file, self.btn_voiceover):
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D; color: white; font-size: 22px; 
                    border-radius: 10px; border: 1px solid #444;
                }
                QPushButton:hover { background-color: #3E3E3E; }
                QPushButton:disabled { background-color: #1A1A1E; color: #555; border-color: #222; }
            """)
            left_layout.addWidget(btn)

        self.btn_voiceover.setEnabled(False)
        
        self.btn_select_area.clicked.connect(self.select_custom_area)
        self.btn_record.clicked.connect(self.toggle_recording)
        self.btn_open_file.clicked.connect(self.open_existing_video)
        self.btn_voiceover.clicked.connect(self.open_voiceover_dialog)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        canvas_container = QWidget()
        canvas_container.setStyleSheet("background-color: #121212;")
        canvas_layout = QVBoxLayout(canvas_container)
        
        self.status_label = QLabel("Click 📐 to select area, 🔴 to record screen,\nOR click 📂 to load an existing video file")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #AAA; font-size: 16px; line-height: 1.5;")
        
        canvas_layout.addWidget(self.status_label)
        main_layout.addWidget(canvas_container, stretch=1)

    def select_custom_area(self):
        self.hide()
        QTimer.singleShot(200, self._launch_selector)

    def _launch_selector(self):
        self.selector = AreaSelector()
        self.selector.area_selected.connect(self.on_area_selected)
        self.selector.show()

    def on_area_selected(self, rect):
        self.show()
        if rect.width() > 10 and rect.height() > 10:
            scale = QGuiApplication.primaryScreen().devicePixelRatio()
            w = int(rect.width() * scale)
            h = int(rect.height() * scale)
            w = w if w % 2 == 0 else w - 1
            h = h if h % 2 == 0 else h - 1

            self.record_region = {
                "top": int(rect.top() * scale),
                "left": int(rect.left() * scale),
                "width": w,
                "height": h
            }
            self.status_label.setText(f"✅ Region Locked: {w}x{h} px\nClick 🔴 to Start Recording")

    def toggle_recording(self):
        if not self.is_recording:
            self.sct = mss.MSS()
            
            if not self.record_region:
                m = self.sct.monitors[1]
                w = m["width"] if m["width"] % 2 == 0 else m["width"] - 1
                h = m["height"] if m["height"] % 2 == 0 else m["height"] - 1
                self.record_region = {
                    "top": m["top"], "left": m["left"], 
                    "width": w, "height": h
                }

            width = self.record_region["width"]
            height = self.record_region["height"]

            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            self.video_writer = cv2.VideoWriter(self.temp_video_path, fourcc, 20.0, (width, height))
            if not self.video_writer.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                self.video_writer = cv2.VideoWriter(self.temp_video_path, fourcc, 20.0, (width, height))

            self.is_recording = True
            self.frame_count = 0
            self.btn_record.setText("⏹️")
            self.btn_record.setStyleSheet("background-color: #AA0000; color: white; font-size: 22px; border-radius: 10px;")
            self.status_label.setText("🔴 Recording in progress...")
            
            self.timer.start(40)
        else:
            self.stop_recording()

    def record_frame(self):
        if self.is_recording and self.sct and self.video_writer:
            try:
                img = np.array(self.sct.grab(self.record_region))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, (self.record_region["width"], self.record_region["height"]))
                
                scale = QGuiApplication.primaryScreen().devicePixelRatio()
                cursor_pos = QCursor.pos()
                cursor_x = int((cursor_pos.x() * scale) - self.record_region["left"])
                cursor_y = int((cursor_pos.y() * scale) - self.record_region["top"])
                
                if 0 <= cursor_x < self.record_region["width"] and 0 <= cursor_y < self.record_region["height"]:
                    pts = np.array([
                        [cursor_x, cursor_y],
                        [cursor_x, cursor_y + int(18 * scale)],
                        [cursor_x + int(5 * scale), cursor_y + int(14 * scale)],
                        [cursor_x + int(10 * scale), cursor_y + int(21 * scale)],
                        [cursor_x + int(13 * scale), cursor_y + int(19 * scale)],
                        [cursor_x + int(8 * scale), cursor_y + int(12 * scale)],
                        [cursor_x + int(14 * scale), cursor_y + int(12 * scale)]
                    ], np.int32)
                    
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 0), thickness=int(2 * scale))
                    cv2.fillPoly(frame, [pts], color=(255, 255, 255))

                self.video_writer.write(frame)
                self.frame_count += 1
            except Exception as e:
                print(f"[Debug] Error: {e}")

    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        
        writer_to_close = self.video_writer
        self.video_writer = None
        if writer_to_close:
            threading.Thread(target=writer_to_close.release, daemon=True).start()

        if self.sct:
            self.sct.close()
            self.sct = None
            
        self.btn_record.setText("🔴")
        self.btn_record.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D; color: white; font-size: 22px; 
                border-radius: 10px; border: 1px solid #444;
            }
            QPushButton:hover { background-color: #3E3E3E; }
        """)

        if os.path.exists(self.temp_video_path) and os.path.getsize(self.temp_video_path) > 0:
            default_save_path = os.path.join(SCRIPT_DIR, "my_screen_recording.mp4")
            save_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Recording", 
                default_save_path, 
                "MP4 Video (*.mp4)"
            )

            if save_path:
                if not save_path.endswith(".mp4"):
                    save_path += ".mp4"
                
                if os.path.exists(save_path):
                    os.remove(save_path)
                os.rename(self.temp_video_path, save_path)

                self.target_video_path = save_path
                self.btn_voiceover.setEnabled(True)
                
                file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
                w, h = self.record_region["width"], self.record_region["height"]
                self.status_label.setText(
                    f"🎉 Saved: {os.path.basename(save_path)} ({file_size_mb:.1f} MB)\n"
                    f"👉 Click 🗣️ on the left panel to add Voiceover!"
                )
                QMessageBox.information(self, "Success", f"Video saved to:\n{save_path}\n\nClick 🗣️ to add Voiceover!")
            else:
                if os.path.exists(self.temp_video_path):
                    os.remove(self.temp_video_path)
                self.status_label.setText("⚠️ Save cancelled (Region retained)")
        else:
            self.status_label.setText("❌ Recording failed")
            QMessageBox.critical(self, "Error", "Video file not created! Please check Screen Recording permissions in macOS System Settings.")

    def open_existing_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            SCRIPT_DIR,
            "Video Files (*.mp4 *.mov *.avi *.mkv)"
        )
        if file_path and os.path.exists(file_path):
            self.target_video_path = file_path
            self.btn_voiceover.setEnabled(True)
            file_name = os.path.basename(file_path)
            self.status_label.setText(f"📁 Loaded Video: {file_name}\n👉 Click 🗣️ on the left panel to add Voiceover!")
            QMessageBox.information(self, "Video Loaded", f"Selected video:\n{file_path}\n\nClick 🗣️ to add Voiceover!")

    def open_voiceover_dialog(self):
        if not self.target_video_path or not os.path.exists(self.target_video_path):
            QMessageBox.warning(self, "Warning", "No video file loaded!")
            return

        dialog = VoiceoverDialog(current_script=self.saved_script_text, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            segments = dialog.get_segments()
            if not segments:
                QMessageBox.warning(self, "Warning", "No valid script lines found!")
                return

            self.saved_script_text = dialog.get_raw_text()

            self.status_label.setText("⏳ Generating Voiceover and merging with video...")
            
            self.progress_dialog = QProgressDialog("Generating Voiceover and merging...", None, 0, 0, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.show()

            self.voice_worker = VoiceoverWorker(self.target_video_path, segments)
            self.voice_worker.finished_signal.connect(self.on_voiceover_finished)
            self.voice_worker.start()

    def on_voiceover_finished(self, success, error_msg):
        if self.progress_dialog:
            self.progress_dialog.close()

        if success:
            output_video = os.path.join(
                os.path.dirname(self.target_video_path), 
                f"voiced_{os.path.basename(self.target_video_path)}"
            )
            self.status_label.setText(f"🎉 Voiceover Complete!\nExported to: {os.path.basename(output_video)}")
            QMessageBox.information(self, "Success", f"Voiceover video exported to:\n{output_video}\n\nYou can click 🗣️ anytime to modify the script and regenerate!")
        else:
            self.status_label.setText("❌ Voiceover Generation Failed")
            QMessageBox.critical(self, "Error", f"Processing failed: {error_msg}\nPlease ensure ffmpeg is installed!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderStudio()
    window.show()
    sys.exit(app.exec())