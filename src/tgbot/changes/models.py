from sqlalchemy import Column, Text, Integer
from src.database import Base


class Changes(Base):
    __tablename__ = 'changes'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False)
    second = Column(Text, nullable=False)
    weekday = Column(Text, nullable=False)
    schedule = Column(Text, nullable=False)
