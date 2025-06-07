import logging
from logging.handlers import RotatingFileHandler
import sys
import os
import datetime
from config import (
    DEFAULT_EXTRACTION_DIR,
    PATH_EXTRACTION_RUNS
)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(DEFAULT_EXTRACTION_DIR, PATH_EXTRACTION_RUNS, f"extraction_{timestamp}.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def get_logger():
    logger = logging.getLogger("llm_to_graph_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG) 
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def logg_print(logger, msg):
    logger.info(msg)
    print(msg)