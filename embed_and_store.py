# high level will receive a list of strings(chunks) and embed them. This converts text chunks into numeric vectors so you can do similarity search, RAG, or other LLM retrieval tasks.

# since I want a fully local, free solution, the best option is Hugging Face / Sentence Transformers.

import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

def generate_embeddings(chunks: list[str]) -> np.ndarray:
	"""
	take a list of strings(chunks), generate an embedding and return it.
	returns np.ndarray. (numpy array)
	"""

	# in the case where no chunks are not passed(files haven't changed) no need to start the model. it takes time
	if not chunks:
		logger.info(f"Nothing to embed, skipping...")
		return

	# lazy import to not slow down the script when there is no need to embed
	from sentence_transformers import SentenceTransformer

	# Load a pre-trained embedding model (small & fast)
	model = SentenceTransformer("all-MiniLM-L6-v2")

	# Generate embeddings
	embeddings = model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

	# embeddings is now a NumPy array: shape (num_chunks, embedding_dim)
	logger.info(f"Shape of embeddings: {embeddings.shape}")

	return embeddings

# then next we will store these embeddings in a vector db. vector db is not only responsible for storing embeddings, but it also does the nearest neighbor search. As an example FAISS uses optimized C++ routines + GPU acceleration for instant nearest neighbor search. We could write this ourselves but it would be less efficient. Nearest neighbour search is so that we don't pass all our embeddings to the model(it will make it less efficient, or we will just break the token limit). This is called top_k: top_k = number of most relevant embeddings to retrieve.

def store_embeddings(embeddings: np.ndarray) -> None:
	"""
	Take a numpy array of embeddings and store them in a local vector db.
	"""
