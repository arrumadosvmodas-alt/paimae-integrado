from fastapi.testclient import TestClient


def _bootstrap_admin(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/bootstrap-admin",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "strong-password",
            "role": "admin",
            "document": "52998224725",
        },
    )
    assert response.status_code == 201, response.text
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "strong-password"},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_create_school_child_and_guardian_scope(client: TestClient):
    admin_token = _bootstrap_admin(client)

    school = client.post(
        "/api/v1/schools",
        json={"name": "Escola Modelo", "document": "123"},
        headers=_auth(admin_token),
    )
    assert school.status_code == 201, school.text
    school_id = school.json()["id"]

    guardian_user = client.post(
        "/api/v1/auth/users",
        json={
            "name": "Responsavel",
            "email": "guardian@example.com",
            "password": "strong-password",
            "role": "guardian",
            "school_id": None,
        },
        headers=_auth(admin_token),
    )
    assert guardian_user.status_code == 201, guardian_user.text
    guardian_id = guardian_user.json()["id"]

    child = client.post(
        "/api/v1/children",
        json={
            "full_name": "Crianca Teste",
            "birth_date": "2018-01-01",
            "school_id": school_id,
            "class_name": "1A",
        },
        headers=_auth(admin_token),
    )
    assert child.status_code == 201, child.text
    child_id = child.json()["id"]

    link = client.post(
        "/api/v1/child-guardians",
        json={
            "child_id": child_id,
            "guardian_id": guardian_id,
            "relationship_type": "mae",
            "can_view": True,
            "can_manage_routine": False,
            "can_mark_notifications": True,
        },
        headers=_auth(admin_token),
    )
    assert link.status_code == 201, link.text

    guardian_login = client.post(
        "/api/v1/auth/login",
        data={"username": "guardian@example.com", "password": "strong-password"},
    )
    assert guardian_login.status_code == 200, guardian_login.text
    guardian_token = guardian_login.json()["access_token"]

    children = client.get("/api/v1/children", headers=_auth(guardian_token))
    assert children.status_code == 200, children.text
    assert [item["id"] for item in children.json()] == [child_id]

    routine = client.post(
        "/api/v1/routines",
        json={
            "child_id": child_id,
            "title": "Estudar leitura",
            "description": "Atividade de leitura",
            "scheduled_time": "13:00:00",
            "weekdays": [0, 1, 2, 3, 4],
            "target_audience": "child",
        },
        headers=_auth(guardian_token),
    )
    assert routine.status_code == 403

