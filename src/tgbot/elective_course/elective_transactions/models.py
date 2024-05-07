from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.database import Base


class ElectiveCourseTransactionsModel(Base):
    __tablename__ = 'elective_transactions'

    course_name: Mapped[str] = mapped_column(ForeignKey('elective_course.subject'),
                                             primary_key=True) 
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'),
                                         primary_key=True)
