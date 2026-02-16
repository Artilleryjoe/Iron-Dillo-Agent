"""Document ingestion and retrieval helpers for the Cybersandbox."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Sequence

from fastapi import UploadFile

from .deps import EmbeddingClient, get_embedding_client
from .security import sanitize_text
from .settings import Settings, get_settings

THREAT_PATTERNS: dict[str, re.Pattern[str]] = {
    "ransomware": re.compile(r"\bransomware\b", re.IGNORECASE),
    "phishing": re.compile(r"\bphish(ing|ed)?\b", re.IGNORECASE),
    "supply_chain": re.compile(r"\bsupply[\s-]?chain\b", re.IGNORECASE),
    "zero_day": re.compile(r"\bzero[\s-]?day\b", re.IGNORECASE),
    "credential_theft": re.compile(r"\bcredential(s)?\b|\bpassword\b", re.IGNORECASE),
    "cloud": re.compile(r"\b(cloud|container|kubernetes|iam)\b", re.IGNORECASE),
    "malware": re.compile(r"\bmalware\b|\btrojan\b|\bloader\b", re.IGNORECASE),
    "c2": re.compile(r"\bcommand and control\b|\bc2\b", re.IGNORECASE),
    "vulnerability": re.compile(r"\bCVE-\d{4}-\d{4,7}\b|\bvulnerability\b", re.IGNORECASE),
}

TACTIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "initial_access": re.compile(r"\binitial access\b|\bphishing\b|\bexploit\b", re.IGNORECASE),
    "execution": re.compile(r"\bexecution\b|\bpowershell\b|\bscript\b", re.IGNORECASE),
    "persistence": re.compile(r"\bpersistence\b|\bautorun\b|\bregistry\b", re.IGNORECASE),
    "privilege_escalation": re.compile(r"\bprivilege escalation\b|\bsudo\b", re.IGNORECASE),
    "defense_evasion": re.compile(r"\bdefense evasion\b|\bobfuscat", re.IGNORECASE),
    "lateral_movement": re.compile(r"\blateral movement\b|\bremote service\b", re.IGNORECASE),
    "collection_exfiltration": re.compile(r"\bexfiltrat\b|\bdata theft\b|\bcollection\b", re.IGNORECASE),
}

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "to",
    "of",
    "in",
    "on",
    "with",
    "by",
    "is",
    "are",
    "be",
    "about",
    "from",
}


@dataclass(frozen=True)
class QueryOptions:
    """Runtime options controlling RAG retrieval behaviour."""

    top_k: int = 5
    retrieval_mode: str = "vector"
    semantic_weight: float = 0.7
    keyword_weight: float = 0.2
    threat_weight: float = 0.1
    doc_ids: tuple[str, ...] = ()
    required_threat_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ThreatIntelProfile:
    """Structured interpretation of threat intent from query text."""

    tags: tuple[str, ...]
    tactics: tuple[str, ...]
    indicators: tuple[str, ...]


def _chunk_text(
    text: str,
    *,
    chunk_size: int = 1000,
    overlap: int = 150,
    chunk_mode: str = "fixed",
) -> List[str]:
    if chunk_mode == "paragraph":
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        chunked: list[str] = []
        for paragraph in paragraphs:
            if len(paragraph) <= chunk_size:
                chunked.append(paragraph)
                continue
            chunked.extend(_chunk_text(paragraph, chunk_size=chunk_size, overlap=overlap, chunk_mode="fixed"))
        return chunked

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


def _tokenize(text: str) -> set[str]:
    words = {word for word in re.findall(r"[a-zA-Z0-9_-]+", text.lower()) if len(word) > 2}
    return {word for word in words if word not in STOPWORDS}


def _extract_threat_profile(text: str) -> ThreatIntelProfile:
    tags = tuple(tag for tag, pattern in THREAT_PATTERNS.items() if pattern.search(text))
    tactics = tuple(tactic for tactic, pattern in TACTIC_PATTERNS.items() if pattern.search(text))
    indicators = tuple(sorted(set(re.findall(r"\b(?:CVE-\d{4}-\d{4,7}|T\d{4}(?:\.\d{3})?)\b", text, re.IGNORECASE))))
    return ThreatIntelProfile(tags=tags, tactics=tactics, indicators=indicators)


def _build_metadata(chunk: str, *, doc_id: str, index: int) -> dict[str, Any]:
    profile = _extract_threat_profile(chunk)
    return {
        "doc_id": doc_id,
        "source": doc_id,
        "chunk_index": index,
        "hash": _hash_text(chunk),
        "threat_tags": list(profile.tags),
        "mitre_tactics": list(profile.tactics),
        "intel_indicators": list(profile.indicators),
        "sanitized_preview": sanitize_text(chunk[:280]),
    }


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
    chunk_mode: str = "fixed",
) -> dict:
    """Persist a single uploaded document into the Chroma store."""

    settings = settings or get_settings()
    embedder = embedder or get_embedding_client(settings)

    upload.file.seek(0)
    raw_text = upload.file.read().decode("utf-8", errors="ignore")
    chunks = _chunk_text(raw_text, chunk_mode=chunk_mode)
    identifiers = []
    metadatas = []
    embeddings_input = []
    for index, chunk in enumerate(chunks):
        chunk_id = f"{upload.filename}:{index}"
        identifiers.append(chunk_id)
        metadatas.append(_build_metadata(chunk, doc_id=upload.filename, index=index))
        embeddings_input.append(chunk)

    embeddings = embedder.embed(embeddings_input)
    collection = _get_collection(settings)
    collection.upsert(
        ids=identifiers,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    profile = _extract_threat_profile(raw_text)
    return {
        "chunks": len(chunks),
        "doc_id": upload.filename,
        "hash": _hash_text(raw_text),
        "threat_tags": list(profile.tags),
        "mitre_tactics": list(profile.tactics),
        "intel_indicators": list(profile.indicators),
        "chunk_mode": chunk_mode,
    }


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


def _keyword_overlap(query: str, text: str) -> float:
    query_tokens = _tokenize(query)
    text_tokens = _tokenize(text)
    if not query_tokens or not text_tokens:
        return 0.0
    return len(query_tokens & text_tokens) / len(query_tokens)


def _threat_alignment(query_profile: ThreatIntelProfile, metadata: dict[str, Any]) -> float:
    if not query_profile.tags:
        return 0.0
    doc_tags = set(metadata.get("threat_tags", []))
    if not doc_tags:
        return 0.0
    overlap = len(doc_tags & set(query_profile.tags))
    return overlap / len(query_profile.tags)


def _normalize_semantic_score(distance: float) -> float:
    return 1.0 / (1.0 + max(distance, 0.0))


def _passes_filters(metadata: dict[str, Any], options: QueryOptions) -> bool:
    if options.doc_ids and metadata.get("doc_id") not in options.doc_ids:
        return False
    if options.required_threat_tags:
        doc_tags = set(metadata.get("threat_tags", []))
        if not doc_tags.issuperset(options.required_threat_tags):
            return False
    return True


def _hybrid_rescore(
    query: str,
    query_profile: ThreatIntelProfile,
    *,
    options: QueryOptions,
    ids: Sequence[str],
    distances: Sequence[float],
    metadatas: Sequence[dict[str, Any]],
    documents: Sequence[str],
) -> list[dict[str, Any]]:
    rescored: list[dict[str, Any]] = []
    for item_id, distance, metadata, document in zip(ids, distances, metadatas, documents):
        metadata = metadata or {}
        if not _passes_filters(metadata, options):
            continue
        semantic_score = _normalize_semantic_score(distance)
        keyword_score = _keyword_overlap(query, document)
        threat_score = _threat_alignment(query_profile, metadata)
        final_score = (
            semantic_score * options.semantic_weight
            + keyword_score * options.keyword_weight
            + threat_score * options.threat_weight
        )
        rescored.append(
            {
                "id": item_id,
                "distance": distance,
                "score": round(final_score, 6),
                "semantic_score": round(semantic_score, 6),
                "keyword_score": round(keyword_score, 6),
                "threat_score": round(threat_score, 6),
                "metadata": metadata,
                "preview": sanitize_text(document[:400]),
            }
        )
    rescored.sort(key=lambda item: item["score"], reverse=True)
    return rescored[: options.top_k]


def query_rag(
    query: str,
    *,
    top_k: int = 5,
    settings: Settings | None = None,
    embedder: EmbeddingClient | None = None,
    retrieval_mode: str = "vector",
    doc_ids: Sequence[str] | None = None,
    required_threat_tags: Sequence[str] | None = None,
) -> dict:
    """Retrieve relevant documents for the supplied query."""

    settings = settings or get_settings()
    embedder = embedder or get_embedding_client(settings)
    collection = _get_collection(settings)

    options = QueryOptions(
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        doc_ids=tuple(doc_ids or ()),
        required_threat_tags=tuple(required_threat_tags or ()),
    )
    query_profile = _extract_threat_profile(query)

    query_embedding = embedder.embed([query])[0]
    fetch_k = max(top_k * 3, top_k)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
        include=["metadatas", "distances", "documents", "ids"],
    )

    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    documents = results.get("documents", [[]])[0]

    if retrieval_mode == "vector":
        hits = []
        for item_id, distance, metadata, document in zip(ids, distances, metadatas, documents):
            metadata = metadata or {}
            if not _passes_filters(metadata, options):
                continue
            hits.append(
                {
                    "id": item_id,
                    "distance": distance,
                    "score": round(_normalize_semantic_score(distance), 6),
                    "metadata": metadata,
                    "preview": sanitize_text(document[:400]),
                }
            )
            if len(hits) >= top_k:
                break
    elif retrieval_mode in {"hybrid", "intel"}:
        hits = _hybrid_rescore(
            query,
            query_profile,
            options=options,
            ids=ids,
            distances=distances,
            metadatas=metadatas,
            documents=documents,
        )
    else:
        raise ValueError(f"Unsupported retrieval mode: {retrieval_mode}")

    return {
        "query": query,
        "retrieval_mode": retrieval_mode,
        "threat_profile": {
            "tags": list(query_profile.tags),
            "mitre_tactics": list(query_profile.tactics),
            "intel_indicators": list(query_profile.indicators),
        },
        "results": hits,
    }


__all__ = [
    "ingest_files",
    "ingest_upload",
    "query_rag",
]
