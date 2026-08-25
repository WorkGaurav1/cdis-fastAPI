# Users API Router.

from typing import List
from fastapi import APIRouter, HTTPException, status

from features.users.schemas import UserCreate, UserResponse

from utils.apiResponse import send_success

router = APIRouter()

# Precomputed bcrypt hash for the word 'password'. 
# We hardcode this here to avoid triggering a known passlib/bcrypt startup bug 
# during module initialization.
fake_hashed_password = "$2b$12$lXBpIAx1aoTzuu9.jNP9J.VBowa/09bmeM41NjDBtFygiAQzg4mzi"

fake_users_db = [
    {
        "id": "user_1",
        "email": "admin@example.com",
        "name": "Super Admin",
        "roles": ["ADMIN", "USER"],
        "permissions": ["read:users", "write:users", "read:dashboard"],
        "hashed_password": fake_hashed_password
    },
    {
        "id": "user_2",
        "email": "manager@example.com",
        "name": "Project Manager",
        "roles": ["MANAGER", "USER"],
        "permissions": ["read:users", "read:dashboard"],
        "hashed_password": fake_hashed_password
    },
    {
        "id": "user_3",
        "email": "user@example.com",
        "name": "Standard User",
        "roles": ["USER"],
        "permissions": ["read:dashboard"],
        "hashed_password": fake_hashed_password
    }
]

def get_user_by_email(email: str) -> dict | None:
    # Look up a fake_users_db entry by email (case-sensitive, matching
    # the exact-match lookup login already did before this was factored
    # out). Returns None if no such user exists.
    return next((u for u in fake_users_db if u.get("email") == email), None)


def get_user_by_id(user_id: str) -> dict | None:
    # Look up a fake_users_db entry by id -- used to resolve the "sub"
    # claim of a verified access-token JWT back to a user.
    return next((u for u in fake_users_db if u.get("id") == user_id), None)


@router.get("")
def read_users(skip: int = 0, limit: int = 100):
    # Retrieve a list of all users.
    safe_users = [
        {k: v for k, v in u.items() if k != "hashed_password"} 
        for u in fake_users_db[skip : skip + limit]
    ]
    return send_success({"users": safe_users})

