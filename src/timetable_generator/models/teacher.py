"""Teacher model for timetable scheduling."""

from enum import Enum
from typing import Dict, List, Optional, Set

from pydantic import Field, validator

from .base import BaseModel
from .time_slot import TimeSlot, DayOfWeek


class TeacherType(str, Enum):
    """Types of teachers."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    VISITING = "visiting"
    GUEST = "guest"


class TeacherStatus(str, Enum):
    """Teacher employment status."""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"


class Teacher(BaseModel):
    """Represents a teacher in the timetable system."""
    
    name: str = Field(..., description="Teacher's full name", min_length=1, max_length=100)
    employee_id: str = Field(..., description="Employee ID", min_length=1, max_length=50)
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Employment details
    teacher_type: TeacherType = Field(default=TeacherType.FULL_TIME, description="Type of employment")
    status: TeacherStatus = Field(default=TeacherStatus.ACTIVE, description="Current status")
    department: Optional[str] = Field(None, description="Department", max_length=100)
    designation: Optional[str] = Field(None, description="Job designation", max_length=100)
    
    # Teaching capabilities
    subjects_qualified: List[str] = Field(default_factory=list, description="List of subject codes teacher can teach")
    max_hours_per_week: int = Field(default=40, description="Maximum teaching hours per week", gt=0)
    max_hours_per_day: int = Field(default=8, description="Maximum teaching hours per day", gt=0)
    max_consecutive_hours: int = Field(default=3, description="Maximum consecutive teaching hours", gt=0)
    
    # Availability and preferences
    available_days: Set[DayOfWeek] = Field(
        default_factory=lambda: {DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                                DayOfWeek.THURSDAY, DayOfWeek.FRIDAY},
        description="Days teacher is available"
    )
    unavailable_slots: List[TimeSlot] = Field(default_factory=list, description="Time slots when teacher is not available")
    preferred_slots: List[TimeSlot] = Field(default_factory=list, description="Preferred time slots")
    
    # Workload tracking
    current_weekly_hours: float = Field(default=0.0, description="Current weekly teaching hours")
    assigned_subjects: Dict[str, int] = Field(default_factory=dict, description="Subject code to hours mapping")
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        """Validate employee ID format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Employee ID must contain only alphanumeric characters, hyphens, or underscores")
        return v.upper()
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation."""
        if v and '@' not in v:
            raise ValueError("Invalid email format")
        return v
    
    @validator('max_hours_per_day')
    def validate_daily_hours(cls, v, values):
        """Validate daily hours don't exceed weekly hours."""
        if 'max_hours_per_week' in values and v * 7 < values['max_hours_per_week']:
            return v
        if 'max_hours_per_week' in values and v > values['max_hours_per_week']:
            raise ValueError("Daily hours cannot exceed weekly hours")
        return v
    
    @validator('max_consecutive_hours')
    def validate_consecutive_hours(cls, v, values):
        """Validate consecutive hours are reasonable."""
        if 'max_hours_per_day' in values and v > values['max_hours_per_day']:
            raise ValueError("Consecutive hours cannot exceed daily hours")
        return v
    
    def is_available_at(self, time_slot: TimeSlot) -> bool:
        """Check if teacher is available at a specific time slot."""
        if self.status != TeacherStatus.ACTIVE:
            return False
        
        if time_slot.day not in self.available_days:
            return False
        
        # Check against unavailable slots
        for unavailable_slot in self.unavailable_slots:
            if time_slot.overlaps_with(unavailable_slot):
                return False
        
        return True
    
    def can_teach_subject(self, subject_code: str) -> bool:
        """Check if teacher is qualified to teach a subject."""
        return subject_code.upper() in [s.upper() for s in self.subjects_qualified]
    
    def add_subject_qualification(self, subject_code: str) -> None:
        """Add a subject qualification."""
        if not self.can_teach_subject(subject_code):
            self.subjects_qualified.append(subject_code.upper())
    
    def remove_subject_qualification(self, subject_code: str) -> None:
        """Remove a subject qualification."""
        self.subjects_qualified = [s for s in self.subjects_qualified 
                                 if s.upper() != subject_code.upper()]
    
    def assign_hours(self, subject_code: str, hours: float) -> None:
        """Assign teaching hours for a subject."""
        subject_code = subject_code.upper()
        if subject_code in self.assigned_subjects:
            self.assigned_subjects[subject_code] += hours
        else:
            self.assigned_subjects[subject_code] = hours
        
        self.current_weekly_hours = sum(self.assigned_subjects.values())
    
    def get_available_hours(self) -> float:
        """Get remaining available hours for the week."""
        return max(0, self.max_hours_per_week - self.current_weekly_hours)
    
    def get_workload_percentage(self) -> float:
        """Get current workload as percentage of maximum."""
        return (self.current_weekly_hours / self.max_hours_per_week) * 100
    
    def __str__(self) -> str:
        """String representation of the teacher."""
        return f"{self.name} ({self.employee_id})"