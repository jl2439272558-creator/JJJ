from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
                                 QSpinBox, QMessageBox, QFrame, QGraphicsDropShadowEffect, QSlider)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from core.timer_manager import PomodoroTimer
from app.config import app_config
from ui.dialogs.glass_dialog import LiquidGlassDialog

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150) # Slightly smaller
        self.value = 0
        self.max_value = 100
        self.color = QColor(app_config.WARM_YELLOW_PALETTE['success'])
        
    def set_value(self, value, max_value):
        self.value = value
        self.max_value = max_value
        self.update() # Trigger repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Draw background circle
        rect = QRectF((width - size) / 2 + 10, (height - size) / 2 + 10, size - 20, size - 20)
        pen = QPen(QColor("rgba(255, 255, 255, 0.3)"), 8) # Thinner, lighter background
        painter.setPen(pen)
        painter.drawEllipse(rect)
        
        # Draw progress arc
        if self.max_value > 0:
            angle = int(360 * 16 * (self.value / self.max_value))
            pen.setColor(self.color)
            pen.setWidth(8)
            pen.setCapStyle(Qt.RoundCap) # Round ends
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, angle)

class TimerDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = PomodoroTimer()
        self.timer.tick.connect(self.update_display)
        self.timer.finished.connect(self.on_finished)
        
        self.default_minutes = 25
        self.total_seconds = self.default_minutes * 60
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with Settings (Top Right)
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # Beautiful Time Selector
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(1, 120)
        self.time_slider.setValue(self.default_minutes)
        self.time_slider.setFixedWidth(120)
        self.time_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border: 1px solid #777;
                height: 10px;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #fff;
                border: 1px solid #777;
                height: 10px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eee, stop:1 #ccc);
                border: 1px solid #777;
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px;
            }
        """)
        self.time_slider.valueChanged.connect(self.update_default_time)
        
        self.time_display_lbl = QLabel(f"{self.default_minutes} min")
        self.time_display_lbl.setStyleSheet("color: #555; font-weight: bold;")
        
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("⏱️"))
        settings_layout.addWidget(self.time_slider)
        settings_layout.addWidget(self.time_display_lbl)
        
        settings_frame = QFrame()
        settings_frame.setLayout(settings_layout)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        header_layout.addWidget(settings_frame)
        layout.addLayout(header_layout)
        
        layout.addSpacing(20)
        
        # Progress Ring & Time Label Container
        # We overlay label on ring
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        
        self.progress = CircularProgress()
        center_layout.addWidget(self.progress, 0, Qt.AlignCenter)
        
        # Time Label (Floating over progress? No, just below or inside if we use layout stack)
        # For simplicity, let's put it below for now, or use negative margin
        self.time_label = QLabel(f"{self.default_minutes:02d}:00")
        self.time_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #333;")
        self.time_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.time_label)
        
        layout.addLayout(center_layout)
        
        layout.addStretch()
        
        # Controls
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.start_btn = QPushButton("开始专注")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.start_btn.setGraphicsEffect(shadow)
        
        self.start_btn.clicked.connect(self.start_timer)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 80, 80, 0.8);
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 0.5);
                color: #999;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
    def update_default_time(self, val):
        self.default_minutes = val
        self.time_display_lbl.setText(f"{val} min")
        if not self.stop_btn.isEnabled(): # Only update display if not running
            self.time_label.setText(f"{val:02d}:00")
            self.total_seconds = val * 60
            self.progress.set_value(0, 100) # Reset progress
        
    def start_timer(self):
        minutes = self.time_slider.value()
        self.total_seconds = minutes * 60
        self.timer.start(minutes)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.time_slider.setEnabled(False) # Disable changing time while running
        self.progress.color = QColor(app_config.WARM_YELLOW_PALETTE['success'])
        
    def stop_timer(self):
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.time_slider.setEnabled(True)
        
        # Reset display
        minutes = self.time_slider.value()
        self.time_label.setText(f"{minutes:02d}:00")
        self.progress.set_value(0, 100)
        
    def update_display(self, remaining_seconds):
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.progress.set_value(remaining_seconds, self.total_seconds)
        
    def on_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.time_slider.setEnabled(True)
        self.time_label.setText("Done!")
        
        # Show liquid glass notification
        dialog = LiquidGlassDialog("倒计时已结束", "恭喜！您已完成本次专注。", self.window())
        dialog.show_animated()
        
        # Reset after dialog
        minutes = self.time_slider.value()
        self.time_label.setText(f"{minutes:02d}:00")

    def update_settings(self):
        theme = app_config.settings.get("theme", "light_glass")
        if theme == "dark_glass":
            text_color = "#ccc"
            time_color = "#eee"
        else:
            text_color = "#555"
            time_color = "#333"
            
        self.time_display_lbl.setStyleSheet(f"color: {text_color}; font-weight: bold;")
        self.time_label.setStyleSheet(f"font-size: 40px; font-weight: bold; color: {time_color};")
