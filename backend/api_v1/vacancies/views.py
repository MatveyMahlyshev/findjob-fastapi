from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from auth.dependencies import http_bearer, get_current_token_payload
from core.models import db_helper
from . import crud
from .schemas import VacancyBase, Vacancy

router = APIRouter(tags=["Vacancy"])

router_with_auth = APIRouter(dependencies=[Depends(http_bearer)])
router_without_auth = APIRouter()


@router_with_auth.post("/new/", response_model=Vacancy)
async def create_vacancy(
    vacancy: VacancyBase,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_vacancy(session=session, payload=payload, vacancy_in=vacancy)


@router_without_auth.get("/")
async def get_vacancy():
    pass


@router_without_auth.get("/id/{vacancy_id}/")
async def get_vacancy_by_id():
    pass


@router_with_auth.put("/edit/")
async def update_vacancy():
    pass


@router_with_auth.delete("/delete/")
async def delete_vacancy():
    pass


router.include_router(router=router_with_auth)
router.include_router(router=router_without_auth)
