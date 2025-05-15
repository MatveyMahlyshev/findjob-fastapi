from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # или ["*"] для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {
        "message": "index",
    }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
