"""Data quality checks: completeness, coherence and outliers.

Why this module exists: any indicator or anonymization built on top of bad
data is silently wrong. These checks run before the pipeline trusts the
frame, and their findings are written to a report a human can read.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

FRANCE_LAT_RANGE = (-21.5, 51.5)  # covers overseas departments to mainland
FRANCE_LON_RANGE = (-63.5, 56.0)


@dataclass
class QualityReport:
    n_rows: int
    completeness: dict[str, float]
    coherence_violations: dict[str, int]
    outliers: dict[str, int]
    notes: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = ["# Data quality report", "", f"Rows evaluated: {self.n_rows}", ""]
        lines.append("## Completeness (% non-null per column)")
        for col, pct in sorted(self.completeness.items(), key=lambda kv: kv[1]):
            lines.append(f"- `{col}`: {pct:.1f}%")
        lines.append("")
        lines.append("## Coherence violations")
        if self.coherence_violations:
            for rule, count in self.coherence_violations.items():
                lines.append(f"- {rule}: {count} row(s)")
        else:
            lines.append("- none detected")
        lines.append("")
        lines.append("## Outliers (IQR method, numeric columns)")
        if self.outliers:
            for col, count in self.outliers.items():
                lines.append(f"- `{col}`: {count} outlier row(s)")
        else:
            lines.append("- none detected")
        if self.notes:
            lines.append("")
            lines.append("## Notes")
            for note in self.notes:
                lines.append(f"- {note}")
        return "\n".join(lines) + "\n"


def completeness_report(df: pd.DataFrame) -> dict[str, float]:
    """Percentage of non-null values per column."""
    return {col: float((1 - df[col].isna().mean()) * 100) for col in df.columns}


def coherence_checks(df: pd.DataFrame) -> dict[str, int]:
    """Business coherence rules, returning a violation count per rule."""
    violations: dict[str, int] = {}

    if "capacité_totale" in df.columns and "capacité_hébergement" in df.columns:
        both_known = df["capacité_totale"].notna() & df["capacité_hébergement"].notna()
        bad = both_known & (df["capacité_hébergement"] > df["capacité_totale"])
        violations["capacite_hebergement_superieure_a_capacite_totale"] = int(bad.sum())

    if "latitude" in df.columns and "longitude" in df.columns:
        lat = pd.to_numeric(df["latitude"], errors="coerce")
        lon = pd.to_numeric(df["longitude"], errors="coerce")
        known = lat.notna() & lon.notna()
        out_of_bounds = known & (
            (lat < FRANCE_LAT_RANGE[0])
            | (lat > FRANCE_LAT_RANGE[1])
            | (lon < FRANCE_LON_RANGE[0])
            | (lon > FRANCE_LON_RANGE[1])
        )
        violations["coordonnees_hors_perimetre_france"] = int(out_of_bounds.sum())

    if "code_postal" in df.columns:
        known = df["code_postal"].notna()
        bad_format = known & ~df["code_postal"].str.fullmatch(r"\d{5}", na=False)
        violations["code_postal_format_invalide"] = int(bad_format.sum())

    return violations


def outlier_report(df: pd.DataFrame, columns: list[str]) -> dict[str, int]:
    """IQR-based outlier count for the given numeric columns."""
    outliers: dict[str, int] = {}
    for col in columns:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers[col] = int(((series < lower) | (series > upper)).sum())
    return outliers


def build_quality_report(df: pd.DataFrame, numeric_columns: list[str] | None = None) -> QualityReport:
    numeric_columns = numeric_columns or [
        c for c in ["capacité_totale", "capacité_hébergement", "nombre_scanners", "nombre_irm"] if c in df.columns
    ]
    notes = []
    if "capacité_totale" in df.columns:
        na_pct = df["capacité_totale"].isna().mean() * 100
        if na_pct > 40:
            notes.append(
                f"capacité_totale is missing for {na_pct:.0f}% of rows: expected, only inpatient "
                "structures report bed capacity in FINESS."
            )
    return QualityReport(
        n_rows=len(df),
        completeness=completeness_report(df),
        coherence_violations=coherence_checks(df),
        outliers=outlier_report(df, numeric_columns),
        notes=notes,
    )
