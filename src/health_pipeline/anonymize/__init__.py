"""Anonymization engine: k-anonymity, l-diversity and re-identification risk
reporting.

This engine is generic: it operates on any dataframe and any set of
quasi-identifier columns. It is demonstrated in this repository on public
FINESS establishment data (never on patient data), but it is written to be
the same engine that would run on a row-level patient extract (for example
age band, sex, commune and pathology group) before that extract leaves a
hospital DIM (Departement d'Information Medicale). No such patient extract
is included or processed anywhere in this repository.
"""
