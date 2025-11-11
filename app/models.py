from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class HabitBase(BaseModel):
    title: str
    periodicity: str

    @field_validator("periodicity")
    @classmethod
    def validate_periodicity(cls, v):
        if v not in ["daily", "weekly"]:
            raise ValueError("Periodicity must be 'daily' or 'weekly'")
        return v


class HabitCreate(HabitBase):
    pass


class Habit(HabitBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckinBase(BaseModel):
    date: datetime


class CheckinCreate(CheckinBase):
    value: Optional[str] = None


class Checkin(CheckinBase):
    id: int
    habit_id: int
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
