from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.tgbot.elective_course.elective_transactions.models import ElectiveCourseTransactionsModel
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.user_models.models import UsersModel
from src.tgbot.user_models.schemas import User


class ElectiveTransactions:
    @staticmethod
    async def get_courses_by_user_id(session: AsyncSession, user_id: int) -> list[ElectiveCourse]:
        query = select(ElectiveCourseTransactionsModel).where(user_id=user_id)
        result = await session.execute(query)
        await session.commit()
        elective_courses = []

        for i in result.scalars().all():
            elective_courses.append(ElectiveCourse(**i.__dict__))

        return elective_courses

    @staticmethod
    async def get_user_ids_by_course_id(course: ElectiveCourse) -> list[int]:
        async with await get_async_session() as session:
            query = select(ElectiveCourseTransactionsModel).where(ElectiveCourseTransactionsModel.course_name == course.id)
            result = await session.execute(query)

        return [int(i.user_id) for i in result.scalars().all()]

    @staticmethod
    async def add_elective_transaction(session: AsyncSession, user: User, course: ElectiveCourse) -> None:
        user_model = UsersModel(**user.model_dump(mode='elective_transaction'))
        course_model = ElectiveCourseModel(**course.model_dump())

        user_model.elective_course_replied.append(course_model)  # добавлять к course не нужно так как при добавлении
        # в user в course добавляется автоматически
        transaction = ElectiveCourseTransactionsModel(course_name=course_model.id, user_id=user_model.id)
        session.add(transaction)

        await session.commit()

    @staticmethod
    async def delete_elective_transaction(session: AsyncSession, user_id: int, courses: list[ElectiveCourse]) -> None:
        for course in courses:
            if isinstance(course, ElectiveCourse):
                course = ElectiveCourseModel(**course.model_dump())

            stmt = delete(ElectiveCourseTransactionsModel).where(
                ElectiveCourseTransactionsModel.user_id == user_id,
                ElectiveCourseTransactionsModel.course_name == course.id)
            await session.execute(stmt)

        await session.commit()
