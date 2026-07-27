from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

# Dummy in-memory database
fake_users_db = []

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve users.
    """
    return fake_users_db[skip : skip + limit]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    """
    Create new user.
    """
    for u in fake_users_db:
        if u.email == user_in.email:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user_in.email,
        "is_active": user_in.is_active,
        "is_superuser": user_in.is_superuser,
        "full_name": user_in.full_name,
        "hashed_password": user_in.password + "notreallyhashed"
    }
    fake_users_db.append(new_user)
    return new_user
