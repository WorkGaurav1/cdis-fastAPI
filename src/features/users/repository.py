# Persistence layer for User -- the only place SQL/session queries for
# users live, mirroring the Node backend's src/repositories/user.repository.ts.
# Callers pass in a Session (via the get_session dependency) rather than
# this module owning one, so each request gets its own transaction scope.

from datetime import datetime

from sqlmodel import Session, select

from features.users.models import User


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def list_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return list(session.exec(select(User).offset(skip).limit(limit)).all())


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
    failed_login_attempts: int,
    locked_until: datetime | None,
) -> None:
    user.failed_login_attempts = failed_login_attempts
    user.locked_until = locked_until
    session.add(user)
    session.commit()


def reset_failed_logins(session: Session, user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    session.add(user)
    session.commit()
