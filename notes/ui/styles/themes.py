from app.config import app_config

class ThemeManager:
    @staticmethod
    def get_glass_stylesheet():
        # Glassmorphism Colors
        # Using RGBA for translucency
        glass_bg = "rgba(255, 255, 255, 0.4)" 
        glass_border = "rgba(255, 255, 255, 0.6)"
        glass_highlight = "rgba(255, 255, 255, 0.8)"
        text_primary = "#333333"
        accent_color = "rgba(255, 215, 0, 0.5)" # Gold/Yellow tint
        
        qss = f"""
        QMainWindow {{
            background: transparent;
        }}
        
        QWidget {{
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            font-size: 14px;
            color: {text_primary};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {glass_bg};
            border: 1px solid {glass_border};
            border-radius: 12px;
            padding: 8px 16px;
            color: {text_primary};
        }}

        QPushButton:hover {{
            background-color: {glass_highlight};
            border-color: white;
        }}

        QPushButton:pressed {{
            background-color: {accent_color};
        }}

        /* Inputs */
        QLineEdit, QTextEdit {{
            background-color: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 6px;
            selection-background-color: {accent_color};
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            background-color: rgba(255, 255, 255, 0.8);
            border-color: {glass_highlight};
        }}

        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        /* Scrollbar */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(0, 0, 0, 0.1);
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* TabWidget (Hidden TabBar mainly) */
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        
        QTabWidget > QTabBar::tab {{
            width: 0px;
            height: 0px;
            padding: 0px;
            border: none;
            margin: 0px;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid white;
            color: #333;
            border-radius: 4px;
        }}
        """
        return qss

    @staticmethod
    def apply_theme(app):
        app.setStyleSheet(ThemeManager.get_glass_stylesheet())
