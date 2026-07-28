"""Hospital activity indicators aggregated per French department.

These indicators are computed on the FINESS establishment registry (counts
and shares of establishments offering a given activity or equipment), not on
patient-level activity data (which is not open data and is never used here).
"""

from __future__ import annotations

import pandas as pd

ACTIVITY_COLUMNS = [
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


def compute_activity_indicators(df: pd.DataFrame, group_column: str = "departement") -> pd.DataFrame:
    """Per-department count of establishments and share offering each activity."""
    present_activities = [c for c in ACTIVITY_COLUMNS if c in df.columns]
    grouped = df.groupby(group_column, dropna=True)

    result = grouped.size().rename("n_etablissements").to_frame()

    for col in present_activities:
        result[f"pct_{col}"] = (grouped[col].mean() * 100).round(1)

    if "nombre_scanners" in df.columns:
        result["total_scanners"] = grouped["nombre_scanners"].sum(min_count=1)
    if "nombre_irm" in df.columns:
        result["total_irm"] = grouped["nombre_irm"].sum(min_count=1)

    return result.sort_values("n_etablissements", ascending=False).reset_index()
