from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str
    user_type: str = "applicant"  # "applicant" or "admin"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    created_at: Optional[datetime] = None
    email: Optional[str] = None
    user_type: str