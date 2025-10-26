# project to create a rag pipeline for my docs

# improvements

- `metadata.json` can store other info, last updated timestamp, number of chunks of the file...
- json logging
- more robusts tests
- hashing chunks, not just files. if a large file changes only a line, no need to reembed the whole file, just that chunk.
- ⚠️ don't read all markdowns into an array but switch to a generator pattern or stream processing.
- Currently using simple fixed-size chunks (you can later use smarter ones like nltk, langchain.text_splitter, or tiktoken).
- chunking size and overlap should be more robust. maybe repeat it twice in chunk_text and chunk_all_texts then modify from main.

# lessons learned

- we take the `.md` files then chunk them. We do this for embedding later to be easier. Embedding is taking these chunks and creating vectors with floats.
- theoretically we could take one file and embed that or take all the file's contents and make one vector out of it. but that wouldn't be effective at capturing the info.

This is what RAG does:

- Embeds the question into a vector.
- Compares that vector to all stored chunk vectors (using cosine similarity).
- Finds the nearest ones (most semantically similar).
- Sends the text of those chunks to the LLM along with your question.

# high level tasks

- [x] create a virtual environment
- [ ] freeze requirements and post

# Ingest & chunk your documents

- [x] Recursively scans top directory for all .md files.

# Preprocessing the Markdown Content

- [ ] Read the content of each .md file you marked for processing.
- [ ] Clean and normalize the text:
  - Remove unnecessary whitespace, HTML tags, or code blocks if they are not relevant.
  - Optionally handle headers, lists, and other Markdown-specific formatting to maintain context.
  - Split the content into smaller chunks for embedding:
  - RAG works better with smaller pieces (e.g., 500–1000 tokens per chunk).
  - Keep some context overlap between chunks to preserve continuity.

- Read the contents and break them into chunks (for later embedding).
- Use a loader to read .md files into text (e.g., with LangChain or LlamaIndex).
- Split text into overlapping chunks (e.g., 500–1000 tokens).

# Embed & store

- Choose a local embedding model (fast + small, e.g. all-MiniLM-L6-v2 from sentence-transformers).
- Store embeddings + metadata in a local vector store (Chroma, FAISS, or SQLite-based).
  - [ ] `pip install chromadb`

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
