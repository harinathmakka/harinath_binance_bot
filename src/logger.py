# src/logger.py
from loguru import logger
import sys
from .config import LOG_PATH

logger.remove()
logger.add(sys.stdout, level="INFO", enqueue=True, backtrace=False, diagnose=False)
logger.add(LOG_PATH, rotation="10 MB", retention="7 days", compression="zip", level="DEBUG", serialize=False)

def log_action(action: str, **kwargs):
    entry = {"action": action}
    entry.update(kwargs)
    logger.info(entry)
