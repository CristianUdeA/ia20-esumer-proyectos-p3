"""Gate de precisión: solo el corpus sintético de 40+ casos cuenta."""

import csv
from collections import Counter
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"
ACCEPTANCE_FILE = FIXTURES / "pqrs_acceptance_40.csv"
SYNTHETIC_TYPES = {"Petición", "Queja", "Reclamo", "Sugerencia"}


def test_acceptance_gate_uses_at_least_40_labeled_synthetic_cases():
    assert ACCEPTANCE_FILE.is_file(), (
        "Missing synthetic acceptance corpus; the 5-case smoke fixture and "
        "the separate 300-row dataset are not substitutes."
    )

    with ACCEPTANCE_FILE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) >= 40
    assert {"texto", "tipo_esperado"} <= set(rows[0])
    assert all(row["tipo_esperado"] in SYNTHETIC_TYPES for row in rows)
    assert {row["tipo_esperado"] for row in rows} == SYNTHETIC_TYPES

    from pqrs_local.services.classification import classify_pqrs

    correct = sum(
        classify_pqrs(row["texto"]).tipo == row["tipo_esperado"] for row in rows
    )
    accuracy = correct / len(rows)
    assert accuracy >= 0.85, (
        f"Synthetic acceptance accuracy {accuracy:.3f} is below 0.85 "
        f"({correct}/{len(rows)})."
    )


def test_smoke_fixture_is_not_counted_as_acceptance_gate():
    with (FIXTURES / "pqrs_smoke_5.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        smoke_rows = list(csv.DictReader(stream))

    assert len(smoke_rows) == 5
    assert Counter(row["tipo_esperado"] for row in smoke_rows)
    assert len(smoke_rows) < 40
