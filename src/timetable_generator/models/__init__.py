"""Data models for timetable generation."""

from .subject import Subject
from .teacher import Teacher
from .classroom import Classroom
from .time_slot import TimeSlot
from .base import BaseModel

__all__ = ["Subject", "Teacher", "Classroom", "TimeSlot", "BaseModel"]