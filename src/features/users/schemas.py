"""
Users Data Schemas.
This file defines the Pydantic (SQLModel) schemas used for data validation.
These schemas dictate exactly what data is allowed to flow in (requests) and out (responses) of the API.
"""

# ---------------------------------------------------------
# External Imports
# ---------------------------------------------------------
from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

# ---------------------------------------------------------
# Internal Imports
# ---------------------------------------------------------
# (No internal imports for the base schemas)

class UserBase(SQLModel):
    """
    The base schema containing fields that are common across almost all user models.
    """
    # EmailStr automatically validates that the input is a properly formatted email address
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """
    The schema used when a client wants to create a new user via a POST request.
    It requires a raw password, which will be hashed before hitting the database.
    """
    password: str

class UserResponse(UserBase):
    """
    The schema used to send user data back to the client.
    Crucially, it includes the 'id' but DOES NOT include the 'password' or 'hashed_password'.
    FastAPI will automatically strip those out for security.
    """
    id: int
