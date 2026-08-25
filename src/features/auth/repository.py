# Persistence layer for RefreshToken -- mirrors the Node backend's
# src/repositories/refreshToken.repository.ts, including the
# rotation-chain bookkeeping (replaced_by_token_id) used to detect reuse
# of an already-rotated token.

from datetime import datetime, timezone

from sqlmodel import Session, select

from features.auth.models import RefreshToken


def _utcnow() -> datetime:
    # Naive but UTC-by-convention -- see models.py's _utcnow() for why.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_refresh_token(
    session: Session,
    *,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
    created_by_ip: str | None = None,
    user_agent: str | None = None,
) -> RefreshToken:
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        created_by_ip=created_by_ip,
        user_agent=user_agent,
    )
    session.add(token)
    session.commit()
    session.refresh(token)
    return token


def get_refresh_token_by_hash(session: Session, token_hash: str) -> RefreshToken | None:
    return session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).first()


def mark_rotated(
    session: Session, token: RefreshToken, replaced_by_token_id: int
) -> None:
    """Marks `token` as revoked and links it to the token that replaced it."""
    token.revoked_at = _utcnow()
    token.replaced_by_token_id = replaced_by_token_id
    session.add(token)
    session.commit()


def revoke(session: Session, token: RefreshToken) -> None:
    token.revoked_at = _utcnow()
    session.add(token)
    session.commit()


def revoke_all_for_user(session: Session, user_id: int) -> None:
    """
    Revokes every active token for a user -- used when reuse of an
    already-rotated token is detected (signals the token chain may be
    compromised) and for "log out everywhere."
    """
    active_tokens = session.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
    ).all()
    now = _utcnow()
    for token in active_tokens:
        token.revoked_at = now
        session.add(token)
    session.commit()
