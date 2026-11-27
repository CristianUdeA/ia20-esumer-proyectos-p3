from fastapi.testclient import TestClient

from pqrs_local.main import app


client = TestClient(app)


def test_no_source_returns_exact_unfounded_state_and_is_blocked():
    response = client.post(
        "/borrador",
        json={"texto_pqrs": "Solicito revisar un cobro duplicado."},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["estado"] == "sin fundamento"
    assert result["revision_requerida"] is True
    assert result["bloqueado_para_liberacion"] is True
    assert result["citas"] == []


def test_invalid_or_missing_text_is_rejected_safely():
    for payload in ({}, {"texto_pqrs": None}, {"texto_pqrs": ""}):
        response = client.post("/borrador", json=payload)
        assert response.status_code == 422
        assert "texto_pqrs" not in response.text


def test_client_text_is_never_returned_as_a_draft():
    marker = "MARCADOR_SINTETICO_PRIVADO_9f7a"
    response = client.post("/borrador", json={"texto_pqrs": marker})

    assert response.status_code == 200
    assert marker not in response.text
    assert response.json()["bloqueado_para_liberacion"] is True


def test_unavailable_generation_or_retrieval_fails_closed():
    response = client.post(
        "/borrador",
        json={"texto_pqrs": "Necesito revisar mi servicio."},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["revision_requerida"] is True
    assert result["bloqueado_para_liberacion"] is True
    assert result["estado"] in {
        "sin fundamento",
        "revision_requerida",
        "no_disponible",
    }
