# Auth cookie helpers -- mirrors the Node backend's src/lib/cookies.ts:
# cookie names, flags, paths, and lifetimes all match it exactly so the
# two backends are interchangeable from the frontend's point of view.

import secrets

from fastapi import Response

from config.config import settings

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"

# Refresh cookie is scoped to the auth routes only -- the browser never
# attaches it to unrelated API calls, shrinking where it can leak.
REFRESH_COOKIE_PATH = f"{settings.API_V1_STR}/auth"

ACCESS_TOKEN_MAX_AGE_SECONDS = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_MAX_AGE_SECONDS = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

# "production" only would silently ship non-Secure cookies on a staging
# deployment -- ENVIRONMENT allows "staging" as a valid value, so it
# needs the same cookie hardening as production does. Also means a
# plain local `development`/`test` run over http still gets cookies the
# browser will actually send back (a Secure cookie is dropped by every
# browser -- and by httpx's own cookie jar -- on a non-https connection).
_SECURE_ENVIRONMENTS = ("production", "staging")


def _is_secure() -> bool:
    return settings.ENVIRONMENT in _SECURE_ENVIRONMENTS


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = _is_secure()

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_MAX_AGE_SECONDS,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
        max_age=REFRESH_TOKEN_MAX_AGE_SECONDS,
    )
    # Readable by frontend JS on purpose -- the double-submit CSRF
    # pattern (P0 step 5) relies on JS being able to read this and echo
    # it back as a header. Issued here already so step 5 only has to add
    # validation, not a second cookie-issuing pass.
    response.set_cookie(
        key=CSRF_COOKIE,
        value=secrets.token_hex(24),
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=REFRESH_TOKEN_MAX_AGE_SECONDS,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE, path="/")
    response.delete_cookie(REFRESH_TOKEN_COOKIE, path=REFRESH_COOKIE_PATH)
    response.delete_cookie(CSRF_COOKIE, path="/")
