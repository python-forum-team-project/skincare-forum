from fastapi import APIRouter, HTTPException, Depends, Query
from data.models.user import User, UserProfile, UserUpdate, UserCreate, BlockUpdate, RoleUpdate, LoginData
from services.users_service import register, login, get_user_profile, update_user_profile, self_delete_user, admin_search_users, admin_set_blocked, admin_set_role
from services.auth_service import create_token
from common.auth import get_current_user, get_current_admin
from common.errors import EXISTING_USERNAME_OR_EMAIL


user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.post('', status_code=201)
def register_user(new_user: UserCreate) -> dict:
    new_user_id = register(new_user)

    if new_user_id is None:
        raise HTTPException(
            status_code=409,
            detail=EXISTING_USERNAME_OR_EMAIL
        )

    return {'user_id' : new_user_id}


@user_router.post('/login', status_code=200)
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


@user_router.get('/me', response_model=UserProfile , status_code=200)
def my_profile(current_user: User = Depends(get_current_user)) -> UserProfile:
    user = get_user_profile(current_user)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    return user


@user_router.patch('/me', status_code=200)
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


@user_router.delete('/me', status_code=204)
def delete_profile(current_user: User = Depends(get_current_user)) -> None:
    deleted_or_not = self_delete_user(current_user)

    if deleted_or_not is False:
        raise HTTPException(
            status_code=409,
            detail='Account could not be deactivated'
        )

@user_router.get('', response_model=list[UserProfile])
def admin_search(search: str, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), current_user: User = Depends(get_current_admin)) -> list[UserProfile]:
    result = admin_search_users(current_user, search, limit, offset)

    if result is None:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return result


@user_router.patch('/{user_id}/block', status_code=200)
def admin_block_user(user_id: int, data: BlockUpdate, current_user: User = Depends(get_current_admin)) -> dict:
    result = admin_set_blocked(current_user, user_id, data.is_blocked)

    if result[0] == False:
        if result[1] == 'not_admin':
            raise HTTPException(
                status_code=403,
                detail='Admin access required'
            )
        elif result[1] == 'self_change':
            raise HTTPException(
                status_code=403,
                detail='Can not change your status'
            )
        elif result[1] == 'not_found':
            raise HTTPException(
                status_code=404,
                detail='User not found'
            )

    return {"message": "User status updated successfully"}


@user_router.patch('/{user_id}/role', status_code=200)
def admin_change_role(user_id: int, data: RoleUpdate, current_user: User = Depends(get_current_admin)) -> dict:
    result = admin_set_role(current_user, user_id, data.role_name)

    if result[0] == False:
        if result[1] == 'not_admin':
            raise HTTPException(
                status_code=403,
                detail='Admin access required'
            )
        elif result[1] == 'self_change':
            raise HTTPException(
                status_code=403,
                detail='Can not change your role'
            )
        elif result[1] == 'not_found':
            raise HTTPException(
                status_code=404,
                detail='User not found'
            )
        elif result[1] == 'invalid_role':
            raise HTTPException(
                status_code=422,
                detail='Invalid role'
            )
        elif result[1] == 'invalid_change':
            raise HTTPException(
                status_code=403,
                detail='Can not demote Admin'
            )

    return {"message": "User role updated successfully"}