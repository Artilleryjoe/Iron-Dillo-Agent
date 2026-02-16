from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile

from iron_dillo_cybersandbox_ai.backend import rag


class DummyEmbedder:
    def embed(self, texts):
        return [[float(len(text)), 1.0] for text in texts]


class DummyCollection:
    def __init__(self):
        self.payload = None

    def upsert(self, **kwargs):
        self.payload = kwargs


class QueryCollection:
    def query(self, **kwargs):
        return {
            "ids": [["docA:0", "docB:0"]],
            "distances": [[0.2, 0.5]],
            "metadatas": [[
                {"doc_id": "docA", "threat_tags": ["ransomware", "vulnerability"]},
                {"doc_id": "docB", "threat_tags": ["phishing"]},
            ]],
            "documents": [[
                "Ransomware operators exploited CVE-2024-3400 for initial access.",
                "Generic phishing awareness guidance for employees.",
            ]],
        }


def test_ingest_upload_adds_threat_metadata(monkeypatch):
    collection = DummyCollection()
    monkeypatch.setattr(rag, "_get_collection", lambda settings=None: collection)

    upload = UploadFile(filename="intel.txt", file=BytesIO(
        b"Ransomware campaign references CVE-2024-3400 and initial access via phishing"
    ))

    summary = rag.ingest_upload(upload, embedder=DummyEmbedder(), chunk_mode="paragraph")

    assert summary["doc_id"] == "intel.txt"
    assert "ransomware" in summary["threat_tags"]
    assert "initial_access" in summary["mitre_tactics"]
    assert "CVE-2024-3400" in summary["intel_indicators"]

    assert collection.payload is not None
    assert collection.payload["metadatas"][0]["threat_tags"]
    assert collection.payload["metadatas"][0]["mitre_tactics"]


def test_query_rag_hybrid_applies_filters_and_scores(monkeypatch):
    monkeypatch.setattr(rag, "_get_collection", lambda settings=None: QueryCollection())

    result = rag.query_rag(
        "Need ransomware intelligence mapped to CVE-2024-3400",
        top_k=2,
        embedder=DummyEmbedder(),
        retrieval_mode="hybrid",
        doc_ids=["docA"],
        required_threat_tags=["ransomware"],
    )

    assert result["retrieval_mode"] == "hybrid"
    assert result["threat_profile"]["tags"]
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "docA:0"
    assert result["results"][0]["score"] >= result["results"][0]["semantic_score"] * 0.7


def test_query_rag_rejects_unknown_mode(monkeypatch):
    monkeypatch.setattr(rag, "_get_collection", lambda settings=None: QueryCollection())

    try:
        rag.query_rag("hello", embedder=DummyEmbedder(), retrieval_mode="bogus")
    except ValueError as exc:
        assert "Unsupported retrieval mode" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported retrieval mode")
