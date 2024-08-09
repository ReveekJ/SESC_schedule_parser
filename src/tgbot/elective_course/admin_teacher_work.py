import datetime

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.tgbot.auxiliary import bot
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.elective_text import ElectiveText
from .getters import ElectiveInfo
from .states import AdminMachine

# from src.tgbot.elective_course.user_work import to_elective

#  проверить является ли юзер зарегистрированным учителем либо админом
#  если да, то предоставить такой функционао
#  1) добавить новый курс
#  2) удалить курс
#  3) посмотреть свои курсы (если ты учитель)
#  4) получить список текущих курсов в виде google sheet


elective_course_scheduler = AsyncIOScheduler()
elective_course_scheduler.start()


# router.callback_query.middleware(ErrorMiddleware)
# router.message.middleware(ErrorMiddleware)


# async def send_pulpit(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     await state.clear()
#     await state.set_state(AdminMachine.pulpit)
#     await state.update_data(action=callback.data, prev=to_elective)
#
#     await callback.message.edit_text(text=ElectiveText.choose_pulpit.value[lang],
#                                      reply_markup=get_pulpit_kb(lang))
#
#     await callback.answer()
async def __save_to_dialog_data(data, dialog_manager: DialogManager):
    await dialog_manager.update({dialog_manager.current_context().state.state.split(':')[-1]: data})


async def save_to_dialog_data_and_next(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                       **kwargs):
    await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)
    await dialog_manager.next()


async def pulpit_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    action = dialog_manager.dialog_data.get('action')

    await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)
    await dialog_manager.switch_to(
        AdminMachine.name_of_course_input if action == 'add' else AdminMachine.name_of_course_selector)


async def name_input_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    if not (await ElectiveCourseDB.get_courses_by_subject(message.text)):
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.update({'name_of_course': message.text})
        await dialog_manager.switch_to(AdminMachine.day_of_week)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=ElectiveText.same_name_already_exist.value[message.from_user.language_code])


async def name_select_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, *args, **kwargs):
    data = callback.data.split(':')[-1]
    await dialog_manager.update({'name_of_course': data})
    await dialog_manager.update({'course': (await ElectiveCourseDB.get_courses_by_subject(data))[0]})

    await dialog_manager.switch_to(AdminMachine.day_of_week)
    # await dialog_manager.switch_to(AdminMachine.)


async def days_of_week_saver(callback: CallbackQuery, widget: MessageInput, dialog_manager: DialogManager, *args,
                             **kwargs):
    days = dialog_manager.dialog_data.get('days_of_week')
    data = int(callback.data.split(':')[-1])

    if not days:
        days = [data]
    elif data in days:
        days: list
        days.remove(data)
    else:
        days.append(data)

    await dialog_manager.update({'days_of_week': days})


async def switch_to_time_from_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                      **kwargs):
    if not dialog_manager.dialog_data.get('days_of_week'):
        return None

    # await dialog_manager.next()
    await dialog_manager.switch_to(AdminMachine.time_from)


async def old_teacher_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await __save_to_dialog_data(dialog_manager.dialog_data.get('course').teacher_name, dialog_manager)
    await dialog_manager.switch_to(AdminMachine.auditory)


async def old_time_from_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
                                **kwargs):
    await __save_to_dialog_data(dialog_manager.dialog_data.get('course').time_from, dialog_manager)
    await dialog_manager.next()


async def old_time_to_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await __save_to_dialog_data(dialog_manager.dialog_data.get('course').time_to, dialog_manager)
    await dialog_manager.next()


async def time_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    row_data = callback.data.split(':')
    data = datetime.datetime.strptime(row_data[-2] + ':' + row_data[-1], ElectiveInfo.date_format.value).time()
    await __save_to_dialog_data(data, dialog_manager)
    await dialog_manager.next()


async def back_time_to_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data.pop('time_from', None)
    dialog_manager.dialog_data.pop('time_to', None)


async def back_teacher_letter_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data.pop('time_to', None)


async def cancel_elective_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    #  TODO: вызвать функцию отмены курса, а затем либо спросить следующий день, либо закунчить работу с изменениями
    pass
    # await dialog_manager.switch_to(AdminMachine)


async def auditory_handler(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await __save_to_dialog_data(callback.data.split(':')[-1], dialog_manager)
    days_of_week = dialog_manager.dialog_data.get('days_of_week')
    if isinstance(days_of_week, list):
        await dialog_manager.update({'days_of_week': next(iter(dialog_manager.dialog_data.get('days_of_week')))})

    # TODO: сохранить информацию до лучших времен
    # print(dialog_manager)
    # print(dialog_manager.dialog_data)
    try:
        await dialog_manager.update({'days_of_week': next(days_of_week)})  # days_of_week is iterator
    except StopIteration:  # значит дни закончились, нужно проводить изменения
        pass
        #  TODO: process data

    # подготовка след диалога
    data_for_next_dialog = dialog_manager.dialog_data.copy()
    for i in ('time_from', 'time_to', 'is_canceled', 'teacher_letter', 'teacher', 'auditory'):
        data_for_next_dialog.pop(i, None)
    print(data_for_next_dialog)
    await dialog_manager.start(AdminMachine.time_from, data_for_next_dialog)
# async def prev_time_from_saver(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args,
# **kwargs): await __save_to_dialog_data(dialog_manager.dialog_data.get('prev_time_from'), dialog_manager) await
# dialog_manager.next()

#
# @router.callback_query(AdminMachine.name_of_course)
# async def name_of_course_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#     state_data = await state.get_data()
#
#     if callback.data == 'back':
#         name_of_course = state_data.get('name_of_course')
#     else:
#         await state.update_data(name_of_course=callback.data, prev=choose_pulpit)
#         name_of_course = callback.data
#
#     selected_days = state_data.get('days_of_week') if state_data.get('days_of_week') else []
#     session = await get_async_session()
#     possible_days = [i.weekday for i in (await ElectiveCourseDB.get_courses_by_subject(name_of_course))]
#     possible_days_dct = {i: TEXT('weekdays_kb', lang)[i] for i in possible_days}
#
#     await state.update_data(possible_days=possible_days_dct)
#     await state.set_state(AdminMachine.day_of_week)
#     await callback.message.edit_text(TEXT('choose_day', lang),
#                                      reply_markup=get_choose_weekday_kb_elective(lang,
#                                                                                  selected_days=selected_days,
#                                                                                  possible_days=possible_days_dct))
#
#     await session.close()
#     await callback.answer()
#
#
# # если срабатывает этот хендлер, то в action == add
# @router.message(AdminMachine.name_of_course)
# async def name_of_course_message(message: Message, state: FSMContext):
#     lang = message.from_user.language_code
#
#     await state.update_data(name_of_course=message.text)
#     await state.set_state(AdminMachine.day_of_week)
#     await message.answer(TEXT('choose_day', lang),
#                          reply_markup=get_choose_weekday_kb_elective(lang, []),
#                          disable_notification=True)
#
#
# @router.callback_query(AdminMachine.removing)  # TODO: выбор дня при удалении
# async def remove_solution(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     if callback.data == 'yes':
#         state_data = await state.get_data()
#         session = await get_async_session()
#         name_of_course, weekdays = state_data.get('name_of_course'), state_data.get('day_of_week')
#
#         await ElectiveCourseDB.delete_course(session, name_of_course, weekdays)
#         await callback.message.edit_text(ElectiveText.remove_done.value[lang] + ' ' + name_of_course)
#
#         await session.close()
#
#     await to_elective(callback, state, edit_messages=False)  # возврат к основной странице факультативов
#     await callback.answer()
#
#
# @router.callback_query(AdminMachine.day_of_week, F.data == 'done')
# async def day_of_week_done(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     # await state.update_data(day_of_week=iter((await state.get_data()).get('day_of_week')))
#     state_data = await state.get_data()
#
#     if state_data.get('day_of_week') in [None, []]:
#         possible_days_dct = state_data.get('possible_days')
#         await callback.message.delete()
#         await callback.message.answer(TEXT('choose_day', lang),
#                                       reply_markup=get_choose_weekday_kb_elective(lang,
#                                                                                   selected_days=[],
#                                                                                   possible_days=possible_days_dct))
#         return None
#
#     action = state_data.get('action')
#
#     if action == 'remove':
#         await state.set_state(AdminMachine.removing)
#         await callback.message.edit_text(text=ElectiveText.are_you_sure_remove.value[lang],
#                                          reply_markup=get_are_you_sure_kb(lang))
#
#         await callback.answer()
#         return None
#     # state_data = await state.get_data()
#     # if state_data.get('action') in ['edit_permanently', 'edit_for_one_day']:
#     #     session = await get_async_session()
#     #     time_from = (await ElectiveCourseDB.get_courses_by_subject(session, state_data.get('name_of_course')))[0].
#     session = await get_async_session()
#     try:
#         old_time = ((await ElectiveCourseDB.get_courses_by_subject(state_data.get('name_of_course')))[0]
#                     .time_from)
#     except IndexError:  # возникает если action=add
#         old_time = None
#
#     await state.set_state(AdminMachine.time_from)
#     await state.update_data(prev=name_of_course_callback,
#                             current_weekday_index=0  # первый день из выбранных
#                             )
#     await callback.message.edit_text(ElectiveText.time_from.value[lang],
#                                      reply_markup=get_time_from_kb(lang, old_time=old_time))
#
#     await session.close()
#     await callback.answer()
#
#
# @router.callback_query(AdminMachine.day_of_week)
# async def day_of_week_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#     state_data = await state.get_data()
#     days_of_week = state_data.get('day_of_week')
#     possible_days = state_data.get('possible_days')
#
#     if days_of_week is None:
#         days_of_week = []
#
#     if callback.data[9:] in days_of_week:
#         days_of_week.remove(callback.data[9:])
#     else:
#         days_of_week.append(int(callback.data[9:]))  # callback вида 'elective_1'
#
#     if state_data.get('is_canceled') is None:
#         state_data['is_canceled'] = [False]
#     else:
#         state_data['is_canceled'].append(False)
#
#     await state.update_data(day_of_week=days_of_week, is_canceled=state_data['is_canceled'])
#
#     await callback.message.edit_text(TEXT('choose_day', lang),
#                                      reply_markup=get_choose_weekday_kb_elective(lang, days_of_week, possible_days))
#
#     await callback.answer()
#
#
# @router.callback_query(AdminMachine.time_from)
# async def time_from_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#     state_data = await state.get_data()
#     session = await get_async_session()
#
#     if callback.data == 'cancel_elective':
#         await state.set_state(AdminMachine.teacher_letter)
#         state_data['is_canceled'][-1] = True
#         await state.update_data(is_canceled=state_data.get('is_canceled'))
#         # await ElectiveCourseDB.cancel_course(session, state_data.get('name_of_course'))
#
#         await callback.message.edit_text(TEXT('choose_letter', lang),
#                                          reply_markup=get_letter_of_teacher_kb(lang))
#
#     else:
#         try:
#             old_time = ((await ElectiveCourseDB.get_courses_by_subject(state_data.get('name_of_course')))[0]
#                         .time_to)
#         except IndexError:  # возникает если action=add
#             old_time = None
#
#         time_from = state_data.get('time_from')
#
#         if time_from is None:
#             time_from = [datetime.datetime.strptime(callback.data, '%H:%M').time()]
#         else:
#             time_from.append(datetime.datetime.strptime(callback.data, '%H:%M').time())
#
#         await state.update_data(time_from=time_from)
#         await state.set_state(AdminMachine.time_to)
#         ind = state_data.get('current_weekday_index')
#         await callback.message.edit_text(ElectiveText.time_to.value[lang], reply_markup=get_time_to_kb(lang,
#                                                                                                        time_from[ind],
#                                                                                                        old_time=old_time
#                                                                                                        ))
#     await session.close()
#     await callback.answer()
#
#
# # TODO: улучшенная работа back (чтобы при нажатии на back откидывало не так далеко)
# @router.callback_query(AdminMachine.time_to)
# async def time_to_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#     state_data = await state.get_data()
#
#     time_to = state_data.get('time_to')
#
#     if time_to is None:
#         time_to = [datetime.datetime.strptime(callback.data, '%H:%M').time()]
#     else:
#         time_to.append(datetime.datetime.strptime(callback.data, '%H:%M').time())
#
#     await state.update_data(time_to=time_to)
#     await state.set_state(AdminMachine.teacher_letter)
#
#     await callback.message.edit_text(TEXT('choose_letter', lang),
#                                      reply_markup=get_letter_of_teacher_kb(lang))
#
#     await callback.answer()
#
#
# # TODO: поменять клавиатуры на клавы с кнопкой same
# @router.callback_query(AdminMachine.teacher_letter)
# async def teacher_letter_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     await state.set_state(AdminMachine.teacher)
#     await callback.message.edit_text(TEXT('choose_sub_info_teacher', lang),
#                                      reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang))
#     await callback.answer()
#
#
# @router.callback_query(AdminMachine.teacher)
# async def teacher_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#
#     teacher = (await state.get_data()).get('teacher')
#     if teacher is None:
#         teacher = [callback.data]
#     else:
#         teacher.append(callback.data)
#
#     await state.update_data(teacher=teacher)
#     await state.set_state(AdminMachine.auditory)
#
#     await callback.message.edit_text(TEXT('choose_sub_info_auditory', lang),
#                                      reply_markup=get_choose_auditory_kb(lang),
#                                      disable_notification=True)
#
#     await callback.answer()
#
#
# # TODO: аудитория "онлайн" и "кафедры"
# @router.callback_query(AdminMachine.auditory)
# async def auditory_callback(callback: CallbackQuery, state: FSMContext):
#     lang = callback.from_user.language_code
#     state_data = await state.get_data()
#     session = await get_async_session()
#
#     auditory = state_data.get('auditory')
#     if auditory is None:
#         auditory = [callback.data]
#     else:
#         auditory.append(callback.data)
#
#     await state.update_data(auditory=auditory)
#     if state_data.get('current_weekday_index') != len(state_data.get('day_of_week')) - 1:
#         await state.set_state(AdminMachine.time_from)
#         next_day = state_data.get('current_weekday_index') + 1
#         await state.update_data(current_weekday_index=next_day)
#
#         try:
#             old_time = (await ElectiveCourseDB.get_course_by_subject_and_weekday(session,
#                                                                                  state_data.get('name_of_course'),
#                                                                                  next_day)).time_from
#         except IndexError:  # если курс не найден
#             old_time = None
#
#         await callback.message.edit_text(ElectiveText.time_from.value[lang],
#                                          reply_markup=get_time_from_kb(lang, old_time))
#     else:  # когда проходим все дни
#         (subject, action, day_of_week,
#          time_from, time_to,
#          teacher, name_of_course, pulpit, is_canceled) = [state_data.get(i) for i in
#                                                           ('name_of_course', 'action', 'day_of_week', 'time_from',
#                                                            'time_to', 'teacher', 'name_of_course', 'pulpit',
#                                                            'is_canceled')]
#         courses: list[ElectiveCourse] = []
#         old_courses: list[ElectiveCourse] = []
#         for _weekday, _time_from, _time_to, _teacher, _auditory, _is_canceled in zip(day_of_week, time_from, time_to,
#                                                                                      teacher,
#                                                                                      auditory, is_canceled):
#             try:
#                 old_courses.append(
#                     (await ElectiveCourseDB.get_course_by_subject_and_weekday(session, subject, int(_weekday))))
#             except IndexError:
#                 old_courses.append(ElectiveCourse(subject=name_of_course,
#                                                   pulpit=pulpit,
#                                                   teacher_name=_teacher,
#                                                   weekday=_weekday,
#                                                   time_from=datetime.time(0, 0),
#                                                   time_to=datetime.time(0, 0),
#                                                   auditory=_auditory))  # заглушка
#             courses.append(ElectiveCourse(subject=name_of_course,
#                                           pulpit=pulpit,
#                                           teacher_name=_teacher,
#                                           weekday=_weekday,
#                                           time_from=old_courses[-1].time_from if _is_canceled else _time_from,
#                                           time_to=old_courses[-1].time_to if _is_canceled else _time_to,
#                                           auditory=_auditory,
#                                           is_canceled=is_canceled if _is_canceled else False,
#                                           is_diffs=old_courses[-1].is_diffs,
#                                           diffs_teacher=old_courses[-1].diffs_teacher,
#                                           diffs_auditory=old_courses[-1].diffs_auditory))
#
#         match action:
#             case 'add':
#                 for course in courses:
#                     await ElectiveCourseDB.add_course(session, course)
#             case 'edit_permanently':
#                 for course in courses:
#                     await ElectiveCourseDB.update_course(session, course, course.weekday)
#             case 'edit_for_one_day':
#                 for old_course, course in zip(old_courses, courses):
#                     old_course: ElectiveCourse
#                     course: ElectiveCourse
#
#                     if course.is_cancelled:
#                         await ElectiveCourseDB.cancel_course(session, course.subject)
#                     else:
#                         new_course = ElectiveCourse(subject=old_course.subject,
#                                                     pulpit=old_course.pulpit,
#                                                     teacher_name=old_course.teacher_name,
#                                                     weekday=old_course.weekday,
#                                                     time_from=old_course.time_from,
#                                                     time_to=old_course.time_to,
#                                                     auditory=old_course.auditory,
#                                                     is_diffs=True,
#                                                     diffs_teacher=course.teacher_name,
#                                                     diffs_auditory=course.auditory)
#                         await ElectiveCourseDB.update_course(session, new_course)
#
#                     #  устанавливаем задачу на отмену этих изменений (изменения же временные)
#                     now = datetime.datetime.now()
#                     day = datetime.datetime(now.year, now.month, now.day, 23, 59)
#                     removing_time = day + datetime.timedelta(days=course.weekday - day.weekday() - 1)
#                     elective_course_scheduler.add_job(ElectiveCourseDB.remove_changes, DateTrigger(removing_time),
#                                                       args=(course,))
#
#         await to_elective(callback, state, edit_messages=True)  # возвращаемся на главную
#
#     await session.close()
#     await callback.answer()

# TODO: если действие - это изменить на один день, то добавить кнопку отменить изменения
# TODO: автоуправление сессиями в бд
# TODO: write to db task to remove changes
