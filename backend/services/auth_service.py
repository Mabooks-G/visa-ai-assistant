"""Auth service: register, login, authenticate users via Supabase + custom tokens."""

import hashlib
import secrets
from datetime import datetime, timezone

from backend.database.db import get_supabase
from backend.middleware.auth import store_token, remove_token


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt."""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f'{salt}:{h}'


def _verify_password(password: str, stored: str) -> bool:
    """Verify a password against its stored hash."""
    try:
        salt, h = stored.split(':', 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    except (ValueError, AttributeError):
        return False


def _generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_hex(32)


def register_user(email: str, password: str, user_type: str = 'user') -> dict:
    """Register a new user in the users table."""
    sb = get_supabase()

    # Check if email already exists
    existing = sb.table('users').select('id').eq('email', email).execute()
    if existing.data and len(existing.data) > 0:
        raise ValueError('Email already registered')

    hashed = _hash_password(password)
    result = sb.table('users').insert({
        'email': email,
        'password': hashed,
        'user_type': user_type,
    }).execute()

    if not result.data or len(result.data) == 0:
        raise RuntimeError('Failed to create user')

    user = result.data[0]
    # Strip password from returned data
    user.pop('password', None)
    return user


def login_user(email: str, password: str) -> dict:
    """Authenticate a user and return a token + user data."""
    sb = get_supabase()

    result = sb.table('users').select('*').eq('email', email).execute()
    if not result.data or len(result.data) == 0:
        raise ValueError('Invalid email or password')

    user = result.data[0]

    if not _verify_password(password, user.get('password', '')):
        raise ValueError('Invalid email or password')

    # Generate token and store
    token = _generate_token()
    user_data = {k: v for k, v in user.items() if k != 'password'}
    store_token(token, user_data)

    return {
        'token': token,
        'user': user_data,
    }


def logout_user(token: str) -> None:
    """Remove a token from the active session store."""
    remove_token(token)


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a user by their UUID."""
    sb = get_supabase()
    result = sb.table('users').select('*').eq('id', user_id).execute()
    if result.data and len(result.data) > 0:
        user = result.data[0]
        user.pop('password', None)
        return user
    return None