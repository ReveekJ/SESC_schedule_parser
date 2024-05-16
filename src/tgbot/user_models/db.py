import datetime
import json
import logging

import aiohttp
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse, ElectiveCourseTimetable
from src.tgbot.user_models.models import UsersModel
from src.tgbot.user_models.schemas import User


class DB:
    @staticmethod
    async def __encrypt_decrypt_login_password(user: User) -> User:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://localhost:8000/crypt/?crypto_string={user.password}') \
                    as password, session.get(f'http://localhost:8000/crypt/?crypto_string={user.login}') \
                    as login:
                user.password = json.loads(await password.text())['crypto_string']
                user.login = json.loads(await login.text())['crypto_string']
        return user

    @staticmethod
    def __login_password_decrypt(func):
        async def inner(*args, **kwargs):
            original_result = await func(*args, **kwargs)
            if original_result is None:
                return None

            if isinstance(original_result, list):
                for i in range(len(original_result)):
                    original_result[i] = await DB.__encrypt_decrypt_login_password(original_result[i])
                return original_result

            if isinstance(original_result, User):
                res = await DB.__encrypt_decrypt_login_password(original_result)
                return res
        return inner

    # Возвращает None если запись не найдется, иначе вернется User
    @__login_password_decrypt
    async def select_user_by_id(self, session: AsyncSession, _id: int) -> User | None:
        query = select(UsersModel).options(selectinload(UsersModel.elective_course_replied)).where(UsersModel.id == _id)

        try:
            temp = await session.execute(query)

            await session.commit()
            return User(**temp.first()[0].__dict__)
        except IndexError:
            await session.commit()
            return None
        except Exception as e:
            logging.error(str(datetime.datetime.now()) + str(e))

    @staticmethod
    @__login_password_decrypt
    async def select_users_by_role_and_sub_info(session: AsyncSession, role: str, sub_info: str) -> list[User]:
        query = select(UsersModel).options(selectinload(UsersModel.elective_course_replied)).where(UsersModel.role == role, UsersModel.sub_info == sub_info)

        res = await session.execute(query)
        final_result = []
        for user in res.all():
            final_result.append(User(**user[0].__dict__))

        await session.commit()
        return final_result

    @__login_password_decrypt
    async def get_all_users(self, session: AsyncSession) -> list[User]:
        query = select(UsersModel)

        res = await session.execute(query)
        final_result = []

        for i, user in enumerate(res.all()):
            final_result.append(User(**user[0].__dict__))

        await session.commit()
        return final_result

    async def create_user(self, session: AsyncSession, user: User):
        # преобразование id в тип id, который находится в бд
        user = await self.__encrypt_decrypt_login_password(user)

        session.add(UsersModel(**user.model_dump()))
        await session.commit()

    @staticmethod
    async def delete_user(session: AsyncSession, _id: int):
        stmt = delete(UsersModel).where(UsersModel.id == _id)
        await session.execute(stmt)
        await session.commit()

    # TODO: check is it working now
    @staticmethod
    async def update_user_info(session: AsyncSession, _id: int, **kwargs):
        stmt = update(UsersModel).where(UsersModel.id == _id).values(**kwargs)

        await session.execute(stmt)
        await session.commit()

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
    # async def get_elective_courses(self, session: AsyncSession, user_id: int) -> list[ElectiveCourse]:
    #     user = await self.select_user_by_id(session, user_id)
    #     if user is None:
    #         raise ValueError('Incorrect user_id')
    #
    #     result = []
    #     for course in user.elective_courses:
    #         temp = await ElectiveCourseDB.get_course(session, course)
    #         result.append(temp)
    #
    #     return result

# SAMPLE USAGE
# async def main():
#     session = await get_async_session()
#     print(await DB().select_users_by_role_and_sub_info(session, 'group', '34'))
#
#
# # Run the main function
# asyncio.run(main())
