"""Document ingestion and retrieval helpers for the Cybersandbox."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List, Sequence

from fastapi import UploadFile

from .deps import EmbeddingClient, get_embedding_client
from .security import sanitize_text
from .settings import Settings, get_settings


def _chunk_text(text: str, *, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        if end == text_length:
            break
        start = max(0, end - overlap)
    return chunks

def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _get_client(settings: Settings | None = None):
    import chromadb

    settings = settings or get_settings()
    client = chromadb.PersistentClient(path=str(settings.chroma_storage_path))
    return client


def _get_collection(settings: Settings | None = None):
    client = _get_client(settings)
    settings = settings or get_settings()
    return client.get_or_create_collection(settings.collection_name)


def ingest_upload(
    upload: UploadFile,
    *,
    settings: Settings | None = None,
    embedder: EmbeddingClient | None = None,
) -> dict:
    """Persist a single uploaded document into the Chroma store."""

    settings = settings or get_settings()
    embedder = embedder or get_embedding_client(settings)

    upload.file.seek(0)
    raw_text = upload.file.read().decode("utf-8", errors="ignore")
    chunks = _chunk_text(raw_text)
    identifiers = []
    metadatas = []
    embeddings_input = []
    for index, chunk in enumerate(chunks):
        chunk_id = f"{upload.filename}:{index}"
        identifiers.append(chunk_id)
        metadatas.append(
            {
                "doc_id": upload.filename,
                "source": upload.filename,
                "hash": _hash_text(chunk),
                "sanitized_preview": sanitize_text(chunk[:280]),
            }
        )
        embeddings_input.append(chunk)

    embeddings = embedder.embed(embeddings_input)
    collection = _get_collection(settings)
    collection.upsert(
        ids=identifiers,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    summary = {
        "chunks": len(chunks),
        "doc_id": upload.filename,
        "hash": _hash_text(raw_text),
    }
    return summary


def ingest_files(paths: Sequence[Path], *, settings: Settings | None = None) -> List[dict]:
    """Ingest the provided documents from disk."""

    settings = settings or get_settings()
    embedder = get_embedding_client(settings)
    results = []
    for path in paths:
        fake_upload = UploadFile(filename=path.name)
        fake_upload.file = path.open("rb")
        try:
            results.append(ingest_upload(fake_upload, settings=settings, embedder=embedder))
        finally:
            fake_upload.file.close()
    return results


def query_rag(
    query: str,
    *,
    top_k: int = 5,
    settings: Settings | None = None,
    embedder: EmbeddingClient | None = None,
) -> dict:
    """Retrieve relevant documents for the supplied query."""

    settings = settings or get_settings()
    embedder = embedder or get_embedding_client(settings)
    collection = _get_collection(settings)

    query_embedding = embedder.embed([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances", "documents", "ids"],
    )

    hits = []
    for index in range(len(results["ids"][0])):
        hits.append(
            {
                "id": results["ids"][0][index],
                "distance": results["distances"][0][index],
                "metadata": results["metadatas"][0][index],
                "preview": sanitize_text(results["documents"][0][index][:400]),
            }
        )
    return {"query": query, "results": hits}


__all__ = [
    "ingest_files",
    "ingest_upload",
    "query_rag",
]
