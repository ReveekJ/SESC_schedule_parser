from enum import Enum


class ElectiveText(Enum):
    add = {'ru': '➕ Добавить факультатив',
           'en': '➕ Add an elective'}
    remove = {'ru': '💥 Удалить факультатив',
              'en': '💥 Remove optional'}
    edit_permanently = {'ru': '📒 Изменить на постоянной основе',
                        'en': '📒 Change permanently'}
    edit_for_one_day = {'ru': '⏱ Изменить на непостоянной основе',
                        'en': '⏱ Change on a non-permanent basis'}
    to_main = {'ru': '⬅ На главную',
               'en': '⬅ To main'}
    main_page = {'ru': 'Факультативы',
                 'en': 'Elective courses'}
    register_to_new_course = {'ru': 'Зарегистрироваться на новый факультатив',
                              'en': 'Register for a new elective'}
    choose_pulpit = {'ru': 'Выберите кафедру',
                     'en': 'Choose a pulpit'}
    choose_elective = {'ru': 'Выберите факультатив',
                       'en': 'Choose an elective'}
    successfully_register = {'ru': '✅ Ты успешно зарегистрировался на факультатив',
                             'en': '✅ You have successfully registered for an elective'}
    successfully_unsubscribe = {'ru': '✅ Ты успешно отписался от факультатива',
                                'en': '✅ You have successfully unsubscribe for an elective'}
    unsubscribe = {'ru': 'Отписаться от факультатива',
                   'en': 'Unsubscribe from an elective'}
    enter_a_name = {'ru': '🖋 Введите название факультатива',
                    'en': '🖋 Enter the name of the elective'}
    are_you_sure_remove = {'ru': 'Ты уверен, что хочешь удалить этот факультатив. Это действие нельзя отменить. Все '
                                 'ученики, записанные на этот курс, автоматически отпишутся от него',
                           'en': 'Are you sure you want to remove this elective? This action cannot be undone. All '
                                 'students enrolled in this course will automatically unsubscribe from it'}
    yes = {'ru': 'Да я уверен',
           'en': "Yes I'm sure"}
    no = {'ru': 'Нет, оставить все как есть',
          'en': 'No, leave everything as it is'}
    remove_done = {'ru': 'Успешно удален факультатив',
                   'en': 'Successfully removed elective course'}
    done = {'ru': '✅ Готово',
            'en': '✅ Done'}
    time_from = {'ru': '⏰ Выберите время начала факультатива',
                 'en': '⏰ Select the start time of the elective'}
    time_to = {'ru': '⏰ Выберите время конца факультатива',
               'en': '⏰ Select the end time of the elective'}
    cancel_elective = {'ru': '❌ Отменить факультатив',
                       'en': '❌ Cancel an elective'}
    error = {'ru': '❌ Произошла ошибка! Попробуй нажать на /start и повторить еще раз. Если ошибка сохраняется, '
                   'то напишите об этом нам в /feedback (приложите описание ваших дейтсвий, чтобы мы могли '
                   'воспроизвести ошибку и исправить её)',
             'en': '❌ An error has occurred! Try clicking start and repeating again. If the error persists, write about '
                   'it to us in feedback (attach a description of your actions so that we can reproduce the error and '
                   'fix it)'}
    same = {'ru': 'Оставить как раньше',
            'en': 'Leave as before'}
    same_name_already_exist = {'ru': '❌ Факультатив с этим названием уже существует, попробуй другое',
                               'en': '❌ An elective with this name already exists, try another one'}
    enter_login = {'ru': '🔐 Введи свой логин от электронного журнала',
                   'en': '🔐 Enter your login from the electronic journal'}
    enter_password = {'ru': '🔐 Введи свой пароль от электронного журнала',
                      'en': '🔐 Enter your password from the electronic journal'}
    login_password_incorrect = {'ru': '❌ Кажется, логин или пароль не подходят, попробуй еще раз',
                                'en': "❌ The username or password doesn't seem to work, try again"}
    settings_for = {'ru': '✅ Ты настраиваешь:',
                    'en': '✅ You\'re setting up:'}
