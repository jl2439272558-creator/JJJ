from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QCheckBox, QWidget, QToolTip
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QTimer
from PySide6.QtGui import QColor, QFont, QIcon
from app.config import app_config
from app.constants import ASSETS_DIR
import os

class NoteCard(QFrame):
    deleted = Signal(int) # note_id
    title_changed = Signal(int, str) # note_id, new_title
    urgent_changed = Signal(int, bool) # note_id, is_urgent
    completed_changed = Signal(int, bool) # note_id, is_completed

    def __init__(self, note_id, index, title, content, color, parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.index = index
        self.title = title
        self.content = content
        self.color = color
        
        # Determine urgency
        self.is_urgent = (color == "#ffcccc")
        self.is_completed = (color == "#e0e0e0")
        if self.is_completed:
            self.is_urgent = False 
        
        self.setFixedHeight(50) 
        self.setMouseTracking(True) 
        
        # Long press logic
        self.press_start_time = 0
        self.long_press_timer = QTimer(self)
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.setInterval(800) # Reduced to 800ms for better UX
        self.long_press_timer.timeout.connect(self.on_long_press)
        
        self.init_ui()
        self.update_style()
        
        # Ensure children are visible
        self.checkbox.show()
        self.num_label.show()
        self.title_edit.show()
        if hasattr(self, 'actions_widget'):
            self.actions_widget.show()

    def update_style(self):
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")

        if self.is_completed:
            if is_dark:
                bg_color = "rgba(80, 80, 80, 0.4)"
                border_color = "rgba(100, 100, 100, 0.5)"
                text_color = "#888"
            else:
                bg_color = "rgba(220, 220, 220, 0.4)"
                border_color = "rgba(200, 200, 200, 0.5)"
                text_color = "#888"
        elif self.is_urgent:
            if is_dark:
                bg_color = "rgba(139, 0, 0, 0.6)" # Dark red
                border_color = "rgba(255, 69, 0, 0.8)"
                text_color = "#fff"
            else:
                bg_color = "rgba(255, 200, 200, 0.6)"
                border_color = "rgba(255, 100, 100, 0.8)"
                text_color = "#333"
        else:
            if is_dark:
                # Use a slightly lighter dark for visibility on dark backgrounds
                bg_color = "rgba(60, 60, 60, 0.4)" 
                border_color = "rgba(255, 255, 255, 0.3)"
                text_color = "#eee"
            else:
                bg_color = "rgba(255, 255, 255, 0.5)"
                border_color = "rgba(255, 255, 255, 0.7)"
                text_color = "#333"
        
        self.setStyleSheet(f"""
            QFrame#NoteCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
                margin: 2px;
            }}
            QFrame#NoteCard:hover {{
                background-color: {bg_color.replace('0.4', '0.6').replace('0.5', '0.7').replace('0.6', '0.8').replace('0.1', '0.2')};
                border: 1px solid {border_color.replace('0.5', '0.7').replace('0.7', '0.9').replace('0.8', '1.0').replace('0.2', '0.3')};
            }}
        """)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        if hasattr(self, 'title_edit'):
            font = self.title_edit.font()
            font.setStrikeOut(self.is_completed)
            self.title_edit.setFont(font)
            
            # Determine colors
            if is_dark:
                placeholder_color = "#aaa"
            else:
                placeholder_color = "#999"

            if self.is_completed:
                style = f"""
                    QLineEdit {{
                        border: none; 
                        background: transparent; 
                        font-size: 14px; 
                        color: {text_color}; 
                        font-weight: normal;
                    }}
                    QLineEdit::placeholder {{
                        color: {placeholder_color};
                    }}
                """
            else:
                weight = "bold"
                style = f"""
                    QLineEdit {{
                        border: none; 
                        background: transparent; 
                        font-size: 14px; 
                        color: {text_color}; 
                        font-weight: {weight};
                    }}
                    QLineEdit::placeholder {{
                        color: {placeholder_color};
                    }}
                """
            self.title_edit.setStyleSheet(style)
        
        # Update number label color
        if hasattr(self, 'num_label'):
            if is_dark:
                num_color = "#aaa"
            else:
                num_color = "#888"
            self.num_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {num_color}; border: none; background: transparent;")

        # Update checkbox style for dark mode
        if hasattr(self, 'checkbox'):
             if is_dark:
                 check_border = "#888"
                 check_bg = "rgba(255,255,255,0.2)"
             else:
                 check_border = "#999"
                 check_bg = "rgba(255,255,255,0.5)"
                 
             self.checkbox.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    border: 1px solid {check_border};
                    background: {check_bg};
                }}
                QCheckBox::indicator:checked {{
                    background: #4CAF50;
                    border: 1px solid #4CAF50;
                    image: url(none); 
                }}
                QCheckBox::indicator:hover {{
                    border-color: #4CAF50;
                }}
            """)

    def init_ui(self):
        self.setObjectName("NoteCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 5, 5) 
        layout.setSpacing(5)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(20, 20)
        self.checkbox.setChecked(self.is_completed)
        self.checkbox.stateChanged.connect(self.on_completed_toggle)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 1px solid #999;
                background: rgba(255,255,255,0.5);
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                image: url(none); 
            }
            QCheckBox::indicator:hover {
                border-color: #4CAF50;
            }
        """)
        layout.addWidget(self.checkbox)
        
        # Number Label (Hidden for input row if note_id is None)
        self.num_label = QLabel(str(self.index))
        self.num_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #888; border: none; background: transparent;")
        self.num_label.setFixedWidth(20)
        self.num_label.setAlignment(Qt.AlignCenter)
        if self.note_id is None: # Input Row
             self.num_label.hide()
        layout.addWidget(self.num_label)
        
        # Title Input
        self.title_edit = QLineEdit(self.title)
        
        # Determine Placeholder and Alignment
        if self.note_id is None: # Input Row
             self.title_edit.setPlaceholderText("待办")
             self.title_edit.setAlignment(Qt.AlignCenter) # Center for input
        else:
             self.title_edit.setPlaceholderText("请输入内容...")
             self.title_edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
             
        self.title_edit.editingFinished.connect(self.on_title_edited)
        # Forward mouse events from line edit to parent for long press detection
        self.title_edit.installEventFilter(self)
        layout.addWidget(self.title_edit, 1) 
        
        # Actions Container
        self.actions_widget = QWidget(self) 
        self.actions_layout = QHBoxLayout(self.actions_widget)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(2)
        
        # Urgent Button - REMOVED as requested
        # self.urgent_btn = ...
        
        # Delete Button
        if self.note_id is not None: # Only for normal notes
            self.delete_btn = QPushButton() 
            self.delete_btn.setFixedSize(30, 30) # Back to square
            self.delete_btn.setCursor(Qt.PointingHandCursor)
            
            trash_icon_path = os.path.join(ASSETS_DIR, "icon_trash.svg")
            if os.path.exists(trash_icon_path):
                self.delete_btn.setIcon(QIcon(trash_icon_path))
                self.delete_btn.setIconSize(QSize(18, 18)) # Slightly larger icon for clarity
    
            self.delete_btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid rgba(150, 150, 150, 0.2); 
                    background: rgba(255, 255, 255, 0.5); 
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: rgba(255, 0, 0, 0.1);
                    border-color: #ff0000;
                }
            """)
            self.delete_btn.clicked.connect(self.on_delete)
            self.actions_layout.addWidget(self.delete_btn)
        
        self.actions_widget.raise_()
        
        self.update_style()
        if self.note_id is not None:
             self.check_actions_visibility()
        else:
             self.actions_widget.hide() # Hide actions for input row

    def eventFilter(self, obj, event):
        # Long press detection on title edit
        if obj == self.title_edit:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.long_press_timer.start()
            elif event.type() == QEvent.MouseButtonRelease:
                self.long_press_timer.stop()
                
        # Custom tooltip for delete button
        if hasattr(self, 'delete_btn') and obj == self.delete_btn:
            if event.type() == QEvent.Enter:
                pass
                
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.long_press_timer.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.long_press_timer.stop()
        super().mouseReleaseEvent(event)

    def on_long_press(self):
        # Toggle urgent status
        self.is_urgent = not self.is_urgent
        if self.is_urgent:
            self.is_completed = False
            self.checkbox.setChecked(False)
        self.update_style()
        self.urgent_changed.emit(self.note_id, self.is_urgent)

    def resizeEvent(self, event):
        if hasattr(self, 'actions_widget'):
            w = self.actions_widget.sizeHint().width()
            h = self.actions_widget.sizeHint().height()
            self.actions_widget.resize(w, h)
            self.actions_widget.move(self.width() - w - 5, (self.height() - h) // 2)
        super().resizeEvent(event)

    def check_actions_visibility(self):
        settings = app_config.settings.get("window", {})
        show_actions = settings.get("show_note_actions", True)
        
        if show_actions:
            self.actions_widget.setVisible(True)
        else:
            self.actions_widget.setVisible(False)

    def enterEvent(self, event):
        settings = app_config.settings.get("window", {})
        show_actions = settings.get("show_note_actions", True)
        
        if not show_actions:
             self.actions_widget.setVisible(True)
             
        super().enterEvent(event)

    def leaveEvent(self, event):
        settings = app_config.settings.get("window", {})
        show_actions = settings.get("show_note_actions", True)
        
        if not show_actions:
            self.actions_widget.setVisible(False)
            
        super().leaveEvent(event)

    def on_title_edited(self):
        # Check if widget is still valid
        try:
            if not self.isVisible(): return
        except RuntimeError:
            return
            
        new_title = self.title_edit.text()
        if new_title != self.title:
            self.title = new_title
            self.title_changed.emit(self.note_id, new_title)

    def on_completed_toggle(self, checked):
        self.is_completed = checked
        if checked:
            self.is_urgent = False
        self.update_style()
        self.completed_changed.emit(self.note_id, checked)

    def on_delete(self):
        # Disconnect signals to prevent errors during deletion
        try:
            self.title_edit.editingFinished.disconnect(self.on_title_edited)
        except RuntimeError:
            pass
        except TypeError:
            pass # Signal might not be connected
            
        self.deleted.emit(self.note_id)
    
    def set_focus(self):
        self.title_edit.setFocus()
