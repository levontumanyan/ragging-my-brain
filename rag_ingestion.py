#!/usr/bin/env python3
import os
import hashlib
import json
import logging
from pathlib import Path
import time
from typing import List

BASE_DIR = Path("../")
IGNORE_DIRS = {".git", ".github", ".DS_Store", "__pycache__"}

def setup_logger():
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s [%(levelname)s] %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

logger = logging.getLogger(__name__)

# retrieve all the md filenames while ignoring irrelevant directories
def retrieve_md_filenames(base_dir: Path) -> List[Path]:
	md_files = []

	for root, dirs, files in os.walk(base_dir):
		# remove ignored dirs from traversal
		dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
		for file in files:
			if file.endswith(".md"):
				md_files.append(Path(root) / file)

	return md_files

# create data dir
def create_data_dir() -> Path:
	data_dir = Path("data/")
	data_dir.mkdir(exist_ok=True)
	return data_dir

# this is where we store the hashes of files, in order to not run the pipeline on those files for which the content hasn't changed.
def create_metadata_file(data_dir: Path) -> Path:
	metadata_file = data_dir / "metadata.json"

	if not metadata_file.exists():
		logger.info(f"Metadata file doesn't exist")
		metadata_file.write_text("{}")  # create an empty JSON file
		logger.info(f"{metadata_file} created with empty json.")
	
	return metadata_file

# say at this point
# for a file from markdown files list. i hash it and i check the metadata.json entry. if it's the same then we good. otherwise we update the entry and will make sure this file is processed again.

# pass a path object and compute the hash. this does it in a memory efficient way but doesn't call md5 several times. only once per file.
def hash_md_file(md_file: Path) -> str:
	h = hashlib.md5()

	# read in chunks for memory efficiency
	with md_file.open("rb") as f:
		while chunk := f.read(8192):
			h.update(chunk)

	return h.hexdigest()

# load metadata.json into a dict and return it
def load_metadata_json(metadata_file) -> dict:
	with open(metadata_file, "r", encoding="utf-8") as f:
		metadata = json.load(f)  # metadata is now a Python dict
		logger.info(f"Loaded metadata.json into a dict")

	return metadata

# for a markdown file receive the path, it's current hash and the metadata dict. compare current hash with the old one(if exists) and if hash has changed update the dict and return True
def needs_processing(md_relative_path: str, current_md_hash: str, metadata: dict) -> bool:
	if md_relative_path in metadata:
		if metadata[md_relative_path] != current_md_hash:
			metadata[md_relative_path] = current_md_hash
			return True
	else:
		# new file → process it
		metadata[md_relative_path] = current_md_hash
		return True

def save_metadata_json(metadata_file: Path, metadata: dict) -> None:
	try:
		with metadata_file.open("w", encoding="utf-8") as f:
			json.dump(metadata, f, indent=2)
			logger.info(f"Wrote dict with hashes to metadata.json")
	except (OSError, json.JSONDecodeError) as e:
		logger.error(f"Error saving metadata to {metadata_file}: {e}")

def read_md_file(md_file: Path) -> str:
	"""
	Read a markdown file and return its content as a string.
	"""
	try:
		with md_file.open("r", encoding="utf-8") as f:
			content = f.read()
		return content
	except Exception as e:
		logger.error(f"Error reading {md_file}: {e}")
		return ""
		
def preprocess_md_content(content: str) -> str:
	"""
	TODO
	Optional preprocessing step. Currently does nothing.
	You can add cleaning, stripping, Markdown parsing, etc. later.
	"""
	return content

def main():
	# start timer
	start_time = time.perf_counter()

	# start logger
	setup_logger()

	logger.info('Rag pipeline started')

	# create a path object to data dir
	data_dir = create_data_dir()

	# create or check metadata.json exists
	metadata_file = create_metadata_file(data_dir)

	# get the dict with metadata
	metadata = load_metadata_json(metadata_file)

	# create an array that will store files to be processed (hash has changed)
	mds_to_process = []

	md_files = retrieve_md_filenames(BASE_DIR)

	for md_file in md_files:
		# compute the md5 hash of the md file
		current_md_hash = hash_md_file(md_file)
		
		# this returns a path without the ../ as a string
		md_relative_path = str(md_file.relative_to(BASE_DIR))

		if needs_processing(md_relative_path, current_md_hash, metadata):
			mds_to_process.append(md_file)

	# write these hashes to the metadata.json file from metadata dict
	try:
		save_metadata_json(metadata_file, metadata)

	except Exception as e:
		logger.error(f"❌ Fatal error: {e}")
		# stop main()
		return
	
	for md_file in md_files:
		pass

	# end timer, count relapsed time
	end_time = time.perf_counter()
	elapsed = end_time - start_time
	logger.info(f'Rag pipeline completed successfully in {elapsed:.9f} seconds.')

# --- entry point ---
if __name__ == "__main__":
	main()
