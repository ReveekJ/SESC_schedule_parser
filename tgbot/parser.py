from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import os
import datetime


class Parser:
    def __init__(self, expiration_time_of_schedule: int = 20):
        # expiration_time_of_schedule в минутах
        self.expiration_time_of_schedule = expiration_time_of_schedule
        self.driver = Firefox()
        self.driver.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii')

    def parse(self, first_select: str, second_select: str, third_select: str) -> str:
        path = (__file__[:__file__.rfind('/', 0, __file__.rfind('/'))] + '/' +
                f'schedules/{first_select}_{second_select}_{third_select}__{datetime.datetime.now()}')

        if not self.__check_file_in_path(path):
            selects = {'tx_suncschedule_schedule[type]': first_select,
                       f'tx_suncschedule_schedule[{first_select}]': second_select,
                       'tx_suncschedule_schedule[weekday]': third_select}

            for i in selects:
                elem = Select(self.driver.find_element(By.NAME, i))
                elem.select_by_value(selects[i])

            schedule = self.driver.find_element(By.TAG_NAME, 'table')

            try:
                schedule.screenshot(path + '.png')
            except WebDriverException:
                print('Поймал ошибку')
                schedule.screenshot(path + '.png')

        return path + '.png'

    def __check_file_in_path(self, path: str) -> bool:
        for files in os.scandir(path[:path.rfind('/')]):
            if files.name[:files.name.find('__')] == path[path.rfind('/') + 1: path.find('__')] and \
                    (datetime.datetime.now() - datetime.datetime.strptime(path[path.find('__') + 2:],
                                                                          '%Y-%m-%d %H:%M:%S.%f')) \
                    < datetime.timedelta(minutes=self.expiration_time_of_schedule):
                return True

        return False

    def quit(self):
        self.driver.quit()
