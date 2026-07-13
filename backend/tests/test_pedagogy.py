from unittest.mock import patch
from fastapi.testclient import TestClient
from app.models.user import User


def test_lookup_isbn_endpoint_success(client: TestClient):
    # Simula autenticação do usuário
    class FakeUser:
        email = "test@school.com"
        role = "admin"
        id = "admin-id"

    with patch("app.api.v1.endpoints.pedagogy.get_current_user", return_value=FakeUser()):
        # Utiliza o cabeçalho de Authorization fake
        response = client.get("/api/v1/pedagogy/isbn/9788532283215", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert data["resolved"] is True
        assert data["data"]["title"] == "Português Compartilhado"


def test_lookup_isbn_endpoint_not_found(client: TestClient):
    class FakeUser:
        email = "test@school.com"
        role = "admin"

    with patch("app.api.v1.endpoints.pedagogy.get_current_user", return_value=FakeUser()):
        response = client.get("/api/v1/pedagogy/isbn/9780000000000", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 404
        assert "ISBN não localizado" in response.json()["detail"]
