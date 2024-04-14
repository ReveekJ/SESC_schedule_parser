from typing import Optional

from pydantic import BaseModel, field_validator


# TODO: сделать более продвинутую модель
class User(BaseModel):
    id: int | str
    role: str
    sub_info: str
    lang: str
    login: Optional[str] = None
    password: Optional[str] = None
    elective_courses: Optional[list[str]] = None

    @field_validator('id')
    def id_validator(cls, value: int | str):
        if isinstance(value, str):
            return int(value)
        return value

    @field_validator('role')
    def role_validate(cls, value: str):
        if value not in ['group', 'teacher', 'administrator']:
            raise ValueError('Bad role')
        return value

    def __getitem__(self, item):
        return self.__dict__[item]  # it works

