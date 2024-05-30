from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from src.database import Base


class ElectiveCourseTransactionsModel(Base):
    __tablename__ = 'elective_transactions'

    course_name: Mapped[BigInteger] = mapped_column(ForeignKey('elective_course.id', ondelete='CASCADE'), type_=BigInteger,
                                                    primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), type_=BigInteger,
                                                primary_key=True)
