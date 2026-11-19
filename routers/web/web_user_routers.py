from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from services.users_service import register, login
from data.models.user import UserCreate, LoginData
from fastapi import Form
from pydantic import ValidationError
from common.errors import EXISTING_USERNAME_OR_EMAIL
from services.auth_service import create_token, EXPIRE_MINUTES

web_user_router = APIRouter(tags=['Web Users'])
templates = Jinja2Templates(directory='templates')


@web_user_router.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html', context={'error': None, 'current_user' : None})


@web_user_router.post('/register')
def register_user(request: Request, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), username: str = Form(...), password: str = Form(...)):
    try:
        new_user = UserCreate(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
    except ValidationError:
       return templates.TemplateResponse(request=request, name='register.html', context={'error': 'Invalid registration data', 'current_user': None}, status_code=422)

    created_user_id = register(new_user)

    if created_user_id is None:
       return templates.TemplateResponse(request=request, name='register.html', context={'error': EXISTING_USERNAME_OR_EMAIL, 'current_user': None}, status_code=409)

    return RedirectResponse(url='/login', status_code=303)


@web_user_router.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name='login.html', context={'error': None, 'current_user': None})


@web_user_router.post('/login')
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        login_data = LoginData(username=username, password=password)
    except ValidationError:
        return templates.TemplateResponse(request=request, name='login.html', context={'error': 'Invalid login data', 'current_user': None}, status_code=422)

    logged_or_not = login(login_data)

    if logged_or_not is None:
        return templates.TemplateResponse(request=request, name='login.html', context={'error': 'Invalid username or password', 'current_user': None})

    token = create_token(logged_or_not.user_id)
    response = RedirectResponse(url='/',status_code=303)
    response.set_cookie(key='access_token', value=token, httponly=True, secure=False, samesite='lax', max_age=EXPIRE_MINUTES * 60)

    return response