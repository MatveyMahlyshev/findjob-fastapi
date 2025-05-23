from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload

from .schemas import VacancyBase, VacancyCreate, VacancyB
from core.models import (
    User,
    UserRole,
    Vacancy,
    Skill,
    VacancySkillAssociation,
    VacancyResponse,
    VacancyResponseStatus,
    VacancyResponseTest,
)
import exceptions
from auth.dependencies import check_access
from api_v1.dependencies import get_user_by_sub
from api_v1.profiles.dependencies import get_statement_for_candidate_profile
from api_v1.skills.crud import get_skill


async def create_vacancy(
    session: AsyncSession, payload: dict, vacancy_in: VacancyCreate
):
    user = await get_user_by_sub(payload=payload, session=session)
    check_access(user=user, role=UserRole.HR)

    vacancy_data = vacancy_in.model_dump()
    skills_data = vacancy_data.pop("vacancy_skills", [])

    stmt = select(Skill).where(Skill.title.in_(skills_data))
    result = await session.execute(stmt)

    vacancy = Vacancy(**vacancy_data, hr_id=user.id)
    session.add(vacancy)
    await session.flush()

    for title in skills_data:
        skill = await get_skill(session=session, title=title)
        assoc = VacancySkillAssociation(vacancy_id=vacancy.id, skill_id=skill.id)
        session.add(assoc)

    await session.commit()
    return {
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": [{"skill": {"title": title}} for title in skills_data],
    }


async def get_vacanies(session: AsyncSession) -> list[VacancyB]:
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.responses),
            selectinload(Vacancy.vacancy_skills).selectinload(
                VacancySkillAssociation.skill
            ),
        )
        .order_by(Vacancy.id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancies = list(result.scalars().all())
    return [
        {
            "id": vacancy.id,
            "title": vacancy.title,
            "company": vacancy.company,
            "description": vacancy.description,
            "vacancy_skills": vacancy.vacancy_skills,
            "responses": len(vacancy.responses),
        }
        for vacancy in vacancies
    ]


async def get_vacancy_by_id(vacancy_id: int, session: AsyncSession) -> VacancyB:
    stmt = (
        select(Vacancy)
        .options(
            selectinload(Vacancy.responses),
            selectinload(Vacancy.vacancy_skills).selectinload(
                VacancySkillAssociation.skill
            ),
        )
        .where(Vacancy.id == vacancy_id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancy: Vacancy = result.scalar_one_or_none()
    if vacancy is None:
        raise exceptions.NotFoundException.VACANCY_NOT_FOUND
    return {
        "id": vacancy.id,
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": vacancy.vacancy_skills,
        "responses": len(vacancy.responses),
    }


async def get_vacancies_by_user(payload: dict, session: AsyncSession) -> list[VacancyB]:
    stmt = (
        select(User)
        .options(
            selectinload(User.vacancy),
            selectinload(User.vacancy, Vacancy.responses),
            selectinload(User.vacancy, Vacancy.vacancy_skills),
            selectinload(
                User.vacancy, Vacancy.vacancy_skills, VacancySkillAssociation.skill
            ),
        )
        .where(User.email == payload.get("sub"))
    )
    user = await get_user_by_sub(payload=payload, session=session, stmt=stmt)
    check_access(user=user, role=UserRole.HR)
    return [
        {
            "id": vacancy.id,
            "title": vacancy.title,
            "company": vacancy.company,
            "description": vacancy.description,
            "vacancy_skills": vacancy.vacancy_skills,
            "responses": len(vacancy.responses),
        }
        for vacancy in user.vacancy
    ]


async def update_vacancy(
    vacancy_in: VacancyBase, vacancy_id: int, payload: dict, session: AsyncSession
):

    user = await get_user_by_sub(payload=payload, session=session)
    check_access(user=user, role=UserRole.HR)
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
    user = await get_user_by_sub(payload=payload, session=session)
    check_access(user=user, role=UserRole.HR)
    vacancy = await session.get(Vacancy, vacancy_id)
    await session.delete(vacancy)
    await session.commit()
    return None


async def vacancy_respond(vacancy_id: int, payload: dict, session: AsyncSession):
    user = await get_user_by_sub(
        payload=payload,
        session=session,
        stmt=get_statement_for_candidate_profile(payload=payload),
    )
    check_access(user=user, role=UserRole.CANDIDATE)
    vacancy = await get_vacancy_by_id(vacancy_id=vacancy_id, session=session)

    vacancy_skills = set(i.skill.title for i in vacancy.vacancy_skills)
    candidate_skills = set(i.skill.title for i in user.candidate_profile.profile_skills)

    intersection = vacancy_skills & candidate_skills
    percent_match = len(intersection) / len(vacancy_skills) * 100
    response = VacancyResponse(
        candidate_profile_id=user.candidate_profile.id,
        vacancy_id=vacancy_id,
        status=VacancyResponseStatus.rejected,
    )
    if percent_match < 70.0:
        session.add(response)
        await session.commit()
        return {
            "detail": "К сожалению, ваши навыки не соответствуют требуемым навыкам компании. Спасибо за отклик!"
        }
    response.status = VacancyResponseStatus.test_sent
    session.add(response)
    await session.flush()
    for skill_title in intersection:
        skill = await get_skill(session=session, title=skill_title)
        test = VacancyResponseTest(
            response_id=response.id,
            skill_id=skill.id,
            is_completed=False,
        )
        session.add(test)

    await session.commit()
    return {"detail": f"Отклик принят. Назначено тестов: {len(intersection)}."}
