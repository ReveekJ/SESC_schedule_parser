from typing import Type, List, Dict

from pydantic import BaseModel, field_validator


# {'type': 'group', 'lessons': [{'uid': 10826, 'subject': 'Математика', 'auditory': '303', 'group': '8Е', 'teacher':
# 'Олейник А.С.', 'subgroup': 0, 'number': 2, 'weekday': 1}, {'uid': 10827, 'subject': 'Русский', 'auditory': '322',
# 'group': '8Е', 'teacher': 'Косова Л. В.', 'subgroup': 0, 'number': 3, 'weekday': 1}, {'uid': 10828, 'subject':
# 'АнглЯзык', 'auditory': '', 'group': '8Е', 'teacher': '', 'subgroup': 0, 'number': 4, 'weekday': 1}, {'uid': 10829,
# 'subject': 'АнглЯзык', 'auditory': '', 'group': '8Е', 'teacher': '', 'subgroup': 0, 'number': 5, 'weekday': 1},
# {'uid': 10830, 'subject': 'Информатика', 'auditory': '226', 'group': '8Е', 'teacher': 'Беляева Т.Д.', 'subgroup':
# 0, 'number': 6, 'weekday': 1}, {'uid': 10831, 'subject': 'Информатика', 'auditory': '226', 'group': '8Е',
# 'teacher': 'Беляева Т.Д.', 'subgroup': 0, 'number': 7, 'weekday': 1}, {'uid': 12495, 'subject': 'Математика',
# 'auditory': '303', 'group': '8Е', 'teacher': 'Олейник А.С.', 'subgroup': 0, 'number': 1, 'weekday': 1}], 'diffs': []}
# class ElectiveCourseTimetable(BaseModel):
#     lessons: list[dict]
#     diffs: list[dict]  # может быть пустым списком, но не может отсутствовать, так как это может сломать посторонние
#
#     # изображения
#
#     @field_validator('lessons')
#     def validate_lessons(cls, value: list[dict]):
#         for i in value:
#             if not all([1 if j in i.keys() else 0 for j in ('auditory', 'teacher', 'subgroup', 'number', 'weekday')]):
#                 raise ValueError('Не достаточное количество полей или их названия неверны')
#         return value
#
#     @field_validator('diffs')
#     def validate_diffs(cls, value: list[dict]):
#         if not value:
#             return value
#
#         for i in value:
#             if not all([1 if j in i.keys() else 0 for j in
#                         ('auditory', 'teacher', 'subgroup', 'number', 'weekday', 'date')]):
#                 raise ValueError('Не достаточное количество полей или их названия неверны')
#         return value
#
#     def to_dict(self) -> dict[str, Type[list[dict]] | list[dict]]:
#         return {'lessons': self.lessons, 'diffs': self.diffs}
#

class ElectiveCourse(BaseModel):
    subject: str
    pulpit: str
    timetable: str  # Просто строчка со временем (e.g. 8:20-9:00)
    teacher_name: str
