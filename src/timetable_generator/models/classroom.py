"""Classroom model for timetable scheduling."""

from enum import Enum
from typing import Dict, List, Optional, Set

from pydantic import Field, validator

from .base import BaseModel
from .time_slot import TimeSlot, DayOfWeek


class RoomType(str, Enum):
    """Types of classrooms."""
    LECTURE_HALL = "lecture_hall"
    CLASSROOM = "classroom"
    LABORATORY = "laboratory"
    COMPUTER_LAB = "computer_lab"
    SEMINAR_ROOM = "seminar_room"
    AUDITORIUM = "auditorium"
    WORKSHOP = "workshop"


class RoomStatus(str, Enum):
    """Classroom status."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class Classroom(BaseModel):
    """Represents a classroom in the timetable system."""
    
    name: str = Field(..., description="Classroom name/number", min_length=1, max_length=50)
    room_number: str = Field(..., description="Room number", min_length=1, max_length=20)
    building: Optional[str] = Field(None, description="Building name", max_length=100)
    floor: Optional[int] = Field(None, description="Floor number")
    
    # Capacity and type
    capacity: int = Field(..., description="Maximum student capacity", gt=0)
    room_type: RoomType = Field(default=RoomType.CLASSROOM, description="Type of classroom")
    status: RoomStatus = Field(default=RoomStatus.AVAILABLE, description="Current status")
    
    # Equipment and facilities
    has_projector: bool = Field(default=False, description="Has projector")
    has_audio_system: bool = Field(default=False, description="Has audio system")
    has_whiteboard: bool = Field(default=True, description="Has whiteboard")
    has_blackboard: bool = Field(default=False, description="Has blackboard")
    has_computers: bool = Field(default=False, description="Has computers")
    computer_count: Optional[int] = Field(None, description="Number of computers", ge=0)
    has_internet: bool = Field(default=True, description="Has internet connection")
    has_air_conditioning: bool = Field(default=False, description="Has air conditioning")
    
    # Special equipment
    special_equipment: List[str] = Field(default_factory=list, description="List of special equipment")
    software_available: List[str] = Field(default_factory=list, description="Available software")
    
    # Availability
    available_days: Set[DayOfWeek] = Field(
        default_factory=lambda: {DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY,
                                DayOfWeek.THURSDAY, DayOfWeek.FRIDAY},
        description="Days room is available"
    )
    unavailable_slots: List[TimeSlot] = Field(default_factory=list, description="Time slots when room is not available")
    maintenance_slots: List[TimeSlot] = Field(default_factory=list, description="Scheduled maintenance slots")
    
    # Usage tracking
    utilization_hours: Dict[str, float] = Field(default_factory=dict, description="Daily utilization hours")
    booking_count: int = Field(default=0, description="Number of current bookings")
    
    @validator('room_number')
    def validate_room_number(cls, v):
        """Validate room number format."""
        if not v.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise ValueError("Room number must contain only alphanumeric characters, hyphens, underscores, or dots")
        return v.upper()
    
    @validator('floor')
    def validate_floor(cls, v):
        """Validate floor number is reasonable."""
        if v is not None and (v < -5 or v > 50):
            raise ValueError("Floor number must be between -5 and 50")
        return v
    
    @validator('capacity')
    def validate_capacity(cls, v):
        """Validate capacity is reasonable."""
        if v > 1000:
            raise ValueError("Capacity cannot exceed 1000")
        return v
    
    @validator('computer_count')
    def validate_computer_count(cls, v, values):
        """Validate computer count against capacity and type."""
        if v is not None:
            if 'capacity' in values and v > values['capacity']:
                raise ValueError("Computer count cannot exceed room capacity")
            if v > 0 and 'has_computers' in values and not values['has_computers']:
                raise ValueError("Computer count specified but has_computers is False")
        return v
    
    def is_available_at(self, time_slot: TimeSlot) -> bool:
        """Check if classroom is available at a specific time slot."""
        if self.status != RoomStatus.AVAILABLE:
            return False
        
        if time_slot.day not in self.available_days:
            return False
        
        # Check against unavailable slots
        for unavailable_slot in self.unavailable_slots:
            if time_slot.overlaps_with(unavailable_slot):
                return False
        
        # Check against maintenance slots
        for maintenance_slot in self.maintenance_slots:
            if time_slot.overlaps_with(maintenance_slot):
                return False
        
        return True
    
    def meets_requirements(self, requirements: Dict[str, bool]) -> bool:
        """Check if classroom meets specific requirements."""
        for requirement, needed in requirements.items():
            if needed and not getattr(self, requirement, False):
                return False
        return True
    
    def can_accommodate(self, student_count: int) -> bool:
        """Check if classroom can accommodate a specific number of students."""
        return self.capacity >= student_count
    
    def add_equipment(self, equipment: str) -> None:
        """Add special equipment to the classroom."""
        if equipment not in self.special_equipment:
            self.special_equipment.append(equipment)
    
    def remove_equipment(self, equipment: str) -> None:
        """Remove special equipment from the classroom."""
        self.special_equipment = [eq for eq in self.special_equipment if eq != equipment]
    
    def add_software(self, software: str) -> None:
        """Add available software to the classroom."""
        if software not in self.software_available:
            self.software_available.append(software)
    
    def get_utilization_rate(self, day: DayOfWeek) -> float:
        """Get utilization rate for a specific day (0-100%)."""
        day_str = day.value
        if day_str not in self.utilization_hours:
            return 0.0
        
        # Assuming 8-hour working day
        return min(100.0, (self.utilization_hours[day_str] / 8.0) * 100)
    
    def get_full_name(self) -> str:
        """Get full name of the classroom including building and floor."""
        parts = [self.name]
        if self.building:
            parts.append(f"Building {self.building}")
        if self.floor is not None:
            parts.append(f"Floor {self.floor}")
        return ", ".join(parts)
    
    def __str__(self) -> str:
        """String representation of the classroom."""
        return f"{self.room_number}: {self.name} (Capacity: {self.capacity})"