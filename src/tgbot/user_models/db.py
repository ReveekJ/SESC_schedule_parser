from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.tgbot.user_models.models import UsersModel, columns_json
from src.tgbot.user_models.schemas import User


class DB:
    # Возвращает None если запись не найдется, иначе вернется dict
    # TODO: сделать чтобы возвращалась схема данных
    async def select_user_by_id(self, session: AsyncSession, _id: int) -> dict | None:
        _id = self.__convert_to_id_type(_id)
        query = select(UsersModel).where(UsersModel.id == _id)

        try:
            temp = await session.execute(query)
            row_res = tuple(*temp)[0]

            final_result = {}

            for index, elem in enumerate([self.__convert_to_id_type(row_res.id), row_res.role, row_res.sub_info,
                                          row_res.lang]):
                final_result[columns_json[index]] = elem
        except IndexError:
            await session.commit()
            return None

        await session.commit()
        return final_result

    @staticmethod
    async def select_users_by_role_and_sub_info(session: AsyncSession, role: str, sub_info: str) -> list[User]:
        query = select(UsersModel).where(UsersModel.role == role, UsersModel.sub_info == sub_info)

        res = await session.execute(query)
        final_result = []
        for user in res.all():
            final_result.append(User(**user[0].__dict__))
            # final_result.append(**user)
            # final_result.append({})
            # for index, elem in enumerate(user):
            #     if index == 0:
            #         elem = self.__convert_from_id_type(elem)
            #     final_result[i][columns_json[index]] = elem

        await session.commit()
        return final_result

    async def get_all_users(self, session: AsyncSession) -> list[dict]:
        query = select(UsersModel)

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
        # what must be in kwargs u can see in user_models.py
        # проверка, что переданы все параметры
        if list(kwargs.keys()) != list(columns_json.values()):
            raise ValueError('Не хватает параметров для создания пользователя')

        # преобразование id в тип id, который находтся в бд
        kwargs['id'] = self.__convert_to_id_type(kwargs['id'])

        stmt = insert(UsersModel).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

    async def delete_user(self, session: AsyncSession, _id):
        _id = self.__convert_to_id_type(_id)

        stmt = delete(UsersModel).where(UsersModel.id == _id)
        await session.execute(stmt)
        await session.commit()

    async def update_user_info(self, session: AsyncSession, _id, **kwargs):
        _id = self.__convert_to_id_type(_id)

        stmt = update(UsersModel).where(UsersModel.id == _id).values(**kwargs)

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
