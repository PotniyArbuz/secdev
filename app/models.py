from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    periodicity: str


class HabitCreate(HabitBase):
    model_config = ConfigDict(extra="forbid")

    @field_validator("periodicity")
    def check_periodicity(cls, v):
        if v not in ("daily", "weekly"):
            raise ValueError("Input should be 'daily' or weekly")
        return v


class Habit(HabitBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckinBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: datetime
    value: Optional[str] = Field(None, max_length=500)


class CheckinCreate(CheckinBase):
    pass


class Checkin(CheckinBase):
    id: int
    habit_id: int

    model_config = ConfigDict(from_attributes=True)
