"""Shared pytest fixtures.

All dataframes here are fully synthetic and fabricated for the sole purpose
of unit-testing the anonymization and quality logic. They do not represent
any real person, patient or establishment.
"""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def toy_establishments_df() -> pd.DataFrame:
    """10 synthetic rows mimicking the shape of a FINESS extract.

    Postal-code + category groups are deliberately built so their
    equivalence class sizes are known in advance:
    - "75001" + "CH": 1 row (k=1, unique, high risk)
    - "75002" + "Clinique": 2 rows (k=2, below a k=5 threshold)
    - "13001" + "CH": 5 rows (k=5, exactly at threshold)
    - "13001" + "Clinique": 2 rows (k=2)
    """
    def row(postal: str, category: str, psy: bool, totale: int, hebergement: int) -> dict:
        return {
            "code_postal": postal,
            "libcategetab": category,
            "psychiatrie": psy,
            "capacité_totale": totale,
            "capacité_hébergement": hebergement,
        }

    rows = [
        row("75001", "CH", True, 100, 80),
        row("75002", "Clinique", False, 50, 40),
        row("75002", "Clinique", False, 60, 45),
        row("13001", "CH", True, 200, 150),
        row("13001", "CH", False, 210, 160),
        row("13001", "CH", True, 190, 140),
        row("13001", "CH", False, 220, 170),
        row("13001", "CH", True, 205, 155),
        row("13001", "Clinique", False, 30, 20),
        row("13001", "Clinique", False, 35, 25),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def homogeneous_sensitive_df() -> pd.DataFrame:
    """Synthetic frame where one equivalence class is homogeneous on a
    sensitive column: k-anonymity would pass (5 rows) but l-diversity fails
    (l=1, everyone in the class shares the same sensitive value)."""
    rows = [
        {"departement": "75", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "75", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "75", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "75", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "75", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "13", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "13", "libcategetab": "CH", "psychiatrie": False},
        {"departement": "13", "libcategetab": "CH", "psychiatrie": True},
        {"departement": "13", "libcategetab": "CH", "psychiatrie": False},
        {"departement": "13", "libcategetab": "CH", "psychiatrie": True},
    ]
    return pd.DataFrame(rows)
