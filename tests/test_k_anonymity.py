from __future__ import annotations

from health_pipeline.anonymize.k_anonymity import (
    detect_quasi_identifiers,
    equivalence_class_sizes,
    generalize_postal_code,
    k_anonymity_metrics,
    suppress_below_k,
)


def test_equivalence_class_sizes_match_known_groups(toy_establishments_df):
    sizes = equivalence_class_sizes(toy_establishments_df, ["code_postal", "libcategetab"])
    # 75001 + CH -> 1 row
    assert sizes.iloc[0] == 1
    # 75002 + Clinique -> 2 rows
    assert sizes.iloc[1] == 2
    assert sizes.iloc[2] == 2
    # 13001 + CH -> 5 rows
    assert sizes.iloc[3] == 5


def test_k_anonymity_metrics_detects_unique_row_as_min_k(toy_establishments_df):
    metrics = k_anonymity_metrics(toy_establishments_df, ["code_postal", "libcategetab"], k_threshold=5)
    assert metrics.min_k == 1
    assert not metrics.satisfies_k_anonymity
    assert metrics.n_groups == 4


def test_k_anonymity_metrics_pass_when_all_groups_above_threshold(toy_establishments_df):
    # 13001+CH is the only group with >= 5 rows; isolate it
    subset = toy_establishments_df[
        (toy_establishments_df["code_postal"] == "13001") & (toy_establishments_df["libcategetab"] == "CH")
    ]
    metrics = k_anonymity_metrics(subset, ["code_postal", "libcategetab"], k_threshold=5)
    assert metrics.min_k == 5
    assert metrics.satisfies_k_anonymity
    assert metrics.rows_below_threshold == 0


def test_generalize_postal_code_extracts_metropolitan_department():
    import pandas as pd

    df = pd.DataFrame({"code_postal": ["75001", "13008", "01000"]})
    out = generalize_postal_code(df)
    assert list(out["departement"]) == ["75", "13", "01"]


def test_generalize_postal_code_extracts_overseas_department():
    import pandas as pd

    df = pd.DataFrame({"code_postal": ["97100", "97400"]})
    out = generalize_postal_code(df)
    assert list(out["departement"]) == ["971", "974"]


def test_suppress_below_k_removes_only_small_groups(toy_establishments_df):
    published, suppressed_count = suppress_below_k(
        toy_establishments_df, ["code_postal", "libcategetab"], k_threshold=5
    )
    # only the 13001+CH group (5 rows) survives
    assert len(published) == 5
    assert suppressed_count == 5
    metrics = k_anonymity_metrics(published, ["code_postal", "libcategetab"], k_threshold=5)
    assert metrics.satisfies_k_anonymity


def test_detect_quasi_identifiers_excludes_near_unique_and_constant_columns():
    import pandas as pd

    df = pd.DataFrame(
        {
            "id": [str(i) for i in range(10)],  # near-unique -> excluded
            "constant": ["A"] * 10,  # constant -> excluded (cardinality 1)
            "category": ["CH", "Clinique"] * 5,  # plausible QI
        }
    )
    flagged = detect_quasi_identifiers(df, ["id", "constant", "category"])
    assert flagged == ["category"]
