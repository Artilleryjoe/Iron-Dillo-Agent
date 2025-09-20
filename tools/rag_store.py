"""In-memory retrieval helper for the Iron Dillo handbook."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Document:
    """Represent a lightweight knowledge base entry."""

    title: str
    content: str
    tags: List[str]

    def preview(self, length: int = 120) -> str:
        """Return a short excerpt for debugging and UI displays."""

        excerpt = self.content.strip().replace("\n", " ")
        if len(excerpt) <= length:
            return excerpt
        return f"{excerpt[:length].rstrip()}…"


class RAGStore:
    """Very small in-memory store useful for unit tests and demos."""

    def __init__(self) -> None:
        self._documents: List[Document] = []

    def add_document(self, *, title: str, content: str, tags: Iterable[str]) -> Document:
        if not title.strip():
            raise ValueError("Document title cannot be empty")
        if not content.strip():
            raise ValueError("Document content cannot be empty")

        doc = Document(title=title.strip(), content=content.strip(), tags=[t.lower() for t in tags])
        self._documents.append(doc)
        return doc

    def search(self, query: str, *, limit: int = 3) -> List[Document]:
        if limit <= 0:
            raise ValueError("limit must be positive")

        normalized_query = [token.lower() for token in query.split() if token.strip()]
        if not normalized_query:
            return []

        def score(document: Document) -> int:
            haystack = f"{document.title.lower()} {document.content.lower()} {' '.join(document.tags)}"
            return sum(token in haystack for token in normalized_query)

        ranked = sorted(
            (doc for doc in self._documents if score(doc) > 0),
            key=lambda doc: score(doc),
            reverse=True,
        )
        return ranked[:limit]


__all__ = ["Document", "RAGStore"]
