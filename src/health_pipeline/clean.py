"""Cleaning and typing of the raw FINESS export.

Business rule (why, not just what): FINESS is exported as an open, flat CSV
mixing identifiers, free text, booleans encoded as Python-style "True"/"False"
strings, and a handful of columns that are always empty or constant in every
observed export (leftover enrichment columns). Cleaning makes the frame safe
to reason about (stable dtypes) before quality checks or anonymization run.
"""

from __future__ import annotations

import pandas as pd

from health_pipeline.ingest import KNOWN_EMPTY_ENRICHMENT_COLUMNS

NUMERIC_COLUMNS = [
    "capacité_totale",
    "capacité_hébergement",
    "nombre_scanners",
    "nombre_irm",
]

BOOLEAN_COLUMNS = [
    "equipement_handicap_enfants",
    "equipement_handicap_adultes",
    "equipement_personnes_agees",
    "activite_sanitaire",
    "medecine",
    "chirurgie",
    "gyneco_obstetrique_neonatal",
    "psychiatrie",
    "hospitalisation_domicile",
    "soins_longue_duree",
    "urgences",
    "soins_critiques",
    "dialyse",
    "traitement_cancer",
    "service_readaptation",
]

TEXT_STRIP_COLUMNS = ["rs", "ville", "libcategetab", "sous_categorie", "code_postal"]


def drop_empty_enrichment_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns that are always empty or single-valued in this export."""
    present = [c for c in KNOWN_EMPTY_ENRICHMENT_COLUMNS if c in df.columns]
    return df.drop(columns=present)


def _to_bool(series: pd.Series) -> pd.Series:
    mapping = {"True": True, "False": False, "true": True, "false": False}
    return series.map(mapping)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a typed, deduplicated, department-enriched copy of ``df``."""
    out = df.copy()

    out = drop_empty_enrichment_columns(out)

    for col in TEXT_STRIP_COLUMNS:
        if col in out.columns:
            out[col] = out[col].str.strip()

    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    for col in BOOLEAN_COLUMNS:
        if col in out.columns:
            out[col] = _to_bool(out[col])

    # French department code: first 2 digits of the postal code for
    # metropolitan France, first 3 for overseas departments (971-976).
    # Documented approximation: this is a generalization used for
    # anonymization, not an official INSEE geographic join.
    if "code_postal" in out.columns:
        out["departement"] = out["code_postal"].apply(_postal_to_departement)

    out = out.drop_duplicates(subset=["finess_et"]) if "finess_et" in out.columns else out.drop_duplicates()

    return out


def _postal_to_departement(code_postal: str | float) -> str | None:
    if not isinstance(code_postal, str) or len(code_postal) < 2:
        return None
    if code_postal.startswith("97") or code_postal.startswith("98"):
        return code_postal[:3]
    return code_postal[:2]
