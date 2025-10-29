import faiss
import numpy as np
import os

def md5_to_int(md5_str: str) -> int:
	# Convert MD5 hex digest to integer
	return int(md5_str, 16)  # FAISS accepts int64 IDs

# === 1️⃣ Create random embeddings ===
N, DIM = 5, 384
embeddings = np.random.rand(N, DIM).astype("float32")

# === 2️⃣ Create or load FAISS index ===
faiss_index_path = "test_index.faiss"

if os.path.exists(faiss_index_path):
	index = faiss.read_index(faiss_index_path)
	print(f"Loaded existing index with {index.ntotal} vectors")
else:
	index = faiss.IndexFlatL2(DIM)
	print("Created new FAISS index")

# === 3️⃣ Add embeddings ===
index.add(embeddings)
print(f"Index now contains {index.ntotal} vectors")

# === 4️⃣ Save to disk ===
faiss.write_index(index, faiss_index_path)
print(f"Index saved to {faiss_index_path}")

# === 5️⃣ Read it back ===
loaded_index = faiss.read_index(faiss_index_path)
print(f"Loaded index has {loaded_index.ntotal} vectors of dimension {loaded_index.d}")



index2 = faiss.IndexIDMap(index)
index2.add_with_ids(embeddings, ids)

# === 6️⃣ Try searching ===
query = np.random.rand(1, DIM).astype("float32")
D, I = loaded_index.search(query, k=3)
print("Query distances:", D)
print("Nearest indices:", I)
