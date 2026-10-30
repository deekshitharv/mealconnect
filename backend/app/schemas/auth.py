from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from app.core.security import MAX_PASSWORD_BYTES

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]


class UserRegister(BaseModel):
    name: Name = Field(examples=["Asha Rao"])
    email: EmailStr = Field(examples=["asha@example.com"])
    password: str = Field(min_length=8, max_length=72, examples=["StrongPass123"])
    # ADMIN is deliberately not allowed here.
    role: Literal["USER", "PROVIDER"] = "USER"

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_not_too_long(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError("Password is too long (maximum 72 bytes)")
        return value


class UserLogin(BaseModel):
    email: EmailStr = Field(examples=["asha@example.com"])
    password: str = Field(min_length=1, max_length=200, examples=["StrongPass123"])

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class UserOut(BaseModel):
    """What we send back about a user. Note: no password_hash here."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    