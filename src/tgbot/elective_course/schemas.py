import datetime
from typing import Optional, Literal, Any, Annotated

from pydantic import BaseModel, field_validator, Field
from pydantic_core.core_schema import ValidationInfo


from src.tgbot.sesc_info import SESC_Info
from .elective_info import ElectiveInfo


class ElectiveCourse(BaseModel):
    id: Optional[int] = 0  # опционально так как при создании курса id не указывается, а определяется автоматически
    # на sql
    subject: str
    short_subject: Annotated[str, Field(validate_default=True, exclude=True)] = ''
    pulpit: str
    teacher_name: str
    weekday: int
    time_from: datetime.time
    time_to: datetime.time
    auditory: str
    is_diffs: Optional[bool] = False
    diffs_teacher: Optional[str] = ''
    diffs_auditory: Optional[str] = ''
    diffs_time_from: Optional[datetime.time | None] = None
    diffs_time_to: Optional[datetime.time | None] = None
    is_cancelled: Optional[bool] = False


    @field_validator('short_subject')
    def set_short_string(cls, v, values: ValidationInfo):
        sub = values.data['subject']
        return sub[:20] + '...' if len(sub) > 20 else sub

    def model_dump(
            self,
            *,
            mode: Literal['timetable', 'common'] | str = 'common',
            include=None,
            exclude=None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
    ) -> dict[str, Any]:
        if mode == 'timetable':
            if self.is_cancelled:
                return {'subject': 'ОТМЕНЕНО',
                        'auditory': 'ОТМЕНЕНО',
                        'teacher': self.subject,
                        'group': '',
                        'subgroup': 0,
                        'number': self.time_from,
                        'date': 1}  # для выделения желтым
            else:
                time_from = (self.time_from if not self.is_diffs else self.diffs_time_from).strftime(ElectiveInfo.date_format.value)
                time_to = (self.time_to if not self.is_diffs else self.diffs_time_to).strftime(ElectiveInfo.date_format.value)
                return {'subject': self.subject,
                        'auditory': SESC_Info.AUDITORY_REVERSE[self.auditory if not self.is_diffs else self.diffs_auditory],
                        'teacher': SESC_Info.TEACHER_REVERSE[self.teacher_name if not self.is_diffs else self.diffs_teacher],
                        'group': '',
                        'subgroup': 0,
                        'number': time_from,
                        'date': 1 if self.is_diffs else None,
                        'custom_time': f'{time_from}-{time_to}'}  # для выделения желтым
        return super().model_dump(mode=mode,
                                  include=include,
                                  exclude=exclude,
                                  by_alias=by_alias,
                                  exclude_unset=exclude_unset,
                                  exclude_defaults=exclude_defaults,
                                  exclude_none=exclude_none,
                                  round_trip=round_trip,
                                  warnings=warnings)


class ElectiveCourseTimetable(BaseModel):
    lessons: list[ElectiveCourse]
    diffs: list[ElectiveCourse]

    def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'python',
            include=None,
            exclude=None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
    ) -> dict[str, Any]:
        return {'lessons': [lesson.model_dump(mode='timetable') for lesson in self.lessons],
                'diffs': [diffs.model_dump(mode='timetable') for diffs in self.diffs]}


class UserWorkSchema(BaseModel):
    pulpit: Optional[str] = None
    name_of_course: Optional[str] = None
