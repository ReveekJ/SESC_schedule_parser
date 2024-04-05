from sqlalchemy import Column, Text

from src.database import Base


class ElectiveCourseModel(Base):
    __tablename__ = "elective_course"

    name = Column(Text, primary_key=True, nullable=False)
    pulpit = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    timetable = Column(Text, nullable=False)  # в виде json
    teacher_name = Column(Text, nullable=False)  # TODO: add foreign key
