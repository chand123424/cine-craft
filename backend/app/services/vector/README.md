# Vector service boundary

`qdrant.py` provides the production Qdrant adapter. Select it with `CINECRAFT_VECTOR_PROVIDER=qdrant` and provide `CINECRAFT_QDRANT_URL`; keep project filtering mandatory and preserve `MemoryRecord` metadata so characters, scenes, locations, story facts, dialogue, and creator preferences remain distinguishable to the RAG layer.
