import asyncio

import aiohttp
import simplejson as json
from PIL import Image, ImageDraw, ImageFont
from tgbot.sesc_info import SESC_Info
from my_typing import ChangesList, ChangesType
from config import PATH_TO_FONT


class Parser:
    def __init__(self, font_path):
        self.changes = ChangesList()
        self.font_path = font_path

    @staticmethod
    def get_path(_second):
        return (__file__[:__file__.rfind('/', 0, __file__.rfind('/'))] + '/' +
                f'schedules/schedule{_second}.png')

    @staticmethod
    def merge_schedule(lessons: list[dict], diffs: list[dict]) -> list[dict]:
        merged_schedule = lessons

        # проходимся по diffs
        for difference in diffs:
            number = difference['number']
            subgroup = difference['subgroup']

            # пытаемся найти соответствие по number и subgroup
            for index, lesson in enumerate(merged_schedule):
                if lesson['number'] == number and lesson['subgroup'] == subgroup:
                    merged_schedule[index] = difference
            # если соответствия нет, то добавляем этот урок
            else:
                merged_schedule.append(difference)

        return merged_schedule

    # Преобразование информации и управление процессом создания таблицы
    async def parse(self, _type: str, _second: str, _weekday: str):
        path = self.get_path(_second)

        info = await self.__get_json(_type, int(_second), int(_weekday))

        if not info['lessons']:
            return 'NO_SCHEDULE'

        self.create_table(_type, self.merge_schedule(info['lessons'], info['diffs']), path)

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

                if schedule.get('diffs') is not None:
                    await self.changes.append(ChangesType('group', group, day, schedule))

                # передышка для сервака urfu
                await asyncio.sleep(0.1)

    async def __check_for_changes_teacher(self) -> None:
        for day in SESC_Info.WEEKDAY.values():
            for teacher in SESC_Info.TEACHER.values():
                schedule = await self.__get_json('teacher', int(teacher), int(day))

                if schedule.get('diffs'):
                    await self.changes.append(ChangesType('teacher', teacher, day, schedule))
                # передышка для сервака urfu
                await asyncio.sleep(0.1)

    async def check_for_changes(self) -> ChangesList:
        await self.__check_for_changes_student()
        await self.__check_for_changes_teacher()

        return self.changes

    # Создание таблицы
    def create_table(self, _type: str, info: list, path: str):
        def get_text_of_lesson(__lesson: dict) -> str:
            nonlocal _type

            match _type:
                case 'teacher':
                    return f"{__lesson['subject']}, {__lesson['group']}, {__lesson['auditory']}" \
                        if __lesson['subject'] != '' else ''
                case 'auditory':
                    return f"{__lesson['subject']}, {__lesson['teacher']}, {__lesson['group']}" \
                        if __lesson['subject'] != '' else ''
                case _:
                    return f"{__lesson['subject']}, {__lesson['teacher']}, {__lesson['auditory']}" \
                        if __lesson['subject'] != '' else ''

        def is_exist_lesson_by_number(_lessons: list[dict], number: int) -> bool:
            for _les in _lessons:
                if _les['number'] == number:
                    return True

            return False

        # Создаем изображение и определяем размеры и шрифт
        width, height = 960, 540
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        font_path = self.font_path
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)

        # Размеры колонок
        column_width1 = 120
        column_width2 = width - column_width1 - 20

        # Расчет высоты строки и высоты текста
        row_height = height // 8
        text_height = font.getbbox('A')[3] - font.getbbox('A')[1] + 4

        # Рисуем шапку таблицы
        header_bg_color = (0, 128, 0)
        header_text = 'Уроки'
        header_text_bounding_box = font.getbbox(header_text)
        header_text_width = header_text_bounding_box[2] - header_text_bounding_box[0]
        header_text_x = column_width1 + (column_width2 - header_text_width) // 2
        header_text_y = (row_height - text_height) // 2
        draw.rectangle(((0, 0), (width, row_height)), fill=header_bg_color)
        draw.text((header_text_x, header_text_y), header_text, font=font, fill=(255, 255, 255))

        # Рисуем разделительную полосу после шапки
        draw.line([(column_width1, 0), (column_width1, row_height)], fill=(128, 128, 128), width=1)

        lessons = info

        # Если уроков меньше 7, добавляем пустые уроки, чтобы получить 7 строк
        for i in range(1, 8):
            if not is_exist_lesson_by_number(lessons, i):
                lessons.append(
                    {'uid': None, 'subject': '', 'auditory': '', 'group': '', 'teacher': '', 'subgroup': 0, 'number': i,
                     'weekday': None})

        lessons = sorted(info, key=lambda x: x['number'])
        print(lessons)
        skipped_rows = 0

        # Рисуем таблицу с данными
        for l in range(177):
            if l == len(lessons):
                break
            lesson = lessons[l]
            start_y = (lesson['number'] - skipped_rows) * row_height

            # Рисуем разделительную полосу
            draw.line([(0, start_y), (width, start_y)], fill=(128, 128, 128), width=1)

            # Рисуем номер урока в первой колонке
            lesson_number = str(lesson['number'])

            lesson_number_bounding_box = font.getbbox(lesson_number)
            lesson_number_width = lesson_number_bounding_box[2] - lesson_number_bounding_box[0]
            lesson_number_x = (column_width1 - lesson_number_width) // 2
            lesson_number_y = start_y + (row_height - text_height) // 2

            # Рисуем разделительные полоски для колонок
            draw.line([(column_width1, start_y), (column_width1, start_y + row_height)], fill=(128, 128, 128), width=1)

            if lesson['subgroup'] == 0:
                # Рисуем урок, учителя и аудиторию во второй колонке с центровкой
                lesson_info = get_text_of_lesson(lesson)

                lesson_info_width = font.getbbox(lesson_info)[2] - font.getbbox(lesson_info)[0]
                lesson_info_x = column_width1 + (column_width2 - lesson_info_width) // 2
                lesson_info_y = start_y + (row_height - text_height) // 2
                if lesson.get('diff'):
                    color = (252, 132, 3)
                else:
                    color = (0, 0, 0)
                draw.text((lesson_info_x, lesson_info_y), lesson_info, font=font, fill=color)

            else:
                # TODO: доюавить разделительную полоску между расписаниеми для subgroup
                lesson_info_subgroup1 = ''
                lesson_info_subgroup2 = ''

                # Рисуем урок, учителя и аудиторию во второй колонке с центровкой
                if lesson['subgroup'] == 1:
                    lesson_info_subgroup1 = get_text_of_lesson(lesson)

                    if lesson.get('diff'):
                        color = (252, 132, 3)
                    else:
                        color = (0, 0, 0)

                    for les in lessons:
                        # ищем подходящий по subgroup и number урок
                        if les['subgroup'] == 2 and les['number'] == lesson['number']:
                            lesson2 = les
                            break
                    else:
                        # если ничего подходящего не нашли, то ставим такю заглушку
                        lesson2 = {'subject': 'Нет', 'teacher': 'Нет', 'group': 'Нет', 'auditory': 'Нет'}

                    lesson_info_subgroup2 = get_text_of_lesson(lesson2)
                elif lesson['subgroup'] == 2:
                    # skipped_rows += 1
                    # continue
                    # lesson_info_subgroup1 = -1
                    lesson_info_subgroup2 = get_text_of_lesson(lesson)
                    # lesson_info_subgroup1 = 'Нет, Нет, Нет'

                    if lesson.get('date') is not None:
                        color = (252, 132, 3)
                    else:
                        color = (0, 0, 0)

                    for les in lessons:
                        # ищем подходящий по subgroup и number урок
                        if les['subgroup'] == 1 and les['number'] == lesson['number']:
                            lesson1 = les
                            break
                    else:
                        # если ничего подходящего не нашли, то ставим такю заглушку
                        lesson1 = {'subject': 'Нет', 'teacher': 'Нет', 'group': 'Нет', 'auditory': 'Нет'}
                    lesson_info_subgroup1 = get_text_of_lesson(lesson1)

                lesson_info_subgroup1_width = (
                        font.getbbox(lesson_info_subgroup1)[2] - font.getbbox(lesson_info_subgroup1)[0])

                lesson_info_subgroup1_x = column_width1 + (column_width2 // 2 - lesson_info_subgroup1_width) // 2
                lesson_info_subgroup1_y = start_y + (row_height - text_height) // 2

                lesson_info_subgroup2_width = font.getbbox(lesson_info_subgroup2)[2] - \
                                              font.getbbox(lesson_info_subgroup2)[0]
                lesson_info_subgroup2_x = column_width1 + column_width2 // 2 + (
                        column_width2 // 2 - lesson_info_subgroup2_width) // 2
                lesson_info_subgroup2_y = start_y + (row_height - text_height) // 2

                draw.text((lesson_info_subgroup2_x, lesson_info_subgroup2_y), lesson_info_subgroup2, font=font,
                          fill=color)
                draw.text((lesson_info_subgroup1_x, lesson_info_subgroup1_y), lesson_info_subgroup1, font=font,
                          fill=color)
                #
                # lesson_info_subgroup1 = f"{lesson2['subject']}, {lesson2['teacher']}, {lesson2['auditory']}"

                # lesson_info_subgroup2_width = font.getbbox(lesson_info_subgroup2)[2] - \
                #                               font.getbbox(lesson_info_subgroup2)[0]
                #
                # lesson_info_subgroup2_x = column_width1 + column_width2 // 2 + (
                #         column_width2 // 2 - lesson_info_subgroup2_width) // 2
                # lesson_info_subgroup2_y = start_y + (row_height - text_height) // 2
                # draw.text((lesson_info_subgroup2_x, lesson_info_subgroup2_y), "Нет, Нет, Нет", font=font,
                #           fill=(0, 0, 0))
                # draw.text((lesson_info_subgroup1_x, lesson_info_subgroup1_y), "Нет, Нет, Нет", font=font,
                #           fill=(255, 255, 255))

                # if lesson_info_subgroup2 != -1:

                # lesson_info_subgroup1_width = (
                #             font.getbbox(lesson_info_subgroup1)[2] - font.getbbox(lesson_info_subgroup1)[0])
                # lesson_info_subgroup1_x = column_width1 + (column_width2 // 2 - lesson_info_subgroup1_width) // 2
                # lesson_info_subgroup1_y = start_y + (row_height - text_height) // 2
                #
                # draw.text((lesson_info_subgroup1_x, lesson_info_subgroup1_y), "Нет, Нет, Нет", font=font,
                #           fill=(0, 0, 0))
                # draw.text((lesson_info_subgroup2_x, lesson_info_subgroup2_y), "Нет, Нет, Нет", font=font,
                #           fill=(255, 255, 255))

            # рисуем номер урока
            draw.text((lesson_number_x, lesson_number_y), lesson_number, font=font, fill=(0, 0, 0))

        # Сохраняем изображение в файл
        image.save(path)


PARSER = Parser(PATH_TO_FONT)
