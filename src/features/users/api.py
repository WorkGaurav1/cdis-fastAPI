"""
Users API Router.
This file defines all the HTTP endpoints (path operations) for the "Users" feature.
It handles incoming web requests, performs business logic, and returns responses.
"""

# ---------------------------------------------------------
# External Imports
# ---------------------------------------------------------
from typing import List
from fastapi import APIRouter, HTTPException, status

# ---------------------------------------------------------
# Internal Imports
# ---------------------------------------------------------
from features.users.schemas import UserCreate, UserResponse

# Create an APIRouter instance specifically for user-related endpoints
router = APIRouter()

# A temporary dummy list to simulate a database for demonstration purposes
fake_users_db = []

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all users.
    Supports pagination through 'skip' and 'limit' query parameters.
    """
    # Slice the dummy database list based on the pagination parameters
    return fake_users_db[skip : skip + limit]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    """
    Create a new user.
    Validates that the email does not already exist before creating.
    """
    # Check if a user with this email already exists to prevent duplicates
    for u in fake_users_db:
        # Note: u is a dict here because fake_users_db stores dicts in this example
        if u.get("email") == user_in.email:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
    # Construct a new user dictionary. In a real app, this would be an SQLModel database insert.
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user_in.email,
        "is_active": user_in.is_active,
        "is_superuser": user_in.is_superuser,
        "full_name": user_in.full_name,
        "hashed_password": user_in.password + "notreallyhashed" # Simulating password hashing
    }
    
    # Save the user to our dummy database
    fake_users_db.append(new_user)
    
    return new_user
