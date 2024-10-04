from aiogram.fsm.state import StatesGroup, State


class SettingsSG(StatesGroup):
    start = State()
    list_of_styles = State()
    is_it_okay = State()
    loading = State()
