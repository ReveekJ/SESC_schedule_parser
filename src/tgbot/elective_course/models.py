import datetime
from typing import Optional, Literal

from sqlalchemy import BigInteger, Sequence
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.database import Base


class ElectiveCourseModel(Base):
    __tablename__ = "elective_course"

    id: Mapped[BigInteger] = mapped_column(Sequence('elective_course_id_seq'), type_=BigInteger,
                                           unique=True, primary_key=True)
    subject: Mapped[str]
    pulpit: Mapped[str]
    teacher_name: Mapped[str]
    weekday: Mapped[int]
    time_from: Mapped[datetime.time]
    time_to: Mapped[datetime.time]
    auditory: Mapped[str]
    is_diffs: Mapped[bool] = mapped_column(default=False)
    diffs_teacher: Mapped[Optional[str]]
    diffs_auditory: Mapped[Optional[str]]
    diffs_time_from: Mapped[Optional[datetime.time]]
    diffs_time_to: Mapped[Optional[datetime.time]]
    is_cancelled: Mapped[Optional[bool]] = mapped_column(default=False)

    users_replied: Mapped[Optional[list['UsersModel']]] = relationship(
        back_populates='elective_course_replied',
        secondary='elective_transactions',
        cascade="delete"
    )


from src.tgbot.user_models.models import UsersModel
