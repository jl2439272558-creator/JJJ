from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                 QScrollArea, QFrame, QGraphicsOpacityEffect, QLineEdit, QLabel)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from core.note_manager import NoteManager
from ui.widgets.note_card import NoteCard
from app.config import app_config

class NoteManagerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = NoteManager()
        self.init_ui()
        self.refresh_notes()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area for Notes (List View)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        
        # Use QVBoxLayout for list
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10)
        self.list_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Page Title "待办"
        self.title_label = QLabel("待办")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 5px;")
        self.list_layout.addWidget(self.title_label)
        
        # 2. Input Field
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("请输入待办事项，回车创建...")
        self.input_edit.setFixedHeight(40)
        self.input_edit.returnPressed.connect(self.on_input_return_pressed)
        
        # Initial style check
        self.update_input_style()
        
        self.list_layout.addWidget(self.input_edit)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

    def update_input_style(self):
        theme = app_config.settings.get("theme", "light_glass")
        is_dark = (theme == "dark_glass")
        
        if is_dark:
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #eee; margin-bottom: 5px;")
            self.input_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 5px 10px;
                    background: rgba(0,0,0,0.2);
                    color: #eee;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    background: rgba(0,0,0,0.4);
                    border: 1px solid rgba(255,255,255,0.3);
                }
            """)
        else:
            self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 5px;")
            self.input_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid rgba(0,0,0,0.1);
                    border-radius: 8px;
                    padding: 5px 10px;
                    background: rgba(255,255,255,0.5);
                    color: #333;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    background: rgba(255,255,255,0.8);
                    border: 1px solid rgba(0,0,0,0.2);
                }
            """)

    def on_input_return_pressed(self):
        text = self.input_edit.text().strip()
        if text:
            # Create new note with this text
            note = self.manager.create_note(text, "")
            
            # Clear input
            self.input_edit.clear()
            
            # Refresh list
            self.refresh_notes()
            
            # Focus back to input
            self.input_edit.setFocus()
        
    def add_note_card(self, note, index):
        card = NoteCard(note.id, index, note.title, note.content, note.color)
        card.title_changed.connect(self.update_note_title)
        card.urgent_changed.connect(self.update_note_urgency)
        card.completed_changed.connect(self.update_note_completion)
        card.deleted.connect(self.delete_note)
        
        # New Note Animation (Fade In)
        # We can't animate geometry easily in layout without doing it before adding to layout
        # Instead, let's use window opacity for fade-in
        # Only animate if it's very new (created just now)? 
        # For simplicity, we skip animation on load, but we can check note timestamp if needed.
        # But here we just add it.
        
        self.list_layout.addWidget(card)
        return card

    def update_note_title(self, note_id, new_title):
        note = self.manager.get_note(note_id)
        if note:
            self.manager.update_note(note_id, new_title, note.content)

    def update_note_urgency(self, note_id, is_urgent):
        note = self.manager.get_note(note_id)
        if note:
            new_color = "#ffcccc" if is_urgent else "#ffffff" 
            self.manager.update_note(note_id, note.title, note.content, new_color)

    def update_note_completion(self, note_id, is_completed):
        note = self.manager.get_note(note_id)
        if note:
            new_color = "#e0e0e0" if is_completed else "#ffffff"
            self.manager.update_note(note_id, note.title, note.content, new_color)
            
            # Find the card
            card = None
            for i in range(self.list_layout.count()):
                item = self.list_layout.itemAt(i)
                w = item.widget()
                if isinstance(w, NoteCard) and w.note_id == note_id:
                    card = w
                    break
            
            if card:
                # Fade out animation before refresh
                opacity_effect = QGraphicsOpacityEffect(card)
                card.setGraphicsEffect(opacity_effect)
                anim = QPropertyAnimation(opacity_effect, b"opacity")
                anim.setDuration(300)
                anim.setStartValue(1)
                anim.setEndValue(0)
                anim.setEasingCurve(QEasingCurve.InQuad)
                anim.finished.connect(self.refresh_notes) # Refresh after fade out to re-sort
                anim.start(QPropertyAnimation.DeleteWhenStopped)
            else:
                self.refresh_notes()

    def delete_note(self, note_id):
        print(f"DEBUG: Attempting to delete note {note_id}")
        # Simplest, most robust delete implementation (Hard Delete)
        success = self.manager.delete_note(note_id)
        if success:
            print(f"DEBUG: Successfully deleted note {note_id}")
            # Refresh immediately to sync UI with DB
            self.refresh_notes()
        else:
            print(f"DEBUG: Failed to delete note {note_id}")
    
    def refresh_notes(self):
        # Clear existing items but KEEP the Title and Input
        # Items 0 and 1 are Title and Input
        # We start removing from index 2
        
        while self.list_layout.count() > 2:
            item = self.list_layout.takeAt(2)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Properly destroy widget
        
        notes = self.manager.get_all_notes()
        
        # Add notes as list items
        for i, note in enumerate(notes, 1):
             self.add_note_card(note, i) 
             
    def update_settings(self):
        self.update_input_style()
