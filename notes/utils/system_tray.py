from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from app.constants import ASSETS_DIR
import os

class SystemTrayManager:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.tray_icon = QSystemTrayIcon(window)
        
        # Load Icon
        icon_path = os.path.join(ASSETS_DIR, "favicon.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback (though file should exist now)
            pass
        
        self.init_menu()
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_activated)

    def init_menu(self):
        menu = QMenu()
        
        show_action = QAction("显示主界面", self.window)
        show_action.triggered.connect(self.window.show)
        menu.addAction(show_action)
        
        settings_action = QAction("设置", self.window)
        settings_action.triggered.connect(self.window.open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", self.window)
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.window.show()
