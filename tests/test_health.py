# Verifies GET /health, mirroring Node's src/controllers/health.controller.ts
# exactly: a real readiness probe (actually queries the DB), wrapped in
# the app's standard {success,data} envelope, not a liveness-only ping.

from fastapi.testclient import TestClient

from app.main import app, get_session


def test_health_check_returns_ok_with_uptime_and_timestamp(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert isinstance(body["data"]["uptimeSeconds"], int)
    assert body["data"]["uptimeSeconds"] >= 0
    assert "timestamp" in body["data"]


def test_health_check_is_actually_db_backed_not_a_liveness_only_ping(
    client: TestClient,
):
    # Regression guard for the bug this replaces: the old /health never
    # touched the database at all, so a DB outage wouldn't be reflected
    # in the health status. Swap in a session dependency that raises,
    # the same way a real DB outage would surface through SQLAlchemy,
    # and confirm that turns into a 500 (via the global exception
    # handler) rather than a false "ok".
    def _broken_session():
        raise ConnectionError("simulated database outage")
        yield  # pragma: no cover - makes this a generator, never reached

    # Capture (rather than re-import) conftest.py's real override:
    # `from tests.conftest import ...` here would load conftest.py a
    # second time under a different module name in pytest's rootless
    # import mode (no tests/__init__.py), handing back a second, empty
    # SQLite engine -- the same pitfall tests/test_users_db.py's
    # db_session fixture comment documents.
    real_override = app.dependency_overrides[get_session]
    app.dependency_overrides[get_session] = _broken_session
    try:
        # raise_server_exceptions=False: TestClient's default propagates
        # unhandled exceptions in-test rather than converting them to
        # the 500 response a real running server would send (see
        # test_error_handlers.py's identical workaround for this).
        with TestClient(app, raise_server_exceptions=False) as broken_client:
            response = broken_client.get("/health")
    finally:
        app.dependency_overrides[get_session] = real_override

    assert response.status_code == 500
    assert response.json()["success"] is False
