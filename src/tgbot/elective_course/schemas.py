import datetime
from typing import Optional, Literal, Any

from pydantic import BaseModel, field_validator

from src.tgbot.sesc_info import SESC_Info


class ElectiveCourse(BaseModel):
    id: Optional[int] = 0  # опционально так как при создании курса id не указывается, а определяется автоматически
    # на sql
    subject: str
    pulpit: str
    teacher_name: str
    weekday: int
    time_from: datetime.time
    time_to: datetime.time
    auditory: Optional[str] = ''
    is_diffs: bool = False
    diffs_teacher: Optional[str] = ''
    diffs_auditory: Optional[str] = ''
    is_cancelled: Optional[bool] = False

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
            return {'subject': self.subject,
                    'auditory': SESC_Info.AUDITORY_REVERSE[self.auditory if not self.is_diffs else self.diffs_auditory],
                    'teacher': SESC_Info.TEACHER_REVERSE[self.teacher_name if not self.is_diffs else self.diffs_teacher],
                    'group': '',
                    'subgroup': 0,
                    'number': self.time_from,
                    'date': 1 if self.is_diffs else None}  # для выделения желтым
        return super().model_dump(mode=mode,
                                  include=include,
                                  exclude=exclude,
                                  by_alias=by_alias,
                                  exclude_unset=exclude_unset,
                                  exclude_defaults=exclude_defaults,
                                  exclude_none=exclude_none,
                                  round_trip=round_trip,
                                  warnings=warnings)

    @field_validator('auditory')
    # @classmethod
    def auditory_validator(cls, v):
        if v is None:
            return ''
        else:
            return v


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
