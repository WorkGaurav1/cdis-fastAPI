import pytest
from fastapi.testclient import TestClient

from app.limiter import limiter
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    # slowapi's Limiter keeps its hit counters in process-global storage,
    # not per-TestClient -- without a reset, tests across different
    # files/modules that each hit a rate-limited endpoint (e.g.
    # POST /auth/login, all sharing the same "testclient" IP key) starve
    # each other out with real 429s as the suite grows, unrelated to
    # what any individual test is actually checking.
    limiter.reset()
    yield


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
