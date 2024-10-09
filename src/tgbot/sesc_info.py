import requests
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString


class SESCInfo:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        self.url = 'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
        self.__r = requests.get(self.url, verify=False)
        self.__soup = bs(self.__r.text, 'html.parser')
        self.__selects = self.__soup.find_all('select')

        # {'8А': '1', '8В': '2', '8Е': '34', '9А': '4', '9Б': '5', '9В': '3', '9Г': '11', '9Е': '9', ...}
        self.GROUP = self.__parse_group_info()
        self.GROUP_REVERSE = {v: k for k, v in self.GROUP.items()}

        # {'Александрова Т. И.': '153', 'Алексеева М. А.': '1', 'Ананьина Т. А.': '2', 'Анисимова Е. Г.': '195', ....}
        self.TEACHER = self.__parse_teacher_info()
        self.TEACHER_REVERSE = {v: key for key, v in self.TEACHER.items()}
        self.ELECTIVE_TEACHER = {**{'Кто-то': '52525252'}, **self.TEACHER}
        self.TEACHER_REVERSE.update({'52525252': 'Кто-то'})

        # {'Понедельник': '1', 'Вторник': '2', 'Среда': '3', 'Четверг': '4', 'Пятница': '5', 'Суббота': '6'}
        self.WEEKDAY = self.__parse_weekday_info()

        # {'АктЗал': '83', 'СпЗал': '79', '101': '64', '102': '65', '103': '66', '104': '67', '105': '68', ....}
        self.AUDITORY = self.__parse_auditory_info()
        self.AUDITORY_REVERSE = {v: key for key, v in self.AUDITORY.items()}
        self.ELECTIVE_AUDITORY = {**{'Онлайн': '525252', 'Какая-то': '12341234'}, **self.AUDITORY}
        self.AUDITORY_REVERSE.update({'525252': 'Онлайн', '12341234': 'Какая-то'})

        # {'Аудитория': 'auditory', 'Учитель/преподаватель': 'teacher', 'Класс': 'group', 'Все аудитории': 'all'}
        self.TYPE = self.__parse_type_info()

        # важно чтобы порядок в одном и другом языке был одинаков
        self.PULPIT = {
            'ru': ['Гуманитарное образование', 'Иностранные языков', 'Математика',
                   'Психофизическая культура', 'Филология', 'Физика и астрономия', 'Химия и биология', 'Информатика',
                   'Отдел воспитательной работы'],
            'en': ['Humanitarian education', 'Foreign languages', 'Mathematics',
                   'Physical education', 'Philology', 'Physics and astronomy', 'Chemistry and biology',
                   'Computer science', 'Department of educational work']
        }

        self.TEACHER_LETTERS = sorted(list(set(i[0] for i in self.TEACHER.keys())))

        self.DEFAULT_TIME_OF_LESSONS = {
            1: '9:00-9:40',
            2: '9:50-10:30',
            3: '10:45-11:25',
            4: '11:40-12:20',
            5: '12:35-13:15',
            6: '13:35-14:15',
            7: '14:35-15:15',
        }


    @classmethod
    def __parse(cls, options: list, exceptions: list):
        res = {}
        for i in options:
            # sample i: <option value="31">11С</option>
            if isinstance(i, NavigableString):
                continue

            i = str(i)
            res[i[i.find('>') + 1: i.find('</option>')]] = i[i.find('="') + 2: i.find('">')]

        return {key: elem for key, elem in res.items() if key not in exceptions}

    def __parse_group_info(self) -> dict:
        return self.__parse(self.__selects[1], ['', 'Выберите класс'])

    def __parse_teacher_info(self) -> dict:
        return self.__parse(self.__selects[3], ['Выберите преподавателя', 'Нет', 'Учитель'])

    def __parse_weekday_info(self) -> dict:
        return self.__parse(self.__selects[4], ['Выберите день'])

    def __parse_auditory_info(self) -> dict:
        return self.__parse(self.__selects[2], ['Выберите аудиторию', 'Нет'])

    def __parse_type_info(self) -> dict:
        return self.__parse(self.__selects[0], [])


SESC_Info = SESCInfo()
