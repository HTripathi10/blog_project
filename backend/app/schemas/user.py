"""
schemas/user.py — Pydantic schemas for User

💡 CONCEPT: Schemas vs Models
   Models (SQLAlchemy) = shape of the DATABASE table
   Schemas (Pydantic) = shape of the HTTP request/response JSON

   They are intentionally separate because:
   - You never want to expose hashed_password in an API response
   - You might accept different fields on create vs update
   - Pydantic validates & coerces types automatically
"""

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


# ── Request schemas (what the CLIENT sends) ──────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdateProfile(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None


# ── Response schemas (what the SERVER sends back) ────────────────────────────

class UserPublic(BaseModel):
    """Safe to expose publicly — no password, no sensitive fields"""
    id: int
    email: str
    name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    provider: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Allows building from SQLAlchemy model


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
