# Verifies GET /api/v1/users and the users repository/mapper are backed
# by a real SQLModel session -- not the old fake_users_db in-memory list
# this replaces.

from fastapi.testclient import TestClient
from sqlmodel import Session

from config.config import settings
from features.users.mapper import to_safe_user
from features.users.repository import (
    count_users,
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
)

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


# Pagination -- matches the Node backend's own paginationQuerySchema
# (back-end/src/data-transfer-object/pagination.dto.ts) exactly: same
# limit/offset param names, same bounds (limit 1-100 default 20, offset
# >=0 default 0), same `pagination: {limit, offset, total}` response
# shape. GET /api/v1/users used to return every row unbounded, in one
# query -- the same "won't survive production" finding the Node fix
# closed; this closes it here too, real rows against a real (SQLite,
# in this suite) database, not mocked.


def test_users_endpoint_bounds_the_page_to_the_requested_limit(
    client: TestClient, default_user_emails: set[str]
):
    _login(client)

    response = client.get(USERS_URL, params={"limit": 1, "offset": 0})

    assert response.status_code == 200
    assert len(response.json()["data"]["users"]) == 1
    # The real point of this endpoint: total reflects the whole
    # collection, not just this page.
    assert response.json()["data"]["pagination"]["total"] >= len(default_user_emails)
    client.cookies.clear()


def test_users_endpoint_offset_moves_the_window(client: TestClient):
    _login(client)

    page1 = client.get(USERS_URL, params={"limit": 1, "offset": 0})
    page2 = client.get(USERS_URL, params={"limit": 1, "offset": 1})

    assert (
        page1.json()["data"]["users"][0]["id"] != page2.json()["data"]["users"][0]["id"]
    )
    client.cookies.clear()


def test_users_endpoint_defaults_to_limit_20_offset_0(client: TestClient):
    _login(client)

    response = client.get(USERS_URL)

    assert response.json()["data"]["pagination"]["limit"] == 20
    assert response.json()["data"]["pagination"]["offset"] == 0
    client.cookies.clear()


def test_users_endpoint_rejects_an_out_of_range_limit(client: TestClient):
    _login(client)

    response = client.get(USERS_URL, params={"limit": 101})

    # 422, not Node's 400 -- FastAPI's own RequestValidationError
    # handler (utils/error_handlers.py), a pre-existing, intentional
    # divergence between the two backends' validation-error status
    # code, not something this fix changes.
    assert response.status_code == 422
    client.cookies.clear()


def test_count_users_matches_the_number_of_rows_list_users_can_page_through(
    db_session: Session,
):
    total = count_users(db_session)

    all_rows = list_users(db_session, offset=0, limit=total)

    assert len(all_rows) == total


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

    safe = to_safe_user(user, roles=["admin"], permissions=["users:read"])

    assert "hashed_password" not in safe
    assert safe["name"] == user.full_name
    assert safe["email"] == "admin@example.com"
    assert safe["roles"] == ["admin"]
    assert safe["permissions"] == ["users:read"]
