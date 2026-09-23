from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_login_success():
    response = client.post(
        "/auth/login",
        json={
            "email": "anushi@example.com",
            "password": "demo-password",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_rejects_invalid_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "anushi@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_rejects_unknown_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "does-not-exist@example.com",
            "password": "demo-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."