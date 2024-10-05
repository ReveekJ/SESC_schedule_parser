import logging

from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_session
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse, ElectiveCourseTimetable
from src.tgbot.user_models.models import UsersModel
from src.tgbot.user_models.schemas import User


class DB:
    # Возвращает None если запись не найдется, иначе вернется User
    @staticmethod
    async def select_user_by_id(session: AsyncSession, _id: int) -> User | None:
        query = (select(UsersModel)
                 .where(UsersModel.id == _id)
                 .options(selectinload(UsersModel.elective_course_replied)))

        try:
            temp = await session.execute(query)

            await session.commit()
            return User(**temp.first()[0].__dict__)
        except IndexError:
            logging.error("User not found for the given ID")
            await session.commit()
            return None
        except SQLAlchemyError as e:
            logging.error(f"An error occurred in SQLAlchemy: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    async def select_users_by_role_and_sub_info(session: AsyncSession, role: str, sub_info: str) -> list[User]:
        query = select(UsersModel).options(selectinload(UsersModel.elective_course_replied)).where(
            UsersModel.role == role, UsersModel.sub_info == sub_info)

        res = await session.execute(query)
        final_result = []
        for user in res.all():
            final_result.append(User(**user[0].__dict__))

        await session.commit()
        return final_result

    async def get_all_users(self, session: AsyncSession) -> list[User]:
        query = select(UsersModel)

        res = await session.execute(query)
        final_result = []

        for i, user in enumerate(res.all()):
            final_result.append(User(**user[0].__dict__))

        await session.commit()
        return final_result

    async def create_user(self, session: AsyncSession, user: User):
        session.add(UsersModel(**user.model_dump()))
        await session.commit()

    @staticmethod
    async def delete_user(session: AsyncSession, _id: int):
        stmt = delete(UsersModel).where(UsersModel.id == _id)
        await session.execute(stmt)
        await session.commit()

    async def update_user_info(self, session: AsyncSession, _id: int, **kwargs):
        # kwargs bug fix
        kwargs['id'] = _id

        # обновляем значение в бд
        stmt = update(UsersModel).where(UsersModel.id == _id).values(**kwargs)

        await session.execute(stmt)
        await session.commit()

    async def update_last_message_id(self, user_id: int, last_message_id: int):
        async with await get_async_session() as session:
            await self.update_user_info(session,
                                        user_id,
                                        last_message_id=last_message_id)

    async def get_elective_courses_for_day(self, session: AsyncSession, user_id: int, weekday: int) \
            -> ElectiveCourseTimetable:
        user = await self.select_user_by_id(session, user_id)
        query = select(ElectiveCourseModel).join(ElectiveCourseModel.users_replied).filter(
            UsersModel.id == user.id, ElectiveCourseModel.weekday == weekday
        ).options(selectinload(ElectiveCourseModel.users_replied))

        res = await session.execute(query)
        res = [ElectiveCourse(**course.__dict__) for course in res.scalars().all()]

        elective_lst = ElectiveCourseTimetable(lessons=[], diffs=[])
        for course in res:
            if course.is_diffs:
                elective_lst.diffs.append(course)
            else:
                elective_lst.lessons.append(course)
        del res

        return elective_lst
