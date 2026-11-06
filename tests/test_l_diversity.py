from __future__ import annotations

from health_pipeline.anonymize.l_diversity import l_diversity_metrics


def test_l_diversity_flags_homogeneous_group(homogeneous_sensitive_df):
    metrics = l_diversity_metrics(
        homogeneous_sensitive_df, ["departement"], sensitive_column="psychiatrie", l_threshold=2
    )
    # departement 75 group is homogeneous (all True) -> l=1 for that group
    assert metrics.min_l == 1
    assert not metrics.satisfies_l_diversity
    assert metrics.groups_below_threshold == 1


def test_l_diversity_passes_when_all_groups_diverse():
    import pandas as pd

    df = pd.DataFrame(
        {
            "departement": ["75", "75", "75", "13", "13", "13"],
            "psychiatrie": [True, False, True, False, True, False],
        }
    )
    metrics = l_diversity_metrics(df, ["departement"], sensitive_column="psychiatrie", l_threshold=2)
    assert metrics.min_l == 2
    assert metrics.satisfies_l_diversity
    assert metrics.groups_below_threshold == 0
