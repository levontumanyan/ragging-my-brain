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
	read_md_files,
	chunk_all_texts
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
	metadata_file = create_metadata_file(data_dir)

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
	
	# read md files here
	contents = read_md_files(mds_to_process)
	
	# chunk all the mds
	all_chunks = chunk_all_texts(contents)

	# end timer, count relapsed time
	end_time = time.perf_counter()
	elapsed = end_time - start_time
	logger.info(f'Rag pipeline completed successfully in {elapsed:.9f} seconds.')

# --- entry point ---
if __name__ == "__main__":
	main()
