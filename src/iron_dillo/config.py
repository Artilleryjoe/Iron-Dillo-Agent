"""Configuration management for the Iron Dillo Cybersecurity Buddy."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

__all__ = ["Settings", "get_settings", "load_settings", "set_settings"]

_SETTINGS_CACHE: Optional["Settings"] = None


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}

    data: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        data[key.strip()] = raw_value.strip().strip('"').strip("'")
    return data


@dataclass(frozen=True)
class Settings:
    """Application configuration resolved from environment variables."""

    environment: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    preferences_filename: str = "preferences.db"
    telemetry_enabled: bool = False

    @property
    def preferences_path(self) -> Path:
        return self.data_dir / self.preferences_filename

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        env_file: Path | None = Path(".env"),
    ) -> "Settings":
        env = dict(os.environ if env is None else env)
        if env_file:
            env.update({k: v for k, v in _load_env_file(env_file).items() if k not in env})

        environment = env.get("IRON_DILLO_ENV", cls.environment).strip() or cls.environment
        environment = environment.lower()

        log_level = env.get("IRON_DILLO_LOG_LEVEL", cls.log_level).strip().upper()
        valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if log_level not in valid_levels:
            raise ValueError(
                f"Unsupported log level '{log_level}'. Choose from {sorted(valid_levels)}."
            )

        data_dir = Path(env.get("IRON_DILLO_DATA_DIR", str(cls.data_dir))).expanduser()
        preferences_filename = env.get(
            "IRON_DILLO_PREFERENCES_FILENAME", cls.preferences_filename
        ).strip() or cls.preferences_filename

        telemetry_enabled = _parse_bool(env.get("IRON_DILLO_TELEMETRY_ENABLED", "false"))

        return cls(
            environment=environment,
            log_level=log_level,
            data_dir=data_dir,
            preferences_filename=preferences_filename,
            telemetry_enabled=telemetry_enabled,
        )

    def with_overrides(self, overrides: Mapping[str, Any]) -> "Settings":
        data_dir = Path(overrides.get("data_dir", self.data_dir)).expanduser()
        pref_override = overrides.get(
            "preferences_filename", self.preferences_filename
        )
        if pref_override is None:
            preferences_filename = self.preferences_filename
        else:
            cleaned_pref = str(pref_override).strip()
            preferences_filename = cleaned_pref or self.preferences_filename
        log_level = str(overrides.get("log_level", self.log_level)).upper()
        environment = str(overrides.get("environment", self.environment)).lower()
        telemetry_raw = overrides.get("telemetry_enabled", self.telemetry_enabled)
        if isinstance(telemetry_raw, str):
            telemetry_enabled = _parse_bool(telemetry_raw)
        else:
            telemetry_enabled = bool(telemetry_raw)

        valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if log_level not in valid_levels:
            raise ValueError(
                f"Unsupported log level '{log_level}'. Choose from {sorted(valid_levels)}."
            )

        return replace(
            self,
            environment=environment or self.environment,
            log_level=log_level,
            data_dir=data_dir,
            preferences_filename=preferences_filename or self.preferences_filename,
            telemetry_enabled=bool(telemetry_enabled),
        )


def get_settings() -> Settings:
    global _SETTINGS_CACHE

    if _SETTINGS_CACHE is None:
        _SETTINGS_CACHE = Settings.from_env()
        _SETTINGS_CACHE.data_dir.mkdir(parents=True, exist_ok=True)
    return _SETTINGS_CACHE


def set_settings(settings: Settings) -> Settings:
    global _SETTINGS_CACHE

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    _SETTINGS_CACHE = settings
    return settings


def load_settings(*, override_files: Optional[Iterable[Path]] = None) -> Settings:
    base = Settings.from_env()

    overrides: Dict[str, Any] = {}
    for file_path in override_files or ():
        if not file_path.exists():
            continue

        if file_path.suffix.lower() == ".json":
            data = json.loads(file_path.read_text())
        elif file_path.suffix.lower() in {".toml", ".tml"}:
            try:
                import tomllib  # type: ignore[attr-defined]
            except ModuleNotFoundError:  # pragma: no cover
                import tomli as tomllib  # type: ignore
            data = tomllib.loads(file_path.read_text())
        else:
            continue

        if not isinstance(data, dict):
            raise ValueError(
                f"Configuration file {file_path} must contain a top-level object/dict."
            )
        overrides.update(data)

    return set_settings(base.with_overrides(overrides))
