"""Ingestion of the Open FINESS dataset (French national registry of health
and social care establishments).

Source: data.gouv.fr, dataset "Open FINESS", published by the Agence du
Numerique en Sante (ANS). License: Licence Ouverte v2.0 (Etalab).
Dataset page: https://www.data.gouv.fr/datasets/open-finess
Resource used: finess-enrichi.csv (establishment-level, real, public data).

This file never contains patient data: FINESS lists institutions
(hospitals, clinics, medico-social structures), not individuals.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

FINESS_ENRICHI_URL = (
    "https://static.data.gouv.fr/resources/open-finess/20250327-210757/finess-enrichi.csv"
)

# Columns that arrive fully empty or constant in every export we have observed
# (leftover OpenStreetMap / healthsites.io enrichment columns with no FINESS
# content). Dropped explicitly during cleaning, kept listed here so the
# reason is documented rather than silently discovered.
KNOWN_EMPTY_ENRICHMENT_COLUMNS = [
    "acces_pmr",
    "etage",
    "facebook",
    "lien_santefr",
    "amenity",
    "healthcare",
    "healthcare_speciality",
    "dispensing",
    "social_facility",
    "social_facility_for",
    "naf",
    "annuaire_entreprises",
    "healthsites",
]


def download_dataset(dest_path: str | Path, url: str = FINESS_ENRICHI_URL, timeout: int = 120) -> Path:
    """Download the real Open FINESS CSV export to ``dest_path``.

    Kept as a thin, explicit function so the exact source URL is traceable
    and testable independently of any network call (network access is not
    required to run the rest of the pipeline once a CSV is on disk).
    """
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    dest.write_bytes(response.content)
    return dest


def load_raw(csv_path: str | Path) -> pd.DataFrame:
    """Load the raw FINESS CSV export as strings (no premature type coercion).

    Typing and cleaning happen explicitly in :mod:`health_pipeline.clean` so
    that ingestion stays a pure, side-effect-free "read what is on disk" step.
    """
    return pd.read_csv(csv_path, dtype=str, encoding="utf-8", low_memory=False)
