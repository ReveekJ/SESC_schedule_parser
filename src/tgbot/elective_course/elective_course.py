from typing import Optional

from sqlalchemy import select, delete, update

from src.database import get_async_session
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse

from src.tgbot.sesc_info import SESC_Info


class ElectiveCourseDB:
    @staticmethod
    async def add_course(course: ElectiveCourse):
        async with await get_async_session() as session:
            session.add(ElectiveCourseModel(**course.model_dump(exclude={'id'})))
            await session.commit()

    @staticmethod
    async def delete_course(course_name: str, weekdays: Optional[list[int]] = None):
        async with await get_async_session() as session:
            if weekdays:
                for weekday in weekdays:
                    stmt = delete(ElectiveCourseModel).where(ElectiveCourseModel.subject == course_name,
                                                             ElectiveCourseModel.weekday == int(weekday))
                    await session.execute(stmt)
            else:
                stmt = delete(ElectiveCourseModel).where(ElectiveCourseModel.subject == course_name)
                await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def update_course(new_course: ElectiveCourse, weekday: Optional[int] = None):
        course = new_course.model_dump(exclude={'id'})  # Exclude 'id' field
        if weekday:
            stmt = (update(ElectiveCourseModel)
                    .where(ElectiveCourseModel.subject == new_course.subject,
                           ElectiveCourseModel.weekday == weekday)
                    .values(**course))
        else:
            stmt = (update(ElectiveCourseModel)
                    .where(ElectiveCourseModel.subject == new_course.subject)
                    .values(**course))

        async with await get_async_session() as session:
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def cancel_course(course_name: str):
        old_course = (await ElectiveCourseDB.get_courses_by_subject(course_name))[0]
        new_course = ElectiveCourse(subject=old_course.subject,
                                    teacher_name=old_course.teacher_name,
                                    pulpit=old_course.pulpit,
                                    weekday=old_course.weekday,
                                    time_from=old_course.time_from,
                                    time_to=old_course.time_to,
                                    auditory=old_course.auditory,
                                    is_cancelled=True)

        await ElectiveCourseDB.update_course(new_course)

    @classmethod
    async def get_courses_by_subject(cls, subject: str) -> list[ElectiveCourse]:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.subject == subject)
        result = await cls.__query_to_list_of_elective(query)
        return result

    @classmethod
    async def get_courses_by_pulpit(cls, pulpit: str) -> list[ElectiveCourse]:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.pulpit == pulpit)
        result = await cls.__query_to_list_of_elective(query)
        return result

    @staticmethod
    async def get_course_by_subject_and_weekday(subject: str, weekday: int) -> ElectiveCourse:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.subject == subject,
                                                  ElectiveCourseModel.weekday == int(weekday))
        async with await get_async_session() as session:
            res = await session.execute(query)

        return ElectiveCourse(**res.scalars().all()[0].__dict__)

    @staticmethod
    async def get_course_by_id(course_id: int) -> ElectiveCourse:
        query = select(ElectiveCourseModel).where(ElectiveCourseModel.id == course_id)

        async with await get_async_session() as session:
            res = await session.execute(query)

        return ElectiveCourse(**res.scalars().all()[0].__dict__)

    @staticmethod
    async def __query_to_list_of_elective(query) -> list[ElectiveCourse]:
        async with await get_async_session() as session:
            query_res = await session.execute(query)
        result = []

        for course in query_res.scalars().all():
            result.append(ElectiveCourse(**course.__dict__))

        return result

    @staticmethod
    async def remove_changes(course: ElectiveCourse):
        new_course = ElectiveCourse(subject=course.subject,
                                    teacher_name=course.teacher_name,
                                    time_from=course.time_from,
                                    time_to=course.time_to,
                                    auditory=course.auditory,
                                    weekday=course.weekday,
                                    pulpit=course.pulpit)
        stmt = (update(ElectiveCourseModel)
                .where(ElectiveCourseModel.subject == course.subject,
                       ElectiveCourseModel.weekday == course.weekday)
                .values(**new_course.model_dump(exclude={'id'})))

        async with await get_async_session() as session:
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def get_exist_pulpits() -> dict[str, list]:
        query = select(ElectiveCourseModel.pulpit)

        async with await get_async_session() as session:
            x = await session.execute(query)
        row_res: list = list(x.scalars().unique())
        res = {
            'en': row_res,
            'ru': [SESC_Info.PULPIT['ru'][SESC_Info.PULPIT['en'].index(i)] for i in row_res]
        }
        return res
