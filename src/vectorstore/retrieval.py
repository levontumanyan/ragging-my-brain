import faiss
from config import logging
# we want to pass a vector and find top-k vectors in the index matching this vector.

def retrieve_top_k(vector: "np.ndarray", index, k: int):
	"""
	Return top-k nearest neighbours to vector in index.
	"""
	logging.info(f"Vector shape is: {vector.shape}")
	D, I = index.search(vector, k)
	print(I)
	print(D)
	return D, I
