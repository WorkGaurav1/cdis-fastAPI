# Verifies the global error handlers registered in
# src/utils/error_handlers.py produce the app's standard
# {success:false,error:{code,message}} envelope on every error path,
# matching back-end/src/utils/apiResponse.ts's contract.

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.config import settings


def test_http_exception_uses_error_envelope(client: TestClient):
    # POST /auth/login with wrong credentials raises a plain HTTPException(401).
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "nobody@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "error": {"code": "UNAUTHORIZED", "message": "Invalid username or password"},
    }


def test_validation_error_uses_error_envelope(client: TestClient):
    # Missing required "password" field triggers Pydantic request validation (422).
    response = client.post(
        f"{settings.API_V1_STR}/auth/login", json={"email": "nobody@example.com"}
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "password" in body["error"]["message"]


def test_not_found_route_uses_error_envelope(client: TestClient):
    # FastAPI/Starlette's automatic 404 for an unmatched route is a
    # Starlette HTTPException too, so it goes through the same handler.
    response = client.get(f"{settings.API_V1_STR}/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_unhandled_exception_uses_error_envelope():
    # Build a throwaway app with a route that raises a plain, unexpected
    # exception, to prove the Exception-level handler produces the safe,
    # generic 500 envelope rather than leaking internals. Uses its own
    # TestClient with raise_server_exceptions=False since Starlette's
    # ServerErrorMiddleware always re-raises after generating the
    # response (so the real running server sends the JSON response; a
    # default TestClient would otherwise propagate the exception in-test).
    from utils.error_handlers import register_error_handlers

    boom_app = FastAPI()
    register_error_handlers(boom_app)

    @boom_app.get("/boom")
    def boom():
        raise RuntimeError("something exploded internally")

    with TestClient(boom_app, raise_server_exceptions=False) as boom_client:
        response = boom_client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Something went wrong. Please try again later.",
        },
    }
