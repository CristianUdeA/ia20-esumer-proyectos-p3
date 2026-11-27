"""Adaptador GCS para fuentes aprobadas e índice privado."""

from typing import Protocol


class ApprovedSourceStorage(Protocol):
    def load_manifest(self) -> dict:
        ...


class MockApprovedSourceStorage:
    """Almacenamiento local vacío y seguro."""

    def load_manifest(self) -> dict:
        return {"approved": True, "sources": []}
