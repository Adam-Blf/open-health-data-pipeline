from __future__ import annotations

import csv
from pathlib import Path

from health_pipeline.pipeline import run_pipeline

CSV_HEADER = [
    "finess_et",
    "finess_ej",
    "rs",
    "libcategetab",
    "code_postal",
    "ville",
    "longitude",
    "latitude",
    "capacité_totale",
    "capacité_hébergement",
    "psychiatrie",
    "medecine",
    "urgences",
    "nombre_scanners",
    "nombre_irm",
]


def _write_synthetic_csv(path: Path, n_per_group: int = 6) -> None:
    """Write a small, fully synthetic CSV shaped like a FINESS export, used
    only to prove the pipeline runs end to end. Not real establishment data."""
    rows = []
    groups = [("75001", "CH"), ("13001", "Clinique")]
    row_id = 0
    for postal, category in groups:
        for _ in range(n_per_group):
            row_id += 1
            rows.append(
                [
                    str(row_id),
                    str(1000 + row_id),
                    f"Etablissement synthetique {row_id}",
                    category,
                    postal,
                    "Ville test",
                    "2.35",
                    "48.85",
                    "100",
                    "80",
                    "True" if row_id % 2 == 0 else "False",
                    "True",
                    "False",
                    "0",
                    "0",
                ]
            )
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)


def test_run_pipeline_end_to_end_writes_all_reports(tmp_path):
    input_csv = tmp_path / "synthetic_sample.csv"
    _write_synthetic_csv(input_csv)
    output_dir = tmp_path / "reports"

    paths = run_pipeline(input_csv, output_dir)

    assert paths["quality_report"].exists()
    assert paths["risk_report"].exists()
    assert paths["activity_indicators"].exists()

    risk_markdown = paths["risk_report"].read_text(encoding="utf-8")
    assert "Re-identification risk report" in risk_markdown
    # both groups have exactly 6 rows -> k=6 >= threshold 5, nothing suppressed
    assert "Rows suppressed: 0" in risk_markdown
