from fastapi import APIRouter, HTTPException, status, Request, Response
from datetime import timedelta

# Imports for rate limiting
from app.limiter import limiter

# Feature imports
from features.users.api import fake_users_db
from features.auth.schemas import LoginRequest, Token
from features.auth.security import verify_password, create_access_token

router = APIRouter()

# The exact, generic exception to prevent Username Enumeration (VAPT Task 1.3)
# We throw this EXACT same error whether the email doesn't exist, OR the password is wrong.
invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute") # Prevents Brute Force Attacks (VAPT Task 1.4)
def login(
    request: Request,
    response: Response,
    login_data: LoginRequest
):
    """
    Authenticate a user and return a JWT token.
    This endpoint is strictly rate-limited and immune to username enumeration.
    """
    # 1. Fetch user by email from the dummy database (would be SQLModel in prod)
    user = next((u for u in fake_users_db if u.get("email") == login_data.email), None)

    # 2. Verify existence AND password using the generic exception
    if not user or not verify_password(login_data.password, user.get("hashed_password")):
        raise invalid_credentials_exception

    # 3. Generate secure JWT token (VAPT Task 1.2)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # 4. Set token in a Secure, HttpOnly cookie (VAPT Task 1.6)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevents XSS attacks from reading the cookie
        secure=True,    # Ensures cookie is only sent over HTTPS
        samesite="lax",
        max_age=1800    # 30 minutes
    )

    return {"access_token": access_token, "token_type": "bearer"}
