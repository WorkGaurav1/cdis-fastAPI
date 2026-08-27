"""
Seeds baseline roles/permissions, the default users, and demo/showcase
data (map/chart/table gallery), mirroring prisma/seed.ts's approach:
idempotent (safe to run more than once) -- upserts roles/permissions
and demo datasets, skips a user email that already exists, re-checks
role assignment even for pre-existing users, and replaces demo chart
points/table rows wholesale rather than assuming an empty DB.

Run with (after `alembic upgrade head`):
    PYTHONPATH=src python -m scripts.seed
"""

import random

from sqlmodel import Session

from config.database import engine
from features.auth.rbac_repository import (
    ensure_role_has_permission,
    ensure_user_has_role,
    get_or_create_permission,
    get_or_create_role,
)
from features.auth.security import get_password_hash
from features.demo.repository import (
    replace_chart_points,
    replace_table_rows,
    upsert_chart_dataset,
    upsert_state_metric,
    upsert_table_dataset,
)
from features.demo.seed_data import (
    DEMO_STATES,
    build_chart_datasets,
    build_table_datasets,
    random_project_count,
)
from features.users.repository import create_user, get_user_by_email
from utils.db import require_id

# Mirrors prisma/seed.ts's PERMISSIONS/ROLES exactly.
PERMISSIONS = [
    {"key": "users:read", "description": "View user accounts"},
    {"key": "users:write", "description": "Create, edit, or deactivate user accounts"},
    {"key": "roles:manage", "description": "Assign or modify roles and permissions"},
]

ROLES = {
    "admin": {
        "description": "Full administrative access",
        "permissions": ["users:read", "users:write", "roles:manage"],
    },
    "manager": {
        "description": "Can view user accounts",
        "permissions": ["users:read"],
    },
    "user": {
        "description": "Standard authenticated user, no elevated access",
        "permissions": [],
    },
}

# All three share this password -- same convention the fake_users_db
# stub this replaces used, so existing local dev workflows/docs that
# reference logging in with "password" keep working. Each is assigned
# the role matching its name (admin@... -> "admin", etc).
DEFAULT_PASSWORD = "password"

DEFAULT_USERS = [
    {"email": "admin@example.com", "full_name": "Super Admin", "role": "admin"},
    {"email": "manager@example.com", "full_name": "Project Manager", "role": "manager"},
    {"email": "user@example.com", "full_name": "Standard User", "role": "user"},
]


def _seed_roles_and_permissions(session: Session) -> None:
    for permission in PERMISSIONS:
        get_or_create_permission(session, permission["key"], permission["description"])

    for name, definition in ROLES.items():
        role = get_or_create_role(session, name, definition["description"])
        for permission_key in definition["permissions"]:
            permission = get_or_create_permission(session, permission_key)
            ensure_role_has_permission(
                session, require_id(role.id), require_id(permission.id)
            )


def _seed_users(session: Session) -> None:
    for entry in DEFAULT_USERS:
        user = get_user_by_email(session, entry["email"])
        if user is None:
            user = create_user(
                session,
                email=entry["email"],
                full_name=entry["full_name"],
                hashed_password=get_password_hash(DEFAULT_PASSWORD),
            )

        role = get_or_create_role(session, entry["role"])
        ensure_user_has_role(session, require_id(user.id), require_id(role.id))


def _seed_demo_data(session: Session) -> None:
    for state_name, state_code in DEMO_STATES:
        upsert_state_metric(
            session,
            state_code=state_code,
            state_name=state_name,
            project_count=random_project_count(),
            activity_intensity=random.randint(0, 100),
        )

    for dataset in build_chart_datasets():
        record = upsert_chart_dataset(
            session,
            slug=dataset["slug"],
            title=dataset["title"],
            chart_type=dataset["chart_type"],
            description=dataset["description"],
        )
        replace_chart_points(session, require_id(record.id), dataset["points"])

    for dataset in build_table_datasets():
        record = upsert_table_dataset(
            session,
            slug=dataset["slug"],
            title=dataset["title"],
            description=dataset["description"],
        )
        replace_table_rows(session, require_id(record.id), dataset["rows"])


def seed() -> None:
    with Session(engine) as session:
        _seed_roles_and_permissions(session)
        _seed_users(session)
        _seed_demo_data(session)


if __name__ == "__main__":
    seed()
    print("Seed complete.")
