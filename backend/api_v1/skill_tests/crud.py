from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result


from .schemas import SkillTestCreate, SkillTestAnswers
from api_v1.skills.crud import get_skill_by_id
from core.models import SkillTest, UserRole, VacancyResponseTest
import exceptions
from auth.dependencies import check_access
from api_v1.dependencies import get_user_by_sub


async def create_skill_question(
    question: SkillTestCreate, session: AsyncSession
) -> SkillTest:
    await get_skill_by_id(session=session, skill_id=question.skill_id)
    skill_test = SkillTest(**question.model_dump())
    session.add(skill_test)
    await session.commit()
    return skill_test


async def get_test_by_skill(skill_id: int, session: AsyncSession) -> list[SkillTest]:
    stmt = select(SkillTest).where(SkillTest.skill_id == skill_id)
    result: Result = await session.execute(statement=stmt)
    test = list(result.scalars().all())
    if test is None:
        raise exceptions.NotFoundException.TEST_NOT_FOUND
    return test


async def accept_test(
    answers: list[SkillTestAnswers], session: AsyncSession, payload: dict
):
    user = await get_user_by_sub(payload=payload, session=session)
    check_access(user=user, role=UserRole.CANDIDATE)
    correct_answers = 0
    response_id = 0
    skill_id = 0
    for answer in answers:
        stmt = select(SkillTest).where(SkillTest.id == answer.info.get("question_id"))
        skill_test: SkillTest = await session.scalar(statement=stmt)
        if skill_test.correct_option_index == int(answer.info.get("answer_id")):
            correct_answers += 1
        response_id = answer.response_id
        skill_id = answer.skill_id

    percentage_of_correct = (correct_answers / len(answers)) * 100

    stmt = select(VacancyResponseTest).where(
        VacancyResponseTest.response_id == response_id,
        VacancyResponseTest.skill_id == skill_id,
    )
    result: Result = await session.execute(statement=stmt)
    vacancy_response_test: VacancyResponseTest = result.scalar_one_or_none()
    vacancy_response_test.score = percentage_of_correct
    vacancy_response_test.is_completed = True
    await session.commit()
    return {"message": "Success"}
