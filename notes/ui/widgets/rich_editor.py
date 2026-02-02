from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QToolBar
from PySide6.QtGui import QAction, QFont, QTextCharFormat
from PySide6.QtCore import Qt

class RichEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.layout.addWidget(self.toolbar)
        
        # Editor
        self.editor = QTextEdit()
        self.layout.addWidget(self.editor)
        
        self.init_toolbar()
        
    def init_toolbar(self):
        bold_action = QAction("Bold", self)
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(self.set_bold)
        self.toolbar.addAction(bold_action)
        
        italic_action = QAction("Italic", self)
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(self.set_italic)
        self.toolbar.addAction(italic_action)
        
        underline_action = QAction("Underline", self)
        underline_action.setShortcut("Ctrl+U")
        underline_action.triggered.connect(self.set_underline)
        self.toolbar.addAction(underline_action)
        
    def set_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.editor.fontWeight() != QFont.Bold else QFont.Normal)
        self.editor.mergeCurrentCharFormat(fmt)
        
    def set_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self.editor.mergeCurrentCharFormat(fmt)
        
    def set_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self.editor.mergeCurrentCharFormat(fmt)

    def get_content(self):
        return self.editor.toHtml()
    
    def set_content(self, html):
        self.editor.setHtml(html)
