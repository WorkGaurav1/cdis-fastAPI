# Verifies CORS origins are configurable via Settings.CORS_ORIGINS
# rather than hardcoded, and that the configured middleware actually
# reflects an allowed origin back on a real request.

from config.config import Settings


def test_cors_origins_list_parses_comma_separated_string():
    settings = Settings(
        SECRET_KEY="test-only-secret-not-used-for-anything-real",
        DATABASE_URL="mysql+pymysql://t:t@localhost/t",
        CORS_ORIGINS="https://a.example.com, https://b.example.com,https://c.example.com",
    )
    assert settings.cors_origins_list == [
        "https://a.example.com",
        "https://b.example.com",
        "https://c.example.com",
    ]


def test_cors_origins_default_covers_local_dev_ports():
    settings = Settings(
        SECRET_KEY="test-only-secret-not-used-for-anything-real",
        DATABASE_URL="mysql+pymysql://t:t@localhost/t",
    )
    assert "http://localhost:3000" in settings.cors_origins_list
    assert "http://localhost:5173" in settings.cors_origins_list


def test_cors_middleware_reflects_a_configured_origin(client):
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    )


def test_cors_middleware_rejects_an_unconfigured_origin(client):
    response = client.get(
        "/health", headers={"Origin": "https://not-an-allowed-origin.example.com"}
    )
    assert "access-control-allow-origin" not in response.headers
