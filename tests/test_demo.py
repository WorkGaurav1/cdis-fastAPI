# Verifies GET /api/v1/demo/map/states requires authentication, mirroring
# Node's requireAuth guard on the demo routes (open to any signed-in
# user, no specific permission).

from fastapi.testclient import TestClient

from config.config import settings

MAP_STATES_URL = f"{settings.API_V1_STR}/demo/map/states"
LOGIN_URL = f"{settings.API_V1_STR}/auth/login"


def test_demo_map_states_requires_authentication(client: TestClient):
    client.cookies.clear()
    response = client.get(MAP_STATES_URL)
    assert response.status_code == 401
    client.cookies.clear()


def test_demo_map_states_returns_data_once_authenticated(client: TestClient):
    login = client.post(
        LOGIN_URL, json={"email": "admin@example.com", "password": "password"}
    )
    assert login.status_code == 200

    response = client.get(MAP_STATES_URL)

    assert response.status_code == 200
    assert len(response.json()["data"]["states"]) > 0
    client.cookies.clear()
