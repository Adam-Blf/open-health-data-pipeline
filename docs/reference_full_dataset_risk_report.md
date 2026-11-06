# Reference measurement: full real dataset

Generated on 2026-07-28 by running:

```bash
python scripts/download_data.py
python -m health_pipeline.pipeline --input data/raw/finess-enrichi.csv --output reports_full/
```

Input: `finess-enrichi.csv`, the real Open FINESS export (data.gouv.fr,
Licence Ouverte v2.0), 102623 rows, 51 columns, downloaded directly from
`https://static.data.gouv.fr/resources/open-finess/20250327-210757/finess-enrichi.csv`.
No patient data, establishment-level only. This file documents the
reference numbers quoted in the README; the raw file itself is not
committed (`data/raw/` is gitignored) but can be reproduced by anyone by
re-running the two commands above.

---

# Re-identification risk report

Quasi-identifiers evaluated: `code_postal, libcategetab` (k threshold = 5)

## 1. Before anonymization (raw quasi-identifiers)
- rows: 102623, equivalence classes: 59540, min k: 1, rows below threshold: 76280 (74.33%) - status: **AT RISK**

## 2. After generalization
Generalized quasi-identifiers: `departement, libcategetab`
- rows: 102623, equivalence classes: 9071, min k: 1, rows below threshold: 9863 (9.61%) - status: **AT RISK**

## 3. After generalization + suppression of residual small groups
Rows suppressed: 9863 (9.61% of the original dataset)
- rows: 92760, equivalence classes: 3758, min k: 5, rows below threshold: 0 (0.0%) - status: **OK**

## 4. l-diversity on the published (post-suppression) dataset
Sensitive column: `psychiatrie` - min l observed: 1 (threshold 2) - status: **AT RISK**
Groups below threshold: 3573 / 3758

## Verdict
- NOT SAFE TO PUBLISH AS-IS: k-anonymity is satisfied but l-diversity is not (homogeneity attack: some equivalence classes reveal the sensitive attribute with certainty even though no single row is identifiable). Add a diversity-based generalization or drop the sensitive column before publishing.

## Reading

This is the intended outcome of the demonstration, not a bug: it shows why
a k-anonymity check alone is not sufficient. Most `departement + categorie`
groups here are homogeneous on the `psychiatrie` activity flag (a "Centre
Hospitalier" group in a department is very often either all psychiatric or
all non-psychiatric), so k-anonymity hides the individual establishment
while l-diversity correctly flags that the sensitive attribute is still
inferable with certainty for 95% of the published groups. On a real patient
extract this is exactly the class of residual risk a DIM has to catch
before any k-anonymous-looking export leaves the hospital.
