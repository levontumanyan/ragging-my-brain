import logging
import time
from pathlib import Path
from dotenv import load_dotenv
import os
import argparse

from src.utils.io_utils import (
	create_data_dir,
	create_metadata_file,
	read_file,
	json_to_dict,
	save_dict_to_json,
	load_jsonl_metadata,
	save_jsonl
)

from src.utils.scan_utils import (
	retrieve_md_filenames
)

from src.utils.hash_utils import (
	hash_file,
	needs_processing,
	compare_old_new_metadata
)

from src.chunking.chunker import (
	chunk_files_and_generate_metadata
)

from src.embedding.embedder import (
	create_embedding_model,
	generate_embeddings
)

from src.vectorstore.faiss_store import (
	load_or_create_faiss_index,
	add_to_index,
	remove_from_faiss_index
)

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

def setup_logger():
	logging.basicConfig(
		level=logging.DEBUG if args.debug else logging.INFO,
		format="%(asctime)s [%(levelname)s] %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

load_dotenv()
logger = logging.getLogger(__name__)
KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR"))
IGNORE_DIRS = set(os.getenv("IGNORE_DIRS", "").split(","))

def main():
	# start timer
	start_time = time.perf_counter()

	# start logger
	setup_logger()

	logger.info("Rag pipeline started")

	# create a path object to data dir
	data_dir = create_data_dir()

	# create or check metadata.json exists
	metadata_file = create_metadata_file(data_dir, "metadata.json")

	# read the metadata file
	metadata_file_text = read_file(metadata_file)

	# get the dict with metadata
	metadata = json_to_dict(metadata_file_text)

	# create an array that will store files to be processed (hash has changed)
	mds_to_process = []

	md_files = retrieve_md_filenames(KNOWLEDGE_BASE_DIR, IGNORE_DIRS)

	for md_file in md_files:
		# compute the md5 hash of the md file
		current_md_hash = hash_file(md_file)
		
		# this returns a path without the ../ as a string
		md_relative_path = str(md_file.relative_to(KNOWLEDGE_BASE_DIR))

		if needs_processing(md_relative_path, current_md_hash, metadata):
			mds_to_process.append(md_file)

	# write these hashes to the metadata.json file from metadata dict
	try:
		save_dict_to_json(metadata_file, metadata)
	except Exception as e:
		logger.error(f"❌ Fatal error: {e}")
		# stop main()
		return

	# create metadata store file path
	metadata_store_file = create_metadata_file(data_dir, "metadata_store.jsonl")

	# read contents to a string
	old_metada_text = read_file(metadata_store_file)

	# list of dicts holding the old chunks metadata
	old_metadata = load_jsonl_metadata(old_metada_text)

	# this will be the list of dicts of chunks and corresponding info.
	# for now gonna pass this md_files later if there is a way maybe only mds_to_process.
	current_metadata_store = chunk_files_and_generate_metadata(md_files)

	entries_to_delete, entries_to_add = compare_old_new_metadata(old_metadata, current_metadata_store)

	# initialize variables
	embeddings = None
	ids = None
	index = None

	# only create embeddings if there are new entries
	if entries_to_add:
		import numpy as np
		# create the embedding model
		model = create_embedding_model("all-MiniLM-L6-v2")
		chunks = [entry["chunk"] for entry in entries_to_add]
		# in order to add the new embeddings let's first get their ids. we need to add to an index (id, embedding) tuples.
		ids = np.array([e["id"] for e in entries_to_add], dtype=np.int64)
		embeddings = generate_embeddings(chunks, model)
		dim = embeddings.shape[1]
	else:
		logger.info("No new entries to add — skipping embedding and index update.")

	# only load index if we need to add or delete entries
	if entries_to_add or entries_to_delete:
		# default dim if embeddings missing
		index = load_or_create_faiss_index("index.faiss", dim or 384,)

	# add new embeddings to the vector store.
	if embeddings is not None:
		add_to_index(ids, embeddings, index)

	if entries_to_delete:
		# get the list of ids to delete
		ids_to_delete = np.array([entry['id'] for entry in entries_to_delete], dtype=np.int64)
		remove_from_faiss_index(ids_to_delete, index, "index.faiss")

	# save the new metadata store and overwrite the old one.
	save_jsonl(current_metadata_store, metadata_store_file)

	# end timer, count relapsed time
	end_time = time.perf_counter()
	elapsed = end_time - start_time
	logger.info(f'Rag pipeline completed successfully in {elapsed:.9f} seconds.')

# --- entry point ---
if __name__ == "__main__":
	main()
