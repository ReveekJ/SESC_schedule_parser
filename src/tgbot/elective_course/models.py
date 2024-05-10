import datetime
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.database import Base


class ElectiveCourseModel(Base):
    __tablename__ = "elective_course"

    id: Mapped[BigInteger] = mapped_column(type_=BigInteger, unique=True, primary_key=True, onupdate='CASCADE',
                                           autoincrement=True)
    subject: Mapped[str]
    pulpit: Mapped[str]
    teacher_name: Mapped[str]
    weekday: Mapped[int]
    time: Mapped[datetime.time]

    users_replied: Mapped[Optional[list['UsersModel']]] = relationship(
        back_populates='elective_course_replied',
        secondary='elective_transactions'
    )


from src.tgbot.user_models.models import UsersModel
