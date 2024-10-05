from enum import Enum

class SettingsText(Enum):
    settings_header = {'ru': 'Здесь ты можешь настроить внешний вид твоего расписания',
                       'en': 'Here you can customize the appearance of your schedule'}
    change_style = {'ru': 'Изменить тему оформления',
                    'en': 'Change the style'}
    choose_style = {'ru': 'Выбери тему оформления',
                    'en': 'Choose a style'}
    # its_okay = {'ru': 'Тебе нравится эта тема оформления?',
    #             'en': 'Do you like this style?'}
    this_is_current_style = {'ru': '✅ Это текущая выбранная тема ✅\n\n',
                             'en': '✅ This is the currently selected style ✅\n\n'}
    style_changed = {'ru': '✅ Тема успешно изменена ✅',
                     'en': '✅ Style successfully changed ✅'}
    # loading = {'ru': 'Загрузка...',
    #            'en': 'Loading...'}
