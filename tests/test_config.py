"""Tests for configuration and logging utilities."""

from __future__ import annotations

import json
import logging

import pytest

from iron_dillo import (
    Settings,
    configure_logging,
    get_logger,
    get_settings,
    load_settings,
    set_settings,
)


@pytest.fixture(autouse=True)
def reset_settings_cache(monkeypatch):
    from iron_dillo import config as config_module

    config_module._SETTINGS_CACHE = None  # type: ignore[attr-defined]
    yield
    config_module._SETTINGS_CACHE = None  # type: ignore[attr-defined]


def test_default_settings_uses_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("IRON_DILLO_DATA_DIR", str(tmp_path / "preferences"))
    settings = get_settings()
    assert settings.data_dir == tmp_path / "preferences"
    assert settings.preferences_path == tmp_path / "preferences" / "preferences.db"


def test_load_settings_from_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"log_level": "debug", "environment": "Prod"}))

    settings = load_settings(override_files=[config_file])
    assert settings.log_level == "DEBUG"
    assert settings.environment == "prod"


def test_invalid_log_level_raises(tmp_path):
    config_file = tmp_path / "bad.json"
    config_file.write_text(json.dumps({"log_level": "verbose"}))

    with pytest.raises(ValueError):
        load_settings(override_files=[config_file])


def test_configure_logging_sets_formatter(tmp_path):
    set_settings(Settings(data_dir=tmp_path))
    logger = configure_logging(get_settings())
    logger.info("configured")

    child = get_logger("test")
    assert isinstance(child, logging.Logger)
    assert child.name == "iron_dillo.test"
