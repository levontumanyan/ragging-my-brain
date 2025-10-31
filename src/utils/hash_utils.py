from pathlib import Path
import hashlib

def hash_text(chunk: str) -> str:
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

# pass a path object and compute the hash. this does it in a memory efficient way but doesn't call md5 several times. only once per file.
def hash_file(md_file: Path) -> str:
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
