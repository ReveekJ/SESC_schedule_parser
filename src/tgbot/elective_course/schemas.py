from pydantic import BaseModel


class ElectiveCourse(BaseModel):
    name: str
    pulpit: str
    subject: str
    timetable: dict
    teacher_name: str
