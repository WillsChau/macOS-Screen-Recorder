import sys
import os
import cv2
import numpy as np
import mss

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QFrame, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QColor, QCursor


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


class ScreenRecorderStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder (Mac)")
        self.resize(600, 350)
        
        self.is_recording = False
        self.temp_video_path = os.path.expanduser("~/Downloads/temp_recording.mp4")
        
        self.sct = None
        self.record_region = None  # 紀錄選取區域（Save 後會保留）
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

        self.btn_select_area = QPushButton("📐")
        self.btn_record = QPushButton("🔴")
        
        for btn in (self.btn_select_area, self.btn_record):
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D; color: white; font-size: 22px; 
                    border-radius: 10px; border: 1px solid #444;
                }
                QPushButton:hover { background-color: #3E3E3E; }
            """)
            left_layout.addWidget(btn)

        self.btn_select_area.setToolTip("選擇錄影區域")
        self.btn_record.setToolTip("開始/停止錄影")
        
        self.btn_select_area.clicked.connect(self.select_custom_area)
        self.btn_record.clicked.connect(self.toggle_recording)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        canvas_container = QWidget()
        canvas_container.setStyleSheet("background-color: #121212;")
        canvas_layout = QVBoxLayout(canvas_container)
        
        self.status_label = QLabel("點擊 📐 選擇區域\n或直接點擊 🔴 開始全螢幕錄影")
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
            self.status_label.setText(f"✅ 已鎖定區域：{w}x{h} px\n按 🔴 開始錄影 (此區域會一直保留)")

    def toggle_recording(self):
        if not self.is_recording:
            self.sct = mss.MSS()
            
            # 若之前沒選過區域，預設抓全螢幕
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

            codecs = ["mp4v", "avc1", "MJPG"]
            self.video_writer = None
            
            for codec in codecs:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                writer = cv2.VideoWriter(self.temp_video_path, fourcc, 20.0, (width, height))
                if writer.isOpened():
                    self.video_writer = writer
                    break

            if not self.video_writer or not self.video_writer.isOpened():
                QMessageBox.critical(self, "錯誤", "無法初始化 Mac 影片寫入器！")
                return

            self.is_recording = True
            self.frame_count = 0
            self.btn_record.setText("⏹️")
            self.btn_record.setStyleSheet("background-color: #AA0000; color: white; font-size: 22px; border-radius: 10px;")
            self.status_label.setText("🔴 錄影中...")
            
            self.timer.start(40)
        else:
            self.stop_recording()

    def record_frame(self):
        if self.is_recording and self.sct and self.video_writer:
            try:
                img = np.array(self.sct.grab(self.record_region))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, (self.record_region["width"], self.record_region["height"]))
                
                # 繪製滑鼠游標
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
                print(f"[Debug] Frame write error: {e}")

    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
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

        # 【關鍵修改】：移除 self.record_region = None，讓選區資訊繼續留給下一次錄影使用！

        if os.path.exists(self.temp_video_path) and os.path.getsize(self.temp_video_path) > 0:
            default_save_path = os.path.expanduser("~/Downloads/my_screen_recording.mp4")
            save_path, _ = QFileDialog.getSaveFileName(
                self, 
                "儲存影片", 
                default_save_path, 
                "MP4 Video (*.mp4)"
            )

            if save_path:
                if not save_path.endswith(".mp4"):
                    save_path += ".mp4"
                
                if os.path.exists(save_path):
                    os.remove(save_path)
                os.rename(self.temp_video_path, save_path)

                w, h = self.record_region["width"], self.record_region["height"]
                self.status_label.setText(f"🎉 儲存成功：{os.path.basename(save_path)}\n📍 目前維持選區 ({w}x{h} px)，可以直接再按 🔴 續錄！")
                QMessageBox.information(self, "成功", f"影片已儲存至：\n{save_path}")
            else:
                if os.path.exists(self.temp_video_path):
                    os.remove(self.temp_video_path)
                self.status_label.setText("⚠️ 取消儲存 (區域仍保留中)")
        else:
            self.status_label.setText("❌ 錄影失敗，未生成檔案")
            QMessageBox.critical(self, "錄影失敗", "檔案未順利生成！請檢查是否有開啟 Mac「螢幕錄製」權限。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenRecorderStudio()
    window.show()
    sys.exit(app.exec())