from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .schemas import VacancyCreate
from api_v1.dependencies import get_user
from core.models import User, UserRole, Vacancy, Skill
import exceptions


async def create_vacancy(
    session: AsyncSession, payload: dict, vacancy_in: VacancyCreate
):
    email = payload.get("sub")
    stmt = select(User).where(User.email == email)
    user = await get_user(session=session, email=email, stmt=stmt)

    if user.role != UserRole.HR:
        raise exceptions.AccessDeniesException.ACCESS_DENIED
    vacancy_data = vacancy_in.model_dump()
    skills_data:dict[str, str] = vacancy_data.pop("vacancy_skills", [])

    vacancy = Vacancy(**vacancy_data)
    for skill in skills_data:
        print(skill)
    print(vacancy.vacancy_skills)
    session.add(vacancy)
    await session.commit()
    return vacancy
