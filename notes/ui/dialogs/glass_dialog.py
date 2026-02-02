from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
                                 QFrame, QGraphicsDropShadowEffect, QDialog)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QPainter, QBrush, QPen
from app.config import app_config

class LiquidGlassDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(title)
        
        self.setFixedSize(280, 80) # Reduced height
        
        # UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")
        text_color = "#eee" if is_dark else "#333"
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {text_color}; font-size: 18px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)
        
        # Auto close timer
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close_animated)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")
        
        # Liquid Glass Background
        rect = self.rect()
        
        if is_dark:
            painter.setBrush(QBrush(QColor(0, 0, 0, 200))) 
            painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        else:
            painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            
        painter.drawRoundedRect(rect, 20, 20)
        
    def show_animated(self):
        screen_geo = self.screen().availableGeometry()
        
        # Target: Bottom Right with margin
        margin_right = 20
        margin_bottom = 20
        
        target_x = screen_geo.x() + screen_geo.width() - self.width() - margin_right
        target_y = screen_geo.y() + screen_geo.height() - self.height() - margin_bottom
        
        start_x = screen_geo.x() + screen_geo.width() # Outside right
        
        self.move(start_x, target_y)
        self.show()
        
        self.animation.setStartValue(QPoint(start_x, target_y))
        self.animation.setEndValue(QPoint(target_x, target_y))
        self.animation.start()
        
        # Start auto close
        self.close_timer.start(3000)
        
    def close_animated(self):
        screen_geo = self.screen().availableGeometry()
        start_pos = self.pos()
        end_pos = QPoint(screen_geo.x() + screen_geo.width(), start_pos.y())
        
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.finished.connect(self.close)
        self.animation.start()
