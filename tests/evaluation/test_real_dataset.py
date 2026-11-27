"""Valida que pytest lee el CSV entregado sin exponer texto de casos."""

import csv
from pathlib import Path


DATASET = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "dataset"
    / "dataset_pqrs_300.csv"
)
EXPECTED_TYPES = {"Petición", "Peticion", "Queja", "Reclamo", "Sugerencia"}


def test_real_dataset_file_is_loaded_and_has_expected_labeled_schema():
    assert DATASET.is_file(), "The provided dataset file is missing."

    with DATASET.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    assert reader.fieldnames is not None
    text_field = "texto_original" if "texto_original" in reader.fieldnames else "exto_original"
    assert text_field in reader.fieldnames
    assert "tipo_esperado" in reader.fieldnames
    assert len(rows) >= 299
    assert all(row[text_field].strip() for row in rows)
