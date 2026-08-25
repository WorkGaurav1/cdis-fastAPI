from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

# Imports for rate limiting
from app.limiter import limiter

# Feature imports
from features.auth.dependencies import get_current_user
from features.auth.schemas import LoginRequest
from features.auth.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from features.users.api import get_user_by_email, get_user_by_id
from utils.apiResponse import send_success

router = APIRouter()

invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)


def _to_safe_user(user: dict) -> dict:
    # Strips the hashed password before a user dict is ever sent back to
    # a client. TODO(P1/mapper item): replace every one of this
    # function's call sites with a single shared mapper once a real User
    # model exists (see docs/parity-notes.md).
    return {k: v for k, v in user.items() if k != "hashed_password"}


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    login_data: LoginRequest
):
    # Authenticate a user and return a JWT token in HttpOnly cookies.
    user = get_user_by_email(login_data.email)

    if not user or not verify_password(login_data.password, user.get("hashed_password")):
        raise invalid_credentials_exception

    # sub = the user's stable id, mirroring the Node backend's access
    # tokens (src/services/token.service.ts: `{ sub: userId }`) -- not
    # email, so a later email change doesn't invalidate outstanding
    # tokens and lookups don't depend on email casing/uniqueness.
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=timedelta(minutes=30)
    )

    # Set cookies as expected by the frontend
    response.set_cookie(key="accessToken", value=access_token, httponly=True, secure=True, samesite="lax")
    response.set_cookie(key="refreshToken", value=access_token, httponly=True, secure=True, samesite="lax")

    return send_success({"user": _to_safe_user(user)})

@router.post("/logout")
def logout(response: Response):
    # Clear HttpOnly cookies on logout.
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken")
    return send_success({"message": "Logged out successfully."})

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    # Returns the user the verified access-token JWT actually names --
    # not a hardcoded stand-in. get_current_user (see
    # features/auth/dependencies.py) already raises 401 for a missing,
    # tampered, or expired token.
    return send_success({"user": _to_safe_user(current_user)})

@router.post("/refresh")
def refresh(request: Request, response: Response):
    # Verifies the refresh-token cookie's JWT the same way /me verifies
    # the access-token cookie, and returns the user it actually names.
    #
    # NOTE: this is still not a real refresh -- refreshToken is set to
    # the exact same JWT as accessToken at login (see login() above), so
    # this only proves the *original* access token hasn't expired; no
    # distinct refresh token, rotation, or reuse detection exists yet.
    # That's tracked separately (P0 step 8 of the gap-analysis priority
    # list / docs/parity-notes.md) and requires real persistence, which
    # doesn't exist yet either.
    refresh_token = request.cookies.get("refreshToken")
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

    user = get_user_by_id(payload.get("sub"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or has expired.",
        )

    return send_success({"user": _to_safe_user(user)})
