# Auth orchestration -- mirrors src/services/auth.service.ts's
# issueTokenPair/refresh/logout flow. Coordinates token generation
# (security.py) and persistence (repository.py, features/users/repository.py);
# the HTTP layer (api.py) only deals with request/response/cookies.

from dataclasses import dataclass
from datetime import timedelta

from fastapi import HTTPException, status
from sqlmodel import Session

from config.config import settings
from features.auth.repository import (
    create_refresh_token,
    get_refresh_token_by_hash,
    mark_rotated,
    revoke,
    revoke_all_for_user,
)
from features.auth.security import (
    create_access_token,
    generate_refresh_token_value,
    hash_refresh_token,
    refresh_token_expiry,
)
from features.users.models import User
from features.users.repository import get_user_by_id
from utils.time import utcnow


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_token_id: int


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def issue_token_pair(
    session: Session,
    user: User,
    *,
    ip: str | None = None,
    user_agent: str | None = None,
) -> TokenPair:
    # sub = the user's stable id, mirroring the Node backend's access
    # tokens (src/services/token.service.ts: `{ sub: userId }`). JWTs
    # serialize sub as a string (RFC 7519) even though the DB id is an int.
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    raw_refresh_token = generate_refresh_token_value()
    stored = create_refresh_token(
        session,
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=refresh_token_expiry(),
        created_by_ip=ip,
        user_agent=user_agent,
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        refresh_token_id=stored.id,
    )


def rotate_refresh_token(
    session: Session,
    raw_token: str,
    *,
    ip: str | None = None,
    user_agent: str | None = None,
) -> tuple[User, TokenPair]:
    """
    Verifies a raw refresh-token cookie value against persisted, hashed
    refresh tokens, rotates it, and returns the user it names plus a
    fresh token pair. Mirrors authService.refresh() exactly, including
    reuse detection: presenting a token that was already rotated away
    revokes every active session for that user (the chain may have been
    stolen).
    """
    token_hash = hash_refresh_token(raw_token)
    existing = get_refresh_token_by_hash(session, token_hash)

    if existing is None:
        raise _unauthorized("Invalid session. Please sign in again.")

    if existing.revoked_at is not None:
        revoke_all_for_user(session, existing.user_id)
        raise _unauthorized("This session is no longer valid. Please sign in again.")

    if existing.expires_at < utcnow():
        raise _unauthorized("Your session has expired. Please sign in again.")

    user = get_user_by_id(session, existing.user_id)
    if user is None:
        raise _unauthorized("Invalid session. Please sign in again.")

    tokens = issue_token_pair(session, user, ip=ip, user_agent=user_agent)
    mark_rotated(session, existing, tokens.refresh_token_id)

    return user, tokens


def revoke_refresh_token(session: Session, raw_token: str) -> None:
    """Mirrors authService.logout(): revoke if still active, no-op otherwise."""
    existing = get_refresh_token_by_hash(session, hash_refresh_token(raw_token))
    if existing is not None and existing.revoked_at is None:
        revoke(session, existing)
