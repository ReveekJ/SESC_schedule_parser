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
    register_to_new_course = {'ru': 'Зарегистрироваться на новый факультатив',
                              'en': 'Register for a new elective'}
    choose_pulpit = {'ru': 'Выберите кафедру',
                     'en': 'Choose a pulpit'}
    choose_elective = {'ru': 'Выберите факультатив',
                       'en': 'Choose an elective'}
    successfully_register = {'ru': 'Ты успешно зарегистрировался на факультатив',
                             'en': 'You have successfully registered for an elective'}
    successfully_unsubscribe = {'ru': 'Ты успешно отписался от факультатива',
                                'en': 'You have successfully unsubscribe for an elective'}
    unsubscribe = {'ru': 'Отписаться от факультатива',
                   'en': 'Unsubscribe from an elective'}
