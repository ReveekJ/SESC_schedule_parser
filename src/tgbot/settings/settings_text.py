from enum import Enum

class SettingsText(Enum):
    settings_header = {'ru': 'Здесь ты можешь настроить внешний вид твоего расписания',
                       'en': 'Here you can customize the appearance of your schedule'}
    change_style = {'ru': 'Изменить тему оформления',
                    'en': 'Change the theme'}
    choose_style = {'ru': 'Выбери тему оформления',
                    'en': 'Choose a theme'}
    its_okay = {'ru': 'Тебе нравится эта тема оформления?',
                'en': 'Do you like this theme?'}