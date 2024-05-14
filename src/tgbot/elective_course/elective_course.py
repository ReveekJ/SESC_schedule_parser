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

    @staticmethod
    async def get_course(session: AsyncSession, course_name: str) -> ElectiveCourse:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.subject == course_name)
        res = await session.execute(query)
        res = res.first()[0]
        res.__dict__['timetable'] = json.loads(res.__dict__['timetable'])
        await session.commit()

        return ElectiveCourse(**res.__dict__)
