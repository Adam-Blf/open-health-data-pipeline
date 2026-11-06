# Sample data

`finess_sample.csv` is a reproducible random subset (2000 rows, seed 42,
`pandas.DataFrame.sample(n=2000, random_state=42)`) of the real, public
Open FINESS dataset:

- Source: https://www.data.gouv.fr/datasets/open-finess (resource
  `finess-enrichi.csv`, published by the Agence du Numerique en Sante).
- License: Licence Ouverte v2.0 (Etalab), reuse and redistribution allowed
  with attribution.
- Content: French health and social care establishments (name, category,
  address, capacity, equipment, authorized activities). No patient data.

Committed here so `make ci` / GitHub Actions can run the full pipeline
end to end without a network call, on real data.

To regenerate the full raw dataset instead of the sample, run
`python scripts/download_data.py`.

**Note on risk-report numbers**: a 2000-row random subsample of a 102623-row
population is statistically sparser than the population itself (rare
quasi-identifier combinations become rarer, or singleton, faster than the
sample shrinks). The risk report generated on this sample will therefore
show a higher suppression rate than the one generated on the full dataset.
The reference measurement (74.3% of rows at risk before anonymization,
9.2% after generalization alone, 0% after generalization plus suppression
of the residual small groups, 9.22% of rows suppressed) is computed on the
**full** real dataset and archived in
`docs/reference_full_dataset_risk_report.md`. The sample exists to prove
the pipeline runs correctly end to end in CI, not to reproduce that exact
figure.
