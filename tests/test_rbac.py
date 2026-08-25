# Verifies the RBAC layer (features/auth/rbac_models.py,
# rbac_repository.py, and the require_permission dependency), mirroring
# the exact seed data prisma/seed.ts defines and the permission gate
# Node applies to GET /users (requirePermission("users:read")).

from fastapi.testclient import TestClient
from sqlmodel import Session

from config.config import settings
from features.auth.rbac_repository import get_roles_and_permissions_for_user
from features.users.repository import get_user_by_email

USERS_URL = f"{settings.API_V1_STR}/users"
LOGIN_URL = f"{settings.API_V1_STR}/auth/login"
REGISTER_URL = f"{settings.API_V1_STR}/auth/register"

PASSWORD = "password"


def _login(client: TestClient, email: str) -> None:
    response = client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.json()


def test_admin_has_all_three_seeded_permissions(client: TestClient):
    _login(client, "admin@example.com")
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    user = response.json()["data"]["user"]
    assert user["roles"] == ["admin"]
    assert set(user["permissions"]) == {"users:read", "users:write", "roles:manage"}
    client.cookies.clear()


def test_manager_has_only_users_read(client: TestClient):
    _login(client, "manager@example.com")
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    user = response.json()["data"]["user"]
    assert user["roles"] == ["manager"]
    assert user["permissions"] == ["users:read"]
    client.cookies.clear()


def test_plain_user_has_no_permissions(client: TestClient):
    _login(client, "user@example.com")
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    user = response.json()["data"]["user"]
    assert user["roles"] == ["user"]
    assert user["permissions"] == []
    client.cookies.clear()


def test_users_list_requires_users_read_permission(client: TestClient):
    _login(client, "user@example.com")

    response = client.get(USERS_URL)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert (
        response.json()["error"]["message"]
        == "You do not have permission to perform this action."
    )
    client.cookies.clear()


def test_users_list_succeeds_for_manager_who_holds_users_read(client: TestClient):
    _login(client, "manager@example.com")

    response = client.get(USERS_URL)

    assert response.status_code == 200
    client.cookies.clear()


def test_register_assigns_the_default_user_role(
    client: TestClient, db_session: Session
):
    response = client.post(
        REGISTER_URL,
        json={
            "email": "rbac-registrant@example.com",
            "name": "RBAC Registrant",
            "password": "a-strong-password",
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["user"]["roles"] == ["user"]
    assert response.json()["data"]["user"]["permissions"] == []

    user = get_user_by_email(db_session, "rbac-registrant@example.com")
    roles, permissions = get_roles_and_permissions_for_user(db_session, user.id)
    assert roles == ["user"]
    assert permissions == []
    client.cookies.clear()


def test_effective_permissions_are_deduplicated_across_roles(db_session: Session):
    # admin's three permissions come from a single role here, but
    # get_roles_and_permissions_for_user must never return duplicates
    # even if a user held multiple roles granting overlapping
    # permissions -- this asserts on the *set* semantics, not just "the
    # admin happens to have 3 items".
    admin = get_user_by_email(db_session, "admin@example.com")
    roles, permissions = get_roles_and_permissions_for_user(db_session, admin.id)
    assert len(permissions) == len(set(permissions))
    assert roles == ["admin"]
