import asyncio

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse


class ElectiveCourseDB:
    @staticmethod
    async def add_course(session: AsyncSession, course: ElectiveCourse):
        session.add(ElectiveCourseModel(**course.model_dump()))
        await session.commit()

    @staticmethod
    async def delete_course(session: AsyncSession, course_name: str):
        stmt = delete(ElectiveCourseModel).where(ElectiveCourseModel.subject == course_name)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def update_course(session: AsyncSession, course_name: str, new_course: ElectiveCourse):
        course = new_course.model_dump(exclude={'id'})  # Exclude 'id' field

        stmt = (update(ElectiveCourseModel)
                .where(ElectiveCourseModel.subject == course_name)
                .values(**course))
        # query = select(ElectiveCourseModel).where(ElectiveCourseModel.subject == course_name)

        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def cancel_course(session: AsyncSession, course_name: str):
        old_course = (await ElectiveCourseDB.get_courses_by_subject(session, course_name))[0]
        new_course = ElectiveCourse(subject=old_course.subject,
                                    teacher_name=old_course.teacher_name,
                                    pulpit=old_course.pulpit,
                                    weekday=old_course.weekday,
                                    time_from=old_course.time_from,
                                    time_to=old_course.time_to,
                                    auditory=old_course.auditory,
                                    is_cancelled=True)

        await ElectiveCourseDB.update_course(session, course_name, new_course)

    @classmethod
    async def get_courses_by_subject(cls, session: AsyncSession, subject: str) -> list[ElectiveCourse]:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.subject == subject)
        result = await cls.__query_to_list_of_elective(session, query)
        return result

    @classmethod
    async def get_courses_by_pulpit(cls, session: AsyncSession, pulpit: str) -> list[ElectiveCourse]:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.pulpit == pulpit)
        result = await cls.__query_to_list_of_elective(session, query)
        return result

    @staticmethod
    async def __query_to_list_of_elective(session: AsyncSession, query) -> list[ElectiveCourse]:
        query_res = await session.execute(query)
        result = []

        for course in query_res.scalars().all():
            result.append(ElectiveCourse(**course.__dict__))

        return result
