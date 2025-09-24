"""Compatibility wrapper for launching the Iron Dillo CLI."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_package_on_path() -> None:
    """Add the local ``src`` directory to ``sys.path`` for in-repo execution."""

    src_dir = Path(__file__).resolve().parent / "src"
    src_str = str(src_dir)
    if src_dir.is_dir() and src_str not in sys.path:
        sys.path.insert(0, src_str)


_ensure_package_on_path()

from iron_dillo.cli import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
