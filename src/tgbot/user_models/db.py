import json
import logging

import aiohttp
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse, ElectiveCourseTimetable
from src.tgbot.user_models.models import UsersModel
from src.tgbot.user_models.schemas import User
from src.config import CRYPTO_KEY


class DB:
    @staticmethod
    async def __decrypt_login_password(user: User) -> User:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://localhost:8000/crypt/decrypt?crypto_string={user.password}&key={CRYPTO_KEY}') \
                    as password, \
                    session.post(f'http://localhost:8000/crypt/decrypt?crypto_string={user.login}&key={CRYPTO_KEY}') as login:
                user.password = json.loads(await password.text())['crypto_string']
                user.login = json.loads(await login.text())['crypto_string']
            # async with session.get(f'http://localhost:8000/lycreg/check_auth_data/?login={user.login}&password={user.
            # password}') as resp:
            #     if json.loads(await resp.text()).get('status') == 200:  # если пароль подходит
            #         return user
            #     else:
            #         pass  # TODO: если пароль не подходит, то нужно придумать что делать
            # raise ValueError('Login or password is incorrect')
            return user

    @staticmethod
    async def __encrypt_login_password(user: User) -> User:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://localhost:8000/crypt/encrypt?crypto_string={user.password}&key={CRYPTO_KEY}') \
                    as password, \
                    session.post(f'http://localhost:8000/crypt/encrypt?crypto_string={user.login}&key={CRYPTO_KEY}') as login:
                user.password = json.loads(await password.text())['crypto_string']
                user.login = json.loads(await login.text())['crypto_string']
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
