"""Validación local de aprobación humana."""

import hashlib


def validate_release_approval(
    aprobado_por: str | None,
    digest_aprobado: str | None,
    texto_final: str,
) -> bool:
    """Valida identidad y coincidencia exacta del texto final."""

    if not aprobado_por or not isinstance(aprobado_por, str):
        return False
    if not digest_aprobado or not isinstance(digest_aprobado, str):
        return False
    if not isinstance(texto_final, str):
        return False

    expected = hashlib.sha256(texto_final.encode("utf-8")).hexdigest()
    return digest_aprobado.lower() == expected
