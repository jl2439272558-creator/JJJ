from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QSlider, QCheckBox, QPushButton, QGroupBox, QComboBox)
from PySide6.QtCore import Qt
from app.config import app_config
from utils.system_utils import SystemUtils

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(400, 450) # Increased height
        self.settings = app_config.settings
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Appearance Settings
        app_group = QGroupBox("外观设置")
        app_layout = QVBoxLayout()
        
        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("主题:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("透明白 (Light Glass)", "light_glass")
        self.theme_combo.addItem("透明黑 (Dark Glass)", "dark_glass")
        # self.theme_combo.addItem("暖黄 (Warm Yellow)", "warm_yellow") # Deprecated? Keep for compat
        theme_layout.addWidget(self.theme_combo)
        app_layout.addLayout(theme_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100) # 20% to 100%
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_value_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_value_label)
        app_layout.addLayout(opacity_layout)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # Window Settings
        win_group = QGroupBox("窗口设置")
        win_layout = QVBoxLayout()
        
        # Always on Top
        self.top_check = QCheckBox("保持置顶")
        win_layout.addWidget(self.top_check)
        
        # Auto Hide
        self.autohide_check = QCheckBox("边缘自动隐藏")
        win_layout.addWidget(self.autohide_check)

        # Show Note Actions
        self.show_actions_check = QCheckBox("显示便签操作按钮 (删除/加急)")
        win_layout.addWidget(self.show_actions_check)
        
        win_group.setLayout(win_layout)
        layout.addWidget(win_group)
        
        # System Settings
        sys_group = QGroupBox("系统设置")
        sys_layout = QVBoxLayout()
        
        # Auto Start
        self.autostart_check = QCheckBox("开机自启动")
        sys_layout.addWidget(self.autostart_check)
        
        sys_group.setLayout(sys_layout)
        layout.addWidget(sys_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def load_current_settings(self):
        win_settings = self.settings.get("window", {})
        
        # Theme
        current_theme = self.settings.get("theme", "light_glass")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Opacity
        opacity = win_settings.get("opacity", 1.0)
        self.opacity_slider.setValue(int(opacity * 100))
        self.opacity_value_label.setText(f"{int(opacity * 100)}%")
        
        # Checks
        self.top_check.setChecked(win_settings.get("always_on_top", False))
        self.autohide_check.setChecked(win_settings.get("auto_hide", False))
        self.show_actions_check.setChecked(win_settings.get("show_note_actions", True))
        
        # Auto Start
        self.autostart_check.setChecked(SystemUtils.is_auto_start_enabled())
        
    def on_opacity_changed(self, value):
        self.opacity_value_label.setText(f"{value}%")
        # Preview opacity on parent if possible
        if self.parent():
            self.parent().setWindowOpacity(value / 100.0)
            
    def save_settings(self):
        # Update config object
        self.settings["theme"] = self.theme_combo.currentData()
        
        win_settings = self.settings.setdefault("window", {})
        win_settings["opacity"] = self.opacity_slider.value() / 100.0
        win_settings["always_on_top"] = self.top_check.isChecked()
        win_settings["auto_hide"] = self.autohide_check.isChecked()
        win_settings["show_note_actions"] = self.show_actions_check.isChecked()
        
        # Save to file
        app_config.save_settings()
        
        # Apply System Utils
        SystemUtils.set_auto_start(self.autostart_check.isChecked())
        
        self.accept()
