from fastapi.testclient import TestClient
from config.config import settings

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_user(client: TestClient):
    data = {"email": "test@example.com", "password": "password123"}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["email"] == data["email"]
    assert "id" in content
