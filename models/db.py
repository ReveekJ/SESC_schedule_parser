import asyncio

from models.database import get_async_session
from models.model import users, columns_json
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession


class DB:
    # Возвращает None если запись не найдется, иначе вернется dict
    async def select_user_by_id(self, session: AsyncSession, _id: int) -> dict | None:
        _id = self.__convert_to_id_type(_id)

        query = select(users).where(users.c.id == _id)
        res = await session.execute(query)
        final_result = {}

        try:
            for index, elem in enumerate(res.all()[0]):
                if index == 0:
                    elem = self.__convert_from_id_type(elem)
                final_result[columns_json[index]] = elem
        except IndexError:
            await session.commit()
            return None

        await session.commit()
        return final_result

    async def select_users_by_role_and_sub_info(self, session: AsyncSession, role: str, sub_info: str) -> list[dict]:
        query = select(users).where(users.c.role == role, users.c.sub_info == sub_info)

        res = await session.execute(query)
        final_result = []

        for i, user in enumerate(res.all()):
            final_result.append({})
            for index, elem in enumerate(user):
                if index == 0:
                    elem = self.__convert_from_id_type(elem)
                final_result[i][columns_json[index]] = elem

        await session.commit()
        return final_result

    async def create_user(self, session: AsyncSession, **kwargs):
        # what must be in kwargs u can see in models.py
        # проверка, что переданы все параметры
        if list(kwargs.keys()) != list(columns_json.values()):
            raise ValueError('Не хватает параметров для создания пользователя')

        # преобразование id в тип id, который находтся в бд
        kwargs['id'] = self.__convert_to_id_type(kwargs['id'])

        stmt = insert(users).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

    async def delete_user(self, session: AsyncSession, _id):
        _id = self.__convert_to_id_type(_id)

        stmt = delete(users).where(users.c.id == _id)
        await session.execute(stmt)
        await session.commit()

    async def update_user_info(self, session: AsyncSession, _id, **kwargs):
        _id = self.__convert_to_id_type(_id)

        stmt = update(users).where(users.c.id == _id).values(**kwargs)

        await session.execute(stmt)
        await session.commit()

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
