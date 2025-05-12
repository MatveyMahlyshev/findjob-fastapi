from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from .schemas import VacancyBase
from core.models import User, UserRole, Vacancy, VacancySkillAssociation
import exceptions
from api_v1.skills.crud import get_skill
from auth.dependencies import check_access
from api_v1.dependencies import get_user


async def create_vacancy(session: AsyncSession, payload: dict, vacancy_in: VacancyBase):

    email = payload.get("sub")
    stmt = select(User).where(User.email == email)
    user = await get_user(session=session, email=email, stmt=stmt)
    await check_access(user=user, role=UserRole.HR)
    vacancy_data = vacancy_in.model_dump()
    s_data: list[dict[dict[str, str]]] = vacancy_data.pop("vacancy_skills", [])
    skills_data = []
    for skill in s_data:
        skills_data.append(skill.get("skill"))
    vacancy = Vacancy(**vacancy_data)
    vacancy.hr_id = user.id
    session.add(vacancy)
    await session.flush()

    for skill_data in skills_data:
        title = skill_data.get("title")
        if title is None:
            raise exceptions.UnprocessableEntityException.NO_TITLE_KEY
        skill = await get_skill(session=session, title=title)
        association = VacancySkillAssociation(vacancy_id=vacancy.id, skill_id=skill.id)
        session.add(association)
    vacancy_skills = [{"skill": i} for i in skills_data]
    await session.commit()
    return {
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": vacancy_skills,
    }


async def get_vacanies(session: AsyncSession) -> list[Vacancy]:
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.vacancy_skills).selectinload(
                VacancySkillAssociation.skill
            )
        )
        .order_by(Vacancy.id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancies = list(result.scalars().all())
    return vacancies


async def get_vacancy_by_id(vacancy_id: int, session: AsyncSession) -> Vacancy:
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.vacancy_skills).selectinload(
                VacancySkillAssociation.skill
            )
        )
        .where(Vacancy.id == vacancy_id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancy: Vacancy = result.scalar_one_or_none()

    if vacancy is None:
        raise exceptions.NotFoundException.VACANCY_NOT_FOUND
    return vacancy


async def get_vacancies_by_user(payload: dict, session: AsyncSession) -> list[Vacancy]:
    email = payload.get("sub")
    stmt = (
        select(User)
        .options(
            selectinload(User.vacancies)
            .selectinload(Vacancy.vacancy_skills)
            .selectinload(VacancySkillAssociation.skill)
        )
        .where(User.email == email)
    )
    user = await get_user(session=session, email=email, stmt=stmt)
    await check_access(user=user, role=UserRole.HR)
    print(user.vacancies)
    for vacancy in user.vacancies:
        print(vacancy.hr_id)
    return user.vacancies
