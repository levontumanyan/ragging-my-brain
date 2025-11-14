# RAG pipeline

`python main.py [--debug]` - to run the rag pipeline.

`.env` - includes configs to modify the location of knowledge base and ignore dirs.

# improvements

- store dim in a metadata store instead of just hardcoding it, since changing the model will break it.
- currently mds_to_process is not used. change code so only those files that have changed are being considered.
- better ids for chunks. for now it is some workaround of hashing and masking to keep it under int64 limits.
- test the correct one to one mapping of the ids to embeddings.
- capture kill signal
- change from vector store to graph store. [text](#light-rag)
- `metadata.json` can store other info, last updated timestamp, number of chunks of the file...
- json logging
- more robust tests
- ⚠️ don't read all markdowns into an array but switch to a generator pattern or stream processing.
- look into lazy imports (faiss, numpy, from sentence_transformers import SentenceTransformer)

# terms

- vector store = Embeddings databases
  - stores vectors(embeddings).
  - provides retrieval algorithms as well. 
  - examples
    - FAISS
    - [chroma](https://github.com/chroma-core/chroma)

# lessons learned

- we take the `.md` files then chunk them. We do this for embedding later to be easier. Embedding is taking these chunks and creating vectors with floats.
- theoretically we could take one file and embed that or take all the file's contents and make one vector out of it. but that wouldn't be effective at capturing the info.
- we cannot pass embeddings to the llm. we have to retrieve the text back and pass that.
- the embedding model used to embed a question should be the same as the one that is used to embed your document store text chunks. Embedding models define the "semantic coordinate system". Keep it consistent.

Rag creation pipeline workflow:

1. find all the text files you need for your model to check.
2. chunk them accordingly.
3. hash the chunk (md5). store the chunk in a metadata store(jsonl).
4. Take the text chunks and embed them using a model.
5. store the embeddings in a vector store (FAISS, chromadb, etc.)

This is what RAG+LLM question flow looks like:

1. User's question -> embed
  - The user asks: "what is the capital of armenia". we take this and embed it using an embedding model (text-embedding-3-small, all-MiniLM, etc.).
2. Search in vector store.
  - (FAISS, chromadb, etc.) vector store finds the most similar vectors (top-k). this is implemented by the vector store itself.
3. at this point we cannot just pass these embeddings to the llm. the llm works with plain text. so we need to recover the original text. the top-k search returned embeddings will need to be converted back to text using a metadata store.

- Embeds the question into a vector.
- Compares that vector to all stored chunk vectors (using cosine similarity).
- Finds the nearest ones (most semantically similar).
- Sends the text of those chunks to the LLM along with your question.

# high level tasks

- [ ] freeze requirements and post

# light rag

[light rag paper](https://arxiv.org/abs/2410.05779)

[github repo lightrag](https://github.com/HKUDS/LightRAG)

[microsoft graph rag](https://microsoft.github.io/graphrag/)

[microsoft blog on graph rag](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/)

# Ingest & chunk your documents

- [x] Recursively scans top directory for all .md files.
- [ ] Currently using simple fixed-size chunks (you can later use smarter ones like nltk, langchain.text_splitter, or tiktoken).

# Preprocessing the Markdown Content

- [x] Read the content of each .md file you marked for processing.
- [ ] Clean and normalize the text:
  - Remove unnecessary whitespace, HTML tags, or code blocks if they are not relevant.
  - Optionally handle headers, lists, and other Markdown-specific formatting to maintain context.
  - Split the content into smaller chunks for embedding:
  - RAG works better with smaller pieces (e.g., 500–1000 tokens per chunk).
  - Keep some context overlap between chunks to preserve continuity.

- [x] Read the contents and break them into chunks (for later embedding).
- [x] Split text into overlapping chunks (e.g., 500–1000 tokens).

# metadata store

Metadata store is a crucial part of the workflow. Its main job is to convert an embedding back to its original plain text form. We will also use it for storing hashes for the chunks to not reembed chunks that haven't been modified.

## structure(jsonl)

{"id": chunk_hash_to_int, "hash": "abcd1234...", "text": "Armenia is a...", "source": "docs/armenia.txt"}

# Embed & store

- [x] Choose a local embedding model (fast + small, e.g. all-MiniLM-L6-v2 from sentence-transformers).
- Store embeddings + metadata in a local vector store (Chroma, FAISS, or SQLite-based).

- Persist this to disk so you don’t have to rebuild each time.

# Choose your local LLM

# Make it dynamic

- Add a file watcher (e.g., watchdog) to re-embed or update files automatically when Markdown files change.

# links

[faiss getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)

# done

- [x] hashing chunks, not just files. if a large file changes only a line, no need to reembed the whole file, just that chunk.
- [x] move `index.faiss` to data directory
- [x] create a virtual environment
- [x] `pip install faiss-cpu` - the gpu version is not supported on mac m series gpus it only supports cuda.
- [x] understand the logging output when for some reason there are supposed to be 100s of embeddings but it shows 1 on subsequent runs, but on the first run it is correct. (Was a bug because i was creating a new index.)
- [ ] embedding model should be an env variable to share between build and query
- [ ] chunking better using libraries.
