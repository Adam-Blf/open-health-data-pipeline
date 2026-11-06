"""l-diversity: guards against the homogeneity attack that k-anonymity alone
does not catch.

A dataset can satisfy k-anonymity (every equivalence class has >= k rows)
and still leak: if every row in an equivalence class shares the same value
of a sensitive attribute, knowing that someone belongs to that class reveals
the sensitive value with certainty, even though the class itself is
"anonymous" in the k-anonymity sense. l-diversity requires at least l
distinct sensitive values per equivalence class.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class LDiversityMetrics:
    quasi_identifiers: list[str]
    sensitive_column: str
    l_threshold: int
    n_groups: int
    min_l: int
    groups_below_threshold: int

    @property
    def satisfies_l_diversity(self) -> bool:
        return self.min_l >= self.l_threshold


def l_diversity_metrics(
    df: pd.DataFrame,
    quasi_identifiers: list[str],
    sensitive_column: str,
    l_threshold: int = 2,
) -> LDiversityMetrics:
    """Compute distinct-value (l-diversity) metrics for a sensitive column."""
    if not quasi_identifiers:
        raise ValueError("quasi_identifiers must be a non-empty list")
    distinct_counts = df.groupby(quasi_identifiers, dropna=False)[sensitive_column].nunique(dropna=True)
    return LDiversityMetrics(
        quasi_identifiers=list(quasi_identifiers),
        sensitive_column=sensitive_column,
        l_threshold=l_threshold,
        n_groups=int(distinct_counts.shape[0]),
        min_l=int(distinct_counts.min()) if len(distinct_counts) else 0,
        groups_below_threshold=int((distinct_counts < l_threshold).sum()),
    )
