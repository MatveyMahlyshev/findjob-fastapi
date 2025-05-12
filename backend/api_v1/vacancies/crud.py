from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from .schemas import VacancyCreate
from api_v1.dependencies import get_user
from core.models import User, UserRole, Vacancy, Skill, VacancySkillAssociation
import exceptions
from api_v1.skills.crud import get_skill
from auth.dependencies import check_access

async def create_vacancy(
    session: AsyncSession, payload: dict, vacancy_in: VacancyCreate
):
    email = payload.get("sub")
    stmt = select(User).where(User.email == email)
    user = await get_user(session=session, email=email, stmt=stmt)

    await check_access(user=user, role=UserRole.HR)
    vacancy_data = vacancy_in.model_dump()
    skills_data: list[dict[str, str]] = vacancy_data.pop("vacancy_skills", [])

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
    await session.commit()
    return {
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": skills_data,
    }

async def get_vacanies(session: AsyncSession):
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.vacancy_skills).selectinload(VacancySkillAssociation.skill)
        )
        .order_by(Vacancy.id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancies = list(result.scalars().all())
    return vacancies
