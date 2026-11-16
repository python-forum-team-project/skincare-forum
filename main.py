from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.api.topics_routers import topics_router

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(topics_router)