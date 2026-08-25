# Verifies the real refresh-token lifecycle (features/auth/service.py),
# mirroring the Node backend's own integration test coverage for this
# exact flow (routes/auth.integration.test.ts): rotate -> old token now
# rejected -> reuse revokes the whole chain for that user.

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from config.config import settings
from features.auth.cookies import CSRF_HEADER
from features.auth.repository import get_refresh_token_by_hash
from features.auth.security import hash_refresh_token
from features.users.repository import get_user_by_email

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
REFRESH_URL = f"{settings.API_V1_STR}/auth/refresh"
ME_URL = f"{settings.API_V1_STR}/auth/me"

PASSWORD = "password"


def _login(client: TestClient, email: str = "admin@example.com") -> dict:
    response = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.json()
    return {
        "access_token": response.cookies["access_token"],
        "refresh_token": response.cookies["refresh_token"],
        "csrf_token": response.cookies["csrf_token"],
    }


def _use_tokens(client: TestClient, tokens: dict) -> None:
    client.cookies.clear()
    client.cookies.set("access_token", tokens["access_token"])
    client.cookies.set("refresh_token", tokens["refresh_token"])
    client.cookies.set("csrf_token", tokens["csrf_token"])


def test_refresh_issues_a_new_distinct_token_pair(client: TestClient):
    tokens = _login(client)
    _use_tokens(client, tokens)

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 200
    new_refresh_token = response.cookies["refresh_token"]
    new_access_token = response.cookies["access_token"]
    # Regression guard for the bug this whole step replaces: refresh_token
    # used to literally equal access_token, and refresh() never issued
    # anything new at all. (Not asserting the new access token's string
    # differs from the old one: JWT signing is deterministic given the
    # same payload/exp, and exp only has second granularity, so two
    # tokens issued for the same user within the same second can be
    # byte-identical -- that's expected, not a bug.)
    assert new_refresh_token != tokens["refresh_token"]
    assert new_refresh_token != new_access_token
    client.cookies.clear()


def test_rotated_token_cannot_be_used_again(client: TestClient):
    tokens = _login(client)
    _use_tokens(client, tokens)

    first = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})
    assert first.status_code == 200

    # Re-present the *original* (now-rotated-away) refresh_token cookie.
    _use_tokens(client, tokens)
    second = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert second.status_code == 401
    assert (
        second.json()["error"]["message"]
        == "This session is no longer valid. Please sign in again."
    )
    client.cookies.clear()


def test_reusing_a_rotated_token_revokes_every_active_session_for_that_user(
    client: TestClient, db_session: Session
):
    # Two independent logins for the same user (e.g. two browser tabs),
    # each with their own refresh token.
    session_a = _login(client)
    session_b = _login(client)

    # Rotate session A once, then try to reuse the now-stale original --
    # this should be treated as theft and kill session B too, not just A.
    _use_tokens(client, session_a)
    rotated = client.post(REFRESH_URL, headers={CSRF_HEADER: session_a["csrf_token"]})
    assert rotated.status_code == 200

    _use_tokens(client, session_a)
    reuse_attempt = client.post(
        REFRESH_URL, headers={CSRF_HEADER: session_a["csrf_token"]}
    )
    assert reuse_attempt.status_code == 401

    # Session B's refresh token, though never itself reused, must now be
    # revoked too -- the whole chain for this user was killed.
    _use_tokens(client, session_b)
    session_b_attempt = client.post(
        REFRESH_URL, headers={CSRF_HEADER: session_b["csrf_token"]}
    )
    assert session_b_attempt.status_code == 401
    assert (
        session_b_attempt.json()["error"]["message"]
        == "This session is no longer valid. Please sign in again."
    )
    client.cookies.clear()


def test_expired_refresh_token_is_401(client: TestClient, db_session: Session):
    tokens = _login(client)
    user = get_user_by_email(db_session, "admin@example.com")
    stored = get_refresh_token_by_hash(
        db_session, hash_refresh_token(tokens["refresh_token"])
    )
    assert stored is not None
    assert stored.user_id == user.id

    # Backdate it past expiry directly, the same way a real token would
    # eventually age out.
    stored.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=1
    )
    db_session.add(stored)
    db_session.commit()

    _use_tokens(client, tokens)
    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 401
    assert (
        response.json()["error"]["message"]
        == "Your session has expired. Please sign in again."
    )
    client.cookies.clear()


def test_logout_revokes_the_refresh_token_so_it_cannot_be_refreshed_after(
    client: TestClient,
):
    tokens = _login(client)
    _use_tokens(client, tokens)

    logout_response = client.post(
        f"{settings.API_V1_STR}/auth/logout",
        headers={CSRF_HEADER: tokens["csrf_token"]},
    )
    assert logout_response.status_code == 200

    # The access_token cookie was cleared by logout, but even restoring
    # just the (now-revoked) refresh_token + a valid CSRF pair must fail.
    client.cookies.clear()
    client.cookies.set("refresh_token", tokens["refresh_token"])
    client.cookies.set("csrf_token", tokens["csrf_token"])
    refresh_after_logout = client.post(
        REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]}
    )

    assert refresh_after_logout.status_code == 401
    client.cookies.clear()
