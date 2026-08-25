"""
Seeds the database with default users for local development, mirroring
prisma/seed.ts's approach: idempotent (safe to run more than once --
skips any email that already exists) rather than assuming an empty DB.

Run with (after `alembic upgrade head`):
    PYTHONPATH=src python -m scripts.seed
"""

from sqlmodel import Session

from config.database import engine
from features.auth.security import get_password_hash
from features.users.repository import create_user, get_user_by_email

# All three share this password -- same convention the fake_users_db
# stub this replaces used, so existing local dev workflows/docs that
# reference logging in with "password" keep working.
DEFAULT_PASSWORD = "password"

DEFAULT_USERS = [
    {"email": "admin@example.com", "full_name": "Super Admin"},
    {"email": "manager@example.com", "full_name": "Project Manager"},
    {"email": "user@example.com", "full_name": "Standard User"},
]


def seed() -> None:
    with Session(engine) as session:
        for entry in DEFAULT_USERS:
            if get_user_by_email(session, entry["email"]) is not None:
                continue
            create_user(
                session,
                email=entry["email"],
                full_name=entry["full_name"],
                hashed_password=get_password_hash(DEFAULT_PASSWORD),
            )


if __name__ == "__main__":
    seed()
    print("Seed complete.")
