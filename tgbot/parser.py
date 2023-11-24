from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class Parser:
    def __init__(self):
        self.driver = Firefox()
        self.driver.get('https://lyceum.urfu.ru/ucheba/raspisanie-zanjatii')

    def parse(self, first_select: str, second_select: str, third_select: str):
        selects = {'tx_suncschedule_schedule[type]': first_select,
                   f'tx_suncschedule_schedule[{first_select}]': second_select,
                   'tx_suncschedule_schedule[weekday]': third_select}

        for i in selects:
            elem = Select(self.driver.find_element(By.NAME, i))
            elem.select_by_value(selects[i])

        schedule = self.driver.find_element(By.TAG_NAME, 'table')
        schedule.screenshot(f'schedules/{first_select}_{second_select}_{third_select}.png')

    def quit(self):
        self.driver.quit()
