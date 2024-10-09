from abc import ABC, abstractmethod

import aiohttp
import grpc
import simplejson as json

from proto import drawing_pb2_grpc, drawing_pb2
from proto.drawing_pb2 import DrawResponse
from src.config import PATH_TO_FONT
from src.database import get_async_session
from src.my_typing import ChangesList, ChangesType
from src.tgbot.sesc_info import SESC_Info
from src.tgbot.user_models.db import DB


class AbstractParser(ABC):
    def __init__(self, font_path: str):
        self.font_path = font_path

    @staticmethod
    def merge_schedule(lessons: list[dict], diffs: list[dict]) -> list[dict]:
        merged_schedule = lessons

        # проходимся по diffs
        for difference in diffs:
            number = difference['number']
            subgroup = difference['subgroup']

            # пытаемся найти соответствие по number и subgroup
            for index, lesson in enumerate(merged_schedule):
                if ((lesson['number'] == number and lesson['subgroup'] == subgroup) or
                        (lesson['number'] == number and subgroup == 0) or
                        (lesson['number'] == number and lesson['subgroup'] == 0)):
                    merged_schedule[index] = difference
            # если соответствия нет, то добавляем этот урок
            else:
                merged_schedule.append(difference)

        return merged_schedule

    @abstractmethod
    async def parse(self, _type: str, _second: str, _weekday: str, style: int):
        pass

    # Создание таблицы
    def _create_table(self, _type: str, info: list, style: int):
        def get_text_of_lesson(__lesson: dict) -> list | None:
            nonlocal _type

            match _type:
                case 'teacher':
                    return (__lesson['subject'], __lesson['group'], __lesson['auditory']) if __lesson['subject'] != '' else None
                case 'auditory':
                    return (__lesson['subject'], __lesson['teacher'], __lesson['group']) if __lesson['subject'] != '' else None
                case _:
                    return (__lesson['subject'], __lesson['teacher'], __lesson['auditory']) if __lesson['subject'] != '' else None

        with grpc.insecure_channel('drawing:8080') as channel:
            stub = drawing_pb2_grpc.DrawerStub(channel)

            lessons = []

            for index, row in enumerate(info):
                les = get_text_of_lesson(row)

                if les is None:
                    continue

                lesson_time = row.get('custom_time') if row.get('custom_time') is not None else SESC_Info.DEFAULT_TIME_OF_LESSONS.get(int(row.get('number')))
                lessons.append(drawing_pb2.Lesson(lessonNumber=int(row.get('number')),
                                                  lessonNumberView=lesson_time,
                                                  first=les[0],
                                                  second=les[1],
                                                  third=les[2],
                                                  subgroup=int(row.get('subgroup', 0)),
                                                  isDiff=True if row.get('date') else False))

            styles_dct: dict[int, str] = {number: name for name, number in drawing_pb2.Style.items()}
            draw_request = drawing_pb2.DrawRequest(lessons=lessons, drawStyle=styles_dct.get(style))

            response: DrawResponse = stub.Draw(draw_request)

            return response.pathToImage


class Parser(AbstractParser):
    def __init__(self, font_path):
        super().__init__(font_path)
        self.changes = ChangesList()

    # Преобразование информации и управление процессом создания таблицы
    async def parse(self, _type: str, _second: str, _weekday: str, user_id: int, style: int | None = None):
        info = await self.__get_json(_type, int(_second), int(_weekday))

        if not info['lessons'] and not info['diffs']:
            return 'NO_SCHEDULE'

        async with await get_async_session() as session:
            if style is None:
                style = (await DB().select_user_by_id(session, user_id)).style

        path = self._create_table(_type, self.merge_schedule(info['lessons'], info['diffs']), style)

        return path

    @staticmethod  # Отправление запроса учителя
    async def __get_json(_type: str, _second: int, weekday: int):
        while True:
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    async with session.get(
                            f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType={_type}&{weekday=}'
                            f'&{_type}={_second}') as resp:
                        return json.loads(await resp.text())
            except Exception as e:
                pass

    async def __check_for_changes_student(self) -> None:
        for day in SESC_Info.WEEKDAY.values():
            for group in SESC_Info.GROUP.values():
                schedule = await self.__get_json('group', int(group), int(day))
                if schedule.get('diffs'):
                    await self.changes.append(ChangesType(type='group', second=group, weekday=day, schedule=schedule))

    async def __check_for_changes_teacher(self) -> None:
        for day in SESC_Info.WEEKDAY.values():
            for teacher in SESC_Info.TEACHER.values():
                schedule = await self.__get_json('teacher', int(teacher), int(day))

                if schedule.get('diffs'):
                    await self.changes.append(ChangesType(type='teacher', second=teacher, weekday=day,
                                                          schedule=schedule))

    async def check_for_changes(self) -> ChangesList:
        await self.__check_for_changes_student()
        await self.__check_for_changes_teacher()

        return self.changes

    @staticmethod
    async def get_free_auditories(weekday: int, lesson: int):
        async def get_table():
            ext = []
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                async with session.get(
                        f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType=all&{weekday=}',
                ) as resp:
                    data = await resp.text()
                    data = json.loads(data)['auditories']
                    for aud in data:
                        if not data[aud][lesson] and aud not in ('Нет', 'Библиотека', 'Общежитие'):
                            ext += [aud]
            return ext

        lesson %= 7
        weekday %= 7
        if not weekday:
            return None
        return await get_table()


class ElectiveParser(AbstractParser):
    @staticmethod
    def __convert_number(func):
        def wrapper(*args, **kwargs):
            origin: list[dict] = func(*args, **kwargs)
            schedule = sorted(origin, key=lambda x: x.get('number'))
            for num, lesson in enumerate(schedule):
                lesson['number'] = num + 1

            return schedule
        return wrapper

    @__convert_number
    def merge_schedule(self, lessons: list[dict], diffs: list[dict]) -> list[dict]:
        return super().merge_schedule(lessons, diffs)

    async def parse(self, user_id: int, style: int | None = None, **kwargs) -> str:
        weekday = int(kwargs['weekday'])
        _type = kwargs['type'] if kwargs.get('type') else 'group'

        async with await get_async_session() as session:
            courses = await DB().get_elective_courses_for_day(session, user_id, weekday)

            if style is None:
                style = (await DB().select_user_by_id(session, user_id)).style

        dumped_courses = courses.model_dump(mode='timetable')

        if not courses.lessons and not courses.diffs:
            return 'NO_SCHEDULE'

        path = self._create_table(_type, self.merge_schedule(dumped_courses['lessons'], dumped_courses['diffs']), style)

        return path


PARSER = Parser(PATH_TO_FONT)
ELECTIVE_PARSER = ElectiveParser(PATH_TO_FONT)
