from pathlib import Path
import logging
from typing import List
import json
import hashlib

logger = logging.getLogger(__name__)

def read_file(file: Path) -> str:
	"""
	Read a markdown file and return its content as a string.
	"""
	content = ""
	logger.info(f"Starting to read file, received {file.name} file to read.")

	try:
		with file.open("r", encoding="utf-8") as f:
			content = f.read()
	except Exception as e:
		logger.error(f"Error reading {file}: {e}")

	return content

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

# take all the chunks, these are already the ones that need to be done because a file's hash has been changed. take an individual chunks. pass a jsonl file.

def hash_chunk(chunk: str) -> str:
	return hashlib.md5(chunk.encode("utf-8")).hexdigest()

# we use this to get ids to later store in faiss with this id for an embedded chunk.
def md5_to_int(md5_str: str) -> int:
	"""
	pass an md5 hash and receive back an int64 represenation of it.
	"""
	# Convert MD5 hex digest to integer
	# FAISS accepts int64 IDs
	x = int(md5_str[-16:], 16)
	return x & 0x7FFFFFFFFFFFFFFF

def generate_chunk_metadata(chunk: str, knowledge_file: Path) -> dict:
	chunk_hash = hash_chunk(chunk)
	return {
		"id": md5_to_int(chunk_hash),
		"chunk": chunk,
		"hash": chunk_hash,
		"source": knowledge_file.name
	}

def chunk_file(knowledge_file: Path) -> list[Path]:
	"""
	This one takes in a file, reads it. chunks the contents, and creates metadata for all the chunks of that particular file.
	"""
	content = read_file(knowledge_file)

	file_chunks = chunk_text(content)

	file_chunks_metadata = []

	for chunk in file_chunks:
		file_chunks_metadata.append(generate_chunk_metadata(chunk, knowledge_file))

	return file_chunks_metadata

def chunk_files_and_generate_metadata(knowledge_files: list[Path]) -> list[dict]:
	all_metadata = []

	for file_path in knowledge_files:
		all_metadata.extend(chunk_file(file_path))

	logger.info(f"Generated {len(all_metadata)} chunks with metadata.")

	return all_metadata

def store_chunks_metadata(metadata: list[dict], metadata_jsonl_file: Path):
	"""
	metadata: is a list of dictionaries(each a json like dict)
	metadata_jsonl_file: jsonl file to write metadata into
	"""
	with open(metadata_jsonl_file, "w", encoding="utf-8") as f:
		for entry in metadata:
			f.write(json.dumps(entry) + "\n")

# this one will be for chunking content
# let's do this. we load the metadata_store which will be all the chunks (jsonl) in this form: {"id": 13473353377554212426091315809737985026, "chunk": "content...", "hash": "0a22df9bde54b2a24b21074bfcb74c02", "source": "unix_horror_stories_cd.md"}. we call this old_metadata_store let's say. then we compute current metadata_store. we compare all the hashes. the chunks(hashes) that are new we need to reembed and add to the vector store. the hashes that are missing we need to delete from the metadata store.
#
# - [ ] remember that we need to delete the chunks metadata from both faiss vector store but also from the jsonl metadata store file.

# get all current chunk hashes. pass the metadata store file prior to updating it and return all the hashes in a list.

def load_old_metadata(old_metadata_jsonl_file: Path) -> list[dict]:
	if not old_metadata_jsonl_file.exists():
		return []

	content = read_file(old_metadata_jsonl_file)

	metadata = []
	for line in content.splitlines():
		# splits on \n efficiently
		line = line.strip()
		if not line:
			continue  # skip empty lines
		try:
			metadata.append(json.loads(line))
		except json.JSONDecodeError as e:
			logger.warning(f"Skipping invalid JSON line: {line[:50]}... ({e})")

	return metadata

# here we accept two dicts, one will be the old metadata store and the current. we compare them see what hash is missing and what is new. then we return maybe a list of hashes/ids to be deleted and ones to add.

def compare_old_new_metadata(old_metadata: list[dict], current_metadata: list[dict]):
	"""
	Pass old_metadata and new. Compare and find the chunk hashes that are not there anymore(to be deleted) and new hashes(to embed).
	"""
	new_hashes = {entry["hash"] for entry in current_metadata}

	# if old metadata doesn't exist create an empty set of old_hashes
	if old_metadata:
		old_hashes = {entry["hash"] for entry in old_metadata}

		# these will need to be removed from the jsonl file. and from the vector store(we need the id.)
		hashes_to_delete = old_hashes - new_hashes

		entries_to_delete = [entry for entry in old_metadata if entry["hash"] in hashes_to_delete]

		entries_to_add = [entry for entry in current_metadata if entry["hash"] not in old_hashes]
	else:
		entries_to_delete = []
		entries_to_add = current_metadata

	return entries_to_delete, entries_to_add
