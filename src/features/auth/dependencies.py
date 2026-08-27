# FastAPI dependencies mirroring the Node backend's auth middlewares
# (src/middlewares/requireAuth.ts, src/middlewares/csrf.ts): verifying
# who a request is from, and (separately) that a state-changing request
# actually originated from our own frontend origin.

from typing import Callable

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlmodel import Session

from config.database import get_session
from features.auth.cookies import CSRF_COOKIE, CSRF_HEADER
from features.auth.rbac_repository import get_roles_and_permissions_for_user
from features.auth.security import decode_access_token
from features.users.models import User
from features.users.repository import get_user_by_id
from utils.db import require_id


def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
) -> User:
    # This is authentication ("who is this request from") -- it does not
    # check what that user is allowed to do; see require_permission()
    # below for the authorization layer built on top of this.
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

    # sub is always serialized as a string in a JWT (RFC 7519), but the
    # real User table's id is an int -- a missing or non-numeric sub is
    # exactly as invalid as a bad signature.
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        )
    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        ) from None

    user = get_user_by_id(session, user_id)
    if user is None:
        # A token that verifies fine but no longer maps to a real user
        # (e.g. the user was deleted after the token was issued).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        )

    return user


def require_csrf_token(request: Request) -> None:
    """
    Double-submit cookie CSRF check, mirroring
    src/middlewares/csrf.ts's requireCsrfToken exactly.

    A cross-site attacker can trigger a request that carries the
    victim's cookies automatically, but they cannot read the
    csrf_token cookie's value (Same-Origin Policy) to also set it as a
    header -- so a header/cookie mismatch means the request didn't
    originate from JS running on our own frontend origin.

    Only applied to authenticated, state-changing routes (refresh,
    logout) -- login/register have no prior session to ride and are the
    endpoints that hand out this cookie in the first place.
    """
    cookie_value = request.cookies.get(CSRF_COOKIE)
    header_value = request.headers.get(CSRF_HEADER)

    if not cookie_value or not header_value or cookie_value != header_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid CSRF token.",
        )


def require_permission(permission: str) -> Callable[..., User]:
    """
    Authorization guard factory, mirroring
    src/middlewares/requirePermission.ts: requires the authenticated
    user to hold the given permission. Always checks permissions, never
    role names -- see Node's comment on the hybrid RBAC decision this
    project is built on.

    Must run after get_current_user (a sub-dependency here, so FastAPI
    resolves it first and 401s before this ever needs to run). Loads the
    user's current permissions fresh from the database on every request
    -- not baked into the JWT -- so a permission revoked server-side
    takes effect on the very next request, the same guarantee Node's
    integration test proves for this exact behavior.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
    ) -> User:
        _, permissions = get_roles_and_permissions_for_user(
            session, require_id(current_user.id)
        )
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency
