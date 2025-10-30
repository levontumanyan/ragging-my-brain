#!/usr/bin/env python3
import os
import logging
import hashlib
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# retrieve all the md filenames while ignoring irrelevant directories
def retrieve_md_filenames(base_dir: Path, ignore_dirs: set) -> List[Path]:
	logger.info(f"Ignoring directories: {ignore_dirs}")
	md_files = []

	for root, dirs, files in os.walk(base_dir):
		# remove ignored dirs from traversal
		dirs[:] = [d for d in dirs if d not in ignore_dirs]
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
def create_metadata_file(data_dir: Path, name: str) -> Path:
	metadata_file = data_dir / name

	if not metadata_file.exists():
		logger.info(f"Metadata file doesn't exist")
		# create an empty JSON file
		metadata_file.write_text("{}")
		logger.info(f"{metadata_file} created with empty json.")

	return metadata_file

# load metadata.json into a dict and return it
def load_metadata_json(metadata_file) -> dict:
	with open(metadata_file, "r", encoding="utf-8") as f:
		metadata = json.load(f)  # metadata is now a Python dict
		logger.info(f"Loaded metadata.json into a dict")

	return metadata

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

# for a markdown file receive the path, it's current hash and the metadata dict. compare current hash with the old one(if exists) and if hash has changed or it is a new file update the dict and return True
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

def preprocess_md_content(content: str) -> str:
	"""
	TODO
	Optional preprocessing step. Currently does nothing.
	You can add cleaning, stripping, Markdown parsing, etc. later.
	"""
	return content
