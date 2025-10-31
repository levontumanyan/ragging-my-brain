# project to create a rag pipeline for my docs

# improvements

- test the correct one to one mapping of the ids to embeddings.
- change from vector store to graph store. [text](#light-rag)
- `metadata.json` can store other info, last updated timestamp, number of chunks of the file...
- json logging
- more robust tests
- hashing chunks, not just files. if a large file changes only a line, no need to reembed the whole file, just that chunk.
- ⚠️ don't read all markdowns into an array but switch to a generator pattern or stream processing.
- Currently using simple fixed-size chunks (you can later use smarter ones like nltk, langchain.text_splitter, or tiktoken).
- chunking size and overlap should be more robust. maybe repeat it twice in chunk_text and chunk_all_texts then modify from main.
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

- [x] create a virtual environment
- [ ] freeze requirements and post

# light rag

[light rag paper](https://arxiv.org/abs/2410.05779)

[github repo lightrag](https://github.com/HKUDS/LightRAG)

[microsoft graph rag](https://microsoft.github.io/graphrag/)

[microsoft blog on graph rag](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/)

# Ingest & chunk your documents

- [x] Recursively scans top directory for all .md files.

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
  - [ ] `pip install faiss-cpu` - the gpu version is not supported on mac m series gpus it only supports cuda.

- Persist this to disk so you don’t have to rebuild each time.

# Choose your local LLM

# Make it dynamic

- Add a file watcher (e.g., watchdog) to re-embed or update files automatically when Markdown files change.

# dir structure long term

rag_project/
├── README.md
├── requirements.txt
├── metadata.json
├── .env
├── data/
│   ├── docs/                  # Original markdown files
│   ├── processed/             # Cleaned and chunked text (optional)
│   └── embeddings/            # Saved embeddings/vectorstore
├── src/
│   ├── __init__.py
│   ├── config.py              # Paths, constants, environment vars
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py      # File scanning, hashing, metadata handling
│   │   ├── text_utils.py      # Cleaning, normalization, markdown handling
│   │   └── logging_utils.py   # JSON logging setup
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── scanner.py         # Recursively find .md files
│   │   └── chunker.py         # Split into overlapping chunks
│   ├── embed/
│   │   ├── __init__.py
│   │   ├── model_loader.py    # Load embedding model (e.g. MiniLM)
│   │   ├── embedder.py        # Create embeddings for chunks
│   │   └── vector_store.py    # Save/retrieve from Chroma or FAISS
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── retriever.py       # Retrieve top chunks (cosine similarity)
│   │   └── pipeline.py        # End-to-end RAG orchestration
│   ├── watcher/
│   │   ├── __init__.py
│   │   └── watcher.py         # Watchdog logic to re-embed on file change
│   └── main.py                # Entry point: orchestrate everything
├── tests/
│   ├── __init__.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_vector_store.py
│   └── test_retriever.py
└── scripts/
    ├── build_embeddings.py    # CLI tool to rebuild all embeddings
    ├── run_rag_query.py       # CLI tool for testing queries
    └── update_metadata.py     # Utility to rebuild metadata.json
