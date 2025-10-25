# project to create a rag pipeline for my docs

# improvements

- `metadata.json` can store other info, last updated timestamp, number of chunks of the file...
- json logging
- more robusts tests

# lessons learned

- we take the `.md` files then chunk them. We do this for embedding later to be easier. Embedding is taking these chunks and creating vectors with floats.

This is what RAG does:

- Embeds the question into a vector.
- Compares that vector to all stored chunk vectors (using cosine similarity).
- Finds the nearest ones (most semantically similar).
- Sends the text of those chunks to the LLM along with your question.

# high level tasks

- [ ] create a virtual environment


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

