import requests
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString


class SESCInfo:
    def __init__(self):
        self.url = 'https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii'
        self.__r = requests.get(self.url)
        self.__soup = bs(self.__r.text, 'html.parser')
        self.__selects = self.__soup.find_all('select')

        self.GROUP = self.__parse_group_info()
        # self.GROUP_REVERSED = {i: j for i, j in self.GROUP.items()}
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
