from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str = Field(..., description="User ID")
    email: EmailStr
    name: str
    is_verified: bool
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class EmailRequest(BaseModel):
    email: EmailStr
