from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from api_v1 import router as api_v1_router
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(
    router=api_v1_router,
    prefix=settings.api_v1_prefix,
)



@app.get("/")
def index():
    return {
        "message": "index",
    }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
