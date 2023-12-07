from unittest import TestCase, main
from models.db import DB


class TestDB(TestCase):
    def setUp(self):
        self.session = DB()

    async def test_connect(self):
        self.assertEqual(await self.session.connect(), None)

    async def test_create_user(self):
        await self.session.connect()
        await self.session.create_user(id=1,
                                       role='group',
                                       sub_info='34',
                                       lang='ru')
        # self.assertEqual(await self.session.select_user_by_id(1), [(1, 'group', '34')])
        self.assertEqual(isinstance(await self.session.select_user_by_id(1), dict), True)

    async def test_update_user(self):
        await self.session.connect()
        await self.session.create_user(id=1,
                                       role='group',
                                       sub_info='34',
                                       lang='ru')
        await self.session.update_user_info(1, role='teacher', sub_info='AAA')

        self.assertEqual(isinstance(await self.session.select_user_by_id(1), dict), True)

    async def test_delete_user(self):
        await self.session.connect()
        await self.session.delete_user(1)
        self.assertEqual(await self.session.select_user_by_id(1), [])


if __name__ == '__main__':
    main()
