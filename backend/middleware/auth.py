from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ── In-memory token store (MVP only — use Redis for production) ────────────
_token_store: dict[str, dict] = {}
_security = HTTPBearer(auto_error=False)


def store_token(token: str, user: dict) -> None:
    _token_store[token] = user


def remove_token(token: str) -> None:
    _token_store.pop(token, None)


def get_user_by_token(token: str) -> dict | None:
    return _token_store.get(token)


def get_active_tokens_count() -> int:
    return len(_token_store)


# ── Dependency guards ──────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail='Authentication required')
    user = get_user_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    return user


async def get_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user.get('user_type') != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    return current_user


# Alias used by routes
admin_required = get_admin_user