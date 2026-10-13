from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: List[str] = []


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str