from fastapi import APIRouter

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

# @router.get("/candidate/me/")
