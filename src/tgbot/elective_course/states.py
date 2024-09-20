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


class ElectiveCourseMachine(StatesGroup):
    start = State()
    all_days = State()
    register_or_unsubscribe = State()
    choose_pulpit = State()
    choose_page = State()
    choose_elective = State()


class AuthMachine(StatesGroup):
    selfie = State()
