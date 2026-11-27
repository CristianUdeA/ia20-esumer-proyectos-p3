"""Configuración no secreta del servicio.

Las credenciales se obtienen mediante ADC; sus valores nunca se cargan aquí.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    google_cloud_project: str | None
    google_cloud_location: str | None
    rag_bucket: str | None
    gemini_model_id: str | None
    embedding_model_id: str
    secret_manager_secret_id: str | None
    max_text_length: int
    classification_confidence_threshold: float

    @classmethod
    def from_environment(cls) -> "Settings":
        """Lee únicamente identificadores de configuración, nunca secretos."""
        try:
            max_text_length = int(os.getenv("PQRS_MAX_TEXT_LENGTH", "50000"))
            confidence_threshold = float(
                os.getenv("PQRS_CLASSIFICATION_CONFIDENCE_THRESHOLD", "0.70")
            )
        except ValueError as exc:
            raise ValueError("Invalid non-secret PQRS configuration") from exc

        if max_text_length < 1 or not 0 <= confidence_threshold <= 1:
            raise ValueError("Invalid non-secret PQRS configuration")

        return cls(
            google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT") or None,
            google_cloud_location=os.getenv("GOOGLE_CLOUD_LOCATION") or None,
            rag_bucket=os.getenv("RAG_BUCKET") or None,
            gemini_model_id=os.getenv("GEMINI_MODEL_ID") or None,
            embedding_model_id=os.getenv(
                "EMBEDDING_MODEL_ID", "text-embedding-004"
            ),
            secret_manager_secret_id=os.getenv(
                "GOOGLE_SECRET_MANAGER_SECRET_ID"
            )
            or None,
            max_text_length=max_text_length,
            classification_confidence_threshold=confidence_threshold,
        )
