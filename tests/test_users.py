from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# NOTE: there used to be a test_create_user here, asserting
# POST /api/v1/users/ returns 201 -- but that route was never actually
# defined on the users router (only GET "" is), so the test could never
# have passed against the real app. Node has no such endpoint either:
# user creation happens through POST /auth/register (tests/test_register.py),
# which is what this template's own users:write-adjacent flow actually
# is. Removed rather than "fixed" by inventing a non-Node-parity route
# just to make a stale test green.
