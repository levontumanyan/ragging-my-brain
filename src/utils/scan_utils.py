import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# retrieve all the md filenames while ignoring irrelevant directories
def retrieve_md_filenames(base_dir: Path, ignore_dirs: set) -> list[Path]:
	logger.info(f"Ignoring directories: {ignore_dirs}")
	md_files = []

	for root, dirs, files in os.walk(base_dir):
		# remove ignored dirs from traversal
		dirs[:] = [d for d in dirs if d not in ignore_dirs]
		for file in files:
			if file.endswith(".md"):
				md_files.append(Path(root) / file)

	return md_files
