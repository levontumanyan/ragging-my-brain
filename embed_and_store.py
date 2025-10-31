# high level will receive a list of strings(chunks) and embed them. This converts text chunks into numeric vectors so you can do similarity search, RAG, or other LLM retrieval tasks.

# since I want a fully local, free solution, the best option is Hugging Face / Sentence Transformers.

import logging
from typing import List
import os

logger = logging.getLogger(__name__)

def create_embedding_model(name: str):
	# lazy import to not slow down the script when there is no need to embed
	from sentence_transformers import SentenceTransformer

	# Load a pre-trained embedding model (small & fast)
	model = SentenceTransformer(name)

	return model

def generate_embeddings(chunks: list[str], model) -> "np.ndarray":
	"""
	take a list of strings(chunks), generate an embedding and return it.
	returns np.ndarray. (numpy array)
	"""

	# in the case where no chunks are not passed(files haven't changed) no need to start the model. it takes time
	if not chunks:
		logger.info(f"Nothing to embed, skipping...")
		return

	# Generate embeddings
	embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

	# embeddings is now a NumPy array: shape (num_chunks, embedding_dim)
	logger.info(f"Shape of embeddings: {embeddings.shape}")

	return embeddings

# then next we will store these embeddings in a vector db. vector db is not only responsible for storing embeddings, but it also does the nearest neighbor search. As an example FAISS uses optimized C++ routines + GPU acceleration for instant nearest neighbor search. We could write this ourselves but it would be less efficient. Nearest neighbour search is so that we don't pass all our embeddings to the model(it will make it less efficient, or we will just break the token limit). This is called top_k: top_k = number of most relevant embeddings to retrieve.

# we are gonna use IndexIDMap. this is so that we can remove stale chunks. https://github.com/facebookresearch/faiss/wiki/Pre--and-post-processing

def load_or_create_faiss_index(faiss_index_path, dim: int):
	import faiss, os, numpy as np

	if os.path.exists(faiss_index_path):
		index = faiss.read_index(faiss_index_path)
	else:
		# Create a flat L2 index
		base_index = faiss.IndexFlatL2(dim)

		# Wrap it with ID map
		index = faiss.IndexIDMap2(base_index)

		faiss.write_index(index, faiss_index_path)
	return index

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

def delete_old_ids(ids_to_delete: "np.array", index, faiss_index_path) -> None:
	"""
	Accepts the faiss index(vector store) and list of dicts which are metadata on the chunks to be deleted
	"""
	import faiss
	import numpy as np
	
	if index is None or ids_to_delete.size == 0:
		return

	index.remove_ids(ids_to_delete)

	faiss.write_index(index, faiss_index_path)
	# delete the ids

# new ids is a bit more involved we need to embed them first then add them to the index
