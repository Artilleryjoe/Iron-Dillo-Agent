"""Vector visualization helpers for the Cybersandbox."""

from __future__ import annotations

from .security import sanitize_text
from .settings import Settings, get_settings


def _fetch_documents(settings: Settings | None = None) -> dict:
    import chromadb

    settings = settings or get_settings()
    client = chromadb.PersistentClient(path=str(settings.chroma_storage_path))
    collection = client.get_or_create_collection(settings.collection_name)
    results = collection.get(include=["embeddings", "metadatas", "ids"])
    return results


def project_vectors(
    *,
    settings: Settings | None = None,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> dict:
    """Project document embeddings into a 2D scatter plot using UMAP."""

    settings = settings or get_settings()
    data = _fetch_documents(settings)
    if not data.get("embeddings"):
        return {"points": [], "metadata": []}

    embeddings = data["embeddings"]
    if len(embeddings) < 2:
        points = [[0.0, 0.0] for _ in embeddings]
    else:
        import umap

        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric="cosine")
        points = reducer.fit_transform(embeddings)

    metadata = []
    for idx, meta in enumerate(data.get("metadatas", [])):
        metadata.append(
            {
                "id": data["ids"][idx],
                "doc_id": meta.get("doc_id"),
                "source": meta.get("source"),
                "hash": meta.get("hash"),
                "preview": sanitize_text(meta.get("sanitized_preview", "")),
            }
        )

    serialized_points = [
        {"x": float(point[0]), "y": float(point[1]), "index": index}
        for index, point in enumerate(points)
    ]
    return {"points": serialized_points, "metadata": metadata}


__all__ = ["project_vectors"]
