import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.limiter import limiter
from app.main import app
from config.database import get_session
from features.auth.security import get_password_hash
from features.users.repository import create_user

# In-memory SQLite for the whole test session -- a real engine/session,
# exercising the same repository code the running app uses, without
# requiring a live MySQL server. A MySQL service container in CI (to
# additionally cover MySQL-specific behavior) is tracked separately as
# its own step (P2 item 24 of the gap-analysis priority list) rather
# than bundled in here.
#
# StaticPool keeps a single connection alive for the engine's lifetime:
# SQLite's default behavior for the special ":memory:"/"" database is
# one throwaway DB *per connection*, so without it every new session
# would see an empty, unrelated database.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = _override_get_session

# Same three users/password the old fake_users_db stub had, so every
# existing test that logs in as admin@example.com / manager@example.com
# / user@example.com with password "password" keeps working unchanged.
DEFAULT_PASSWORD = "password"
DEFAULT_USERS = [
    {"email": "admin@example.com", "full_name": "Super Admin"},
    {"email": "manager@example.com", "full_name": "Project Manager"},
    {"email": "user@example.com", "full_name": "Standard User"},
]


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        for entry in DEFAULT_USERS:
            create_user(
                session,
                email=entry["email"],
                full_name=entry["full_name"],
                hashed_password=get_password_hash(DEFAULT_PASSWORD),
            )
    yield
    SQLModel.metadata.drop_all(test_engine)


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
