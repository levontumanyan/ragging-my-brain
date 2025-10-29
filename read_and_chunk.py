from pathlib import Path
import logging
from typing import List
import json
import hashlib

logger = logging.getLogger(__name__)

# in this one we take a markdown and read
def read_md_files(md_files: List[Path]) -> List[str]:
	"""
	Read a markdown file and return its content as a string.
	"""
	logger.info(f"Starting to read files, received {len(md_files)} files to read.")

	contents = []

	for md_file in md_files:
		try:
			with md_file.open("r", encoding="utf-8") as f:
				contents.append(f.read())
		except Exception as e:
			logger.error(f"Error reading {md_file}: {e}")

	return contents

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
	"""
	Take a string and chunk it into a list of chunk_sized strings with an overlap.
	"""
	chunks = []

	start = 0

	while start < len(text):
		end = start + chunk_size
		chunks.append(text[start:end])
		start = end - overlap

	return chunks

def chunk_all_texts(texts: list[str]) -> list[str]:
	"""
	Takes a list of strings and passes them to chunk_text and returns the result in a list of strings.
	"""
	all_chunks = []

	for text in texts:
		# we use extend to end up with a flat list.
		all_chunks.extend(chunk_text(text))
	
	logger.info(f"Created {len(all_chunks)} chunks.")

	return all_chunks

# take all the chunks, these are already the ones that need to be done because a file's hash has been changed. take an individual chunks. pass a jsonl file.
def hash_chunk(chunk: str) -> str:
	return hashlib.md5(chunk.encode("utf-8")).hexdigest()

def generate_chunks_metadata(all_chunks: list[str]) -> list[dict]:
	metadata = []
	for chunk in all_chunks:
		chunk_hash = hash_chunk(chunk)
		metadata.append({
			"chunk": chunk,
			"hash": chunk_hash
		})
	return metadata

def store_chunks_metadata(metadata: list[dict], metadata_jsonl_file):
	"""
	metadata: is a list of dictionaries(each a json like dict)
	metadata_jsonl_file: jsonl file to write metadata into
	"""
	with open(metadata_jsonl_file, "w", encoding="utf-8"):
		for entry in metadata:
			metadata_jsonl_file.write(json.dumps(entry) + "\n")

# this one will be for chunking content
