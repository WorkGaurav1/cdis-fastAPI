from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    # Field constraints mirror Node's registerSchema exactly
    # (src/data-transfer-object/auth.dto.ts): trimmed email, name
    # 1-255 chars after trimming, password >= 8 chars.
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)

    @field_validator("email", "name", mode="before")
    @classmethod
    def _trim(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value
