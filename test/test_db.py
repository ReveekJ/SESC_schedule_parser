from unittest import TestCase, main
from models.db import DB
from models.database import get_async_session


class TestDB(TestCase):
    async def setUp(self):
        self.session = await get_async_session()

    async def test_create_user(self):
        await DB().create_user(self.session,
                               id=1,
                               role='group',
                               sub_info='34',
                               lang='ru')
        # self.assertEqual(await self.session.select_user_by_id(1), [(1, 'group', '34')])
        self.assertEqual(isinstance(await DB().select_user_by_id(self.session, 1), dict), True)

    async def test_update_user(self):
        await DB().update_user_info(self.session, 1, role='teacher', sub_info='AAA')

        self.assertEqual(isinstance(await DB().select_user_by_id(self.session, 1), dict), True)

    async def test_delete_user(self):
        await DB().delete_user(self.session, 1)
        self.assertEqual(await DB().select_user_by_id(self.session, 1), [])


if __name__ == '__main__':
    main()
