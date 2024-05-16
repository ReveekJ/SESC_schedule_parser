import datetime
from typing import Optional

from sqlalchemy import BigInteger, Sequence
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.database import Base


class ElectiveCourseModel(Base):
    __tablename__ = "elective_course"

    id: Mapped[BigInteger] = mapped_column(Sequence('elective_course_id_seq'), type_=BigInteger,
                                           unique=True, primary_key=True, onupdate='CASCADE')
    subject: Mapped[str]
    pulpit: Mapped[str]
    teacher_name: Mapped[str]
    weekday: Mapped[int]
    time_from: Mapped[datetime.time]
    time_to: Mapped[datetime.time]
    auditory: Mapped[Optional[str]] = mapped_column(default='')
    is_diffs: Mapped[bool] = mapped_column(default=False)

    users_replied: Mapped[Optional[list['UsersModel']]] = relationship(
        back_populates='elective_course_replied',
        secondary='elective_transactions'
    )


from src.tgbot.user_models.models import UsersModel
