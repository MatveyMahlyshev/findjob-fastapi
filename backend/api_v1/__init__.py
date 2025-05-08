from fastapi import APIRouter

from api_v1.skills.views import router as skills_router
from auth.views import router as auth_router
from api_v1.profiles.views import router as profile_router

router = APIRouter()
router.include_router(
    skills_router,
    prefix="/skills",
)
router.include_router(
    router=auth_router,
    prefix="/auth",
)
router.include_router(
    router=profile_router,
    prefix="/profile",
)
