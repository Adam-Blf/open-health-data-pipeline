from __future__ import annotations

import pandas as pd

from health_pipeline.quality import (
    build_quality_report,
    coherence_checks,
    completeness_report,
    outlier_report,
)


def test_completeness_report_computes_non_null_percentage():
    df = pd.DataFrame({"a": [1, None, 3, 4], "b": [1, 2, 3, 4]})
    report = completeness_report(df)
    assert report["a"] == 75.0
    assert report["b"] == 100.0


def test_coherence_checks_flags_hebergement_above_totale():
    df = pd.DataFrame(
        {
            "capacité_totale": [100, 50, None],
            "capacité_hébergement": [80, 60, 10],  # row 1: 60 > 50 -> violation
        }
    )
    violations = coherence_checks(df)
    assert violations["capacite_hebergement_superieure_a_capacite_totale"] == 1


def test_coherence_checks_flags_coordinates_outside_france():
    df = pd.DataFrame({"latitude": ["48.85", "90.0"], "longitude": ["2.35", "2.0"]})
    violations = coherence_checks(df)
    assert violations["coordonnees_hors_perimetre_france"] == 1


def test_coherence_checks_flags_invalid_postal_code_format():
    df = pd.DataFrame({"code_postal": ["75001", "ABCDE", "7500"]})
    violations = coherence_checks(df)
    assert violations["code_postal_format_invalide"] == 2


def test_outlier_report_detects_extreme_value():
    df = pd.DataFrame({"nombre_scanners": [1, 1, 2, 1, 2, 1, 500]})
    outliers = outlier_report(df, ["nombre_scanners"])
    assert outliers["nombre_scanners"] == 1


def test_build_quality_report_renders_markdown():
    df = pd.DataFrame({"capacité_totale": [10, None], "capacité_hébergement": [5, None]})
    report = build_quality_report(df)
    markdown = report.to_markdown()
    assert "# Data quality report" in markdown
    assert "Rows evaluated: 2" in markdown
