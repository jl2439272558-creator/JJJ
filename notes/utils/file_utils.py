import os
import shutil
from datetime import datetime

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_file(content, path):
    ensure_directory(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_file(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def get_backup_filename():
    return f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
