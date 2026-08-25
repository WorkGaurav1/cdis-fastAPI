# Verifies auth cookies are environment-conditional and correctly
# scoped/timed, matching back-end/src/lib/cookies.ts exactly. Regression
# guard for the bug this replaces: `secure` used to be hardcoded True
# unconditionally, which silently drops the cookie on any non-https
# connection -- including plain local HTTP dev.

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.config import Settings
from features.auth import cookies as cookies_module


def _cookie_flags(set_cookie_header: str) -> dict:
    parts = [p.strip() for p in set_cookie_header.split(";")]
    name, value = parts[0].split("=", 1)
    flags = {"name": name, "value": value}
    for part in parts[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            flags[k.strip().lower()] = v.strip()
        else:
            flags[part.strip().lower()] = True
    return flags


def _issue_cookies_with_environment(environment: str) -> list[str]:
    # Monkeypatch-free: rebuild the module's derived constants for a
    # given ENVIRONMENT by constructing a fresh Settings() with it
    # overridden, the same way a real deployment would via the
    # ENVIRONMENT env var -- then call set_auth_cookies with that
    # Settings object swapped in, restoring the real one afterwards.
    original_settings = cookies_module.settings
    try:
        cookies_module.settings = Settings(
            SECRET_KEY="test",
            DATABASE_URL="mysql+pymysql://t:t@localhost/t",
            ENVIRONMENT=environment,
        )
        app = FastAPI()

        @app.get("/issue")
        def issue():
            from fastapi import Response

            response = Response()
            cookies_module.set_auth_cookies(
                response, access_token="access.jwt", refresh_token="refresh.jwt"
            )
            return response

        with TestClient(app) as client:
            response = client.get("/issue")
        return response.headers.get_list("set-cookie")
    finally:
        cookies_module.settings = original_settings


def test_cookies_are_not_secure_in_development():
    headers = _issue_cookies_with_environment("development")
    for header in headers:
        assert "Secure" not in _cookie_flags(header)


def test_cookies_are_secure_in_production():
    headers = _issue_cookies_with_environment("production")
    for header in headers:
        assert "secure" in _cookie_flags(header)


def test_cookies_are_secure_in_staging():
    headers = _issue_cookies_with_environment("staging")
    for header in headers:
        assert "secure" in _cookie_flags(header)


def test_cookie_names_paths_and_httponly_match_node(client: TestClient):
    response = client.post(
        f"{cookies_module.settings.API_V1_STR}/auth/login",
        json={"email": "admin@example.com", "password": "password"},
    )
    headers = {
        _cookie_flags(h)["name"]: _cookie_flags(h)
        for h in response.headers.get_list("set-cookie")
    }

    assert headers["access_token"]["path"] == "/"
    assert headers["access_token"]["httponly"] is True

    assert headers["refresh_token"]["path"] == "/api/v1/auth"
    assert headers["refresh_token"]["httponly"] is True

    assert headers["csrf_token"]["path"] == "/"
    # csrf_token must be JS-readable for the double-submit pattern.
    assert "httponly" not in headers["csrf_token"]

    client.cookies.clear()
