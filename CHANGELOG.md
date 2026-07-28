# Changelog

Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-07-28

### Added
- Ingestion of the real Open FINESS dataset (French health/social care
  establishment registry, data.gouv.fr, Licence Ouverte v2.0).
- Cleaning and typing module (`clean.py`).
- Data quality checks: completeness, coherence rules, IQR outlier detection
  (`quality.py`).
- Anonymization engine: quasi-identifier detection, k-anonymity metrics,
  postal-code generalization, suppression of residual small groups,
  l-diversity, and an automatically generated before/after re-identification
  risk report (`anonymize/`).
- Hospital activity indicators aggregated per French department
  (`indicators.py`).
- End-to-end pipeline orchestration and CLI (`pipeline.py`).
- Full pytest suite (TDD on the anonymization engine) and GitHub Actions CI
  (ruff + pytest + pipeline run on a committed real data sample).
