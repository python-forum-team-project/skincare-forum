from fastapi import APIRouter, HTTPException, Depends
from data.models.user import User, UserProfile, UserUpdate, UserCreate, BlockUpdate, RoleUpdate, LoginData
from services.users_service import register, login, get_user_profile, update_user_profile, self_delete_user
from services.auth_service import create_token
from common.auth import get_current_user


users_router = APIRouter(prefix='/users', tags=['Users'])


@users_router.post('', status_code=201)
def register_user(new_user: UserCreate) -> dict:
    new_user_id = register(new_user)

    if new_user_id is None:
        raise HTTPException(
            status_code=409,
            detail='Username or email address already exists'
        )

    return {'user_id' : new_user_id}


@users_router.post('/login', status_code=200)
def login_user(data: LoginData) -> dict:
    logged_or_not = login(data)

    if logged_or_not is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid username or password'
        )

    token = create_token(logged_or_not.user_id)

    return {'access_token' : token,
            'token_type' : 'bearer'}


@users_router.get('/me', status_code=200)
def my_profile(current_user: User = Depends(get_current_user)) -> UserProfile:
    user = get_user_profile(current_user)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    return user


@users_router.patch('/me', status_code=200)
def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user)) -> dict:
    updated_profile = update_user_profile(current_user, data)

    if updated_profile is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    if updated_profile is False:
        raise HTTPException(
            status_code=409,
            detail='Email address already exists'
        )

    return {'message' : 'Profile updated successfully'}


@users_router.delete('/me', status_code=204)
def delete_profile(current_user: User = Depends(get_current_user)) -> None:
    deleted_or_not = self_delete_user(current_user)

    if deleted_or_not is False:
        raise HTTPException(
            status_code=409,
            detail='Account could not be deactivated'
        )