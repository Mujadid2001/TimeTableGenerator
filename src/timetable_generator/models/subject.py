"""Subject model for timetable scheduling."""

from enum import Enum
from typing import List, Optional

from pydantic import Field, validator

from .base import BaseModel


class SubjectType(str, Enum):
    """Types of subjects."""
    LECTURE = "lecture"
    LAB = "lab"
    TUTORIAL = "tutorial"
    SEMINAR = "seminar"
    WORKSHOP = "workshop"


class SubjectPriority(str, Enum):
    """Priority levels for subjects."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Subject(BaseModel):
    """Represents a subject in the timetable."""
    
    name: str = Field(..., description="Subject name", min_length=1, max_length=100)
    code: str = Field(..., description="Subject code", min_length=1, max_length=20)
    subject_type: SubjectType = Field(default=SubjectType.LECTURE, description="Type of subject")
    priority: SubjectPriority = Field(default=SubjectPriority.MEDIUM, description="Scheduling priority")
    duration_minutes: int = Field(..., description="Duration per session in minutes", gt=0)
    sessions_per_week: int = Field(default=1, description="Number of sessions per week", gt=0)
    max_students: Optional[int] = Field(None, description="Maximum number of students", gt=0)
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite subject codes")
    description: Optional[str] = Field(None, description="Subject description", max_length=500)
    
    # Resource requirements
    requires_lab: bool = Field(default=False, description="Whether subject requires a lab")
    requires_projector: bool = Field(default=False, description="Whether subject requires a projector")
    requires_computer: bool = Field(default=False, description="Whether subject requires computers")
    special_equipment: List[str] = Field(default_factory=list, description="List of special equipment needed")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate subject code format."""
        if not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError("Subject code must contain only alphanumeric characters, spaces, hyphens, or underscores")
        return v.upper()
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        """Validate duration is reasonable."""
        if v > 480:  # 8 hours
            raise ValueError("Duration cannot exceed 8 hours (480 minutes)")
        if v < 15:  # 15 minutes minimum
            raise ValueError("Duration must be at least 15 minutes")
        return v
    
    @validator('sessions_per_week')
    def validate_sessions(cls, v):
        """Validate sessions per week is reasonable."""
        if v > 10:
            raise ValueError("Sessions per week cannot exceed 10")
        return v
    
    def get_total_hours_per_week(self) -> float:
        """Calculate total hours per week for this subject."""
        return (self.duration_minutes * self.sessions_per_week) / 60.0
    
    def has_prerequisite(self, subject_code: str) -> bool:
        """Check if this subject has a specific prerequisite."""
        return subject_code.upper() in [prereq.upper() for prereq in self.prerequisites]
    
    def __str__(self) -> str:
        """String representation of the subject."""
        return f"{self.code}: {self.name}"