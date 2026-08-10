from fastapi import APIRouter, HTTPException, status, Request, Response
from datetime import timedelta

# Imports for rate limiting
from app.limiter import limiter

# Feature imports
from features.users.api import fake_users_db
from features.auth.schemas import LoginRequest, Token
from features.auth.security import verify_password, create_access_token

from utils.apiResponse import send_success, send_error

router = APIRouter()

invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)

@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    login_data: LoginRequest
):
    """Authenticate a user and return a JWT token in HttpOnly cookies."""
    user = next((u for u in fake_users_db if u.get("email") == login_data.email), None)

    if not user or not verify_password(login_data.password, user.get("hashed_password")):
        raise invalid_credentials_exception

    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=timedelta(minutes=30)
    )

    # Set cookies as expected by the frontend
    response.set_cookie(key="accessToken", value=access_token, httponly=True, secure=True, samesite="lax")
    response.set_cookie(key="refreshToken", value=access_token, httponly=True, secure=True, samesite="lax")

    # Safe user dict without hashed_password
    safe_user = {k: v for k, v in user.items() if k != "hashed_password"}
    return send_success({"user": safe_user})

@router.post("/logout")
def logout(response: Response):
    """Clear HttpOnly cookies on logout."""
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken")
    return send_success({"message": "Logged out successfully."})

@router.get("/me")
def me(request: Request):
    """Return the currently authenticated user."""
    # Since we aren't enforcing strict auth middleware right now,
    # we'll just mock returning the first user if the cookie is present.
    # In a real app, this parses the accessToken from cookies.
    access_token = request.cookies.get("accessToken")
    if not access_token:
        raise HTTPException(status_code=401, detail="No session found.")
    
    # Just return admin user for dummy purposes
    user = fake_users_db[0]
    safe_user = {k: v for k, v in user.items() if k != "hashed_password"}
    return send_success({"user": safe_user})

@router.post("/refresh")
def refresh(request: Request, response: Response):
    """Refresh the HttpOnly cookies."""
    # In a real app, this validates the refresh token from cookies and issues a new one.
    # For dummy purposes, we just return a success since the user already has a valid token.
    refresh_token = request.cookies.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found.")
    
    # Just return the same safe dummy user data
    user = fake_users_db[0]
    safe_user = {k: v for k, v in user.items() if k != "hashed_password"}
    return send_success({"user": safe_user})
