from fastapi import APIRouter

from api_v1.skills.views import router as skills_router

router = APIRouter()
router.include_router(
    skills_router,
    prefix="/skills",
)

