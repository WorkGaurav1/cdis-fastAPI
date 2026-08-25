# Verifies GET /api/v1/users and the users repository/mapper are backed
# by a real SQLModel session -- not the old fake_users_db in-memory list
# this replaces.

from fastapi.testclient import TestClient
from sqlmodel import Session

from config.config import settings
from features.users.mapper import to_safe_user
from features.users.repository import create_user, get_user_by_email, get_user_by_id

USERS_URL = f"{settings.API_V1_STR}/users"
LOGIN_URL = f"{settings.API_V1_STR}/auth/login"


def _login(client: TestClient) -> None:
    response = client.post(
        LOGIN_URL, json={"email": "admin@example.com", "password": "password"}
    )
    assert response.status_code == 200, response.json()


def test_users_endpoint_requires_authentication(client: TestClient):
    client.cookies.clear()
    response = client.get(USERS_URL)
    assert response.status_code == 401
    client.cookies.clear()


def test_users_endpoint_returns_the_seeded_db_rows_not_a_fake_list(
    client: TestClient, default_user_emails: set[str]
):
    _login(client)

    response = client.get(USERS_URL)

    assert response.status_code == 200
    emails = {u["email"] for u in response.json()["data"]["users"]}
    # >= rather than == : other tests in this session-scoped DB (e.g.
    # tests/test_register.py) legitimately add more rows over the
    # course of the suite -- what this test is actually verifying is
    # that the seeded rows are present and real, not that these three
    # are the *only* rows that will ever exist.
    assert emails >= default_user_emails
    client.cookies.clear()


def test_users_endpoint_never_leaks_hashed_password(client: TestClient):
    _login(client)
    response = client.get(USERS_URL)
    for user in response.json()["data"]["users"]:
        assert "hashed_password" not in user
    client.cookies.clear()


def test_create_user_persists_and_is_retrievable_by_email_and_id(db_session: Session):
    created = create_user(
        db_session,
        email="repo-test-user@example.com",
        hashed_password="irrelevant-for-this-test",
        full_name="Repo Test User",
    )
    assert created.id is not None

    by_email = get_user_by_email(db_session, "repo-test-user@example.com")
    assert by_email is not None
    assert by_email.id == created.id

    by_id = get_user_by_id(db_session, created.id)
    assert by_id is not None
    assert by_id.email == "repo-test-user@example.com"


def test_get_user_by_email_returns_none_for_unknown_email(db_session: Session):
    assert get_user_by_email(db_session, "nobody-like-this-exists@example.com") is None


def test_to_safe_user_strips_hashed_password_and_maps_full_name_to_name(
    db_session: Session,
):
    user = get_user_by_email(db_session, "admin@example.com")

    safe = to_safe_user(user)

    assert "hashed_password" not in safe
    assert safe["name"] == user.full_name
    assert safe["email"] == "admin@example.com"
    # Honest placeholders until P0 step 10 (RBAC tables) lands -- not
    # fabricated authorization data.
    assert safe["roles"] == []
    assert safe["permissions"] == []
