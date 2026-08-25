# FastAPI dependency mirroring the Node backend's requireAuth middleware
# (src/middlewares/requireAuth.ts): verifies the access-token cookie's
# JWT signature and expiry, and resolves it to the actual authenticated
# user. This is authentication ("who is this request from") -- it does
# not check what that user is allowed to do; permission checks build on
# top of this once a real permission model exists.

import jwt
from fastapi import Cookie, HTTPException, status

from features.auth.security import decode_access_token
from features.users.api import get_user_by_id


def get_current_user(access_token: str | None = Cookie(default=None)) -> dict:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    try:
        payload = decode_access_token(access_token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        ) from None

    user = get_user_by_id(payload.get("sub"))
    if user is None:
        # A token that verifies fine but no longer maps to a real user
        # (e.g. the user was deleted after the token was issued).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        )

    return user
