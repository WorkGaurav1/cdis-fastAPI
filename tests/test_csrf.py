# Verifies the double-submit CSRF check (features/auth/dependencies.py::
# require_csrf_token), mirroring back-end/src/middlewares/csrf.ts, on the
# two routes Node applies it to: /auth/refresh and /auth/logout.

from fastapi.testclient import TestClient

from config.config import settings
from features.auth.cookies import CSRF_HEADER

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
REFRESH_URL = f"{settings.API_V1_STR}/auth/refresh"
LOGOUT_URL = f"{settings.API_V1_STR}/auth/logout"

PASSWORD = "password"


def _login(client: TestClient) -> dict:
    response = client.post(
        LOGIN_URL, json={"email": "admin@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200, response.json()
    return {
        "access_token": response.cookies["access_token"],
        "refresh_token": response.cookies["refresh_token"],
        "csrf_token": response.cookies["csrf_token"],
    }


def test_refresh_without_csrf_header_is_403(client: TestClient):
    tokens = _login(client)
    client.cookies.clear()
    client.cookies.set("refresh_token", tokens["refresh_token"])
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(REFRESH_URL)  # no X-CSRF-Token header sent

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert response.json()["error"]["message"] == "Missing or invalid CSRF token."
    client.cookies.clear()


def test_refresh_with_mismatched_csrf_header_is_403(client: TestClient):
    tokens = _login(client)
    client.cookies.clear()
    client.cookies.set("refresh_token", tokens["refresh_token"])
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: "some-other-value"})

    assert response.status_code == 403
    client.cookies.clear()


def test_refresh_with_no_csrf_cookie_at_all_is_403(client: TestClient):
    # Attacker-controlled header with no corresponding cookie at all --
    # the whole point of double-submit is that an attacker can guess or
    # supply a header value, but can't read the victim's cookie to match it.
    tokens = _login(client)
    client.cookies.clear()
    client.cookies.set("refresh_token", tokens["refresh_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: "attacker-guess"})

    assert response.status_code == 403
    client.cookies.clear()


def test_refresh_with_matching_csrf_pair_passes(client: TestClient):
    tokens = _login(client)
    client.cookies.clear()
    client.cookies.set("refresh_token", tokens["refresh_token"])
    client.cookies.set("csrf_token", tokens["csrf_token"])

    response = client.post(REFRESH_URL, headers={CSRF_HEADER: tokens["csrf_token"]})

    assert response.status_code == 200
    client.cookies.clear()


def test_logout_without_csrf_header_is_403_even_when_authenticated(client: TestClient):
    _login(client)
    # access_token stays in the jar (login set it, ENVIRONMENT=development
    # so it isn't Secure-filtered) -- only the CSRF header is missing.

    response = client.post(LOGOUT_URL)

    assert response.status_code == 403
    assert response.json()["error"]["message"] == "Missing or invalid CSRF token."
    client.cookies.clear()


def test_logout_with_neither_auth_nor_csrf_is_401_not_403(client: TestClient):
    # Regression guard: logout's dependencies must resolve in Node's
    # order (auth checked before CSRF, src/routes/auth.routes.ts:
    # requireAuth, requireCsrfToken) so a request failing *both* checks
    # simultaneously gets 401 (who are you?), not 403 (you can't do
    # that). A route-level `dependencies=[Depends(require_csrf_token)]`
    # silently reverses this -- FastAPI resolves those before any
    # function-parameter Depends() regardless of declaration order --
    # so this is the one case that actually distinguishes the two
    # orderings; test_logout_without_auth_is_401 above sends a *valid*
    # CSRF pair and so can't catch it.
    client.cookies.clear()

    response = client.post(LOGOUT_URL)  # no cookies, no CSRF header at all

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    client.cookies.clear()
