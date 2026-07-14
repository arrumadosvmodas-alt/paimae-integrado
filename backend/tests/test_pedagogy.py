from unittest.mock import patch, MagicMock
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.main import app
from app.models.school import School


class FakeUser:
    email = "test@school.com"
    role = "admin"
    id = "admin-id"
    school_id = None


@pytest.fixture(autouse=True)
def _ensure_school(db_session: Session):
    db_session.add(School(name="Escola Teste", document="00000000000191"))
    db_session.commit()


def test_lookup_isbn_endpoint_success(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        response = client.get("/api/v1/pedagogy/isbn/9788532283215", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert data["resolved"] is True
        assert data["data"]["title"] == "Português Compartilhado"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_lookup_isbn_endpoint_not_found(client: TestClient):
    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        response = client.get("/api/v1/pedagogy/isbn/9780000000000", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 404
        assert "ISBN não localizado" in response.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_lookup_isbn_real_api_mocked(client: TestClient):
    # Simula resposta da Google Books API
    mock_json = {
        "totalItems": 1,
        "items": [
            {
                "volumeInfo": {
                    "title": "Clean Code",
                    "authors": ["Robert C. Martin"],
                    "categories": ["Computers"],
                    "description": "A handbook of agile software craftsmanship"
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_json).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    try:
        with patch("urllib.request.urlopen", return_value=mock_response):
            response = client.get("/api/v1/pedagogy/isbn/9780132350884", headers={"Authorization": "Bearer fake"})
            assert response.status_code == 200
            data = response.json()
            assert data["resolved"] is True
            assert data["data"]["title"] == "Clean Code"
            assert data["data"]["author"] == "Robert C. Martin"
            assert data["data"]["subject"] == "Computers"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
