from sqlalchemy import Column, Text
from src.database import Base

columns_json = {0: 'id',
                1: 'role',
                2: 'sub_info',
                3: 'lang'}


class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Text, primary_key=True)
    role = Column(Text)
    sub_info = Column(Text)
    lang = Column(Text)
    login = Column(Text, nullable=True)
    password = Column(Text, nullable=True)
    elective_courses = Column(Text, nullable=True)
