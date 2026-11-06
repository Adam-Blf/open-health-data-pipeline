"""Download the real Open FINESS dataset to data/raw/.

Usage:
    python scripts/download_data.py
"""

from __future__ import annotations

from pathlib import Path

from health_pipeline.ingest import FINESS_ENRICHI_URL, download_dataset

DEST = Path(__file__).resolve().parent.parent / "data" / "raw" / "finess-enrichi.csv"


def main() -> None:
    print(f"Downloading {FINESS_ENRICHI_URL} -> {DEST}")
    path = download_dataset(DEST)
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Done: {path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
