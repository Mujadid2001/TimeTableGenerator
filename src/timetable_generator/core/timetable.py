"""Core TimeTable class for managing timetable data and operations."""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

from ..models.base import BaseModel
from ..models.time_slot import TimeSlot, DayOfWeek
from ..models.subject import Subject
from ..models.teacher import Teacher
from ..models.classroom import Classroom
from ..exceptions.timetable_exceptions import (
    SchedulingConflictError,
    ResourceNotAvailableError,
    InvalidConfigurationError
)


class ScheduleEntry(BaseModel):
    """Represents a single entry in the timetable."""
    
    time_slot: TimeSlot
    subject: Subject
    teacher: Teacher
    classroom: Classroom
    student_count: Optional[int] = None
    notes: Optional[str] = None
    
    def conflicts_with(self, other: 'ScheduleEntry') -> bool:
        """Check if this entry conflicts with another."""
        if not self.time_slot.overlaps_with(other.time_slot):
            return False
        
        # Check for resource conflicts
        return (
            self.teacher.id == other.teacher.id or
            self.classroom.id == other.classroom.id
        )
    
    def __str__(self) -> str:
        return f"{self.time_slot} - {self.subject.name} ({self.teacher.name} in {self.classroom.name})"


class TimeTable(BaseModel):
    """Main TimeTable class for managing the complete timetable."""
    
    name: str
    academic_year: str
    semester: str
    start_date: datetime
    end_date: datetime
    
    # Resources
    subjects: Dict[str, Subject] = {}
    teachers: Dict[str, Teacher] = {}
    classrooms: Dict[str, Classroom] = {}
    
    # Schedule data
    schedule: List[ScheduleEntry] = []
    
    # Constraints and settings
    working_days: Set[DayOfWeek] = {
        DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY,
        DayOfWeek.THURSDAY, DayOfWeek.FRIDAY
    }
    daily_start_time: str = "09:00"
    daily_end_time: str = "17:00"
    break_duration_minutes: int = 15
    lunch_break_duration_minutes: int = 60
    
    def add_subject(self, subject: Subject) -> None:
        """Add a subject to the timetable."""
        if subject.code in self.subjects:
            raise InvalidConfigurationError("subject", f"Subject {subject.code} already exists")
        self.subjects[subject.code] = subject
    
    def add_teacher(self, teacher: Teacher) -> None:
        """Add a teacher to the timetable."""
        if teacher.employee_id in self.teachers:
            raise InvalidConfigurationError("teacher", f"Teacher {teacher.employee_id} already exists")
        self.teachers[teacher.employee_id] = teacher
    
    def add_classroom(self, classroom: Classroom) -> None:
        """Add a classroom to the timetable."""
        if classroom.room_number in self.classrooms:
            raise InvalidConfigurationError("classroom", f"Classroom {classroom.room_number} already exists")
        self.classrooms[classroom.room_number] = classroom
    
    def remove_subject(self, subject_code: str) -> None:
        """Remove a subject from the timetable."""
        if subject_code not in self.subjects:
            raise ResourceNotAvailableError("Subject", subject_code)
        
        # Remove related schedule entries
        self.schedule = [entry for entry in self.schedule if entry.subject.code != subject_code]
        del self.subjects[subject_code]
    
    def remove_teacher(self, employee_id: str) -> None:
        """Remove a teacher from the timetable."""
        if employee_id not in self.teachers:
            raise ResourceNotAvailableError("Teacher", employee_id)
        
        # Remove related schedule entries
        self.schedule = [entry for entry in self.schedule if entry.teacher.employee_id != employee_id]
        del self.teachers[employee_id]
    
    def remove_classroom(self, room_number: str) -> None:
        """Remove a classroom from the timetable."""
        if room_number not in self.classrooms:
            raise ResourceNotAvailableError("Classroom", room_number)
        
        # Remove related schedule entries
        self.schedule = [entry for entry in self.schedule if entry.classroom.room_number != room_number]
        del self.classrooms[room_number]
    
    def add_schedule_entry(self, entry: ScheduleEntry) -> None:
        """Add a schedule entry to the timetable."""
        # Validate resources exist
        if entry.subject.code not in self.subjects:
            raise ResourceNotAvailableError("Subject", entry.subject.code)
        if entry.teacher.employee_id not in self.teachers:
            raise ResourceNotAvailableError("Teacher", entry.teacher.employee_id)
        if entry.classroom.room_number not in self.classrooms:
            raise ResourceNotAvailableError("Classroom", entry.classroom.room_number)
        
        # Check for conflicts
        conflicts = self.get_conflicts(entry)
        if conflicts:
            raise SchedulingConflictError(
                f"Schedule entry conflicts with existing entries",
                [str(conflict) for conflict in conflicts]
            )
        
        # Validate resource availability
        if not entry.teacher.is_available_at(entry.time_slot):
            raise ResourceNotAvailableError("Teacher", entry.teacher.employee_id, str(entry.time_slot))
        
        if not entry.classroom.is_available_at(entry.time_slot):
            raise ResourceNotAvailableError("Classroom", entry.classroom.room_number, str(entry.time_slot))
        
        # Validate teacher can teach subject
        if not entry.teacher.can_teach_subject(entry.subject.code):
            raise InvalidConfigurationError(
                "teacher_subject", 
                f"Teacher {entry.teacher.name} is not qualified to teach {entry.subject.name}"
            )
        
        # Validate classroom capacity
        if entry.student_count and not entry.classroom.can_accommodate(entry.student_count):
            raise InvalidConfigurationError(
                "classroom_capacity",
                f"Classroom {entry.classroom.name} cannot accommodate {entry.student_count} students"
            )
        
        self.schedule.append(entry)
    
    def remove_schedule_entry(self, entry: ScheduleEntry) -> None:
        """Remove a schedule entry from the timetable."""
        self.schedule = [e for e in self.schedule if e.id != entry.id]
    
    def get_conflicts(self, entry: ScheduleEntry) -> List[ScheduleEntry]:
        """Get all conflicts for a potential schedule entry."""
        conflicts = []
        for existing_entry in self.schedule:
            if entry.conflicts_with(existing_entry):
                conflicts.append(existing_entry)
        return conflicts
    
    def get_schedule_by_day(self, day: DayOfWeek) -> List[ScheduleEntry]:
        """Get all schedule entries for a specific day."""
        return [entry for entry in self.schedule if entry.time_slot.day == day]
    
    def get_teacher_schedule(self, teacher_id: str) -> List[ScheduleEntry]:
        """Get schedule entries for a specific teacher."""
        return [entry for entry in self.schedule if entry.teacher.employee_id == teacher_id]
    
    def get_classroom_schedule(self, room_number: str) -> List[ScheduleEntry]:
        """Get schedule entries for a specific classroom."""
        return [entry for entry in self.schedule if entry.classroom.room_number == room_number]
    
    def get_subject_schedule(self, subject_code: str) -> List[ScheduleEntry]:
        """Get schedule entries for a specific subject."""
        return [entry for entry in self.schedule if entry.subject.code == subject_code]
    
    def get_weekly_hours_by_teacher(self) -> Dict[str, float]:
        """Get weekly teaching hours for each teacher."""
        hours = defaultdict(float)
        for entry in self.schedule:
            hours[entry.teacher.employee_id] += entry.subject.duration_minutes / 60.0
        return dict(hours)
    
    def get_classroom_utilization(self) -> Dict[str, Dict[str, float]]:
        """Get classroom utilization by day."""
        utilization = defaultdict(lambda: defaultdict(float))
        for entry in self.schedule:
            day = entry.time_slot.day.value
            room = entry.classroom.room_number
            utilization[room][day] += entry.subject.duration_minutes / 60.0
        return dict(utilization)
    
    def validate_schedule(self) -> List[str]:
        """Validate the entire schedule and return list of issues."""
        issues = []
        
        # Check for conflicts
        for i, entry1 in enumerate(self.schedule):
            for entry2 in self.schedule[i+1:]:
                if entry1.conflicts_with(entry2):
                    issues.append(f"Conflict between {entry1} and {entry2}")
        
        # Check if subjects meet their weekly requirements
        subject_hours = defaultdict(float)
        for entry in self.schedule:
            subject_hours[entry.subject.code] += entry.subject.duration_minutes / 60.0
        
        for subject_code, subject in self.subjects.items():
            required_hours = subject.get_total_hours_per_week()
            actual_hours = subject_hours.get(subject_code, 0)
            if actual_hours < required_hours:
                issues.append(
                    f"Subject {subject.name} has {actual_hours}h scheduled but requires {required_hours}h per week"
                )
        
        # Check teacher workload
        teacher_hours = self.get_weekly_hours_by_teacher()
        for teacher_id, hours in teacher_hours.items():
            teacher = self.teachers[teacher_id]
            if hours > teacher.max_hours_per_week:
                issues.append(
                    f"Teacher {teacher.name} is scheduled for {hours}h but max is {teacher.max_hours_per_week}h"
                )
        
        return issues
    
    def get_statistics(self) -> Dict[str, any]:
        """Get timetable statistics."""
        teacher_hours = self.get_weekly_hours_by_teacher()
        classroom_util = self.get_classroom_utilization()
        
        return {
            "total_schedule_entries": len(self.schedule),
            "total_subjects": len(self.subjects),
            "total_teachers": len(self.teachers),
            "total_classrooms": len(self.classrooms),
            "average_teacher_hours": sum(teacher_hours.values()) / len(teacher_hours) if teacher_hours else 0,
            "total_teaching_hours": sum(teacher_hours.values()),
            "schedule_conflicts": len([issue for issue in self.validate_schedule() if "Conflict" in issue]),
            "classroom_utilization": classroom_util
        }
    
    def clear_schedule(self) -> None:
        """Clear all schedule entries."""
        self.schedule = []
    
    def __str__(self) -> str:
        return f"TimeTable: {self.name} ({self.academic_year} - {self.semester})"