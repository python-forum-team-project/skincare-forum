import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.api.topics_routers import topics_router
from routers.api.user_routers import user_router
from routers.api.home_routers import home_router

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(topics_router)
app.include_router(user_router)
app.include_router(home_router)




if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)