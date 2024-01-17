# порядок ввода: tuple(краткое имя, русское вариант, англиский вариант) ......
class TextMessage:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self, *args):
        self.__text = self.__args_to_dict(args)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        raise 'You can not change this attribute'

    @classmethod
    def __args_to_dict(cls, arguments: tuple):
        res = {'ru': {},
               'en': {}
               }

        for i in arguments:
            for index, value in enumerate(i):
                if index % 3 == 1:
                    res['ru'][i[0]] = value
                elif index % 3 == 2:
                    res['en'][i[0]] = value
                else:
                    continue
        return res

    def __call__(self, short_name_text_mes: str, lang: str):
        # session = DB()
        # await session.connect()
        # lang = await session.select_user_by_id(user_id)
        # lang = lang[columns_json[3]]
        return self.__text[lang][short_name_text_mes]


TEXT = TextMessage(('hello', 'Привет! Это бот, котрый может показать тебе актуальное расписание у любого класса и на '
                             'любой день в СУНЦ УрФУ!', 'Hi! This is a bot that can show you the current schedule for '
                                                        'any class and on any day in SESC UrFU!'),
                   ('choose_role', 'Выберите Вашу роль', 'Choose your role'),
                   ('choose_sub_info_group', 'Выберите Ваш класс', 'Choose your class'),
                   ('choose_sub_info_teacher', 'Выберите Ваше ФИО', 'Choose your name'),
                   ('choose_sub_info_auditory', 'Выберите аудиторию', 'Choose auditory'),
                   ('student', 'Ученик', 'Student'),
                   ('teacher', 'Учитель', 'Teacher'),
                   ('parent', 'Родитель', 'Parent'),
                   ('today', 'Расписание на сегодня', 'Schedule for today'),
                   ('tomorrow', 'Расписание на завтра', 'Schedule for tomorrow'),
                   ('all', 'Показать все расписание', 'View all schedule'),
                   ('main', 'Расписание на', 'Schedule for'),
                   ('month', ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                              'Октябрь', 'Ноябрь', 'Декабрь'],
                    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                     'November', 'December']),
                   ('weekdays', {
                       1: 'Понедельник',
                       2: 'Вторник',
                       3: 'Среду',
                       4: 'Четверг',
                       5: 'Пятницу',
                       6: 'Субботу',
                       7: 'Воскресенье'
                   },
                    {
                        1: 'Monday',
                        2: 'Tuesday',
                        3: 'Wednesday',
                        4: 'Thursday',
                        5: 'Friday',
                        6: 'Saturday',
                        7: 'Sunday'
                    }),
                   ('choose_type', 'Для кого/чего вы ищете расписание?',
                    'Who/what are you looking for a schedule for?'),
                   ('choose_day', 'Выберите день', 'Choose a day'),
                   ('no_schedule', 'Занятий нет', 'There are no classes'),
                   ('all_days', 'Показать на конкретный день', 'View all days'),
                   ('choose_letter', 'Выберите первую букву Вашей фамилии',
                    'Choose the first letter of your last name'),
                   ('back', 'Назад', 'Back'),
                   ('changed_schedule', 'Изменения в расписании на', 'Schedule changes for'),
                   ('yes', 'Да', 'Yes'),
                   ('no', 'Нет', 'No'),
                   ('aus', "Вы уверены?", 'Are you sure?'),
                   ('use', 'Чтобы продолжить используйте /start', 'To continue use /start'))
