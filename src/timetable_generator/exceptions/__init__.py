"""Custom exceptions for timetable operations."""

from .timetable_exceptions import (
    TimeTableError,
    SchedulingConflictError,
    ResourceNotAvailableError,
    InvalidConfigurationError,
)

__all__ = [
    "TimeTableError",
    "SchedulingConflictError", 
    "ResourceNotAvailableError",
    "InvalidConfigurationError",
]