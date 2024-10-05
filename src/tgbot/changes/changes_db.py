import json

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.tgbot.changes.models import Changes
from src.tgbot.changes.schemas import ChangesType


class ChangesDB:
    @staticmethod
    async def get_id_last_change(session: AsyncSession) -> int:
        query = select(Changes).order_by(Changes.id.desc())

        res = await session.execute(query)
        await session.commit()

        try:
            return res.first()[0].id
        except TypeError:
            return 0  # возникает когда в бд ничего нет

    @staticmethod
    async def add_changes(session: AsyncSession, changed_schedule: ChangesType):
        last_id = await ChangesDB.get_id_last_change(session)
        stmt = insert(Changes).values((last_id + 1, changed_schedule.type, changed_schedule.second,
                                       changed_schedule.weekday, json.dumps(changed_schedule.schedule)))

        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def get_all_changes(session: AsyncSession) -> list[ChangesType]:
        query = select(Changes)

        query_result = await session.execute(query)
        await session.commit()
        result = []

        for i in query_result.all():
            i: Changes = i[0]
            result.append(ChangesType(id=i.id, type=i.type, second=i.second, weekday=i.weekday,
                                      schedule=json.loads(i.schedule)))

        return result

    @staticmethod
    async def delete_all_changes(session: AsyncSession):
        stmt = delete(Changes)

        await session.execute(stmt)
        await session.commit()
