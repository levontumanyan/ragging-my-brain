import json
import numpy as np

from src.utils.io_utils import (
	ensure_data_dir,
	load_jsonl_metadata,
	read_file,
	create_metadata_file
)

from src.embedding.embedder import (
	create_embedding_model,
	embed_text
)

from src.vectorstore.faiss_store import (
	load_or_create_faiss_index
)

from src.vectorstore.retrieval import (
	retrieve_top_k
)

def main(logger):
	# take a question, embed it with the same model as the index store uses.
	# pass this to a top_k search function to get the top_k neighbours of the query from our knowledge base index store
	# take back all those and the query embedding and convert back to the original texts
	# pass the text to the llm
	# print the result on the screen.
	dim = 384
	k = 10

	# take a question, embed it with the same model as the index store uses.
	query = "What is my email addresses?"
	model = create_embedding_model("all-MiniLM-L6-v2")
	vector = embed_text(query, model)

	# load the local index

	data_dir = ensure_data_dir()

	faiss_index_path = data_dir / "index.faiss"

	index = load_or_create_faiss_index(faiss_index_path, dim)

	D, I = retrieve_top_k(vector, index, k)

	# create metadata store file path
	metadata_store_file = create_metadata_file(data_dir, "metadata_store.jsonl")

	# read contents to a string
	metada_text = read_file(metadata_store_file)

	metadata = load_jsonl_metadata(metada_text)

	logger.info(f"\n=== Top {k} Matches ===")
	for rank, (dist, idx) in enumerate(zip(D[0], I[0]), start=1):
		entry = next((e for e in metadata if e["id"] == idx), None)
		if entry:
			logger.info(f"#{rank} — ID: {idx}, distance: {dist:.4f}")
			# print first 200 chars
			logger.info(f"Text: {entry['chunk'][:200]}...")
		else:
			logger.info(f"#{rank} — ID: {idx} (no metadata found)")

if __name__ == "__main__":
	main()
