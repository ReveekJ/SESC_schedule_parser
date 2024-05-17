from enum import Enum


class ElectiveText(Enum):
    add = {'ru': 'Добавить факультатив',
           'en': 'Add an elective'}
    remove = {'ru': 'Удалить факультатив',
              'en': 'Remove optional'}
    to_main = {'ru': 'На главную',
               'en': 'To main'}
    main_page = {'ru': 'Факультативы',
                 'en': 'Elective courses'}
