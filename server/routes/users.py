"""
User routes — registration, login, and profile management.
"""

import hashlib
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from server.database import db
from server.models.user import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _hash_password(password: str) -> str:
    """Simple password hashing (not production-grade — for hackathon use)."""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate):
    """Register a new applicant account."""
    # Check if email already exists
    existing = db.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create user — all new users are 'applicant' type
    user_data = {
        "email": payload.email,
        "password": _hash_password(payload.password),
        "user_type": "applicant",  # Always applicant by default
    }
    user = db.create_user(user_data)
    return {
        "id": user["id"],
        "email": user.get("email"),
        "user_type": user.get("user_type", "applicant"),
        "created_at": user.get("created_at"),
    }


@router.post("/login")
def login(payload: UserLogin):
    """Login with email and password."""
    user = db.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    stored_hash = user.get("password", "")
    if _hash_password(payload.password) != stored_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "user": {
            "id": user["id"],
            "email": user.get("email"),
            "user_type": user.get("user_type", "applicant"),
        },
        "token": f"simple-token-{user['id']}",  # Simple token for hackathon
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """Get user details by ID."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "email": user.get("email"),
        "user_type": user.get("user_type", "applicant"),
        "created_at": user.get("created_at"),
    }