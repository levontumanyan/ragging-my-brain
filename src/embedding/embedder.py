import logging

logger = logging.getLogger(__name__)

def create_embedding_model(name: str):
	# lazy import to not slow down the script when there is no need to embed
	from sentence_transformers import SentenceTransformer

	# Load a pre-trained embedding model (small & fast)
	model = SentenceTransformer(name)

	logger.info(f"Created embedding model: {name}")
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
	logger.info(f"Created embeddings for {len(chunks)} chunk.")
	logger.info(f"Shape of embeddings: {embeddings.shape}")

	return embeddings
