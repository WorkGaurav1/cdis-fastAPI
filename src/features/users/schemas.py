# Users Data Schemas.

from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

# (No internal imports for the base schemas)


class UserBase(SQLModel):
    # The base schema containing fields that are common across almost
    # all user models.
    # EmailStr automatically validates that the input is a properly
    # formatted email address
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# NOTE: there used to be UserCreate/UserResponse schemas here, for a
# POST /api/v1/users/ endpoint that was never actually wired up on the
# router (see tests/test_users.py's removed test_create_user). User
# creation is POST /auth/register (features/auth/schemas.py's
# RegisterRequest); removed rather than keeping unused dead code around.
