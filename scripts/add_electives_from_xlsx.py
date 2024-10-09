import asyncio
from pprint import pprint

import pandas as pd

from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.sesc_info import SESC_Info
from datetime import datetime, time


table = pd.read_excel('elec.xlsx')

#  переделываем кафедры
dct = {'гуманитарного образования': 'Humanitarian education',
       'иностранных языков': 'Foreign languages',
       'математики': 'Mathematics',
       'психофизической культуры': 'Physical education',
       'филологии': 'Philology',
       'химии и биологии': 'Chemistry and biology',
       'информатики': 'Computer science',
       'физики и астрономии': 'Physics and astronomy'}
for i in range(len(table.pulpit)):
    table['pulpit'][i] = dct[table.pulpit[i]]

def get_time(t: str) -> time:
    try:
        return datetime.strptime(t, "%H.%M").time()
    except ValueError:
        return datetime.strptime(t, "%H:%M").time()

def parse_time_range(time_str):
    # Список доступных времен
    available_times = sorted([
        time(8, 10), time(11, 40), time(15, 30),
        time(19, 0), time(19, 40), time(17, 0),
        time(18, 15), time(14, 15), time(13, 15),
        time(18, 30), time(20, 0), time(21, 0),
        time(9, 0), time(17, 30)
    ])

    # Проверяем, содержит ли строка дефис
    if '-' in time_str:
        start_str, end_str = time_str.split('-')
    else:
        start_str = time_str
        end_str = None  # Устанавливаем end_str в None, если его нет

    # Преобразуем строку в объект time
    start_time = get_time(start_str)

    # Если end_str не задан, ищем следующий элемент в available_times
    if end_str is None:
        # Находим следующий элемент за start_time
        for t in available_times:
            if t > start_time:
                end_time = t
                break
        else:
            end_time = start_time  # Если нет следующего времени
    else:
        end_time = get_time(end_str)

    return start_time, end_time


def rename_teacher(wrong: str, right: str):
    for index, elem in enumerate(table.teacher):
        if elem == wrong:
            table['teacher'][index] = right


wrongs = ['Девяткова А.А.',
          'Ананьина Т.А.',
          'Бабушкина С. В. ',
          'Бабушкина С.В.',
          'Белькова А.В. Салтыкова О.И.',
          'Беляева В.В.',
          'Бондарь А.А.',
          'Гулика С.В.',
          'Гусева А.Ф.',
          'Джозеф Доусон Ио',
          'Екимов Д.А.',
          'Зайнетдинова О.Ф.',
          'ИЕНиМ, Сокольский С.А.',
          'Ибатуллин А.А.',
          'Иванова Е.В.',
          'Иванова М.Э.',
          'Камалиева Я.Г.',
          'Келина М.А.',
          'Киямова И.М.',
          'Колпакова Е.В.',
          'Кремешкова С.А.',
          'Кузьмина Л.Г.',
          'Кузьмина Л.Г. ',
          'Ланских А.В.',
          'Лямжин А.С.',
          'Ляховец Д.Ю.',
          'Малыгин И.В.',
          'Мартынов К.В.',
          'Масленникова М.И.',
          'Наумова Ю.В.',
          'Невская М.А.',
          'Некоз Е.П. ',
          'Нохрин С.Э.',
          'Овчинников А.Г.',
          'Пузикова А.А.',
          'Савинов И.А.',
          'Салтыкова О.И.',
          'Симонова А.А.',
          'Соколова Е.М.',
          'Ульянченко Е.В.',
          'Усачев С.А.',
          'Храмцов М.В.',
          'Цалковская Л.А.',
          'Черемичкина И.А.',
          'Чернова М.В. ',
          'Черноусова Н.А.',
          'Черных О.А.',
          'Шабалина А.А.',
          'Шерстобитова О.Г.',
          'Щербак Т.Л.',
          'Юнышев Д.Л.',
          'Юткин Г.А.',
          'Ярина Е.Г.']

rights = ['Девяткова А. А.',
          'Ананьина Т. А.',
          'Бабушкина С. В.',
          'Бабушкина С. В.',
          'Салтыкова О. И.',
          'Беляева В. В.',
          'Бондарь А. А.',
          'Гулика С. В.',
          'Гусева А. Ф.',
          'Доусон',
          'Екимов Д. А.',
          'Зайнетдинова О. Ф.',
          'ИЕНиМ, Сокольский С. А.',
          'Ибатуллин А. А.',
          'Иванова Е. В.',
          'Иванова М. Э.',
          'Камалиева Я. Г.',
          'Келина М. А.',
          'Киямова И. М.',
          'Колпакова Е. В.',
          'Кремешкова С. А.',
          'Кузьмина Л. Г.',
          'Кузьмина Л. Г. ',
          'Ланских А. В.',
          'Лямжин А. С.',
          'Ляховец Д. Ю.',
          'Малыгин И. В.',
          'Мартынов К. В.',
          'Масленникова М. И.',
          'Наумова Ю. В.',
          'Невская М. А.',
          'Некоз Е. П. ',
          'Нохрин С. Э.',
          'Овчинников А. Г.',
          'Пузикова А. А.',
          'Савинов И. А.',
          'Салтыкова О. И.',
          'Симонова А. А.',
          'Соколова Е. М.',
          'Ульянченко Е. В.',
          'Усачев С. А.',
          'Храмцов М. В.',
          'Цалковская Л. А.',
          'Черемичкина И. А.',
          'Чернова М. В. ',
          'Черноусова Н. А.',
          'Черных О. А.',
          'Шабалина А. А.',
          'Шерстобитова О. Г.',
          'Щербак Т. Л.',
          'Юнышев Д. Л.',
          'Юткин Г. А.',
          'Ярина Е. Г.']


for w, r in zip(wrongs, rights):
    rename_teacher(w, r.strip())


electives = []
days_of_week = {
    'понедельник': 1,
    'вторник': 2,
    'среда': 3,
    'четверг': 4,
    'пятница': 5,
    'суббота': 6,
    'воскресенье': 7
}


for name, pulpit, teacher, data, ____ in table.values:
    try:
        teacher_num = SESC_Info.TEACHER[teacher]
    except KeyError:
        teacher_num = '52525252'

    try:
        weekday, times, auditory = data.split(', ')
        try:
            auditory = SESC_Info.ELECTIVE_AUDITORY[auditory.strip().capitalize()]
        except Exception as e:
            auditory = '12341234'
    except Exception as e:
        weekday, times = data.split(', ')
        auditory = '12341234'

    start, end = parse_time_range(times)

    course = ElectiveCourse(
        subject=name.strip(),
        pulpit=pulpit,
        teacher_name=teacher_num,
        weekday=days_of_week[weekday.lower()],
        time_from=start,
        time_to=end,
        auditory=auditory,
    )
    electives.append(course)


async def add_to_db():
    for i in electives:
        await ElectiveCourseDB.add_course(i)

asyncio.run(add_to_db())
