# Persistence layer for User -- the only place SQL/session queries for
# users live, mirroring the Node backend's src/repositories/user.repository.ts.
# Callers pass in a Session (via the get_session dependency) rather than
# this module owning one, so each request gets its own transaction scope.

from datetime import datetime

from sqlalchemy import func, update
from sqlmodel import Session, col, select

from features.users.models import User
from utils.db import require_id


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def list_users(session: Session, offset: int = 0, limit: int = 100) -> list[User]:
    # Param named `offset`, not `skip` -- matches the Node backend's
    # userRepository.findAll()/pagination.dto.ts exactly, so a shared
    # frontend (or any client) can point at either backend with the
    # same query-string contract.
    return list(session.exec(select(User).offset(offset).limit(limit)).all())


def count_users(session: Session) -> int:
    return session.exec(select(func.count()).select_from(User)).one()


def create_user(
    session: Session, *, email: str, hashed_password: str, full_name: str | None = None
) -> User:
    user = User(email=email, hashed_password=hashed_password, full_name=full_name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def record_failed_login(
    session: Session,
    user: User,
    *,
    lockout_max_attempts: int,
    locked_until_if_tripped: datetime,
) -> User:
    """
    Atomically increments failed_login_attempts (a single UPDATE, not a
    Python read-modify-write), then locks the account if the real,
    post-increment count has reached lockout_max_attempts.

    The read-modify-write this replaces (read attempts into Python,
    compute +1, write it back) is a textbook lost-update race: two
    concurrent wrong-password requests for the same account can both
    read attempts=4, both compute 5, both write 5 -- one real attempt
    silently vanishes, delaying lockout past the intended threshold.
    `failed_login_attempts + 1` here is evaluated server-side inside an
    atomically-executed UPDATE, so concurrent requests correctly
    serialize into 5 then 6 rather than colliding on 5 twice.

    Deliberately two round trips, not one combined statement: MySQL
    evaluates a multi-column UPDATE's SET clauses left-to-right, so a
    later SET expression referencing the same column sees the column's
    *new* value from an earlier SET in the same statement (standard SQL
    -- and PostgreSQL -- has every SET expression see only pre-update
    values, evaluated as if simultaneously; MySQL does not). A single
    statement setting both failed_login_attempts and a
    failed_login_attempts-derived locked_until tripped lockout one
    attempt early on MySQL for exactly this reason, silently correct on
    SQLite. Splitting into two statements and reading the real,
    committed count back via refresh() removes the dependency on that
    ordering entirely, and is correct on both.
    """
    session.execute(
        update(User)
        .where(col(User.id) == require_id(user.id))
        .values(failed_login_attempts=User.failed_login_attempts + 1)
    )
    session.commit()
    session.refresh(user)

    if user.failed_login_attempts >= lockout_max_attempts:
        session.execute(
            update(User)
            .where(col(User.id) == require_id(user.id))
            .values(locked_until=locked_until_if_tripped)
        )
        session.commit()
        session.refresh(user)

    return user


def reset_failed_logins(session: Session, user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    session.add(user)
    session.commit()
