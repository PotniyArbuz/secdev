from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class HabitCreate(BaseModel):
    name: str
    periodicity: str

    @field_validator("periodicity")
    @classmethod
    def validate_periodicity(cls, v):
        if v not in ["daily", "weekly"]:
            raise ValueError("Periodicity must be 'daily' or 'weekly'")
        return v


class Habit(HabitCreate):
    id: int
    owner_id: int


class CheckinCreate(BaseModel):
    date: date
    value: Optional[str] = None


class Checkin(CheckinCreate):
    id: int
    habit_id: int
