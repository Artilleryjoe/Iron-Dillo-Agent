"""Configuration helpers for the Iron Dillo Cybersandbox API."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration loaded from ``.env`` values when present."""

    allow_egress: bool = Field(False, alias="ALLOW_EGRESS")
    docs_path: Path = Field(Path("iron_dillo_cybersandbox_ai/vault"), alias="DOCS_PATH")
    chroma_path: Path = Field(
        Path("iron_dillo_cybersandbox_ai/data/chroma"), alias="CHROMA_PATH"
    )
    model: str = Field("llama3", alias="OLLAMA_MODEL")
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )
    audit_log_path: Path = Field(
        Path("iron_dillo_cybersandbox_ai/data/audit.log"), alias="AUDIT_LOG_PATH"
    )
    log_format: Literal["json", "text"] = Field("json", alias="AUDIT_LOG_FORMAT")
    collection_name: str = Field("idcsa_docs", alias="CHROMA_COLLECTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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

    return Settings()


__all__ = ["Settings", "get_settings"]
