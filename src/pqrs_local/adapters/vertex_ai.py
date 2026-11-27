"""Adaptador Vertex AI; solo se usa para integración real, no en pruebas locales."""

from typing import Protocol


class VertexGenerator(Protocol):
    def generate(self, controlled_labels: str, approved_extracts: list[str]) -> str:
        ...


class MockVertexGenerator:
    """Generador local seguro para desarrollo y pruebas."""

    def generate(self, controlled_labels: str, approved_extracts: list[str]) -> str:
        if not approved_extracts:
            raise ValueError("No hay extractos aprobados")
        return ""
