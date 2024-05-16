import datetime
from typing import Optional, Literal, Any

from pydantic import BaseModel, field_validator


class ElectiveCourse(BaseModel):
    id: Optional[int]  # опционально так как при создании курса id не указывается, а определяется автоматически на sql
    subject: str
    pulpit: str
    teacher_name: str
    weekday: int
    time_from: datetime.time
    time_to: datetime.time
    auditory: Optional[str] = ''
    is_diffs: bool = False

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
                    'auditory': self.auditory,
                    'teacher': self.teacher_name,
                    'group': '',
                    'subgroup': 0,
                    'number': self.time_from}
        return super().model_dump()

    @field_validator('auditory')
    @classmethod
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
