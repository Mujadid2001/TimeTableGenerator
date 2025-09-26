"""Time slot model for timetable scheduling."""

from datetime import time, timedelta
from enum import Enum
from typing import Optional

from pydantic import Field, validator

from .base import BaseModel


class DayOfWeek(str, Enum):
    """Days of the week."""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class TimeSlot(BaseModel):
    """Represents a time slot in the timetable."""
    
    day: DayOfWeek = Field(..., description="Day of the week")
    start_time: time = Field(..., description="Start time of the slot")
    end_time: time = Field(..., description="End time of the slot")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    break_time: bool = Field(default=False, description="Whether this is a break time")
    
    @validator('duration_minutes', always=True)
    def calculate_duration(cls, v, values):
        """Calculate duration if not provided."""
        if v is None and 'start_time' in values and 'end_time' in values:
            start = values['start_time']
            end = values['end_time']
            duration = timedelta(
                hours=end.hour - start.hour,
                minutes=end.minute - start.minute
            )
            return int(duration.total_seconds() / 60)
        return v
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        """Validate that end time is after start time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another."""
        if self.day != other.day:
            return False
        
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def is_adjacent_to(self, other: 'TimeSlot') -> bool:
        """Check if this time slot is adjacent to another."""
        if self.day != other.day:
            return False
        
        return self.end_time == other.start_time or self.start_time == other.end_time
    
    def __str__(self) -> str:
        """String representation of the time slot."""
        return f"{self.day.value} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"