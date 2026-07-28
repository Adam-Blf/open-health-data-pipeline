"""k-anonymity: quasi-identifier detection, equivalence classes, generalization
and suppression.

k-anonymity definition used here: a dataset satisfies k-anonymity for a set
of quasi-identifier (QI) columns if every combination of values on those
columns is shared by at least k rows (an "equivalence class" of size >= k).
A row alone in its equivalence class (k=1) is trivially re-identifiable by
anyone who knows its QI values from another source; that is exactly the
attack a re-identification risk report has to catch before any extract is
published or shared outside its collection context.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


def detect_quasi_identifiers(
    df: pd.DataFrame,
    candidate_columns: list[str],
    min_cardinality: int = 2,
    max_cardinality_ratio: float = 0.5,
) -> list[str]:
    """Heuristic quasi-identifier detection among candidate columns.

    A column is flagged as a plausible quasi-identifier when it is neither
    a near-unique identifier (cardinality close to the row count, e.g. a
    primary key or a full name) nor a constant (cardinality 1). This is a
    heuristic starting point, not a substitute for a human privacy review.
    """
    n = len(df)
    if n == 0:
        return []
    flagged = []
    for col in candidate_columns:
        if col not in df.columns:
            continue
        cardinality = df[col].nunique(dropna=True)
        if cardinality < min_cardinality:
            continue
        if cardinality > n * max_cardinality_ratio:
            continue
        flagged.append(col)
    return flagged


def equivalence_class_sizes(df: pd.DataFrame, quasi_identifiers: list[str]) -> pd.Series:
    """Size of the equivalence class (group of identical QI values) each row belongs to."""
    if not quasi_identifiers:
        raise ValueError("quasi_identifiers must be a non-empty list")
    group_sizes = df.groupby(quasi_identifiers, dropna=False)[quasi_identifiers[0]].transform("size")
    group_sizes.name = "equivalence_class_size"
    return group_sizes


@dataclass
class KAnonymityMetrics:
    quasi_identifiers: list[str]
    k_threshold: int
    n_rows: int
    n_groups: int
    min_k: int
    rows_below_threshold: int

    @property
    def pct_rows_below_threshold(self) -> float:
        if self.n_rows == 0:
            return 0.0
        return round(self.rows_below_threshold / self.n_rows * 100, 2)

    @property
    def satisfies_k_anonymity(self) -> bool:
        return self.min_k >= self.k_threshold


def k_anonymity_metrics(
    df: pd.DataFrame, quasi_identifiers: list[str], k_threshold: int = 5
) -> KAnonymityMetrics:
    """Compute k-anonymity metrics for the given quasi-identifiers."""
    sizes = equivalence_class_sizes(df, quasi_identifiers)
    group_sizes = df.assign(_size=sizes).groupby(quasi_identifiers, dropna=False)["_size"].first()
    return KAnonymityMetrics(
        quasi_identifiers=list(quasi_identifiers),
        k_threshold=k_threshold,
        n_rows=len(df),
        n_groups=int(group_sizes.shape[0]),
        min_k=int(group_sizes.min()) if len(group_sizes) else 0,
        rows_below_threshold=int((sizes < k_threshold).sum()),
    )


def generalize_postal_code(df: pd.DataFrame, column: str = "code_postal", new_column: str = "departement") -> pd.DataFrame:
    """Generalize a 5-digit French postal code to its 2-digit department (3 for overseas)."""
    out = df.copy()

    def _to_departement(value: object) -> str | None:
        if not isinstance(value, str) or len(value) < 2:
            return None
        if value.startswith("97") or value.startswith("98"):
            return value[:3]
        return value[:2]

    out[new_column] = out[column].apply(_to_departement)
    return out


def suppress_below_k(
    df: pd.DataFrame, quasi_identifiers: list[str], k_threshold: int = 5
) -> tuple[pd.DataFrame, int]:
    """Remove rows whose equivalence class is smaller than ``k_threshold``.

    Returns the filtered (compliant) dataframe and the number of rows
    suppressed. Suppression is the standard fallback when generalization
    alone cannot bring every equivalence class above the threshold; it
    trades completeness for a hard privacy guarantee, and the trade-off is
    always reported explicitly rather than hidden.
    """
    sizes = equivalence_class_sizes(df, quasi_identifiers)
    keep_mask = sizes >= k_threshold
    return df.loc[keep_mask].copy(), int((~keep_mask).sum())
