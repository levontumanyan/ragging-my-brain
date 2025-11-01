import os
import logging
from dotenv import load_dotenv
from pathlib import Path

def setup_logger(debug: bool=False):
	logger = logging.getLogger("rag")
	logging.basicConfig(
		level=logging.DEBUG if debug else logging.INFO,
		format="%(asctime)s [%(levelname)s] %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)
	return logger

load_dotenv()
KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR"))
IGNORE_DIRS = set(os.getenv("IGNORE_DIRS", "").split(","))
