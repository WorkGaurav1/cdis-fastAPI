# Verifies POST /auth/register, mirroring Node's registerSchema
# contract (src/data-transfer-object/auth.dto.ts) and register() flow
# (src/services/auth.service.ts).

from fastapi.testclient import TestClient

from config.config import settings
from features.users.repository import get_user_by_email

REGISTER_URL = f"{settings.API_V1_STR}/auth/register"


def test_register_creates_a_real_user_and_issues_cookies(
    client: TestClient, db_session
):
    response = client.post(
        REGISTER_URL,
        json={
            "email": "new-registrant@example.com",
            "name": "New Registrant",
            "password": "a-strong-password",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["user"]["email"] == "new-registrant@example.com"
    assert body["data"]["user"]["name"] == "New Registrant"
    assert "hashed_password" not in body["data"]["user"]
    assert set(response.cookies.keys()) >= {
        "access_token",
        "refresh_token",
        "csrf_token",
    }

    persisted = get_user_by_email(db_session, "new-registrant@example.com")
    assert persisted is not None
    assert persisted.hashed_password != "a-strong-password"  # never stored raw

    client.cookies.clear()


def test_register_duplicate_email_is_409(client: TestClient):
    payload = {
        "email": "duplicate-registrant@example.com",
        "name": "First",
        "password": "a-strong-password",
    }
    first = client.post(REGISTER_URL, json=payload)
    assert first.status_code == 201
    client.cookies.clear()

    second = client.post(REGISTER_URL, json={**payload, "name": "Second"})

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CONFLICT"
    assert (
        second.json()["error"]["message"]
        == "An account with this email already exists."
    )
    client.cookies.clear()


def test_register_password_too_short_is_422(client: TestClient):
    response = client.post(
        REGISTER_URL,
        json={
            "email": "short-password@example.com",
            "name": "Someone",
            "password": "short",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_register_empty_name_is_422(client: TestClient):
    response = client.post(
        REGISTER_URL,
        json={
            "email": "empty-name@example.com",
            "name": "   ",
            "password": "a-strong-password",
        },
    )
    assert response.status_code == 422


def test_register_trims_email_and_name(client: TestClient, db_session):
    response = client.post(
        REGISTER_URL,
        json={
            "email": "  padded-email@example.com  ",
            "name": "  Padded Name  ",
            "password": "a-strong-password",
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["user"]["email"] == "padded-email@example.com"
    assert response.json()["data"]["user"]["name"] == "Padded Name"

    persisted = get_user_by_email(db_session, "padded-email@example.com")
    assert persisted is not None
    client.cookies.clear()
