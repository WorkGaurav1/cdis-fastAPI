from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlmodel import Session

# Imports for rate limiting
from app.limiter import limiter

# Feature imports
from config.config import settings
from config.database import get_session
from features.auth.cookies import clear_auth_cookies, set_auth_cookies
from features.auth.dependencies import get_current_user, require_csrf_token
from features.auth.schemas import LoginRequest, RegisterRequest
from features.auth.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from features.users.mapper import to_safe_user
from features.users.models import User
from features.users.repository import create_user, get_user_by_email, get_user_by_id
from utils.apiResponse import send_success

router = APIRouter()

invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)


def _issue_tokens_and_set_cookies(response: Response, user: User) -> None:
    # sub = the user's stable id, mirroring the Node backend's access
    # tokens (src/services/token.service.ts: `{ sub: userId }`) -- not
    # email, so a later email change doesn't invalidate outstanding
    # tokens and lookups don't depend on email casing/uniqueness. JWTs
    # serialize sub as a string (RFC 7519) even though the DB id is an int.
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # access_token/refresh_token/csrf_token, flags, paths, and lifetimes
    # all mirror the Node backend's src/lib/cookies.ts exactly (see
    # features/auth/cookies.py). refresh_token is still literally the
    # same JWT as access_token for now -- see refresh()'s docstring.
    set_auth_cookies(response, access_token=access_token, refresh_token=access_token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    response: Response,
    register_data: RegisterRequest,
    session: Session = Depends(get_session),
):
    # NOTE: Node also assigns the default "user" role here
    # (roleRepository.findByName("user") + userRepository.assignRole).
    # No role/permission tables exist yet -- that's P0 step 10 -- so a
    # freshly registered user has no roles until then, same as every
    # other user in to_safe_user()'s current [] placeholder.
    if get_user_by_email(session, register_data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = create_user(
        session,
        email=register_data.email,
        full_name=register_data.name,
        hashed_password=get_password_hash(register_data.password),
    )

    _issue_tokens_and_set_cookies(response, user)

    return send_success({"user": to_safe_user(user)})


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    session: Session = Depends(get_session),
):
    # Authenticate a user and return a JWT token in HttpOnly cookies.
    user = get_user_by_email(session, login_data.email)

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise invalid_credentials_exception

    _issue_tokens_and_set_cookies(response, user)

    return send_success({"user": to_safe_user(user)})


@router.post("/logout", dependencies=[Depends(require_csrf_token)])
def logout(response: Response, current_user=Depends(get_current_user)):
    # Mirrors Node's route wiring exactly: requireAuth then
    # requireCsrfToken (src/routes/auth.routes.ts). current_user isn't
    # used yet (no server-side revocation exists until P0 step 8 adds
    # real refresh-token persistence) but the auth check itself matters:
    # without it, logout would be reachable by anyone holding a valid
    # CSRF cookie/header pair, logged in or not.
    _ = current_user
    clear_auth_cookies(response)
    return send_success({"message": "Logged out successfully."})


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    # Returns the user the verified access-token JWT actually names --
    # not a hardcoded stand-in. get_current_user (see
    # features/auth/dependencies.py) already raises 401 for a missing,
    # tampered, or expired token.
    return send_success({"user": to_safe_user(current_user)})


@router.post("/refresh", dependencies=[Depends(require_csrf_token)])
def refresh(
    request: Request, response: Response, session: Session = Depends(get_session)
):
    # Verifies the refresh-token cookie's JWT the same way /me verifies
    # the access-token cookie, and returns the user it actually names.
    #
    # NOTE: this is still not a real refresh -- refresh_token is set to
    # the exact same JWT as access_token at login (see login() above), so
    # this only proves the *original* access token hasn't expired; no
    # distinct refresh token, rotation, or reuse detection exists yet.
    # That's tracked separately (P0 step 8 of the gap-analysis priority
    # list / docs/parity-notes.md) and requires real persistence.
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    try:
        payload = decode_access_token(refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        ) from None

    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        ) from None

    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        )

    return send_success({"user": to_safe_user(user)})
