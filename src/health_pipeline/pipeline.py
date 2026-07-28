"""End-to-end pipeline orchestration: ingest -> clean -> quality -> anonymize
-> indicators -> write reports.

Usage:
    python -m health_pipeline.pipeline --input data/sample/finess_sample.csv --output reports/
"""

from __future__ import annotations

import argparse
from pathlib import Path

from health_pipeline.anonymize.risk_report import build_risk_report
from health_pipeline.clean import clean
from health_pipeline.indicators import compute_activity_indicators
from health_pipeline.ingest import load_raw
from health_pipeline.quality import build_quality_report

RAW_QUASI_IDENTIFIERS = ["code_postal", "libcategetab"]
SENSITIVE_COLUMN = "psychiatrie"
K_THRESHOLD = 5
L_THRESHOLD = 2


def run_pipeline(input_csv: str | Path, output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw(input_csv)
    clean_df = clean(raw_df)

    quality = build_quality_report(clean_df)
    quality_path = output / "quality_report.md"
    quality_path.write_text(quality.to_markdown(), encoding="utf-8")

    risk = build_risk_report(
        clean_df,
        raw_qi=RAW_QUASI_IDENTIFIERS,
        postal_code_column="code_postal",
        department_column="departement",
        k_threshold=K_THRESHOLD,
        sensitive_column=SENSITIVE_COLUMN,
        l_threshold=L_THRESHOLD,
    )
    risk_path = output / "risk_report.md"
    risk_path.write_text(risk.to_markdown(), encoding="utf-8")

    indicators_df = compute_activity_indicators(clean_df)
    indicators_path = output / "activity_indicators.csv"
    indicators_df.to_csv(indicators_path, index=False, encoding="utf-8")

    summary = {
        "n_rows_raw": len(raw_df),
        "n_rows_clean": len(clean_df),
        "min_k_before": risk.before.min_k,
        "min_k_after_suppression": risk.after_suppression.min_k,
        "rows_suppressed": risk.rows_suppressed,
    }
    print(
        f"[pipeline] rows raw={summary['n_rows_raw']} clean={summary['n_rows_clean']} "
        f"min_k_before={summary['min_k_before']} "
        f"min_k_after_suppression={summary['min_k_after_suppression']} "
        f"rows_suppressed={summary['rows_suppressed']}"
    )

    return {
        "quality_report": quality_path,
        "risk_report": risk_path,
        "activity_indicators": indicators_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the open health data pipeline")
    parser.add_argument("--input", required=True, help="Path to a FINESS CSV export")
    parser.add_argument("--output", default="reports", help="Output directory for reports")
    args = parser.parse_args()
    run_pipeline(args.input, args.output)


if __name__ == "__main__":
    main()
