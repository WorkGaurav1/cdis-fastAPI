from sqlmodel import Field
from typing import Optional
from app.schemas.user import UserBase

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
