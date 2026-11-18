import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.api.topics_routers import topics_router
from routers.api.users_routers import users_router

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(topics_router)
app.include_router(users_router)




if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)