from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from .schemas import VacancyBase
from core.models import User, UserRole, Vacancy, Skill, VacancySkillAssociation
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
    raw_skills = vacancy_data.pop("vacancy_skills", [])
    skills_data = [item.get("skill") for item in raw_skills]

    titles = [s.get("title") for s in skills_data]
    if any(t is None for t in titles):
        raise exceptions.UnprocessableEntityException.NO_TITLE_KEY

    stmt = select(Skill).where(Skill.title.in_(titles))
    result = await session.execute(stmt)
    skills = {skill.title: skill for skill in result.scalars()}

    vacancy = Vacancy(**vacancy_data, hr_id=user.id)
    session.add(vacancy)
    await session.flush()

    # Ассоциации
    associations = [
        VacancySkillAssociation(vacancy_id=vacancy.id, skill_id=skills[title].id)
        for title in titles
    ]
    session.add_all(associations)

    await session.commit()

    return {
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": [{"skill": {"title": title}} for title in titles],
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
            selectinload(User.vacancy)
            .selectinload(Vacancy.vacancy_skills)
            .selectinload(VacancySkillAssociation.skill)
        )
        .where(User.email == email)
    )
    user = await get_user(session=session, email=email, stmt=stmt)
    await check_access(user=user, role=UserRole.HR)

    return user.vacancy


async def update_vacancy(
    vacancy_in: VacancyBase, vacancy_id: int, payload: dict, session: AsyncSession
):

    email = payload.get("sub")
    stmt = select(User).where(User.email == email)
    user = await get_user(session=session, email=email, stmt=stmt)
    await check_access(user=user, role=UserRole.HR)

    vacancy = await get_vacancy_by_id(vacancy_id=vacancy_id, session=session)
    if vacancy.hr_id != user.id:
        raise exceptions.AccessDeniesException.ACCESS_DENIED
    vacancy.company = vacancy_in.company
    vacancy.description = vacancy_in.description
    vacancy.title = vacancy_in.title
    session.add(vacancy)
    await session.commit()
    return vacancy


async def delete_vacancy(vacancy_id: int, payload: dict, session: AsyncSession):
    email = payload.get("sub")
    stmt = select(User).where(User.email == email)
    user = await get_user(session=session, email=email, stmt=stmt)
    await check_access(user=user, role=UserRole.HR)

    vacancy = await get_vacancy_by_id(vacancy_id=vacancy_id, session=session)
    await session.delete(vacancy)
    await session.commit()
    return None
