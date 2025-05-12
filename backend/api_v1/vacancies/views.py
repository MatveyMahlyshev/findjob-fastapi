from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from auth.dependencies import http_bearer, get_current_token_payload
from core.models import db_helper
from . import crud
from .schemas import VacancyCreate, Vacancy

router = APIRouter(tags=["Vacancy"])

router_with_auth = APIRouter(dependencies=[Depends(http_bearer)])
router_without_auth = APIRouter()


@router_with_auth.post("/new/", response_model=VacancyCreate)
async def create_vacancy(
    vacancy: VacancyCreate,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_vacancy(
        session=session, payload=payload, vacancy_in=vacancy
    )


@router_without_auth.get("/", response_model=list[Vacancy])
async def get_vacancies(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_vacanies(session=session)


@router_without_auth.get("/id/{vacancy_id}/", response_model=Vacancy)
async def get_vacancy_by_id(
    vacancy_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_vacancy_by_id(vacancy_id=vacancy_id, session=session)


@router_with_auth.put("/edit/")
async def update_vacancy():
    pass


@router_with_auth.delete("/delete/")
async def delete_vacancy():
    pass


router.include_router(router=router_with_auth)
router.include_router(router=router_without_auth)
