from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from services.users_service import register, login, get_user_profile, self_delete_user, update_user_profile
from data.models.user import UserCreate, LoginData, UserUpdate
from fastapi import Form
from pydantic import ValidationError
from common.errors import EXISTING_USERNAME_OR_EMAIL
from services.auth_service import create_token, EXPIRE_MINUTES
from common.auth import get_web_current_user
from common.csrf import csrf_context, verify_csrf

web_user_router = APIRouter(tags=['Web Users'])
templates = Jinja2Templates(directory='templates', context_processors=[csrf_context])


@web_user_router.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html',
                                      context={'error': None, 'current_user' : None})


@web_user_router.post('/register')
def register_user(request: Request, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)

    try:
        new_user = UserCreate(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
    except ValidationError:
       return templates.TemplateResponse(request=request, name='register.html',
                                         context={'error': 'Invalid registration data', 'current_user': None}, status_code=422)

    created_user_id = register(new_user)

    if created_user_id is None:
       return templates.TemplateResponse(request=request, name='register.html',
                                         context={'error': EXISTING_USERNAME_OR_EMAIL, 'current_user': None}, status_code=409)

    return RedirectResponse(url='/login', status_code=303)


@web_user_router.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name='login.html', context={'error': None, 'current_user': None})


@web_user_router.post('/login')
def login_user(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)

    try:
        login_data = LoginData(username=username, password=password)
    except ValidationError:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'error': 'Invalid login data', 'current_user': None}, status_code=422)

    logged_or_not = login(login_data)

    if logged_or_not is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'error': 'Invalid username or password', 'current_user': None}, status_code=401)

    token = create_token(logged_or_not.user_id)
    response = RedirectResponse(url='/',status_code=303)
    response.set_cookie(key='access_token', value=token, httponly=True, secure=False, samesite='lax', max_age=EXPIRE_MINUTES * 60)

    return response


@web_user_router.post('/logout')
def logout_user(request: Request, csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)

    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie(key='access_token')

    return response


@web_user_router.get('/profile', response_class=HTMLResponse)
def user_profile(request: Request):
    current_user = get_web_current_user(request)

    if current_user is None:
        return RedirectResponse(url='/', status_code=303)

    profile = get_user_profile(current_user)

    message = request.session.pop('success_message', None)

    return templates.TemplateResponse(request=request, name='profile.html',
                                      context={'error': None, 'message': message, 'current_user': current_user, 'profile': profile})


@web_user_router.post('/profile/delete')
def delete_user(request: Request, username: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)

    current_user = get_web_current_user(request)

    if current_user is None:
        return RedirectResponse(url='/', status_code=303)

    profile = get_user_profile(current_user)

    try:
        confirmed_user = login(LoginData(username=username, password=password))
    except ValidationError:
        confirmed_user = None

    if confirmed_user is None or confirmed_user.user_id != current_user.user_id:
        return templates.TemplateResponse(request=request, name='profile.html',
                                          context={'error': 'Invalid username or password', 'current_user': current_user, 'profile': profile}, status_code=401)

    is_deleted = self_delete_user(current_user)

    if is_deleted is False:
        return RedirectResponse(url='/profile', status_code=303)

    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie(key='access_token')

    return response


@web_user_router.get('/profile/edit', response_class=HTMLResponse)
def edit_profile_page(request: Request):
    current_user = get_web_current_user(request)

    if current_user is None:
        return RedirectResponse(url='/login', status_code=303)

    profile = get_user_profile(current_user)

    return templates.TemplateResponse( request=request, name='edit_profile.html',
                                       context={'error': None, 'current_user': current_user, 'profile': profile})


@web_user_router.post('/profile/edit')
def update_user(request: Request, first_name: str | None = Form(None), last_name: str | None = Form(None), email: str | None = Form(None), csrf_token: str = Form(...)):
    verify_csrf(request, csrf_token)

    current_user = get_web_current_user(request)

    if current_user is None:
        return RedirectResponse(url='/', status_code=303)

    profile = get_user_profile(current_user)

    first_name = (first_name or '').strip() or None
    last_name = (last_name or '').strip() or None
    email = (email or '').strip() or None

    try:
        user_update = UserUpdate(first_name=first_name, last_name=last_name, email=email)
    except ValidationError:
        return templates.TemplateResponse(request=request, name='edit_profile.html',
                                          context={'error': 'Invalid data', 'current_user': current_user, 'profile': profile}, status_code=422)

    updated_or_not = update_user_profile(current_user, user_update)

    if updated_or_not is False:
        return templates.TemplateResponse(request=request, name='edit_profile.html',
                                          context={'error': 'Could not update profile. Email is already in use.', 'current_user': current_user, 'profile': profile}, status_code=409)

    if updated_or_not is None:
        return RedirectResponse(url='/', status_code=303)

    request.session['success_message'] = 'Profile updated successfully'

    return RedirectResponse(url='/profile', status_code=303)