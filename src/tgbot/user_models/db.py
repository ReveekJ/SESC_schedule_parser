import datetime
import json
import logging
from os import urandom

import aiohttp
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        _id = self.__convert_to_id_type(_id)
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
            user[0].id = self.__convert_to_id_type(user[0].id)
            final_result.append(User(**user[0].__dict__))

        await session.commit()
        return final_result

    async def create_user(self, session: AsyncSession, user: User):
        # преобразование id в тип id, который находится в бд
        user.id = self.__convert_to_id_type(user.id)
        user = await self.__encrypt_decrypt_login_password(user)

        session.add(UsersModel(**user.model_dump()))
        await session.commit()

    async def delete_user(self, session: AsyncSession, _id: int):
        _id = self.__convert_to_id_type(_id)

        stmt = delete(UsersModel).where(UsersModel.id == _id)
        await session.execute(stmt)
        await session.commit()

    # TODO: check is it working now
    async def update_user_info(self, session: AsyncSession, _id: int, **kwargs):
        _id = self.__convert_to_id_type(_id)

        stmt = update(UsersModel).where(UsersModel.id == _id).values(**kwargs)

        await session.execute(stmt)
        await session.commit()

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

    @staticmethod
    def __convert_to_id_type(_id) -> str:
        return str(_id)

    @staticmethod
    def __convert_from_id_type(_id) -> int:
        return int(_id)

# SAMPLE USAGE
# async def main():
#     session = await get_async_session()
#     print(await DB().select_users_by_role_and_sub_info(session, 'group', '34'))
#
#
# # Run the main function
# asyncio.run(main())
