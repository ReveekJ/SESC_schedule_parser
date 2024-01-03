import aiohttp
import simplejson as json
from PIL import Image, ImageDraw, ImageFont
from tgbot.sesc_info import SESC_Info


class Parser:

    # Инициализация json-файла
    def __init__(self, font_path):
        self.font_path = font_path
        # self.data = SESC_Info

    # Преобразование информации и управление процессом создания таблицы
    async def parse(self, _type: str, _second: str, _weekday: str):
        path = (__file__[:__file__.rfind('/', 0, __file__.rfind('/'))] + '/' +
                f'schedules/schedule{_second}.png')

        if _type == 'group':
            info = await self.__get_student_json(int(_weekday), int(_second))
        elif _type == 'teacher':
            info = await self.__get_teacher_json(int(_weekday), _second)
        else:
            raise ValueError('IDK')

        if not info['lessons']:
            return 'NO_SCHEDULE'

        await self.__create_table(info['lessons'], path)

        return path

    @staticmethod  # Отправление запроса учителя
    async def __get_teacher_json(weekday: int, teacher: str):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(
                    f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType=teacher&{weekday=}'
                    f'&teacher={teacher}') as resp:
                return json.loads(await resp.text())

    @staticmethod  # Отправление запроса ученика
    async def __get_student_json(weekday: int, group: int):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(
                    f'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii?type=11&scheduleType=group&{weekday=}&{group=}'
            ) as resp:
                return json.loads(await resp.text())

    async def check_for_changes_student(self):
        changed_groups = []

        for day in SESC_Info.WEEKDAY.values():
            for group in SESC_Info.GROUP.values():
                schedule = await self.__get_student_json(int(day), int(group))
                print(group, day)
                if schedule['diffs']:
                    changed_groups.append(('group', group, day))
        return changed_groups

    async def check_for_changes_teacher(self):
        changed_teachers = []

        for day in SESC_Info.WEEKDAY.values():
            for teacher in SESC_Info.TEACHER.values():
                schedule = await self.__get_teacher_json(int(day), teacher)
                print(teacher, day)
                if schedule['diffs']:
                    changed_teachers.append(('teacher', teacher, day))

        return changed_teachers

    # Создание таблицы
    async def __create_table(self, info: list, path: str):
        # написал ChatGPT
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

        # Рисуем таблицу с данными
        lessons = sorted(info, key=lambda x: x['number'])

        # TODO: пофиксить баг. Когда есть subgroup этот цикл никогда не исполнится, нужно переписать условие,
        #  не по длинне, а по наибольшему number
        p = len(lessons) + 1
        # Если уроков меньше 7, добавляем пустые уроки, чтобы получить 7 строк
        while len(lessons) < 7:
            lessons.append(
                {'uid': None, 'subject': '', 'auditory': '', 'group': '', 'teacher': '', 'subgroup': 0, 'number': p,
                 'weekday': None})
            p += 1

        skipped_rows = 0
        # Рисуем таблицу с данными
        for i, lesson in enumerate(lessons):
            start_y = (i - skipped_rows + 1) * row_height

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
                lesson_info = f"{lesson['subject']}, {lesson['teacher']}, {lesson['auditory']}" \
                    if lesson['subject'] != '' else ''
                lesson_info_width = font.getbbox(lesson_info)[2] - font.getbbox(lesson_info)[0]
                lesson_info_x = column_width1 + (column_width2 - lesson_info_width) // 2
                lesson_info_y = start_y + (row_height - text_height) // 2

                draw.text((lesson_info_x, lesson_info_y), lesson_info, font=font, fill=(0, 0, 0))

                # рисуем номер урока
                draw.text((lesson_number_x, lesson_number_y), lesson_number, font=font, fill=(0, 0, 0))

            else:
                # TODO: доюавить разделительную полоску между расписаниеми для subgroup
                lesson_info_subgroup1 = ''
                lesson_info_subgroup2 = ''

                # Рисуем урок, учителя и аудиторию во второй колонке с центровкой
                if lesson['subgroup'] == 1:
                    lesson_info_subgroup1 = f"{lesson['subject']}, {lesson['teacher']}, {lesson['auditory']}"

                    lesson2 = [i for i in lessons if i['subgroup'] == 2 and i['number'] == lesson['number']][0]
                    lesson_info_subgroup2 = f"{lesson2['subject']}, {lesson2['teacher']}, {lesson2['auditory']}"
                elif lesson['subgroup'] == 2:
                    skipped_rows += 1
                    continue

                lesson_info_subgroup1_width = (font.getbbox(lesson_info_subgroup1)[2] -
                                               font.getbbox(lesson_info_subgroup1)[0])

                lesson_info_subgroup1_x = column_width1 + (column_width2 // 2 - lesson_info_subgroup1_width) // 2
                lesson_info_subgroup1_y = start_y + (row_height - text_height) // 2

                lesson_info_subgroup2_width = font.getbbox(lesson_info_subgroup2)[2] - \
                                              font.getbbox(lesson_info_subgroup2)[0]

                lesson_info_subgroup2_x = column_width1 + column_width2 // 2 + (
                        column_width2 // 2 - lesson_info_subgroup2_width) // 2
                lesson_info_subgroup2_y = start_y + (row_height - text_height) // 2

                draw.text((lesson_info_subgroup1_x, lesson_info_subgroup1_y), lesson_info_subgroup1, font=font,
                          fill=(0, 0, 0))
                draw.text((lesson_info_subgroup2_x, lesson_info_subgroup2_y), lesson_info_subgroup2, font=font,
                          fill=(0, 0, 0))

                # рисуем номер урока
                draw.text((lesson_number_x, lesson_number_y), lesson_number, font=font, fill=(0, 0, 0))

        # Сохраняем изображение в файл
        image.save(path)


PARSER = Parser('/usr/share/fonts/truetype/freefont/FreeSans.ttf')
