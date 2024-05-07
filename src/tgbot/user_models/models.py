from typing import Optional

from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base

columns_json = {0: 'id',
                1: 'role',
                2: 'sub_info',
                3: 'lang'}


class UsersModel(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(unique=True, primary_key=True, onupdate='CASCADE')
    role: Mapped[str]
    sub_info: Mapped[str]
    lang: Mapped[str]
    login: Mapped[Optional[str]]
    password: Mapped[Optional[str]]

    elective_course_replied: Mapped[Optional[list['ElectiveCourseModel']]] = relationship(
        back_populates='users_replied',
        secondary='elective_transactions'
    )


from src.tgbot.elective_course.models import ElectiveCourseModel
