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


TEXT = TextMessage(('hello', '''Осторожно 🐌 расписание СУНЦ УрФУ!
Этот бот может:
🎓 Быстро найти актуальное расписание по твоему запросу
🎓 Оперативно уведомить о любых изменениях в твоем школьном расписании

✅ Пройди регистрацию в пару кликов:''',
                    '''Watch out for the SESC URFU 🐌  schedule!
This bot can:
🎓 Quickly find the current schedule according to your request
🎓 Promptly notify you of any changes in your school schedule

✅ Register in a couple of clicks:'''),
                   ('choose_role',  'Выбери свою роль', 'Choose your role'),
                   ('choose_sub_info_group', 'Выбери свой класс', 'Choose your class'),
                   ('choose_sub_info_teacher', 'Выбери ФИО учителя', 'Choose your name'),
                   ('choose_sub_info_auditory', 'Выбери аудиторию', 'Choose auditory'),
                   ('student', 'Ученик', 'Student'),
                   ('teacher', 'Преподаватель', 'Teacher'),
                   ('parent', 'Родитель', 'Parent'),
                   ('auditory', 'Аудитория', 'Auditory'),
                   ('group', 'Класс', 'Group'),
                   ('today', 'Расписание на сегодня', 'Schedule for today'),
                   ('tomorrow', 'Расписание на завтра', 'Schedule for tomorrow'),
                   ('all', 'Все расписание', 'All schedule'),
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
                   ('weekdays_kb', {
                       1: 'Понедельник',
                       2: 'Вторник',
                       3: 'Среда',
                       4: 'Четверг',
                       5: 'Пятница',
                       6: 'Суббота',
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
                   ('choose_type', 'Для кого/чего ищешь расписание?',
                    'Who/what are you looking for a schedule for?'),
                   ('choose_day', 'Выбери день недели', 'Choose a day of the week'),
                   ('no_schedule', 'Занятий нет', 'There are no classes'),
                   ('all_days', 'Конкретный день недели', 'A specific day of the week'),
                   ('choose_letter', 'Выбери первую букву фамилии учителя',
                    "Choose the first letter of the teacher's last name"),
                   ('back', '⬅ Назад', '⬅ Back'),
                   ('changed_schedule', 'Изменения в расписании на', 'Schedule changes for'),
                   ('yes', 'Да', 'Yes'),
                   ('no', 'Нет', 'No'),
                   ('aus', "Вы уверены?", 'Are you sure?'),
                   ('admin_sending_message', 'Сообщения отправлены, ошибок - ', 'Messages sent, errors - '),
                   ('get_feedback', 'Напишите и отправьте свой отзыв прямо здесь',
                    'Write and send your feedback right here'),
                   ('feedback_done', 'Отзыв успешно отправлен', 'The review has been sent successfully'),
                   ('administration_role', 'Администрация', 'Administration'))
