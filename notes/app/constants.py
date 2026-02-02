import os

import sys

# Application Info
APP_NAME = "Warm WorkLog"
APP_VERSION = "0.1.0"
ORG_NAME = "MyOrg"
ORG_DOMAIN = "myorg.com"

# Paths
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(os.path.expanduser("~"), ".worklog_desktop")
DB_PATH = os.path.join(DATA_DIR, "worklog.db")

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Timer Defaults
POMODORO_WORK_MINUTES = 25
POMODORO_BREAK_MINUTES = 5
