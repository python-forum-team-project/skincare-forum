from data.models.user import User
from services.auth_service import get_user_id_from_token
from services.users_service import get_user_by_id
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)

def resolve_user(token: str | None) -> User | None:
    if not token:
        return None

    user_id = get_user_id_from_token(token)

    if user_id is None:
        return None

    user = get_user_by_id(user_id)

    if user is None or user.is_blocked:
        return None

    return user

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> User:
    if credentials is None:
        raise HTTPException(401, "Not authenticated")

    user_id = get_user_id_from_token(credentials.credentials)
    user = get_user_by_id(user_id) if user_id is not None else None

    if user is None or user.is_blocked:
        raise HTTPException(401, "Not authenticated")

    return user