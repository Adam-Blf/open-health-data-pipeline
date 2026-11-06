from __future__ import annotations

import pandas as pd

from health_pipeline.indicators import compute_activity_indicators


def test_compute_activity_indicators_aggregates_per_department():
    df = pd.DataFrame(
        {
            "departement": ["75", "75", "13"],
            "urgences": [True, False, True],
            "psychiatrie": [True, True, False],
            "nombre_scanners": [1, 0, 2],
        }
    )
    result = compute_activity_indicators(df)
    result = result.set_index("departement")

    assert result.loc["75", "n_etablissements"] == 2
    assert result.loc["75", "pct_urgences"] == 50.0
    assert result.loc["75", "pct_psychiatrie"] == 100.0
    assert result.loc["13", "total_scanners"] == 2
