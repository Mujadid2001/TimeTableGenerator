"""
TimeTable Generator - A professional timetable generation system for educational institutes.

This package provides a comprehensive solution for generating and managing timetables
using object-oriented programming principles and modern Python best practices.
"""

__version__ = "0.1.0"
__author__ = "TimeTable Generator Team"
__email__ = "contact@example.com"

from .core.timetable import TimeTable
from .core.scheduler import Scheduler
from .models.subject import Subject
from .models.teacher import Teacher
from .models.classroom import Classroom
from .models.time_slot import TimeSlot
from .exceptions.timetable_exceptions import (
    TimeTableError,
    SchedulingConflictError,
    ResourceNotAvailableError,
    InvalidConfigurationError,
)

__all__ = [
    "TimeTable",
    "Scheduler",
    "Subject",
    "Teacher", 
    "Classroom",
    "TimeSlot",
    "TimeTableError",
    "SchedulingConflictError",
    "ResourceNotAvailableError",
    "InvalidConfigurationError",
]