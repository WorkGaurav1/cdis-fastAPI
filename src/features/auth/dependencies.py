# FastAPI dependencies mirroring the Node backend's auth middlewares
# (src/middlewares/requireAuth.ts, src/middlewares/csrf.ts): verifying
# who a request is from, and (separately) that a state-changing request
# actually originated from our own frontend origin.

import jwt
from fastapi import Cookie, HTTPException, Request, status

from features.auth.cookies import CSRF_COOKIE, CSRF_HEADER
from features.auth.security import decode_access_token
from features.users.api import get_user_by_id


def get_current_user(access_token: str | None = Cookie(default=None)) -> dict:
    # This is authentication ("who is this request from") -- it does not
    # check what that user is allowed to do; permission checks build on
    # top of this once a real permission model exists (P0 step 10).
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
