from fastapi.testclient import TestClient

from pqrs_local.main import app


def test_health_is_operational_and_does_not_expose_configuration():
    response = TestClient(app).get("/salud")

    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"status", "components"}
    assert result["status"] in {"ok", "degraded"}
    assert all(
        state in {"ready", "unavailable", "not_configured"}
        for state in result["components"].values()
    )
    serialized = response.text.lower()
    assert "secret" not in serialized
    assert "credential" not in serialized
    assert "project_id" not in serialized
