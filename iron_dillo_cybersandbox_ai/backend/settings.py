"""Configuration helpers for the Iron Dillo Cybersandbox API."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration loaded from environment variables when present."""

    allow_egress: bool = Field(False)
    docs_path: Path = Field(Path("iron_dillo_cybersandbox_ai/vault"))
    chroma_path: Path = Field(Path("iron_dillo_cybersandbox_ai/data/chroma"))
    model: str = Field("llama3")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2")
    audit_log_path: Path = Field(Path("iron_dillo_cybersandbox_ai/data/audit.log"))
    log_format: Literal["json", "text"] = Field("json")
    collection_name: str = Field("idcsa_docs")

    @property
    def sanitized_docs_path(self) -> Path:
        """Ensure the vault path exists and return it."""

        self.docs_path.mkdir(parents=True, exist_ok=True)
        return self.docs_path

    @property
    def chroma_storage_path(self) -> Path:
        """Ensure the Chroma persistence directory exists and return it."""

        self.chroma_path.mkdir(parents=True, exist_ok=True)
        return self.chroma_path

    @property
    def audit_log_file(self) -> Path:
        """Return the path to the append-only audit log file."""

        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        return self.audit_log_path


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings for dependency injection."""

    def read_bool(name: str, default: bool) -> bool:
        raw = os.getenv(name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    return Settings(
        allow_egress=read_bool("ALLOW_EGRESS", False),
        docs_path=Path(os.getenv("DOCS_PATH", "iron_dillo_cybersandbox_ai/vault")),
        chroma_path=Path(os.getenv("CHROMA_PATH", "iron_dillo_cybersandbox_ai/data/chroma")),
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        audit_log_path=Path(os.getenv("AUDIT_LOG_PATH", "iron_dillo_cybersandbox_ai/data/audit.log")),
        log_format=os.getenv("AUDIT_LOG_FORMAT", "json"),
        collection_name=os.getenv("CHROMA_COLLECTION", "idcsa_docs"),
    )


__all__ = ["Settings", "get_settings"]
