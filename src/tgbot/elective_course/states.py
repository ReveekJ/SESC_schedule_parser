from aiogram.fsm.state import State, StatesGroup


class AdminMachine(StatesGroup):
    action = State()
    pulpit = State()
    name_of_course_input = State()
    name_of_course_selector = State()
    removing = State()
    day_of_week = State()
    time_from = State()
    is_canceled = State()
    time_to = State()
    teacher_letter = State()  # ничего нового, как при регистрации
    teacher = State()
    auditory = State()


class UserWorkMachine(StatesGroup):
    start = State()
    all_days = State()
    choose_pulpit = State()
    choose_elective = State()
    choose_weekday = State()


class AuthMachine(StatesGroup):
    selfie = State()
