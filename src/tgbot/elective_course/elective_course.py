import json

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

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

    # TODO: fix it, now it does not work
    # @staticmethod
    # async def update_course(session: AsyncSession, course: ElectiveCourse):
    #     course.timetable = json.dumps(course.timetable)
    #     stmt = update(ElectiveCourseModel).where(ElectiveCourseModel.name == course.name).values(dict(course))
    #
    #     await session.execute(stmt)
    #     await session.commit()

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
