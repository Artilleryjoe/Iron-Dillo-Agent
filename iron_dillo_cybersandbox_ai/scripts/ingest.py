"""CLI helper to ingest documents into the local Chroma instance."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..backend import rag
from ..backend.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Paths to documents to ingest")
    args = parser.parse_args()

    files = [Path(path) for path in args.paths]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise SystemExit(f"Missing files: {', '.join(missing)}")

    results = rag.ingest_files(files, settings=get_settings())
    for result in results:
        print(f"Ingested {result['doc_id']} with {result['chunks']} chunks")


if __name__ == "__main__":
    main()
