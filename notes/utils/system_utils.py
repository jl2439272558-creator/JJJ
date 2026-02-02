import sys
import os
import winreg

class SystemUtils:
    APP_NAME = "WarmWorkLog"
    
    @staticmethod
    def set_auto_start(enable: bool):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                exe_path = sys.executable
                # If running as script, use python.exe + script path, but usually for auto start we want the frozen exe
                # If we are not frozen, we might skip this or point to python
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    # Development mode: point to main.py
                    # Note: This might not work perfectly if dependencies are complex, but good for testing
                    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "main.py")
                    exe_path = f'"{sys.executable}" "{script_path}"'
                
                winreg.SetValueEx(key, SystemUtils.APP_NAME, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, SystemUtils.APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Auto start error: {e}")
            return False

    @staticmethod
    def is_auto_start_enabled():
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, SystemUtils.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
