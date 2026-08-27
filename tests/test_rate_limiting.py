# Verifies the two rate-limiting behaviors added to close the P1 step 16
# gap: a global baseline limiter across all routes (was: only /auth/login
# had any throttling), and /auth/login's limiter keyed by IP + attempted
# email rather than IP alone (mirrors src/middlewares/rateLimiters.ts's
# loginRateLimiter exactly).

from fastapi.testclient import TestClient

from app.limiter import limiter
from config.config import settings

LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
HEALTH_URL = "/health"


def test_login_rate_limit_is_keyed_by_email_not_just_ip(client: TestClient):
    # Exhaust the login limiter (10/15min) against one email...
    for _ in range(10):
        client.post(
            LOGIN_URL, json={"email": "rl-victim-a@example.com", "password": "wrong"}
        )

    exhausted = client.post(
        LOGIN_URL, json={"email": "rl-victim-a@example.com", "password": "wrong"}
    )
    assert exhausted.status_code == 429
    # Regression guard: slowapi's own default 429 handler returns
    # {"error": "..."}, not this app's {success,error} envelope.
    assert exhausted.json()["success"] is False
    assert exhausted.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    # ...a different email from the same IP (same TestClient) must not
    # be affected -- if the key were IP-only, this would also be 429.
    other_email = client.post(
        LOGIN_URL, json={"email": "rl-victim-b@example.com", "password": "wrong"}
    )
    assert other_email.status_code != 429


def test_global_baseline_limiter_applies_to_a_route_with_no_own_limit(
    client: TestClient,
):
    # /health has no route-specific @limiter.limit() of its own -- only
    # the global default_limits (100/15min, app/limiter.py) protects it.
    # 101 requests: 100 should succeed, the 101st must be throttled.
    for _ in range(100):
        response = client.get(HEALTH_URL)
        assert response.status_code == 200

    throttled = client.get(HEALTH_URL)
    assert throttled.status_code == 429

    limiter.reset()
