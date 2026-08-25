import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config.config import settings
from utils.time import utcnow


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify a plain password against a hashed password.
    # Bcrypt requires bytes, so we encode strings to utf-8 before hashing
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Hash a password using bcrypt.
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generate a secure JWT token.
    Uses the strong SECRET_KEY and ALGORITHM specified in config.py.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    # Sign the JWT using our secure secret key
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Verify a JWT's signature and expiry, and return its decoded payload.

    Raises jwt.PyJWTError (e.g. ExpiredSignatureError, InvalidSignatureError,
    DecodeError) if the token is tampered, malformed, or expired -- callers
    are expected to catch jwt.PyJWTError and turn it into a 401, mirroring
    the Node backend's requireAuth middleware (src/middlewares/requireAuth.ts).
    The algorithm allow-list is pinned to settings.ALGORITHM, the same
    algorithm we sign with, so a token claiming a different algorithm
    (e.g. "none") is rejected rather than trusted.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_refresh_token_value() -> str:
    """Raw refresh token value -- sent to the client, never stored as-is."""
    return secrets.token_hex(32)


def hash_refresh_token(raw_token: str) -> str:
    """
    SHA-256, not bcrypt: this hashes a 256-bit random value, not a
    low-entropy password, so there's no brute-force risk to slow down --
    a fast, deterministic hash is the correct tool for a lookup key.
    Mirrors src/services/token.service.ts's hashRefreshToken exactly.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    return utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
