from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager

from src.tgbot.auxiliary import send_schedule
from src.tgbot.elective_course.elective_course import ElectiveCourseDB
from src.tgbot.parser import ELECTIVE_PARSER
from src.tgbot.text import TEXT


async def get_course_name(dialog_manager: DialogManager) -> str:
    course_id: str = dialog_manager.dialog_data.get('name_of_course')

    if not course_id.isdigit():
        return course_id

    return (await ElectiveCourseDB.get_course_by_id(int(course_id))).subject


async def send_elective_schedule(callback: CallbackQuery, lang: str, day: str, pass_if_no_schedule: bool = False):
    user_id = callback.from_user.id
    file = await ELECTIVE_PARSER.parse(user_id, weekday=day)

    try:
        await callback.message.delete()
    except TelegramBadRequest: # когда сообщения нету
        pass

    if file == 'NO_SCHEDULE':
        if pass_if_no_schedule:
            return None
        await callback.message.answer(TEXT('no_schedule', lang), disable_notification=True)
    else:
        schedule = FSInputFile(file)

        await send_schedule(chat_id=callback.message.chat.id,
                            schedule=schedule,
                            short_name_text_mes='main_schedule',
                            role='elective',
                            sub_info='',
                            weekday=int(day),
                            lang=lang)
