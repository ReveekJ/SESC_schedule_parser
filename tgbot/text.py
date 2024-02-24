import googletrans
from googletrans import Translator


# Порядок ввода: tuple(краткое имя, русское вариант) ......
# Перевод на англ, автоматический
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
        raise ValueError('You can not change this attribute')

    @classmethod
    def __args_to_dict(cls, arguments: tuple):
        res = {'ru': {},
               'en': {}}

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
        return self.__text[lang][short_name_text_mes]


TEXT = TextMessage(('welcome', 'Добро пожаловать, ', 'Welcome, '),
                   ('hello', '✅ Пройди регистрацию в пару кликов', '✅ Register in a couple of clicks:'),
                   ('choose_role', 'Выбери роль', 'Choose your role'),
                   ('choose_sub_info_group', 'Выбери класс', 'Choose your class'),
                   ('choose_sub_info_teacher', 'Выбери ФИО', "Choose the teacher's full name"),
                   ('choose_sub_info_auditory', 'Выбери аудиторию', 'Choose auditory'),
                   ('student', '👨‍🎓Ученик', '👨‍🎓Student'),
                   ('teacher', '👩‍🎓Преподаватель', '👩‍🎓Teacher'),
                   ('parent', '👨‍👩‍👧Родитель', '👨‍👩‍👧Parent'),
                   ('auditory', 'Аудитория', 'Auditory'),
                   ('group', 'Класс', 'Group'),
                   ('registration_done', '✅ Регистрация прошла успешно', '✅ Registration was successful'),
                   ('today', 'На сегодня', 'Today'),
                   ('tomorrow', 'На завтра', 'Tomorrow'),
                   ('all', 'Все расписание', 'All schedule'),
                   ('main', 'Расписание', 'Schedule'),
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
                   ('choose_letter', 'Выбери первую букву фамилии',
                    "Choose the first letter of last name"),
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

print(TEXT)
