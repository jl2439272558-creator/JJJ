from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, QDate
from core.note_manager import NoteManager
from datetime import datetime, timedelta
from app.config import app_config

class LogItem(QFrame):
    def __init__(self, log, parent=None):
        super().__init__(parent)
        self.log = log
        self.init_ui()
        self.update_style()
        
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(15)
        
        # Action Icon
        # action_map = {
        #     "create": "🆕",
        #     "complete": "✅",
        #     "delete": "🗑️",
        #     "restore": "♻️"
        # }
        # icon_text = action_map.get(self.log.action_type, "📝")
        # self.icon_lbl = QLabel(icon_text)
        # self.icon_lbl.setFixedSize(24, 24)
        # self.icon_lbl.setAlignment(Qt.AlignCenter)
        # self.icon_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        # self.layout.addWidget(self.icon_lbl)
        
        # Content Layout (Vertical)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Note Content
        content_text = self.log.note_content or "无内容"
        if len(content_text) > 18:
            content_text = content_text[:18] + "..."
            
        self.content_lbl = QLabel(content_text)
        self.content_lbl.setStyleSheet("font-size: 14px; background: transparent; border: none;")
        content_layout.addWidget(self.content_lbl)
        
        # Time & Action Name
        action_name_map = {
            "create": "新建便签",
            "complete": "完成任务",
            "delete": "删除便签",
            "restore": "恢复便签"
        }
        action_name = action_name_map.get(self.log.action_type, self.log.action_type)
        # time_str = self.log.created_at.strftime("%H:%M")
        
        # Only show action name, no time
        self.meta_lbl = QLabel(f"{action_name}")
        self.meta_lbl.setStyleSheet("font-size: 11px; background: transparent; border: none;")
        content_layout.addWidget(self.meta_lbl)
        
        self.layout.addLayout(content_layout)
        self.layout.addStretch()

    def update_style(self):
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")
        
        if is_dark:
            bg_color = "rgba(255, 255, 255, 0.08)"
            border_color = "rgba(255, 255, 255, 0.15)"
            text_primary = "#ffffff"
            text_secondary = "#rgba(255, 255, 255, 0.6)"
            hover_bg = "rgba(255, 255, 255, 0.12)"
        else:
            bg_color = "rgba(255, 255, 255, 0.6)"
            border_color = "rgba(255, 255, 255, 0.8)"
            text_primary = "#333333"
            text_secondary = "#666666"
            hover_bg = "rgba(255, 255, 255, 0.8)"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: {hover_bg};
            }}
        """)
        
        self.content_lbl.setStyleSheet(f"color: {text_primary}; font-weight: 500; background: transparent; border: none;")
        self.meta_lbl.setStyleSheet(f"color: {text_secondary}; background: transparent; border: none;")

class OperationLogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = NoteManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title Layout
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Spacer to center title (approximate)
        title_layout.addStretch()
        
        self.title_lbl = QLabel("操作日志 (最近7天)")
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.title_lbl)
        
        title_layout.addStretch()
        
        # Clear Button
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setFixedSize(60, 30) # Increased size
        self.clear_btn.clicked.connect(self.on_clear_logs)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.05);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                color: #666;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.1);
                color: #d00;
                border-color: rgba(255, 0, 0, 0.2);
            }
        """)
        title_layout.addWidget(self.clear_btn)
        
        layout.addLayout(title_layout)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(5)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        self.update_style()
        self.refresh_logs()
        
    def on_clear_logs(self):
        reply = QMessageBox.question(self, '确认清空', 
                                     '确定要清空所有操作日志吗？此操作不可恢复。',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.manager.clear_all_logs():
                self.refresh_logs()
    
    def refresh_logs(self):
        # Clear
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                
        # Fetch logs for last 7 days
        logs = self.manager.get_logs()
        
        # Filter in python for last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        recent_logs = [log for log in logs if log.created_at >= cutoff]
        
        if not recent_logs:
            empty_lbl = QLabel("无操作记录")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #888; margin-top: 20px;")
            self.list_layout.addWidget(empty_lbl)
        else:
            # Group by date
            current_date_str = None
            today_date = datetime.now().date()
            
            for log in recent_logs:
                log_date_obj = log.created_at.date()
                log_date_str = log_date_obj.strftime("%Y-%m-%d")
                
                if log_date_str != current_date_str:
                    # Calculate friendly date
                    delta = (today_date - log_date_obj).days
                    
                    if delta == 0:
                        header_text = "今天"
                    elif delta > 0:
                        header_text = f"{delta * -1}" # Shows -1, -2, etc.
                    else:
                        header_text = log_date_str # Future date? Should not happen
                        
                    # Add Date Header
                    header = QLabel(header_text)
                    is_dark = (app_config.settings.get("theme", "light_glass") == "dark_glass")
                    color = "#aaa" if is_dark else "#666"
                    header.setStyleSheet(f"color: {color}; font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
                    self.list_layout.addWidget(header)
                    current_date_str = log_date_str
                    
                item = LogItem(log)
                self.list_layout.addWidget(item)
                
    def showEvent(self, event):
        self.refresh_logs()
        super().showEvent(event)
        
    def update_settings(self):
        self.update_style()
        self.refresh_logs()
        
    def update_style(self):
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")
        
        if is_dark:
            self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #eee;")
            self.clear_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    color: #ccc;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(255, 0, 0, 0.2);
                    color: #ffcccc;
                    border-color: rgba(255, 0, 0, 0.3);
                }
            """)
        else:
            self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
            self.clear_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 0, 0, 0.05);
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 4px;
                    color: #666;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(255, 0, 0, 0.1);
                    color: #d00;
                    border-color: rgba(255, 0, 0, 0.2);
                }
            """)