# Verifies /auth/me and /auth/refresh actually authenticate the caller
# via a verified JWT, rather than trusting mere cookie presence and
# always returning the hardcoded first user (the bug this replaces).

from fastapi.testclient import TestClient

from config.config import settings

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
ME_URL = f"{settings.API_V1_STR}/auth/me"
REFRESH_URL = f"{settings.API_V1_STR}/auth/refresh"

# All three fake_users_db entries share this password (see
# features/users/api.py's fake_hashed_password comment).
PASSWORD = "password"


def _login_and_get_tokens(client: TestClient, email: str) -> dict:
    # The login cookies are Secure, so TestClient's cookie jar won't
    # re-attach them to a follow-up request against the http://testserver
    # test transport (that mismatch is the real, separately-tracked P0
    # step 4 gap -- cookie flags aren't environment-conditional yet).
    # Reading the values back out and setting them on the jar directly
    # (rather than letting the jar capture them from the Secure
    # Set-Cookie header itself) sidesteps that, so this test verifies
    # only what P0 step 3 actually changed: real JWT verification.
    response = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.json()
    return {
        "accessToken": response.cookies["accessToken"],
        "refreshToken": response.cookies["refreshToken"],
    }


def test_me_returns_the_actual_logged_in_user_not_always_admin(client: TestClient):
    tokens = _login_and_get_tokens(client, "manager@example.com")
    client.cookies.set("accessToken", tokens["accessToken"])

    response = client.get(ME_URL)

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "manager@example.com"
    # Regression guard for the bug this replaces: /me used to always
    # return fake_users_db[0] (the admin) no matter who logged in.
    assert response.json()["data"]["user"]["email"] != "admin@example.com"
    client.cookies.clear()


def test_refresh_returns_the_actual_logged_in_user_not_always_admin(client: TestClient):
    tokens = _login_and_get_tokens(client, "user@example.com")
    client.cookies.set("refreshToken", tokens["refreshToken"])

    response = client.post(REFRESH_URL)

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
    client.cookies.set("accessToken", "not-a-real-jwt")
    response = client.get(ME_URL)
    assert response.status_code == 401
    assert (
        response.json()["error"]["message"] == "Your session is invalid or has expired."
    )
    client.cookies.clear()


def test_refresh_without_cookie_is_401(client: TestClient):
    client.cookies.clear()
    response = client.post(REFRESH_URL)
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Authentication is required."


def test_refresh_with_tampered_cookie_is_401(client: TestClient):
    client.cookies.clear()
    client.cookies.set("refreshToken", "not-a-real-jwt")
    response = client.post(REFRESH_URL)
    assert response.status_code == 401
    assert (
        response.json()["error"]["message"] == "Your session is invalid or has expired."
    )
    client.cookies.clear()


def test_safe_user_never_leaks_hashed_password(client: TestClient):
    tokens = _login_and_get_tokens(client, "admin@example.com")
    client.cookies.set("accessToken", tokens["accessToken"])
    response = client.get(ME_URL)
    assert "hashed_password" not in response.json()["data"]["user"]
    client.cookies.clear()
