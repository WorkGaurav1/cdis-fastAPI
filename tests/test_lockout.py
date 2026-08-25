# Verifies account lockout (features/auth/service.py::authenticate_user),
# mirroring authService.login()'s exact behavior: lockout triggers after
# LOCKOUT_MAX_ATTEMPTS consecutive failures, the lockout check runs
# *before* password verification (so a correct password during the
# window still fails, with 403 not 401), and a successful login resets
# the counter.

from fastapi.testclient import TestClient

from app.limiter import limiter
from config.config import settings
from features.users.repository import get_user_by_email

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
REGISTER_URL = f"{settings.API_V1_STR}/auth/register"

CORRECT_PASSWORD = "a-correct-password"


def _register_fresh_user(client: TestClient, email: str) -> None:
    # A dedicated user per test, isolated from the shared
    # admin/manager/user accounts other test files also log in as
    # (the test DB is shared across the whole session).
    response = client.post(
        REGISTER_URL,
        json={"email": email, "name": "Lockout Test", "password": CORRECT_PASSWORD},
    )
    assert response.status_code == 201, response.json()
    client.cookies.clear()


def test_account_locks_after_max_failed_attempts(client: TestClient, db_session):
    _register_fresh_user(client, "lockout-1@example.com")

    for _ in range(settings.LOCKOUT_MAX_ATTEMPTS):
        response = client.post(
            LOGIN_URL, json={"email": "lockout-1@example.com", "password": "wrong"}
        )
        assert response.status_code == 401

    user = get_user_by_email(db_session, "lockout-1@example.com")
    assert user.failed_login_attempts == settings.LOCKOUT_MAX_ATTEMPTS
    assert user.locked_until is not None


def test_correct_password_during_lockout_still_gets_403(client: TestClient):
    _register_fresh_user(client, "lockout-2@example.com")

    for _ in range(settings.LOCKOUT_MAX_ATTEMPTS):
        client.post(
            LOGIN_URL, json={"email": "lockout-2@example.com", "password": "wrong"}
        )

    # The rate limiter (5/minute) and LOCKOUT_MAX_ATTEMPTS (5) happen to
    # be the same number -- reset it explicitly so this next request
    # tests lockout, not the rate limiter.
    limiter.reset()

    response = client.post(
        LOGIN_URL,
        json={"email": "lockout-2@example.com", "password": CORRECT_PASSWORD},
    )

    assert response.status_code == 403
    assert response.json()["error"]["message"] == (
        "This account is temporarily locked due to repeated failed "
        "sign-in attempts. Please try again later."
    )


def test_successful_login_resets_failed_attempts(client: TestClient, db_session):
    _register_fresh_user(client, "lockout-3@example.com")

    # Two failures -- below the lockout threshold.
    client.post(LOGIN_URL, json={"email": "lockout-3@example.com", "password": "wrong"})
    client.post(LOGIN_URL, json={"email": "lockout-3@example.com", "password": "wrong"})

    user = get_user_by_email(db_session, "lockout-3@example.com")
    assert user.failed_login_attempts == 2

    response = client.post(
        LOGIN_URL,
        json={"email": "lockout-3@example.com", "password": CORRECT_PASSWORD},
    )
    assert response.status_code == 200

    db_session.refresh(user)
    assert user.failed_login_attempts == 0
    assert user.locked_until is None
    client.cookies.clear()
