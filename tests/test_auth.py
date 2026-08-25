# Verifies /auth/me and /auth/refresh actually authenticate the caller
# via a verified JWT, rather than trusting mere cookie presence and
# always returning the hardcoded first user (the bug this replaces).
#
# /auth/refresh and /auth/logout also require a valid double-submit
# CSRF header (see tests/test_csrf.py for the dedicated CSRF checks) --
# tests below that exercise those two endpoints send a matching
# X-CSRF-Token header so they can isolate the JWT/auth behavior they're
# actually testing.

from fastapi.testclient import TestClient

from config.config import settings
from features.auth.cookies import CSRF_HEADER

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
ME_URL = f"{settings.API_V1_STR}/auth/me"
REFRESH_URL = f"{settings.API_V1_STR}/auth/refresh"
LOGOUT_URL = f"{settings.API_V1_STR}/auth/logout"

# All three fake_users_db entries share this password (see
# features/users/api.py's fake_hashed_password comment).
PASSWORD = "password"


def _login_and_get_tokens(client: TestClient, email: str) -> dict:
    # Cookies are Secure outside "development"/"test" (see
    # features/auth/cookies.py), but the test suite runs with the
    # default ENVIRONMENT=development, so TestClient's cookie jar does
    # attach them to follow-up requests here. Still reading the values
    # back explicitly and setting them per-test keeps each test isolated
    # (module-scoped client, shared cookie jar across tests otherwise).
    response = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.json()
    return {
        "access_token": response.cookies["access_token"],
        "refresh_token": response.cookies["refresh_token"],
        "csrf_token": response.cookies["csrf_token"],
    }


def test_login_issues_access_refresh_and_csrf_cookies(client: TestClient):
    response = client.post(
        LOGIN_URL, json={"email": "admin@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200
    assert set(response.cookies.keys()) >= {
        "access_token",
        "refresh_token",
        "csrf_token",
    }
    client.cookies.clear()


def test_me_returns_the_actual_logged_in_user_not_always_admin(client: TestClient):
    tokens = _login_and_get_tokens(client, "manager@example.com")
    client.cookies.set("access_token", tokens["access_token"])

    response = client.get(ME_URL)

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "manager@example.com"
    # Regression guard for the bug this replaces: /me used to always
    # return fake_users_db[0] (the admin) no matter who logged in.
    assert response.json()["data"]["user"]["email"] != "admin@example.com"
    client.cookies.clear()


def test_refresh_returns_the_actual_logged_in_user_not_always_admin(client: TestClient):
    tokens = _login_and_get_tokens(client, "user@example.com")
    client.cookies.set("refresh_token", tokens["refresh_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "user@example.com"
    client.cookies.clear()


def test_me_without_cookie_is_401(client: TestClient):
    client.cookies.clear()
    response = client.get(ME_URL)
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Authentication is required."


def test_me_with_tampered_cookie_is_401(client: TestClient):
    client.cookies.clear()
    client.cookies.set("access_token", "not-a-real-jwt")
    response = client.get(ME_URL)
    assert response.status_code == 401
    assert (
        response.json()["error"]["message"] == "Your session is invalid or has expired."
    )
    client.cookies.clear()


def test_refresh_without_cookie_is_401(client: TestClient):
    # Valid CSRF pair but no refresh_token cookie -- isolates the
    # "no refresh token" 401 from the CSRF check (which runs first, and
    # has its own dedicated tests in tests/test_csrf.py).
    tokens = _login_and_get_tokens(client, "admin@example.com")
    client.cookies.clear()
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Authentication is required."
    client.cookies.clear()


def test_refresh_with_unknown_token_is_401(client: TestClient):
    # Refresh tokens are opaque, DB-backed values now (not JWTs) -- see
    # tests/test_refresh_rotation.py for the full rotation/reuse-
    # detection lifecycle. This just proves a value that was never
    # actually issued is rejected the same way Node's authService.refresh
    # rejects a token with no matching tokenHash row.
    tokens = _login_and_get_tokens(client, "admin@example.com")
    client.cookies.clear()
    client.cookies.set("refresh_token", "never-issued-by-this-server")
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 401
    assert (
        response.json()["error"]["message"] == "Invalid session. Please sign in again."
    )
    client.cookies.clear()


def test_safe_user_never_leaks_hashed_password(client: TestClient):
    tokens = _login_and_get_tokens(client, "admin@example.com")
    client.cookies.set("access_token", tokens["access_token"])
    response = client.get(ME_URL)
    assert "hashed_password" not in response.json()["data"]["user"]
    client.cookies.clear()


def test_logout_clears_all_three_auth_cookies(client: TestClient):
    tokens = _login_and_get_tokens(client, "admin@example.com")

    response = client.post(LOGOUT_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 200
    set_cookie_headers = response.headers.get_list("set-cookie")
    cleared_names = {h.split("=", 1)[0] for h in set_cookie_headers}
    assert cleared_names == {"access_token", "refresh_token", "csrf_token"}
    for header in set_cookie_headers:
        assert "Max-Age=0" in header or "01 Jan 1970" in header
    client.cookies.clear()


def test_logout_without_auth_is_401(client: TestClient):
    # Node's route wiring is requireAuth then requireCsrfToken -- without
    # a valid access_token, logout must 401 even with a fully valid CSRF
    # pair, matching the equivalent check on /auth/me.
    tokens = _login_and_get_tokens(client, "admin@example.com")
    client.cookies.clear()
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(LOGOUT_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 401
    client.cookies.clear()
