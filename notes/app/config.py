from .constants import DATA_DIR
import os
import json

class Config:
    WARM_YELLOW_PALETTE = {
        "primary_background": "#FFF9E6",      # 主背景 - 柔和米黄
        "secondary_background": "#FFF3CD",    # 次背景 - 浅卡其
        "primary_accent": "#FFD166",          # 主强调色 - 琥珀黄
        "secondary_accent": "#FFE8A0",        # 次强调色 - 淡黄
        "text_primary": "#5C4B00",            # 主要文字 - 深棕黄
        "text_secondary": "#8A7B3D",          # 次要文字
        "border_light": "#E6D8AD",            # 浅边框
        "border_dark": "#D4B74A",             # 深边框
        "success": "#8AC926",                 # 成功色
        "warning": "#FF9F1C",                 # 警告色
        "error": "#FF595E",                   # 错误色
        "info": "#1982C4",                    # 信息色
    }

    def __init__(self):
        self.config_path = os.path.join(DATA_DIR, "config.json")
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self.default_settings()
        else:
            return self.default_settings()

    def default_settings(self):
        return {
            "theme": "light_glass", # default to light glass
            "timer": {
                "work_duration": 25,
                "break_duration": 5,
                "sound_enabled": True
            },
            "window": {
                "width": 300,
                "height": 500,
                "opacity": 1.0,
                "always_on_top": True,
                "auto_start": False,
                "auto_hide": True,
                "show_note_actions": True
            }
        }

    def save_settings(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

# Global config instance
app_config = Config()
