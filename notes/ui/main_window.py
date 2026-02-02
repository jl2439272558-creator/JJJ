from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                                 QApplication, QToolButton, QHBoxLayout, QButtonGroup,
                                 QGraphicsDropShadowEffect, QFrame, QPushButton, QLabel)
from PySide6.QtGui import QIcon, QAction, QScreen, QPainter, QColor, QPen, QBrush, QRegion, QPainterPath, QCursor, QPixmap
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QPoint, QEasingCurve, QSize
from app.constants import APP_NAME, ASSETS_DIR
from app.config import app_config
from ui.widgets.note_manager_widget import NoteManagerWidget
from ui.widgets.timer_display import TimerDisplayWidget
from ui.widgets.log_widget import OperationLogWidget
from ui.dialogs.settings_dialog import SettingsDialog
from utils.system_tray import SystemTrayManager
import os

class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(40, 40) # Smaller buttons
        self.setCursor(Qt.PointingHandCursor)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(32, 32))
            self.setToolTip(text) # Use text as tooltip
        else:
            self.setText(text)
            
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #555;
                font-size: 24px; 
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2); 
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(300, 500) 
        
        # Icon
        self.icon_path = os.path.join(ASSETS_DIR, "favicon.ico")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        
        # Frameless Window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool) 
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Disable context menu globally
        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        # Central Widget Container (for rounded corners)
        self.container = QWidget()
        self.container.setObjectName("container")
        self.setCentralWidget(self.container)
        
        # Main Layout (Horizontal)
        self.main_layout = QHBoxLayout(self.container)
        self.main_layout.setContentsMargins(5, 5, 5, 5) 
        self.main_layout.setSpacing(5)
        
        # 1. Sidebar
        self.init_sidebar()
        
        # 2. Content Area
        self.init_content_area()
        
        # Initialize Tabs
        self.init_tabs()
        
        # System Tray
        self.tray = SystemTrayManager(QApplication.instance(), self)
        
        # Edge Docking Logic
        self.dock_timer = QTimer(self)
        self.dock_timer.setInterval(300)
        self.dock_timer.timeout.connect(self.check_docking)
        self.dock_timer.start()
        
        self.dock_state = "normal"
        self.is_hidden = False
        
        # Load Settings
        self.apply_settings()
        
        # Dragging logic
        self.drag_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear
        painter.fillRect(self.rect(), Qt.transparent)
        
        # Draw Dock Icon when hidden
        if self.is_hidden and os.path.exists(self.icon_path):
             # Force hide all child widgets
             self.sidebar.hide()
             self.content_frame.hide()
             
             icon_size = 32
             # Calculate position for the 56x56 bubble
             rect_size = 56
             
             bubble_rect = QRect(0, 0, rect_size, rect_size)
             
             if self.dock_state == "left":
                 bubble_rect.moveTopRight(QPoint(self.width() - 5, (self.height() - rect_size) // 2))
             elif self.dock_state == "right":
                 bubble_rect.moveTopLeft(QPoint(5, (self.height() - rect_size) // 2))
             elif self.dock_state == "top":
                 bubble_rect.moveBottomLeft(QPoint((self.width() - rect_size) // 2, self.height() - 5))
             
             # Draw Bubble Background - Transparent
             # painter.setBrush(QBrush(QColor(255, 255, 255, 200))) # Removed background
             # painter.setPen(Qt.NoPen)
             # painter.drawRoundedRect(bubble_rect, 15, 15)
             
             # Draw Icon
             icon_pixmap = QPixmap(self.icon_path).scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             icon_x = bubble_rect.x() + (rect_size - icon_size) // 2
             icon_y = bubble_rect.y() + (rect_size - icon_size) // 2
             painter.drawPixmap(icon_x, icon_y, icon_pixmap)
             
             return # Do not draw the rest of the window when hidden

        # Draw Main Window Background (Normal State)
        # Ensure child widgets are visible
        if self.sidebar.isHidden(): self.sidebar.show()
        if self.content_frame.isHidden(): self.content_frame.show()
        
        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.setBrush(QBrush(QColor(255, 255, 255, 180))) # Semi-transparent white
        painter.setPen(Qt.NoPen)
        # painter.drawRoundedRect(rect, 15, 15) # Optional: if you want a global background
        pass

    def init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(50) # Reduced width by 50%
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.4);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 15, 0, 15)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignHCenter)
        
        # Buttons
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        # Icons (Text, Index, IconName)
        items = [
            ("便签", 0, "icon_notes.svg"), 
            ("番茄钟", 1, "icon_timer.svg"),
            ("日志", 2, "icon_log.svg"),
        ]
        
        for text, idx, icon_name in items:
            icon_path = os.path.join(ASSETS_DIR, icon_name)
            btn = SidebarButton(text, icon_path)
            btn.setFixedSize(30, 30) # Reduced size by 50%
            btn.setIconSize(QSize(20, 20)) # Reduced icon size
            self.btn_group.addButton(btn, idx)
            layout.addWidget(btn)
            btn.clicked.connect(lambda checked, i=idx: self.tabs.setCurrentIndex(i))
            
        layout.addStretch()
        
        self.main_layout.addWidget(self.sidebar)
        
        # Default check
        self.btn_group.button(0).setChecked(True)

    def init_content_area(self):
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.8);
            }
        """)
        
        layout = QVBoxLayout(self.content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab Widget (Hidden Header)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().hide()
        self.tabs.setStyleSheet("background: transparent; border: none;")
        
        layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.content_frame)

    def init_tabs(self):
        self.note_tab = NoteManagerWidget()
        self.timer_tab = TimerDisplayWidget()
        self.log_tab = OperationLogWidget()
        
        self.tabs.addTab(self.note_tab, "便签")
        self.tabs.addTab(self.timer_tab, "番茄钟")
        self.tabs.addTab(self.log_tab, "操作日志")
        
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.apply_settings()
            
    def apply_settings(self):
        settings = app_config.settings.get("window", {})
        
        # Apply Theme
        theme = app_config.settings.get("theme", "light_glass")
        self.apply_theme(theme)
        
        # Always on Top
        flags = self.windowFlags()
        if settings.get("always_on_top", False):
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        
        # Ensure Tool flag is always set to hide from taskbar
        flags |= Qt.Tool
            
        self.setWindowFlags(flags)
        self.show()
        
        # Notify child widgets of settings update
        if hasattr(self, 'note_tab') and hasattr(self.note_tab, 'update_settings'):
            self.note_tab.update_settings()
        if hasattr(self, 'timer_tab') and hasattr(self.timer_tab, 'update_settings'):
            self.timer_tab.update_settings()
        if hasattr(self, 'log_tab') and hasattr(self.log_tab, 'update_settings'):
            self.log_tab.update_settings()

    def apply_theme(self, theme):
        if theme == "dark_glass":
            # Dark Theme
            self.sidebar.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.4);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
            """)
            self.content_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.5);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
            """)
            # Buttons text color for dark mode
            for btn in self.btn_group.buttons():
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        color: #ccc;
                        font-size: 24px; 
                        border-radius: 10px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.1); 
                    }
                    QPushButton:checked {
                        background-color: rgba(255, 255, 255, 0.2);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                    }
                """)
        else:
            # Light Theme (Default)
            self.sidebar.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.4);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.6);
                }
            """)
            self.content_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.5);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }
            """)
            # Reset buttons
            for btn in self.btn_group.buttons():
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        color: #555;
                        font-size: 24px; 
                        border-radius: 10px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.2); 
                    }
                    QPushButton:checked {
                        background-color: rgba(255, 255, 255, 0.4);
                        border: 1px solid rgba(255, 255, 255, 0.6);
                    }
                """)
        
    # --- Dragging Logic ---
    def mousePressEvent(self, event):
        # Allow dragging from sidebar or margins
        # Check if click is not on a button
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    # --- Edge Docking Logic ---
    
    def check_docking(self):
        settings = app_config.settings.get("window", {})
        if not settings.get("auto_hide", False):
            return

        if self.isFullScreen() or self.isMaximized():
            return

        pos = self.pos()
        geo = self.geometry()
        screen_geo = self.screen().availableGeometry()
        
        margin = 20
        docked = False
        
        if pos.y() < screen_geo.y() + margin:
            self.dock_state = "top"
            docked = True
        elif pos.x() < screen_geo.x() + margin:
            self.dock_state = "left"
            docked = True
        elif pos.x() + geo.width() > screen_geo.x() + screen_geo.width() - margin:
            self.dock_state = "right"
            docked = True
        else:
            self.dock_state = "normal"
            self.is_hidden = False
            
        if not docked:
            return

        # Auto Hide Logic
        if self.underMouse():
            if self.is_hidden:
                self.animate_slide(show=True)
        else:
            if not self.is_hidden and not self.isActiveWindow():
                self.animate_slide(show=False)

    def animate_slide(self, show):
        screen_geo = self.screen().availableGeometry()
        geo = self.geometry()
        target_pos = QPoint(geo.x(), geo.y())
        
        hidden_margin = 40 # Increased to allow icon to be visible
        
        if self.dock_state == "top":
            if show:
                target_pos.setY(screen_geo.y())
            else:
                target_pos.setY(screen_geo.y() - geo.height() + hidden_margin)
                
        elif self.dock_state == "left":
            if show:
                target_pos.setX(screen_geo.x())
            else:
                target_pos.setX(screen_geo.x() - geo.width() + hidden_margin)
                
        elif self.dock_state == "right":
            if show:
                target_pos.setX(screen_geo.x() + screen_geo.width() - geo.width())
            else:
                target_pos.setX(screen_geo.x() + screen_geo.width() - hidden_margin)
        
        if target_pos != self.pos():
            self.anim = QPropertyAnimation(self, b"pos")
            self.anim.setDuration(300)
            self.anim.setStartValue(self.pos())
            self.anim.setEndValue(target_pos)
            self.anim.setEasingCurve(QEasingCurve.OutQuad)
            self.anim.start()
            self.is_hidden = not show
            self.update() # Trigger repaint to show/hide icon
