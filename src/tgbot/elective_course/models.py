from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.database import Base


class ElectiveCourseModel(Base):
    __tablename__ = "elective_course"

    subject: Mapped[str] = mapped_column(unique=True, primary_key=True, onupdate='CASCADE')
    pulpit: Mapped[str]
    timetable: Mapped[str]  # Просто строчка со временем (e.g. 8:20-9:00)
    teacher_name: Mapped[str]

    users_replied: Mapped[list['UsersModel']] = relationship(
        back_populates='elective_course_replied',
        secondary='elective_transactions'
    )


from src.tgbot.user_models.models import UsersModel
