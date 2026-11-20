import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.api.topics_routers import topics_router
from routers.api.user_routers import user_router
from routers.api.home_routers import home_router
from routers.web.web_home_routers import web_home_router
from routers.web.web_user_routers import web_user_router
from starlette.middleware.sessions import SessionMiddleware
from os import environ
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=environ["SESSION_SECRET"], same_site="lax", https_only=False)

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(topics_router)
app.include_router(user_router)
app.include_router(home_router)
app.include_router(web_home_router)
app.include_router(web_user_router)



if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)