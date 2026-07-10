"""User authentication routes — register, login, logout, me."""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr

from backend.services.auth_service import (
    register_user,
    login_user,
    logout_user,
)
from backend.middleware.auth import get_current_user

router = APIRouter(prefix='/api', tags=['auth'])


# ── Request / Response models ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    user_type: str = 'user'


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str | None = None
    user_type: str | None = None
    created_at: str | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post('/auth/register', response_model=AuthResponse)
async def register(body: RegisterRequest):
    """Register a new user account."""
    try:
        user = register_user(body.email, body.password, body.user_type)
        # Auto-login after registration
        result = login_user(body.email, body.password)
        return AuthResponse(token=result['token'], user=result['user'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/auth/login', response_model=AuthResponse)
async def login(body: LoginRequest):
    """Authenticate and receive a session token."""
    try:
        result = login_user(body.email, body.password)
        return AuthResponse(token=result['token'], user=result['user'])
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post('/auth/logout')
async def logout(request: Request, current_user: dict = Depends(get_current_user)):
    """Invalidate the current session token."""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '') if auth_header else ''
    if token:
        logout_user(token)
    return {'message': 'Logged out successfully'}


@router.get('/auth/me', response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserResponse(
        id=current_user.get('id', ''),
        email=current_user.get('email'),
        user_type=current_user.get('user_type'),
        created_at=current_user.get('created_at'),
    )