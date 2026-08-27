import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.limiter import limiter
from app.main import app
from config.database import engine as real_engine
from config.database import get_session
from scripts.seed import DEFAULT_USERS
from scripts.seed import _seed_demo_data as seed_demo_data
from scripts.seed import _seed_roles_and_permissions as seed_roles_and_permissions
from scripts.seed import _seed_users as seed_users

# TEST_DB_BACKEND=mysql (set by CI's integration-test job, see
# .github/workflows/lint-and-test.yml) runs this exact same suite
# against a real, Alembic-migrated MySQL service container instead of
# SQLite -- covering MySQL-specific behavior (collation, JSON columns,
# real FK enforcement, real datetime precision) that SQLite can't, the
# same role a MySQL service container plays in the Node backend's CI.
# Defaults to SQLite so local `pytest` stays fast and needs no live
# database server.
TEST_DB_BACKEND = os.environ.get("TEST_DB_BACKEND", "sqlite")

if TEST_DB_BACKEND == "mysql":
    # config.database.engine is already built from settings.DATABASE_URL
    # (pointed at the real service container by CI) -- no
    # dependency_override needed; requests hit it directly, the same
    # way they would in production.
    test_engine = real_engine
else:
    # In-memory SQLite for the whole test session -- a real
    # engine/session, exercising the same repository code the running
    # app uses, without requiring a live MySQL server.
    #
    # StaticPool keeps a single connection alive for the engine's
    # lifetime: SQLite's default behavior for the special ":memory:"/""
    # database is one throwaway DB *per connection*, so without it every
    # new session would see an empty, unrelated database.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    def _override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    # Reuses the exact same seed logic (roles/permissions/default users,
    # scripts/seed.py) the real app is seeded with -- so tests never
    # drift from what a real deployment actually has, and admin/manager/
    # user's role-gated behavior (e.g. GET /users needing users:read) is
    # real, not a test-only fixture guess. Idempotent either way, so
    # re-seeding a MySQL instance CI already seeded is a safe no-op.
    if TEST_DB_BACKEND == "sqlite":
        SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        seed_roles_and_permissions(session)
        seed_users(session)
        seed_demo_data(session)
    yield
    if TEST_DB_BACKEND == "sqlite":
        SQLModel.metadata.drop_all(test_engine)
    # Real MySQL is never dropped here -- it's CI's ephemeral service
    # container (or a developer's own local instance), torn down (or
    # not) by whatever started it, not by the test suite.


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


@pytest.fixture
def db_session():
    # For tests that exercise the repository layer directly rather than
    # going through the HTTP client. Deliberately not imported by test
    # modules as `from tests.conftest import test_engine` -- pytest's
    # rootless import mode (no tests/__init__.py) would load conftest.py
    # a second time under a different module name in that case, handing
    # back a second, empty SQLite engine instead of the seeded one.
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def default_user_emails() -> set[str]:
    return {entry["email"] for entry in DEFAULT_USERS}
