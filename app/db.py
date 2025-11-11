from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    periodicity = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    checkins = relationship("Checkin", back_populates="habit")


class Checkin(Base):
    __tablename__ = "checkins"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    value = Column(String, nullable=True)

    habit = relationship("Habit", back_populates="checkins")
