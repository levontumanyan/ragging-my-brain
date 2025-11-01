import logging
from pathlib import Path
from src.utils.io_utils import read_file
from src.utils.hash_utils import hash_text, md5_to_int

logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
	"""
	Take a string and chunk it into a list of chunk_sized strings with an overlap.
	"""
	chunks = []

	start = 0

	while start < len(text):
		end = start + chunk_size
		chunks.append(text[start:end])
		logger.debug(f"Chunk [{start}:{end}]")
		start = end - overlap

	# merge last chunk if it's too small
	if len(chunks) > 1 and len(chunks[-1]) < overlap:
		logger.debug(f"Last chunk is too small({len(chunks[-1])}), merging...")
		chunks[-2] += chunks[-1]
		chunks.pop()

	logger.debug(f"{len(chunks)} chunks generated.")
	return chunks

def generate_chunk_metadata(chunk: str, knowledge_file: Path) -> dict:
	chunk_hash = hash_text(chunk)
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

	num_of_chunks = 0

	for chunk in file_chunks:
		num_of_chunks += 1
		file_chunks_metadata.append(generate_chunk_metadata(chunk, knowledge_file))
		logger.debug(f"Chunk {num_of_chunks}:{knowledge_file.name} loaded to metadata dict.")

	return file_chunks_metadata

def chunk_files_and_generate_metadata(knowledge_files: list[Path]) -> list[dict]:
	all_metadata = []
	num_of_files = 0

	for file_path in knowledge_files:
		all_metadata.extend(chunk_file(file_path))
		num_of_files += 1

	logger.info(f"Generated {len(all_metadata)} chunks with metadata from {len(knowledge_files)} files.")

	return all_metadata
