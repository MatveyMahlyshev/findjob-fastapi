from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload
from openpyxl import Workbook
from io import BytesIO
from statistics import mean
from fastapi import Response

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
    CandidateProfile,
)
import exceptions
from auth.dependencies import check_access
from api_v1.dependencies import get_user_by_sub
from api_v1.profiles.dependencies import get_statement_for_candidate_profile
from api_v1.skills.crud import get_skill, get_skill_by_id


async def create_vacancy(
    session: AsyncSession, payload: dict, vacancy_in: VacancyCreate
):
    user = await get_user_by_sub(payload=payload, session=session)
    check_access(user=user, role=UserRole.HR)

    vacancy_data = vacancy_in.model_dump()
    skills_data = vacancy_data.pop("vacancy_skills", [])

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
            selectinload(Vacancy.hr),
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
    vacancy_in: VacancyCreate, vacancy_id: int, payload: dict, session: AsyncSession
):

    user = await get_user_by_sub(payload=payload, session=session)
    await check_access(user=user, role=UserRole.HR)
    stmt = (
        select(Vacancy)
        .options(selectinload(Vacancy.vacancy_skills))
        .where(Vacancy.id == vacancy_id)
    )
    result: Result = await session.execute(statement=stmt)
    vacancy = result.scalar_one_or_none()

    if vacancy.hr_id != user.id:
        raise exceptions.AccessDeniesException.ACCESS_DENIED
    vacancy.company = vacancy_in.company
    vacancy.description = vacancy_in.description
    vacancy.title = vacancy_in.title
    session.add(vacancy)

    for association in vacancy.vacancy_skills:
        await session.delete(association)
    await session.flush()
    vacancy_skills = []
    for skill in vacancy_in.vacancy_skills:
        s = await get_skill(session=session, title=skill)
        assoc = VacancySkillAssociation(vacancy_id=vacancy.id, skill_id=s.id)
        session.add(assoc)
        vacancy_skills.append(s.title)

    await session.commit()
    return {
        "title": vacancy.title,
        "company": vacancy.company,
        "description": vacancy.description,
        "vacancy_skills": vacancy_skills,
    }


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

    vacancy_skills = set(i.skill.title for i in vacancy["vacancy_skills"])
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


async def get_data_for_excel(vacancy_id: int, session: AsyncSession):
    stmt = (
        select(User)
        .join(User.candidate_profile)
        .join(CandidateProfile.vacancy_responses)
        .options(
            selectinload(User.candidate_profile)
            .selectinload(CandidateProfile.vacancy_responses)
            .selectinload(VacancyResponse.tests),
            selectinload(User.candidate_profile).selectinload(
                CandidateProfile.profile_skills
            ),
        )
        .where(
            User.role == UserRole.CANDIDATE,
            VacancyResponse.vacancy_id == vacancy_id,
        )
    )

    result: Result = await session.execute(statement=stmt)
    users: list[User] = result.scalars().all()
    successful_users: list[User] = []
    for user in users:
        for response in user.candidate_profile.vacancy_responses:
            if response.vacancy_id == vacancy_id:
                for test in response.tests:
                    if not test.is_completed or test.score == 0.0:
                        break
                else:
                    successful_users.append(user)

    stmt = select(Skill).options(selectinload(Skill.skill_vacancies))
    result = await session.execute(statement=stmt)
    vacancy_skills = [i.title for i in result.scalars().all()]
    return {
        "candidates": [
            {
                "email": user.email,
                "name": f"{user.candidate_profile.surname} {user.candidate_profile.name} {user.candidate_profile.patronymic}",
                "age": user.candidate_profile.age,
                "about": user.candidate_profile.about_candidate,
                "education": user.candidate_profile.education,
                "skills": [
                    {
                        "title": (
                            await get_skill_by_id(
                                session=session, skill_id=skill.skill_id
                            )
                        ).title,
                        "score": f"{next(  
                            (
                                test.score
                                for response in user.candidate_profile.vacancy_responses
                                for test in response.tests
                                if response.vacancy_id == vacancy_id
                                and test.skill_id == skill.skill_id
                                and test.response_id == response.id
                            ), "N/A"
                        )}%",
                    }
                    for skill in user.candidate_profile.profile_skills
                ],
            }
            for user in successful_users
        ],
        "vacancy_skills": vacancy_skills,
    }


async def get_candidates_by_responses(
    vacancy_id: int,
    session: AsyncSession,
    payload: dict,
):
    user = await get_user_by_sub(
        payload=payload,
        session=session,
    )
    check_access(user=user, role=UserRole.HR)

    response_data = await get_data_for_excel(vacancy_id=vacancy_id, session=session)

    candidates = response_data["candidates"]
    vacancy_skills = response_data["vacancy_skills"]  # Список строк

    # Добавляем средний балл и фильтруем кандидатов
    processed_candidates = []
    for candidate in candidates:
        skills_dict = {skill["title"]: skill["score"] for skill in candidate["skills"]}

        # Считаем средний балл (игнорируем "N/A")
        scores = []
        for skill_name in vacancy_skills:
            score = skills_dict.get(skill_name, "N/A")
            if score != "N/A":
                try:
                    scores.append(float(score.strip("%")))
                except (ValueError, AttributeError):
                    pass

        avg_score = round(mean(scores), 2) if scores else 0

        processed_candidates.append(
            {**candidate, "skills_dict": skills_dict, "avg_score": avg_score}
        )

    # Сортируем по среднему баллу (по убыванию)
    processed_candidates.sort(key=lambda x: x["avg_score"], reverse=True)

    # Создаем Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Кандидаты"

    # Формируем заголовки (добавляем столбец для среднего балла)
    headers = (
        ["Email", "ФИО", "Возраст", "О себе", "Образование"]
        + vacancy_skills
        + ["Средний балл"]
    )
    ws.append(headers)

    # Заполняем данные
    for candidate in processed_candidates:
        row_data = [
            candidate["email"],
            candidate["name"],
            candidate["age"],
            candidate["about"],
            candidate["education"],
        ]

        # Добавляем оценки навыков
        for skill_name in vacancy_skills:
            row_data.append(candidate["skills_dict"].get(skill_name, "N/A"))

        # Добавляем средний балл
        row_data.append(f"{candidate['avg_score']}%")

        ws.append(row_data)

    # Автонастройка ширины столбцов
    for column in ws.columns:
        column_letter = column[0].column_letter
        max_length = max((len(str(cell.value)) for cell in column) if column else 0)
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = adjusted_width

    # Подготовка файла для скачивания
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=vacancy_responds.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
