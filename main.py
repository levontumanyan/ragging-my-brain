import logging
import time
from pathlib import Path
from dotenv import load_dotenv
import os

from scan_and_hash import (
	create_data_dir,
	create_metadata_file,
	load_metadata_json,
	retrieve_md_filenames,
	hash_md_file,
	needs_processing,
	save_metadata_json
)

from read_and_chunk import (
	load_old_metadata,
	compare_old_new_metadata,
	chunk_files_and_generate_metadata,
	store_chunks_metadata
)

from embed_and_store import (
	delete_old_ids,
	create_embedding_model,
	generate_embeddings,
	load_or_create_faiss_index,
	store_embeddings
)

def setup_logger():
	logging.basicConfig(
		level=logging.INFO,
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

	logger.info('Rag pipeline started')

	# create a path object to data dir
	data_dir = create_data_dir()

	# create or check metadata.json exists
	metadata_file = create_metadata_file(data_dir, "metadata.json")

	# get the dict with metadata
	metadata = load_metadata_json(metadata_file)

	# create an array that will store files to be processed (hash has changed)
	mds_to_process = []

	md_files = retrieve_md_filenames(KNOWLEDGE_BASE_DIR, IGNORE_DIRS)

	for md_file in md_files:
		# compute the md5 hash of the md file
		current_md_hash = hash_md_file(md_file)
		
		# this returns a path without the ../ as a string
		md_relative_path = str(md_file.relative_to(KNOWLEDGE_BASE_DIR))

		if needs_processing(md_relative_path, current_md_hash, metadata):
			mds_to_process.append(md_file)

	# write these hashes to the metadata.json file from metadata dict
	try:
		save_metadata_json(metadata_file, metadata)

	except Exception as e:
		logger.error(f"❌ Fatal error: {e}")
		# stop main()
		return

	# create metadata store file path
	metadata_store_file = create_metadata_file(data_dir, "metadata_store.json")

	# list of dicts holding the old chunks metadata
	old_metadata = load_old_metadata(metadata_store_file)

	# this will be the list of dicts of chunks and corresponding info.
	# for now gonna pass this md_files later if there is a way maybe only mds_to_process.
	current_metadata_store = chunk_files_and_generate_metadata(md_files)

	entries_to_delete, entries_to_add = compare_old_new_metadata(old_metadata, current_metadata_store)

	# create a list of texts to embed then add to the faiss index, if there is something to add.
	if not entries_to_add:
		logger.info("No new entries to add — skipping embedding and index update.")
	else:
		import numpy as np
		# create the embedding model
		model = create_embedding_model("all-MiniLM-L6-v2")
		chunks = [entry["chunk"] for entry in entries_to_add]
		# in order to add the new embeddings let's first get their ids. we need to add to an index (id, embedding) tuples.
		ids = np.array([e["id"] for e in entries_to_add], dtype=np.int64)
		embeddings = generate_embeddings(chunks, model)
		dim = embeddings.shape[1]

	# probably better ways to do... too much repetition i feel like.
	# for now check if we need to add anything or delete anything. if that is the case load or create an index.
	if entries_to_add or entries_to_delete:
		index = load_or_create_faiss_index(dim or 384, "index.faiss")  # default dim if embeddings missing

	# if there are new embeddings then we add it to the vector store.
	if embeddings is not None:
		store_embeddings(ids, embeddings, index)

	# get the list of ids to delete
	ids_to_delete = np.array([entry['id'] for entry in entries_to_delete], dtype=np.int64)

	if ids_to_delete is not None:
		# delete the old ids/chunks from the vector store (faiss)
		delete_old_ids(ids_to_delete, index, "index.faiss")

	# save the new metadata store and overwrite the old one.
	store_chunks_metadata(current_metadata_store, metadata_store_file)

	# add saving the metadata store to the file.

	# end timer, count relapsed time
	end_time = time.perf_counter()
	elapsed = end_time - start_time
	logger.info(f'Rag pipeline completed successfully in {elapsed:.9f} seconds.')

# --- entry point ---
if __name__ == "__main__":
	main()
