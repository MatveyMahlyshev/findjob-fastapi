from fastapi import APIRouter

from api_v1.skills.views import router as skills_router
from api_v1.users.views import router as users_router

router = APIRouter()
router.include_router(
    skills_router,
    prefix="/skills",
)
router.include_router(
    users_router,
    prefix="/users",
)

