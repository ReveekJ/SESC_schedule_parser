import json
import logging

import aiohttp
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import CRYPTO_KEY
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse, ElectiveCourseTimetable
from src.tgbot.user_models.models import UsersModel
from src.tgbot.user_models.schemas import User


class DB:
    @staticmethod
    async def __send_request_to_crypto_service(url: str, data_login: dict, data_password: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data_login) as login, session.post(url, json=data_password) as password:
                return json.loads(await login.text())['crypto_string'], json.loads(await password.text())['crypto_string']

    @staticmethod
    async def __decrypt_login_password(user: User) -> User:
        url = 'http://localhost:8000/crypt/decrypt'
        data_login = {'crypto_string': user.login,
                      'key': CRYPTO_KEY}
        data_passwd = {'crypto_string': user.password,
                       'key': CRYPTO_KEY}
        login, password = await DB.__send_request_to_crypto_service(url, data_login, data_passwd)
        user.login, user.password = login, password
        return user

    @staticmethod
    async def __encrypt_login_password(user: User) -> User:
        url = 'http://localhost:8000/crypt/encrypt'
        data_login = {'crypto_string': user.login,
                      'key': CRYPTO_KEY}
        data_passwd = {'crypto_string': user.password,
                       'key': CRYPTO_KEY}
        login, password = await DB.__send_request_to_crypto_service(url, data_login, data_passwd)
        user.login, user.password = login, password
        return user

    @staticmethod
    def __login_password_decrypt(func):
        async def inner(*args, **kwargs):
            try:
                original_result = await func(*args, **kwargs)
                if original_result is None:
                    return None

                if isinstance(original_result, list):
                    for i in range(len(original_result)):
                        original_result[i] = await DB.__decrypt_login_password(original_result[i])
                    return original_result

                if isinstance(original_result, User):
                    res = await DB.__decrypt_login_password(original_result)
                    return res
            except Exception as e:
                logging.error(f"Error in decryption: {str(e)}")
                raise

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
            logging.error("User not found for the given ID")
            await session.commit()
            return None
        except SQLAlchemyError as e:
            logging.error(f"An error occurred in SQLAlchemy: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    @__login_password_decrypt
    async def select_users_by_role_and_sub_info(session: AsyncSession, role: str, sub_info: str) -> list[User]:
        query = select(UsersModel).options(selectinload(UsersModel.elective_course_replied)).where(
            UsersModel.role == role, UsersModel.sub_info == sub_info)

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
        user = await self.__encrypt_login_password(user)

        session.add(UsersModel(**user.model_dump()))
        await session.commit()

    @staticmethod
    async def delete_user(session: AsyncSession, _id: int):
        stmt = delete(UsersModel).where(UsersModel.id == _id)
        await session.execute(stmt)
        await session.commit()

    async def update_user_info(self, session: AsyncSession, _id: int, **kwargs):
        user = await self.select_user_by_id(session, _id)

        # kwargs bug fix
        kwargs['id'] = _id

        # шифруем логин и пароль
        if kwargs.get('login') is not None:
            user.login = kwargs.get('login')
        if kwargs.get('password') is not None:
            user.password = kwargs.get('password')

        user = await self.__encrypt_login_password(user)
        kwargs['login'] = user.login
        kwargs['password'] = user.password

        # обновляем значение в бд
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
