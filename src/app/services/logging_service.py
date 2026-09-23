import logging
from pathlib import Path

from app.config.settings import APP_NAME, LOG_DIR


class LoggingService:
    _configured = False

    @classmethod
    def configure(cls) -> logging.Logger:
        logger = logging.getLogger(APP_NAME)
        if cls._configured:
            return logger

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.FileHandler(LOG_DIR / "subforge.log", encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        cls._configured = True
        return logger

    @classmethod
    def get_logger(cls, name: str | None = None) -> logging.Logger:
        cls.configure()
        return logging.getLogger(f"{APP_NAME}.{name}" if name else APP_NAME)

    @staticmethod
    def log_path() -> Path:
        return LOG_DIR / "subforge.log"
