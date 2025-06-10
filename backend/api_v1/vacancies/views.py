from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession


from auth.dependencies import http_bearer, get_current_token_payload
from core.models import db_helper

from .schemas import Vacancy, VacancyBase, VacancyCreate, VacancyB
from api_v1.vacancies import crud

router = APIRouter(tags=["Vacancy"])

router_with_auth = APIRouter(dependencies=[Depends(http_bearer)])
router_without_auth = APIRouter()


@router_with_auth.post("/new/", response_model=VacancyBase)
async def create_vacancy(
    vacancy: VacancyCreate,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_vacancy(
        session=session, payload=payload, vacancy_in=vacancy
    )


@router_with_auth.get("/company/", response_model=list[VacancyB])
async def get_vacancies_by_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_vacancies_by_user(payload=payload, session=session)


@router_without_auth.get("/", response_model=list[VacancyB])
async def get_vacancies(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_vacanies(session=session)


@router_without_auth.get("/id/{vacancy_id}/", response_model=VacancyB)
async def get_vacancy_by_id(
    vacancy_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_vacancy_by_id(vacancy_id=vacancy_id, session=session)


@router_with_auth.put("/vacancy/edit/{vacancy_id}/", response_model=Vacancy)
async def update_vacancy(
    vacancy_in: VacancyCreate,
    vacancy_id: int,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_vacancy(
        vacancy_in, vacancy_id=vacancy_id, payload=payload, session=session
    )


@router_with_auth.delete("/vacancy/delete/{vacancy_id}/")
async def delete_vacancy(
    vacancy_id: int,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.delete_vacancy(
        vacancy_id=vacancy_id, payload=payload, session=session
    )


@router_with_auth.post("/vacancy/{vacancy_id}/respond/")
async def vacancy_respond(
    vacancy_id: int,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.vacancy_respond(
        vacancy_id=vacancy_id, payload=payload, session=session
    )


@router_with_auth.get("/vacancy/{vacancy_id}/responds/")
async def get_vacancy_responds(
    vacancy_id: int,
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    # Получаем данные
    return await crud.get_candidates_by_responses(
        vacancy_id=vacancy_id, payload=payload, session=session
    )


router.include_router(router=router_without_auth)
router.include_router(router=router_with_auth)
