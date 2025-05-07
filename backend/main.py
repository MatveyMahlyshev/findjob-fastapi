from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from api_v1 import router as api_v1_router
from core.config import settings
from users.views import router as users_router
from auth.views import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(
    router=api_v1_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(router=users_router)
app.include_router(router=auth_router)


@app.get("/")
def index():
    return {
        "message": "index",
    }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
