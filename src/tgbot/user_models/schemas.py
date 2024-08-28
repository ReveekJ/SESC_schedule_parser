from typing import Optional, Any
from typing_extensions import Literal

from pydantic import BaseModel
from pydantic.functional_validators import field_validator
from src.tgbot.elective_course.models import ElectiveCourseModel
from src.tgbot.elective_course.schemas import ElectiveCourse


class User(BaseModel):
    id: int | str
    role: str
    sub_info: str
    lang: str
    login: Optional[str] = 'None'
    password: Optional[str] = 'None'
    elective_course_replied: list[ElectiveCourse] = []

    # автоматически конвертирует из типа в бд в тип во всем остальном коде
    @field_validator('id', mode='before')
    @classmethod
    def id_validator(cls, value: int | str):
        if isinstance(value, str):
            return int(value)
        return value

    @field_validator('role', mode='before')
    @classmethod
    def role_validate(cls, value: str):
        if value not in ['group', 'teacher', 'administrator']:
            raise ValueError('Bad role')
        return value

    @field_validator('elective_course_replied', mode='before')
    @classmethod
    def elective_course_replied_validate(cls, value: list[ElectiveCourseModel]) -> list[ElectiveCourse]:
        res = []
        for i in value:
            res.append(ElectiveCourse(**i.__dict__))
        return res

    def model_dump(
        self,
        *,
        mode: Literal['json', 'python', 'elective_transaction'] | str = 'python',
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        dct = super().model_dump()

        if mode == 'elective_transaction':
            for index, elem in enumerate(dct.get('elective_course_replied')):
                dct['elective_course_replied'][index] = ElectiveCourseModel(**elem)
        return dct

    # @model_validator(mode='before')
    # @classmethod
    # def elective_course_replied_validate(cls, self):
    #     self.id = cls.id_validator(self.id)
    #     self.role = cls.role_validate(self.role)
    #
    #     if isinstance(self.elective_course_replied, list):
    #         for index, elem in enumerate(self.elective_course_replied):
    #             if isinstance(elem, ElectiveCourseModel):
    #                 self.elective_course_replied[index] = ElectiveCourse(**elem.__dict__)
    #     else:
    #         raise ValueError('Bad Elective Course Replied')
    #     return self

    def __getitem__(self, item):
        return self.__dict__[item]  # it works
