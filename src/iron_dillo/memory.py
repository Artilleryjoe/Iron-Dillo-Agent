"""Simple preference storage using SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Optional

from .config import get_settings


def _default_preferences_path() -> Path:
    settings = get_settings()
    return settings.preferences_path


class PreferenceStore:
    """Persist lightweight user preferences for the Iron Dillo buddy."""

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            self._path: str | Path = _default_preferences_path()
        else:
            self._path = path

        if isinstance(self._path, Path):
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path_str = str(self._path)
        else:
            self._path_str = self._path

        self._memory_connection: Optional[sqlite3.Connection] = None

        with self._managed_connection() as conn:
            self._ensure_schema(conn)

    def _connect(self) -> sqlite3.Connection:
        if self._path_str == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(self._path_str)
            return self._memory_connection
        return sqlite3.connect(self._path_str)

    @contextmanager
    def _managed_connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
        finally:
            if self._path_str != ":memory:":
                conn.close()

    @staticmethod
    def _ensure_schema(conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()

    def set_preference(self, key: str, value: str) -> None:
        """Store a preference value, replacing existing entries."""

        cleaned_key = key.strip()
        if not cleaned_key:
            raise ValueError("Preference key cannot be empty")

        with self._managed_connection() as conn:
            conn.execute(
                "INSERT INTO preferences(key, value) VALUES(?, ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (cleaned_key, value),
            )
            conn.commit()

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a stored value, returning `default` if it does not exist."""

        cleaned_key = key.strip()
        if not cleaned_key:
            raise ValueError("Preference key cannot be empty")

        with self._managed_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM preferences WHERE key = ?",
                (cleaned_key,),
            )
            row = cursor.fetchone()

        return row[0] if row else default

    def list_preferences(self) -> Dict[str, str]:
        """Return all stored preferences sorted by key."""

        with self._managed_connection() as conn:
            cursor = conn.execute("SELECT key, value FROM preferences ORDER BY key")
            rows = cursor.fetchall()

        return {key: value for key, value in rows}


__all__ = ["PreferenceStore"]
