"""Security helpers for the Iron Dillo Cybersandbox API."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from .settings import Settings

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class AuditLogger(Protocol):
    """Protocol for append-only logging of sensitive operations."""

    def log(self, *, route: str, payload: dict) -> None:
        ...


class FileAuditLogger:
    """Simple append-only logger writing JSON lines to disk."""

    def __init__(self, log_path: Path, *, format: str = "json") -> None:
        self.log_path = log_path
        self.format = format

    def log(self, *, route: str, payload: dict) -> None:  # noqa: D401 - short method
        """Write the payload to disk with a timestamp."""

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        record = {"ts": timestamp, "route": route, "payload": payload}
        if self.format == "json":
            line = json.dumps(record, sort_keys=True)
        else:
            line = f"{timestamp}\t{route}\t{json.dumps(payload, sort_keys=True)}"
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


class EgressBlockedError(RuntimeError):
    """Raised when an operation attempts to perform an outbound network call."""


def assert_egress_allowed(settings: Settings) -> None:
    """Fail closed if outbound requests are not permitted."""

    if not settings.allow_egress:
        raise EgressBlockedError(
            "Outbound network calls are disabled. Set ALLOW_EGRESS=true to override."
        )


def sanitize_text(text: str) -> str:
    """Scrub direct identifiers from text before visualization or export."""

    sanitized = EMAIL_RE.sub("<EMAIL>", text)
    sanitized = PHONE_RE.sub("<PHONE>", sanitized)
    sanitized = SSN_RE.sub("<SSN>", sanitized)
    sanitized = re.sub(r"\b([A-Z][a-z]+)\s([A-Z][a-z]+)\b", "CLIENT_NAME", sanitized)
    return sanitized


def scrub_collection_metadata(records: Iterable[dict]) -> list[dict]:
    """Remove raw text fields while retaining identifiers for plotting."""

    sanitized_records: list[dict] = []
    for record in records:
        sanitized_records.append(
            {
                "doc_id": record.get("doc_id"),
                "source": record.get("source"),
                "hash": record.get("hash"),
            }
        )
    return sanitized_records


def build_audit_logger(settings: Settings) -> AuditLogger:
    """Create the default audit logger for API routes."""

    return FileAuditLogger(settings.audit_log_file, format=settings.log_format)


def raise_if_egress_attempt(*_args, **_kwargs) -> None:
    """Utility compatible with HTTP client hooks to enforce offline mode."""

    allow_flag = os.environ.get("ALLOW_EGRESS", "false").lower() in {"1", "true", "yes"}
    if not allow_flag:
        raise EgressBlockedError("Outbound requests are disabled by policy")


__all__ = [
    "AuditLogger",
    "FileAuditLogger",
    "EgressBlockedError",
    "assert_egress_allowed",
    "sanitize_text",
    "scrub_collection_metadata",
    "build_audit_logger",
    "raise_if_egress_attempt",
]
