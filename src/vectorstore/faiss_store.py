import faiss, os, numpy as np

def load_or_create_faiss_index(faiss_index_path, dim: int):

	if os.path.exists(faiss_index_path):
		index = faiss.read_index(faiss_index_path)
	else:
		# Create a flat L2 index
		base_index = faiss.IndexFlatL2(dim)

		# Wrap it with ID map
		index = faiss.IndexIDMap2(base_index)

		faiss.write_index(index, faiss_index_path)
	return index

# we are gonna use IndexIDMap. this is so that we can remove stale chunks. https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing

def store_embeddings(ids: "np.ndarray", embeddings: "np.ndarray", index) -> None:
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
	index.add_with_ids(embeddings, ids)
	
# now let's write a function that will accept the faiss index and delete ids that are not needed anymore.

def delete_embeddings(ids_to_delete: "np.array", index, faiss_index_path) -> None:
	"""
	Accepts the faiss index(vector store) and list of dicts which are metadata on the chunks to be deleted.
	"""
	import faiss
	import numpy as np
	
	if index is None or ids_to_delete.size == 0:
		return

	index.remove_ids(ids_to_delete)

	faiss.write_index(index, faiss_index_path)
	# delete the ids
