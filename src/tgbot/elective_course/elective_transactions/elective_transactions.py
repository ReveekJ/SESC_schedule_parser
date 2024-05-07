from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.tgbot.elective_course.elective_transactions.models import ElectiveCourseTransactionsModel
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.user_models.schemas import User
from src.tgbot.user_models.models import UsersModel


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
    async def get_users_by_course_name(session: AsyncSession, course: ElectiveCourse) -> list[User]:
        query = select(ElectiveCourseTransactionsModel).where(course_id=course.subject)
        result = await session.execute(query)
        await session.commit()
        users = []

        for user in result.scalars().all():
            users.append(User(**user.__dict__))
        return users

    @staticmethod
    async def add_elective_transaction(session: AsyncSession, user: User, course: ElectiveCourse) -> None:
        user_model = UsersModel(**user.model_dump())
        course_model = ElectiveCourseModel(**course.model_dump())

        user_model.elective_course_replied.append(course_model)
        # course_model.users_replied.append(user_model)
        transaction = ElectiveCourseTransactionsModel(course_name=course_model.subject, user_id=str(user_model.id))
        session.add(transaction)

        await session.commit()

    # @staticmethod
    # async def delete_elective_transaction(session: AsyncSession, user_id: int, course: ElectiveCourse) -> None:
    #     stmt = delete(ElectiveCourseTransactionsModel).where(user_id=user_id, course_name=course.subject)
    #     await session.execute(stmt)
    #     await session.commit()
