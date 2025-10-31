import faiss, os, numpy as np
import logging

logger = logging.getLogger(__name__)

def load_or_create_faiss_index(faiss_index_path: str, dim: int):
	"""
		Load a FAISS index from disk if it exists; otherwise, create a new flat L2 index
		wrapped in an ID map and save it.

		Args:
			faiss_index_path (str | Path): Path to the FAISS index file.
			dim (int): Dimensionality of the vectors.

		Returns:
			faiss.Index: The loaded or newly created FAISS index.
	"""
	if os.path.exists(faiss_index_path):
		index = faiss.read_index(faiss_index_path)
		logger.info(f"Index already exists, loading {faiss_index_path}")
	else:
		# Create a flat L2 index
		base_index = faiss.IndexFlatL2(dim)

		# Wrap it with ID map
		index = faiss.IndexIDMap2(base_index)

		faiss.write_index(index, faiss_index_path)
		logger.info(f"Creating a new index. {faiss_index_path} with dimension: {dim}")
	return index

# we are gonna use IndexIDMap. this is so that we can remove stale chunks. https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing

def add_to_index(ids: "np.ndarray", embeddings: "np.ndarray", index) -> None:
	"""
	Stores embeddings in a FAISS index and writes corresponding metadata entries to a JSONL file.

	Args:
		chunks: list of text chunks
		embeddings: numpy array of shape (N, dim)
		metadata_path: path to metadata JSONL file
		faiss_path: path to FAISS index file
		source: optional string for source info (e.g., filename)
	"""

	import faiss
	import numpy as np

	# we read the existing index if it exists to add to it. Currently the implementation is not so clear to me, but assuming we will be adding embeddings say because we have a new file or a file has changed, we want to read the current index into memory and add embeddings to it. i am not sure how deleting old parts would work. We create an indexidmap index to be able to assign ids to each index instead of arbitrary ids.
	
	# --- add to index ---
	logger.info(f"Current index size before adding: {index.ntotal}")
	num_to_add = ids.size
	index.add_with_ids(embeddings, ids)
	logger.info(f"Stored {num_to_add} embeddings to the index.")
	logger.info(f"Index size after adding: {index.ntotal}")

def remove_from_faiss_index(ids: "np.array", index, faiss_index_path) -> None:
	"""
	Accepts the faiss index(vector store) and list of dicts which are metadata on the chunks to be deleted.
	"""
	"""
		Delete embeddings from a FAISS index by their IDs and persist the updated index.

		Args:
			ids (np.ndarray): Array of integer IDs to remove from the index.
			index (faiss.Index): The FAISS index to update.
			faiss_index_path (str | Path): Path where the FAISS index is stored.

		Returns:
			None
	"""
	import faiss
	import numpy as np

	if index is None or ids.size == 0:
		logger.info("No embeddings to delete.")
		return

	num_to_delete = ids.size
	index.remove_ids(ids)
	
	logger.info(f"Deleted {num_to_delete} embeddings from the FAISS index.")
	logger.info(f"Index size after deletion: {index.ntotal}")

	faiss.write_index(index, faiss_index_path)
	logger.info(f"Wrote updated FAISS index to {faiss_index_path}.")
