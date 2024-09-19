from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base


columns_json = {0: 'id',
                1: 'role',
                2: 'sub_info',
                3: 'lang'}


class UsersModel(Base):
    __tablename__ = 'users'

    id: Mapped[BigInteger] = mapped_column(type_=BigInteger, unique=True, primary_key=True, onupdate='CASCADE')
    role: Mapped[str]
    sub_info: Mapped[str]
    lang: Mapped[str]
    is_approved_user: Mapped[Optional[bool]] = mapped_column(default=False)
    style: Mapped[int]

    elective_course_replied: Mapped[Optional[list['ElectiveCourseModel']]] = relationship(
        back_populates='users_replied',
        secondary='elective_transactions',
        cascade="delete"
    )


from src.tgbot.elective_course.models import ElectiveCourseModel
