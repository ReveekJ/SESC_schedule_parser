import requests
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString


class UnchangeableType:
    def __init__(self):
        self.count_of_change = 0

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __set__(self, instance, value):
        if self.count_of_change < 3:
            self.count_of_change += 1
            return setattr(instance, self.name, value)
        else:
            raise ValueError('You can not change this attribute')

    def __get__(self, instance, owner):
        return getattr(instance, self.name)


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
        self.__r = requests.get(self.url)
        self.__soup = bs(self.__r.text, 'html.parser')
        self.__selects = self.__soup.find_all('select')

        self.GROUP = self.__parse_group_info()
        self.TEACHER = self.__parse_teacher_info()
        self.WEEKDAY = self.__parse_weekday_info()
        self.AUDITORY = self.__parse_auditory_info()
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
