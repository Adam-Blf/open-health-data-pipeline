"""Re-identification risk report: before / after generalization and
suppression, combining k-anonymity and l-diversity metrics into a single
human-readable artifact.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from health_pipeline.anonymize.k_anonymity import (
    KAnonymityMetrics,
    generalize_postal_code,
    k_anonymity_metrics,
    suppress_below_k,
)
from health_pipeline.anonymize.l_diversity import LDiversityMetrics, l_diversity_metrics


@dataclass
class ReidentificationRiskReport:
    raw_qi: list[str]
    generalized_qi: list[str]
    k_threshold: int
    before: KAnonymityMetrics
    after_generalization: KAnonymityMetrics
    after_suppression: KAnonymityMetrics
    rows_suppressed: int
    l_diversity: LDiversityMetrics | None

    def to_markdown(self) -> str:
        lines = ["# Re-identification risk report", ""]
        lines.append(
            f"Quasi-identifiers evaluated: `{', '.join(self.raw_qi)}` "
            f"(k threshold = {self.k_threshold})"
        )
        lines.append("")
        lines.append("## 1. Before anonymization (raw quasi-identifiers)")
        lines.append(self._k_block(self.before))
        lines.append("## 2. After generalization")
        lines.append(
            f"Generalized quasi-identifiers: `{', '.join(self.generalized_qi)}`"
        )
        lines.append(self._k_block(self.after_generalization))
        lines.append("## 3. After generalization + suppression of residual small groups")
        lines.append(
            f"Rows suppressed: {self.rows_suppressed} "
            f"({self._pct(self.rows_suppressed, self.before.n_rows)}% of the original dataset)"
        )
        lines.append(self._k_block(self.after_suppression))
        if self.l_diversity is not None:
            lines.append("## 4. l-diversity on the published (post-suppression) dataset")
            ld = self.l_diversity
            status = "OK" if ld.satisfies_l_diversity else "AT RISK"
            lines.append(
                f"Sensitive column: `{ld.sensitive_column}` - min l observed: {ld.min_l} "
                f"(threshold {ld.l_threshold}) - status: **{status}**"
            )
            lines.append(
                f"Groups below threshold: {ld.groups_below_threshold} / {ld.n_groups}"
            )
        lines.append("")
        lines.append("## Verdict")
        k_ok = self.after_suppression.satisfies_k_anonymity
        l_ok = self.l_diversity is None or self.l_diversity.satisfies_l_diversity
        if k_ok and l_ok:
            verdict = "PUBLISHABLE: k-anonymity and l-diversity both satisfied on the published data"
        elif k_ok and not l_ok:
            verdict = (
                "NOT SAFE TO PUBLISH AS-IS: k-anonymity is satisfied but l-diversity is not "
                "(homogeneity attack: some equivalence classes reveal the sensitive attribute with "
                "certainty even though no single row is identifiable). Add a diversity-based "
                "generalization or drop the sensitive column before publishing."
            )
        else:
            verdict = "NOT PUBLISHABLE: residual groups still below the k threshold"
        lines.append(f"- {verdict}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _pct(part: int, total: int) -> float:
        return round(part / total * 100, 2) if total else 0.0

    @staticmethod
    def _k_block(metrics: KAnonymityMetrics) -> str:
        status = "OK" if metrics.satisfies_k_anonymity else "AT RISK"
        return (
            f"- rows: {metrics.n_rows}, equivalence classes: {metrics.n_groups}, "
            f"min k: {metrics.min_k}, rows below threshold: {metrics.rows_below_threshold} "
            f"({metrics.pct_rows_below_threshold}%) - status: **{status}**\n"
        )


def build_risk_report(
    df: pd.DataFrame,
    raw_qi: list[str],
    postal_code_column: str,
    department_column: str,
    k_threshold: int = 5,
    sensitive_column: str | None = None,
    l_threshold: int = 2,
) -> ReidentificationRiskReport:
    """Build a full before/after re-identification risk report.

    ``raw_qi`` must include ``postal_code_column``; it is replaced by
    ``department_column`` for the generalized evaluation.
    """
    before = k_anonymity_metrics(df, raw_qi, k_threshold=k_threshold)

    generalized_df = generalize_postal_code(df, column=postal_code_column, new_column=department_column)
    generalized_qi = [department_column if col == postal_code_column else col for col in raw_qi]
    after_generalization = k_anonymity_metrics(generalized_df, generalized_qi, k_threshold=k_threshold)

    published_df, rows_suppressed = suppress_below_k(generalized_df, generalized_qi, k_threshold=k_threshold)
    after_suppression = k_anonymity_metrics(published_df, generalized_qi, k_threshold=k_threshold)

    l_metrics = None
    if sensitive_column is not None and sensitive_column in published_df.columns:
        l_metrics = l_diversity_metrics(published_df, generalized_qi, sensitive_column, l_threshold=l_threshold)

    return ReidentificationRiskReport(
        raw_qi=raw_qi,
        generalized_qi=generalized_qi,
        k_threshold=k_threshold,
        before=before,
        after_generalization=after_generalization,
        after_suppression=after_suppression,
        rows_suppressed=rows_suppressed,
        l_diversity=l_metrics,
    )
