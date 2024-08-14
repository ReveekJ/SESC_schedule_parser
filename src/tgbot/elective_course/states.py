from aiogram.fsm.state import State, StatesGroup


class AdminMachine(StatesGroup):
    # start = State()
    action = State()
    pulpit = State()
    name_of_course_input = State()
    name_of_course_selector = State()
    removing = State()
    # possible_days = State()  # этот стейт используется только для хранения
    day_of_week = State()  # список
    # current_weekday_index = State()  # этот стейт используется только для хранения
    time_from = State()  # list
    is_canceled = State()  # list
    time_to = State()  # list
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