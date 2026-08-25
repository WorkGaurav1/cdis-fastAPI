# Auth-specific database models.

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from utils.time import utcnow


class RefreshToken(SQLModel, table=True):
    """
    Mirrors the Node backend's RefreshToken Prisma model
    (prisma/schema.prisma -- @@map("refresh_tokens")) field for field.

    Only tokenHash is ever stored -- never the raw value the client
    holds (features/auth/security.py hashes it with SHA-256 before this
    is written; that's a deliberate choice, not bcrypt, since this is a
    256-bit random value rather than a low-entropy password, so there's
    no brute-force risk to slow down).

    replaced_by_token_id forms the rotation chain used to detect reuse
    of an already-rotated token: when a token with revoked_at already
    set is presented again at /auth/refresh, every active token for
    that user gets revoked as a theft response (see
    features/auth/service.py's refresh_tokens()).
    """

    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    token_hash: str = Field(unique=True, index=True, max_length=255)

    expires_at: datetime
    revoked_at: Optional[datetime] = None

    replaced_by_token_id: Optional[int] = Field(
        default=None, foreign_key="refresh_tokens.id", unique=True
    )

    created_by_ip: Optional[str] = Field(default=None, max_length=64)
    user_agent: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=utcnow)
