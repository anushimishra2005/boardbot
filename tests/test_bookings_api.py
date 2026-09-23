from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from uuid import uuid4
from api.main import app


client = TestClient(app)


def get_auth_token():
    response = client.post(
        "/auth/login",
        json={
            "email": "anushi@example.com",
            "password": "demo-password",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_booking_api():
    token = get_auth_token()

    start_time = datetime(
        2099,
        12,
        16,
        14,
        0,
        0,
        0,
    )
    end_time = start_time + timedelta(hours=1)

    response = client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "room_id": 1,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attendees": 4,
        },
    )

    print("API RESPONSE:", response.status_code, response.json())
    assert response.status_code == 201

    data = response.json()

    assert data["room_id"] == 1
    assert data["attendees"] == 4
    assert "id" in data

    booking_id = data["id"]

    delete_response = client.delete(
        f"/bookings/{booking_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert delete_response.status_code in (200, 204)