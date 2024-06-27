import datetime
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import Router, F, BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, TelegramObject, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from src.database import get_async_session
from src.tgbot.auxiliary import Form, bot
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.elective_course.elective_text import ElectiveText
from src.tgbot.elective_course.keyboard import get_pulpit_kb, get_elective_kb, get_back_kb, get_are_you_sure_kb, \
    get_choose_weekday_kb_elective, get_time_from_kb, \
    get_time_to_kb
from src.tgbot.elective_course.schemas import ElectiveCourse
from src.tgbot.elective_course.user_work import to_elective
from src.tgbot.keyboard import get_letter_of_teacher_kb, get_choose_teacher_kb, get_choose_auditory_kb
from src.tgbot.text import TEXT


#  проверить является ли юзер зарегистрированным учителем либо админом
#  если да, то предоставить такой функционао
#  1) добавить новый курс
#  2) удалить курс
#  3) посмотреть свои курсы (если ты учитель)
#  4) получить список текущих курсов в виде google sheet


class AdminMachine(Form):
    action = State()
    pulpit = State()
    name_of_course = State()
    removing = State()
    possible_days = State()  # этот стейт используется только для хранения
    day_of_week = State()  # список
    current_weekday_index = State()  # этот стейт используется только для хранения
    time_from = State()  # list
    is_canceled = State()  # list
    time_to = State()  # list
    teacher_letter = State()  # ничего нового, как при регистрации
    teacher = State()
    auditory = State()


class ErrorMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: CallbackQuery | Message,
                       data: Dict[str, Any]):
        try:
            await handler(event, data)
        except Exception as e:
            logging.error(e)
            await bot.send_message(text=ElectiveText.error.value[event.from_user.language_code],
                                   chat_id=event.from_user.id)


router = Router()
elective_course_scheduler = AsyncIOScheduler()
elective_course_scheduler.start()


# router.callback_query.middleware(ErrorMiddleware)
# router.message.middleware(ErrorMiddleware)

@router.callback_query(F.data == 'add')
@router.callback_query(F.data == 'remove')
@router.callback_query(F.data == 'edit_for_one_day')
@router.callback_query(F.data == 'edit_permanently')
async def send_pulpit(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    await state.clear()
    await state.set_state(AdminMachine.pulpit)
    await state.update_data(action=callback.data, prev=to_elective)

    await callback.message.edit_text(text=ElectiveText.choose_pulpit.value[lang],
                                     reply_markup=get_pulpit_kb(lang))

    await callback.answer()


@router.callback_query(AdminMachine.pulpit)
async def choose_pulpit(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    if callback.data == 'back':
        await state.update_data(prev=send_pulpit)
    else:
        await state.update_data(pulpit=callback.data, prev=send_pulpit)

    await state.set_state(AdminMachine.name_of_course)
    action = (await state.get_data()).get('action')

    if action == 'add':
        await callback.message.edit_text(text=ElectiveText.enter_a_name.value[lang],
                                         reply_markup=get_back_kb(lang))
    else:
        pulpit = (await state.get_data()).get('pulpit')
        session = await get_async_session()
        courses = await ElectiveCourseDB.get_courses_by_pulpit(session, pulpit)

        await callback.message.edit_text(text=ElectiveText.choose_elective.value[lang],
                                         reply_markup=get_elective_kb(lang, courses, []))

        await session.close()
    await callback.answer()


@router.callback_query(AdminMachine.name_of_course)
async def name_of_course_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    state_data = await state.get_data()

    if callback.data == 'back':
        name_of_course = state_data.get('name_of_course')
    else:
        await state.update_data(name_of_course=callback.data, prev=choose_pulpit)
        name_of_course = callback.data

    selected_days = state_data.get('days_of_week') if state_data.get('days_of_week') else []
    session = await get_async_session()
    possible_days = [i.weekday for i in (await ElectiveCourseDB.get_courses_by_subject(name_of_course))]
    possible_days_dct = {i: TEXT('weekdays_kb', lang)[i] for i in possible_days}

    await state.update_data(possible_days=possible_days_dct)
    await state.set_state(AdminMachine.day_of_week)
    await callback.message.edit_text(TEXT('choose_day', lang),
                                     reply_markup=get_choose_weekday_kb_elective(lang,
                                                                                 selected_days=selected_days,
                                                                                 possible_days=possible_days_dct))

    await session.close()
    await callback.answer()


# если срабатывает этот хендлер, то в action == add
@router.message(AdminMachine.name_of_course)
async def name_of_course_message(message: Message, state: FSMContext):
    lang = message.from_user.language_code

    await state.update_data(name_of_course=message.text)
    await state.set_state(AdminMachine.day_of_week)
    await message.answer(TEXT('choose_day', lang),
                         reply_markup=get_choose_weekday_kb_elective(lang, []),
                         disable_notification=True)


@router.callback_query(AdminMachine.removing)  # TODO: выбор дня при удалении
async def remove_solution(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    if callback.data == 'yes':
        state_data = await state.get_data()
        session = await get_async_session()
        name_of_course, weekdays = state_data.get('name_of_course'), state_data.get('day_of_week')

        await ElectiveCourseDB.delete_course(session, name_of_course, weekdays)
        await callback.message.edit_text(ElectiveText.remove_done.value[lang] + ' ' + name_of_course)

        await session.close()

    await to_elective(callback, state, edit_messages=False)  # возврат к основной странице факультативов
    await callback.answer()


@router.callback_query(AdminMachine.day_of_week, F.data == 'done')
async def day_of_week_done(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    # await state.update_data(day_of_week=iter((await state.get_data()).get('day_of_week')))
    state_data = await state.get_data()

    if state_data.get('day_of_week') in [None, []]:
        subject = state_data.get('name_of_course')
        possible_days = [i.weekday for i in (await ElectiveCourseDB.get_courses_by_subject(subject))]
        possible_days_dct = {i: TEXT('weekdays_kb', lang)[i] for i in possible_days}
        await callback.message.delete()
        await callback.message.answer(TEXT('choose_day', lang),
                                      reply_markup=get_choose_weekday_kb_elective(lang,
                                                                                  selected_days=[],
                                                                                  possible_days=possible_days_dct))
        return None

    action = state_data.get('action')

    if action == 'remove':
        await state.set_state(AdminMachine.removing)
        await callback.message.edit_text(text=ElectiveText.are_you_sure_remove.value[lang],
                                         reply_markup=get_are_you_sure_kb(lang))

        await callback.answer()
        return None
    # state_data = await state.get_data()
    # if state_data.get('action') in ['edit_permanently', 'edit_for_one_day']:
    #     session = await get_async_session()
    #     time_from = (await ElectiveCourseDB.get_courses_by_subject(session, state_data.get('name_of_course')))[0].
    session = await get_async_session()
    try:
        old_time = ((await ElectiveCourseDB.get_courses_by_subject(state_data.get('name_of_course')))[0]
                    .time_from)
    except IndexError:  # возникает если action=add
        old_time = None

    await state.set_state(AdminMachine.time_from)
    await state.update_data(prev=name_of_course_callback,
                            current_weekday_index=0  # первый день из выбранных
                            )
    await callback.message.edit_text(ElectiveText.time_from.value[lang],
                                     reply_markup=get_time_from_kb(lang, old_time=old_time))

    await session.close()
    await callback.answer()


@router.callback_query(AdminMachine.day_of_week)
async def day_of_week_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    state_data = await state.get_data()
    days_of_week = state_data.get('day_of_week')
    possible_days = state_data.get('possible_days')

    if days_of_week is None:
        days_of_week = []

    if callback.data[9:] in days_of_week:
        days_of_week.remove(callback.data[9:])
    else:
        days_of_week.append(int(callback.data[9:]))  # callback вида 'elective_1'

    if state_data.get('is_canceled') is None:
        state_data['is_canceled'] = [False]
    else:
        state_data['is_canceled'].append(False)

    await state.update_data(day_of_week=days_of_week, is_canceled=state_data['is_canceled'])

    await callback.message.edit_text(TEXT('choose_day', lang),
                                     reply_markup=get_choose_weekday_kb_elective(lang, days_of_week, possible_days))

    await callback.answer()


@router.callback_query(AdminMachine.time_from)
async def time_from_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    state_data = await state.get_data()
    session = await get_async_session()

    if callback.data == 'cancel_elective':
        await state.set_state(AdminMachine.teacher_letter)
        state_data['is_canceled'][-1] = True
        await state.update_data(is_canceled=state_data.get('is_canceled'))
        # await ElectiveCourseDB.cancel_course(session, state_data.get('name_of_course'))

        await callback.message.edit_text(TEXT('choose_letter', lang),
                                         reply_markup=get_letter_of_teacher_kb(lang))

    else:
        try:
            old_time = ((await ElectiveCourseDB.get_courses_by_subject(state_data.get('name_of_course')))[0]
                        .time_to)
        except IndexError:  # возникает если action=add
            old_time = None

        time_from = state_data.get('time_from')

        if time_from is None:
            time_from = [datetime.datetime.strptime(callback.data, '%H:%M').time()]
        else:
            time_from.append(datetime.datetime.strptime(callback.data, '%H:%M').time())

        await state.update_data(time_from=time_from)
        await state.set_state(AdminMachine.time_to)
        ind = state_data.get('current_weekday_index')
        await callback.message.edit_text(ElectiveText.time_to.value[lang], reply_markup=get_time_to_kb(lang,
                                                                                                       time_from[ind],
                                                                                                       old_time=old_time
                                                                                                       ))
    await session.close()
    await callback.answer()


# TODO: улучшенная работа back (чтобы при нажатии на back откидывало не так далеко)
@router.callback_query(AdminMachine.time_to)
async def time_to_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    state_data = await state.get_data()

    time_to = state_data.get('time_to')

    if time_to is None:
        time_to = [datetime.datetime.strptime(callback.data, '%H:%M').time()]
    else:
        time_to.append(datetime.datetime.strptime(callback.data, '%H:%M').time())

    await state.update_data(time_to=time_to)
    await state.set_state(AdminMachine.teacher_letter)

    await callback.message.edit_text(TEXT('choose_letter', lang),
                                     reply_markup=get_letter_of_teacher_kb(lang))

    await callback.answer()


# TODO: поменять клавиатуры на клавы с кнопкой same
@router.callback_query(AdminMachine.teacher_letter)
async def teacher_letter_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    await state.set_state(AdminMachine.teacher)
    await callback.message.edit_text(TEXT('choose_sub_info_teacher', lang),
                                     reply_markup=get_choose_teacher_kb(callback.data.split('_')[-1], lang))
    await callback.answer()


@router.callback_query(AdminMachine.teacher)
async def teacher_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code

    teacher = (await state.get_data()).get('teacher')
    if teacher is None:
        teacher = [callback.data]
    else:
        teacher.append(callback.data)

    await state.update_data(teacher=teacher)
    await state.set_state(AdminMachine.auditory)

    await callback.message.edit_text(TEXT('choose_sub_info_auditory', lang),
                                     reply_markup=get_choose_auditory_kb(lang),
                                     disable_notification=True)

    await callback.answer()


# TODO: аудитория онлайн и кафедры
@router.callback_query(AdminMachine.auditory)
async def auditory_callback(callback: CallbackQuery, state: FSMContext):
    lang = callback.from_user.language_code
    state_data = await state.get_data()
    session = await get_async_session()

    auditory = state_data.get('auditory')
    if auditory is None:
        auditory = [callback.data]
    else:
        auditory.append(callback.data)

    await state.update_data(auditory=auditory)
    if state_data.get('current_weekday_index') != len(state_data.get('day_of_week')) - 1:
        await state.set_state(AdminMachine.time_from)
        next_day = state_data.get('current_weekday_index') + 1
        await state.update_data(current_weekday_index=next_day)

        try:
            old_time = (await ElectiveCourseDB.get_course_by_subject_and_weekday(session,
                                                                                 state_data.get('name_of_course'),
                                                                                 next_day)).time_from
        except IndexError:  # если курс не найден
            old_time = None

        await callback.message.edit_text(ElectiveText.time_from.value[lang],
                                         reply_markup=get_time_from_kb(lang, old_time))
    else:  # когда проходим все дни
        (subject, action, day_of_week,
         time_from, time_to,
         teacher, name_of_course, pulpit, is_canceled) = [state_data.get(i) for i in
                                                          ('name_of_course', 'action', 'day_of_week', 'time_from',
                                                           'time_to', 'teacher', 'name_of_course', 'pulpit',
                                                           'is_canceled')]
        courses: list[ElectiveCourse] = []
        old_courses: list[ElectiveCourse] = []
        for _weekday, _time_from, _time_to, _teacher, _auditory, _is_canceled in zip(day_of_week, time_from, time_to,
                                                                                     teacher,
                                                                                     auditory, is_canceled):
            try:
                old_courses.append(
                    (await ElectiveCourseDB.get_course_by_subject_and_weekday(session, subject, int(_weekday))))
            except IndexError as e:
                old_courses.append(ElectiveCourse(subject=name_of_course,
                                                  pulpit=pulpit,
                                                  teacher_name=_teacher,
                                                  weekday=_weekday,
                                                  time_from=datetime.time(0, 0),
                                                  time_to=datetime.time(0, 0),
                                                  auditory=_auditory))  # заглушка
            courses.append(ElectiveCourse(subject=name_of_course,
                                          pulpit=pulpit,
                                          teacher_name=_teacher,
                                          weekday=_weekday,
                                          time_from=old_courses[-1].time_from if _is_canceled else _time_from,
                                          time_to=old_courses[-1].time_to if _is_canceled else _time_to,
                                          auditory=_auditory,
                                          is_canceled=is_canceled if _is_canceled else False,
                                          is_diffs=old_courses[-1].is_diffs,
                                          diffs_teacher=old_courses[-1].diffs_teacher,
                                          diffs_auditory=old_courses[-1].diffs_auditory))

        match action:
            case 'add':
                for course in courses:
                    await ElectiveCourseDB.add_course(session, course)
            case 'edit_permanently':
                for course in courses:
                    await ElectiveCourseDB.update_course(session, course, course.weekday)
            case 'edit_for_one_day':
                for old_course, course in zip(old_courses, courses):
                    old_course: ElectiveCourse
                    course: ElectiveCourse

                    if course.is_cancelled:
                        await ElectiveCourseDB.cancel_course(session, course.subject)
                    else:
                        new_course = ElectiveCourse(subject=old_course.subject,
                                                    pulpit=old_course.pulpit,
                                                    teacher_name=old_course.teacher_name,
                                                    weekday=old_course.weekday,
                                                    time_from=old_course.time_from,
                                                    time_to=old_course.time_to,
                                                    auditory=old_course.auditory,
                                                    is_diffs=True,
                                                    diffs_teacher=course.teacher_name,
                                                    diffs_auditory=course.auditory)
                        await ElectiveCourseDB.update_course(session, new_course)

                    #  устанавливаем задачу на отмену этих изменений (изменения же временные)
                    now = datetime.datetime.now()
                    day = datetime.datetime(now.year, now.month, now.day, 23, 59)
                    removing_time = day + datetime.timedelta(days=course.weekday - day.weekday() - 1)
                    elective_course_scheduler.add_job(ElectiveCourseDB.remove_changes, DateTrigger(removing_time),
                                                      args=(course,))

        await to_elective(callback, state, edit_messages=True)  # возвращаемся на главную

    await session.close()
    await callback.answer()

# TODO: если действие - это изменить на один день, то добавить кнопку отменить изменения
# TODO: автоуправление сессиями в бд
# TODO: bug when start with crypto_key, when xor of passwd and crypto_key larger than utf-8 can contain
# TODO: write to db task to remove changes
