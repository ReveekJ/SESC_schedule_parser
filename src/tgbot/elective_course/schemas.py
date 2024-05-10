import datetime

from pydantic import BaseModel


class ElectiveCourse(BaseModel):
    subject: str
    pulpit: str
    teacher_name: str
    weekday: int
    time_from: datetime.time
    time_to: datetime.time
