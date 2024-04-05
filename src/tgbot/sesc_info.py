import requests
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString

from src.my_typing import UnchangeableType


class SESCInfo:
    __instance = None

    GROUP = UnchangeableType()
    TEACHER = UnchangeableType()
    WEEKDAY = UnchangeableType()
    AUDITORY = UnchangeableType()
    TYPE = UnchangeableType()

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

        # {'Понедельник': '1', 'Вторник': '2', 'Среда': '3', 'Четверг': '4', 'Пятница': '5', 'Суббота': '6'}
        self.WEEKDAY = self.__parse_weekday_info()

        # {'АктЗал': '83', 'СпЗал': '79', '101': '64', '102': '65', '103': '66', '104': '67', '105': '68', ....}
        self.AUDITORY = self.__parse_auditory_info()
        self.AUDITORY_REVERSE = {v: key for key, v in self.AUDITORY.items()}

        # {'Аудитория': 'auditory', 'Учитель/преподаватель': 'teacher', 'Класс': 'group', 'Все аудитории': 'all'}
        self.TYPE = self.__parse_type_info()

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
