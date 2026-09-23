from pathlib import Path

APP_NAME = "SubForge"
APP_VERSION = "0.1.0"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 560

APP_DATA_DIR = Path.home() / "AppData" / "Local" / APP_NAME
LOG_DIR = APP_DATA_DIR / "logs"
