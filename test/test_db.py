from unittest import TestCase, main
from src.tgbot.user_models import DB
from src.database import get_async_session


class TestDB(TestCase):
    async def test_create_user(self):
        self.session = await get_async_session()
        await DB().create_user(self.session,
                               id=1,
                               role='group',
                               sub_info='34',
                               lang='ru')
        # self.assertEqual(await self.session.select_user_by_id(1), [(1, 'group', '34')])
        self.assertEqual(isinstance(await DB().select_user_by_id(self.session, 1), dict), True)

    async def test_update_user(self):
        self.session = await get_async_session()
        await DB().update_user_info(self.session, 1, role='teacher', sub_info='AAA')

        self.assertEqual(isinstance(await DB().select_user_by_id(self.session, 1), dict), True)

    async def test_delete_user(self):
        self.session = await get_async_session()
        await DB().delete_user(self.session, 1)
        self.assertEqual(await DB().select_user_by_id(self.session, 1), [])


if __name__ == '__main__':
    main()
