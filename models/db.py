import os
import sys

import asyncpg
from models.model import users, columns_json
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))


class DB:
    def __init__(self):
        self.session = AsyncSession()
        self.engine = AsyncEngine
        self.conn = asyncpg.Connection
        # set DB_URL
        self.DB_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

    async def connect(self):
        self.conn = await asyncpg.connect(self.DB_URL)
        # set db url for sqlalchemy
        self.engine = create_async_engine(
            f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
        self.session = AsyncSession(self.engine)

    async def select_user_by_id(self, _id):
        _id = self.__convert_to_id_type(_id)

        query = select(users).where(users.c.id == _id)
        res = await self.session.execute(query)
        final_result = {}

        for index, elem in enumerate(res.all()[0]):
            final_result[columns_json[index]] = elem

        await self.session.commit()
        return final_result

    async def create_user(self, **kwargs):
        # what must be in kwargs u can see in models.py
        # проверка, что переданы все параметры
        if kwargs.keys() != columns_json.values():
            raise ValueError('Не хватает параметров для создания пользователя')

        # преобразование id в тип id, который находтся в бд
        kwargs['id'] = self.__convert_to_id_type(kwargs['id'])

        stmt = insert(users).values(**kwargs)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_user(self, _id):
        _id = self.__convert_to_id_type(_id)

        stmt = delete(users).where(users.c.id == _id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_user_info(self, _id, **kwargs):
        _id = self.__convert_to_id_type(_id)

        stmt = update(users).where(users.c.id == _id).values(**kwargs)

        await self.session.execute(stmt)
        await self.session.commit()

    @staticmethod
    def __convert_to_id_type(_id):
        return str(_id)
