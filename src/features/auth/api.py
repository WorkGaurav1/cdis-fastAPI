from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlmodel import Session

# Imports for rate limiting
from app.limiter import limiter

# Feature imports
from config.database import get_session
from features.auth.cookies import clear_auth_cookies, set_auth_cookies
from features.auth.dependencies import get_current_user, require_csrf_token
from features.auth.rbac_repository import (
    ensure_user_has_role,
    get_role_by_name,
    get_roles_and_permissions_for_user,
)
from features.auth.schemas import LoginRequest, RegisterRequest
from features.auth.security import get_password_hash, verify_password
from features.auth.service import (
    TokenPair,
    issue_token_pair,
    revoke_refresh_token,
    rotate_refresh_token,
)
from features.users.mapper import to_safe_user
from features.users.models import User
from features.users.repository import create_user, get_user_by_email
from utils.apiResponse import send_success

router = APIRouter()

invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)


def _request_context(request: Request) -> dict:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def _set_cookies_from(response: Response, tokens: TokenPair) -> None:
    # access_token/refresh_token/csrf_token, flags, paths, and lifetimes
    # all mirror the Node backend's src/lib/cookies.ts exactly (see
    # features/auth/cookies.py).
    set_auth_cookies(
        response, access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


def _safe_user_payload(session: Session, user: User) -> dict:
    roles, permissions = get_roles_and_permissions_for_user(session, user.id)
    return to_safe_user(user, roles, permissions)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    response: Response,
    register_data: RegisterRequest,
    session: Session = Depends(get_session),
):
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

    # Mirrors Node's register() assigning the default "user" role
    # (roleRepository.findByName("user") + userRepository.assignRole).
    # A missing default role is a deployment/seed problem, not something
    # the client did wrong -- same as Node's raw `throw new Error(...)`
    # here, it surfaces as a generic 500 (via the global exception
    # handler) rather than a client-facing 4xx.
    default_role = get_role_by_name(session, "user")
    if default_role is None:
        raise RuntimeError(
            "Default role 'user' is missing. Run `python -m scripts.seed`."
        )
    ensure_user_has_role(session, user.id, default_role.id)

    tokens = issue_token_pair(session, user, **_request_context(request))
    _set_cookies_from(response, tokens)

    return send_success({"user": _safe_user_payload(session, user)})


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

    tokens = issue_token_pair(session, user, **_request_context(request))
    _set_cookies_from(response, tokens)

    return send_success({"user": _safe_user_payload(session, user)})


@router.post("/logout", dependencies=[Depends(require_csrf_token)])
def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Mirrors Node's route wiring exactly: requireAuth then
    # requireCsrfToken (src/routes/auth.routes.ts), then revokes the
    # refresh token server-side so a copy of it (e.g. stolen from
    # storage) can't be used at /auth/refresh after this point.
    _ = current_user
    raw_refresh_token = request.cookies.get("refresh_token")
    if raw_refresh_token:
        revoke_refresh_token(session, raw_refresh_token)

    clear_auth_cookies(response)
    return send_success({"message": "Logged out successfully."})


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Returns the user the verified access-token JWT actually names --
    # not a hardcoded stand-in. get_current_user (see
    # features/auth/dependencies.py) already raises 401 for a missing,
    # tampered, or expired token.
    return send_success({"user": _safe_user_payload(session, current_user)})


@router.post("/refresh", dependencies=[Depends(require_csrf_token)])
def refresh(
    request: Request, response: Response, session: Session = Depends(get_session)
):
    raw_refresh_token = request.cookies.get("refresh_token")
    if not raw_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    # Verifies, rotates, and (on reuse of an already-rotated token)
    # revokes the whole session chain -- see
    # features/auth/service.py::rotate_refresh_token for the full flow.
    # Raises HTTPException(401) itself on any failure.
    user, tokens = rotate_refresh_token(
        session, raw_refresh_token, **_request_context(request)
    )

    _set_cookies_from(response, tokens)

    return send_success({"user": _safe_user_payload(session, user)})
