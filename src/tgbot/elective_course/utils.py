from aiogram_dialog import DialogManager

from src.tgbot.elective_course.elective_course import ElectiveCourseDB


async def get_course_name(dialog_manager: DialogManager) -> str:
    course_id: str = dialog_manager.dialog_data.get('name_of_course')

    if not course_id.isdigit():
        return course_id

    return (await ElectiveCourseDB.get_course_by_id(int(course_id))).subject
