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

@router.get("")
def read_users(skip: int = 0, limit: int = 100):
    # Retrieve a list of all users.
    safe_users = [
        {k: v for k, v in u.items() if k != "hashed_password"} 
        for u in fake_users_db[skip : skip + limit]
    ]
    return send_success({"users": safe_users})

