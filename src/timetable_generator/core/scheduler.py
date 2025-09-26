"""Scheduler class for automatic timetable generation."""

import random
from datetime import time, timedelta
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

from ..models.time_slot import TimeSlot, DayOfWeek
from ..models.subject import Subject, SubjectPriority
from ..models.teacher import Teacher
from ..models.classroom import Classroom
from .timetable import TimeTable, ScheduleEntry
from ..exceptions.timetable_exceptions import (
    SchedulingConflictError,
    ResourceNotAvailableError,
    InvalidConfigurationError
)


class SchedulingConstraints:
    """Configuration class for scheduling constraints."""
    
    def __init__(self):
        self.max_attempts: int = 1000
        self.prefer_morning_sessions: bool = True
        self.avoid_single_hour_gaps: bool = True
        self.max_consecutive_hours: int = 3
        self.lunch_break_start: time = time(12, 0)
        self.lunch_break_end: time = time(13, 0)
        self.min_break_between_sessions: int = 0  # minutes
        self.max_daily_hours_per_subject: int = 4
        self.prefer_same_classroom_for_subject: bool = True


class Scheduler:
    """Intelligent scheduler for automatic timetable generation."""
    
    def __init__(self, timetable: TimeTable, constraints: Optional[SchedulingConstraints] = None):
        self.timetable = timetable
        self.constraints = constraints or SchedulingConstraints()
        self.available_time_slots: List[TimeSlot] = []
        self._generate_time_slots()
    
    def _generate_time_slots(self) -> None:
        """Generate available time slots based on timetable settings."""
        self.available_time_slots = []
        
        start_time = time.fromisoformat(self.timetable.daily_start_time)
        end_time = time.fromisoformat(self.timetable.daily_end_time)
        
        for day in self.timetable.working_days:
            current_time = start_time
            
            while current_time < end_time:
                # Skip lunch break
                if (self.constraints.lunch_break_start <= current_time < self.constraints.lunch_break_end):
                    current_time = self.constraints.lunch_break_end
                    continue
                
                # Create time slot (assuming 1-hour slots by default)
                slot_end = (
                    time(current_time.hour + 1, current_time.minute)
                    if current_time.hour < 23
                    else end_time
                )
                
                if slot_end <= end_time:
                    time_slot = TimeSlot(
                        day=day,
                        start_time=current_time,
                        end_time=slot_end
                    )
                    self.available_time_slots.append(time_slot)
                
                current_time = slot_end
    
    def generate_schedule(self, optimize: bool = True) -> bool:
        """
        Generate a complete schedule for all subjects.
        
        Args:
            optimize: Whether to optimize the generated schedule
            
        Returns:
            True if scheduling was successful, False otherwise
        """
        # Clear existing schedule
        self.timetable.clear_schedule()
        
        # Sort subjects by priority and requirements
        sorted_subjects = self._sort_subjects_by_priority()
        
        scheduled_subjects = set()
        
        for subject in sorted_subjects:
            sessions_needed = subject.sessions_per_week
            sessions_scheduled = 0
            
            for _ in range(self.constraints.max_attempts):
                if sessions_scheduled >= sessions_needed:
                    break
                
                # Find best time slot for this subject
                best_slot = self._find_best_time_slot(subject, scheduled_subjects)
                if not best_slot:
                    continue
                
                # Find available teacher
                teacher = self._find_available_teacher(subject, best_slot)
                if not teacher:
                    continue
                
                # Find available classroom
                classroom = self._find_available_classroom(subject, best_slot)
                if not classroom:
                    continue
                
                # Create schedule entry
                entry = ScheduleEntry(
                    time_slot=best_slot,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom
                )
                
                try:
                    self.timetable.add_schedule_entry(entry)
                    sessions_scheduled += 1
                    scheduled_subjects.add(subject.code)
                except (SchedulingConflictError, ResourceNotAvailableError):
                    continue
            
            if sessions_scheduled < sessions_needed:
                print(f"Warning: Could only schedule {sessions_scheduled}/{sessions_needed} sessions for {subject.name}")
        
        if optimize:
            self._optimize_schedule()
        
        return len(self.timetable.schedule) > 0
    
    def _sort_subjects_by_priority(self) -> List[Subject]:
        """Sort subjects by scheduling priority."""
        subjects = list(self.timetable.subjects.values())
        
        priority_order = {
            SubjectPriority.CRITICAL: 0,
            SubjectPriority.HIGH: 1,
            SubjectPriority.MEDIUM: 2,
            SubjectPriority.LOW: 3
        }
        
        return sorted(
            subjects,
            key=lambda s: (
                priority_order.get(s.priority, 4),
                -s.sessions_per_week,  # More sessions = higher priority
                s.requires_lab,  # Lab subjects first
                s.name
            )
        )
    
    def _find_best_time_slot(self, subject: Subject, scheduled_subjects: Set[str]) -> Optional[TimeSlot]:
        """Find the best available time slot for a subject."""
        available_slots = [
            slot for slot in self.available_time_slots
            if self._is_slot_suitable(slot, subject)
        ]
        
        if not available_slots:
            return None
        
        # Score each slot
        scored_slots = []
        for slot in available_slots:
            score = self._score_time_slot(slot, subject, scheduled_subjects)
            scored_slots.append((slot, score))
        
        # Sort by score (higher is better)
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        
        return scored_slots[0][0] if scored_slots else None
    
    def _is_slot_suitable(self, slot: TimeSlot, subject: Subject) -> bool:
        """Check if a time slot is suitable for a subject."""
        # Check if slot duration matches subject duration
        if slot.duration_minutes != subject.duration_minutes:
            # For now, accept standard slots and adjust subject duration
            pass
        
        # Check if there are any conflicting entries
        for entry in self.timetable.schedule:
            if slot.overlaps_with(entry.time_slot):
                return False
        
        return True
    
    def _score_time_slot(self, slot: TimeSlot, subject: Subject, scheduled_subjects: Set[str]) -> float:
        """Score a time slot for a subject (higher score = better)."""
        score = 0.0
        
        # Prefer morning sessions if configured
        if self.constraints.prefer_morning_sessions and slot.start_time.hour < 12:
            score += 10.0
        
        # Prefer not to have gaps in the schedule
        adjacent_entries = self._get_adjacent_entries(slot)
        if adjacent_entries:
            score += 5.0
        
        # Avoid scheduling around lunch time
        if (self.constraints.lunch_break_start <= slot.start_time < self.constraints.lunch_break_end or
            self.constraints.lunch_break_start < slot.end_time <= self.constraints.lunch_break_end):
            score -= 15.0
        
        # Prefer certain days for certain subjects (you can customize this)
        if subject.subject_type.value == "lab" and slot.day in [DayOfWeek.TUESDAY, DayOfWeek.THURSDAY]:
            score += 8.0
        
        # Add randomness to avoid always picking the same slots
        score += random.uniform(0, 2)
        
        return score
    
    def _get_adjacent_entries(self, slot: TimeSlot) -> List[ScheduleEntry]:
        """Get schedule entries adjacent to the given time slot."""
        adjacent = []
        for entry in self.timetable.schedule:
            if (entry.time_slot.day == slot.day and 
                entry.time_slot.is_adjacent_to(slot)):
                adjacent.append(entry)
        return adjacent
    
    def _find_available_teacher(self, subject: Subject, time_slot: TimeSlot) -> Optional[Teacher]:
        """Find an available teacher for the subject at the given time slot."""
        qualified_teachers = [
            teacher for teacher in self.timetable.teachers.values()
            if (teacher.can_teach_subject(subject.code) and
                teacher.is_available_at(time_slot))
        ]
        
        if not qualified_teachers:
            return None
        
        # Check for conflicts with existing schedule
        available_teachers = []
        for teacher in qualified_teachers:
            has_conflict = any(
                entry.teacher.id == teacher.id and entry.time_slot.overlaps_with(time_slot)
                for entry in self.timetable.schedule
            )
            if not has_conflict:
                available_teachers.append(teacher)
        
        if not available_teachers:
            return None
        
        # Prefer teachers with lower current workload
        return min(available_teachers, key=lambda t: t.current_weekly_hours)
    
    def _find_available_classroom(self, subject: Subject, time_slot: TimeSlot) -> Optional[Classroom]:
        """Find an available classroom for the subject at the given time slot."""
        # Filter classrooms based on requirements
        suitable_classrooms = []
        for classroom in self.timetable.classrooms.values():
            if not classroom.is_available_at(time_slot):
                continue
            
            # Check subject-specific requirements
            requirements = {
                'has_projector': subject.requires_projector,
                'has_computers': subject.requires_computer,
            }
            
            if subject.requires_lab and classroom.room_type.value != "laboratory":
                continue
            
            if classroom.meets_requirements(requirements):
                suitable_classrooms.append(classroom)
        
        if not suitable_classrooms:
            return None
        
        # Check for conflicts with existing schedule
        available_classrooms = []
        for classroom in suitable_classrooms:
            has_conflict = any(
                entry.classroom.id == classroom.id and entry.time_slot.overlaps_with(time_slot)
                for entry in self.timetable.schedule
            )
            if not has_conflict:
                available_classrooms.append(classroom)
        
        if not available_classrooms:
            return None
        
        # Prefer classrooms with appropriate capacity
        return min(available_classrooms, key=lambda c: abs(c.capacity - (subject.max_students or 30)))
    
    def _optimize_schedule(self) -> None:
        """Optimize the generated schedule by resolving conflicts and improving efficiency."""
        # This is a simplified optimization - in a real system, you might use
        # more sophisticated algorithms like genetic algorithms or simulated annealing
        
        # Try to minimize gaps in teacher schedules
        self._minimize_teacher_gaps()
        
        # Try to group same subjects
        self._group_related_sessions()
    
    def _minimize_teacher_gaps(self) -> None:
        """Try to minimize gaps in teacher schedules."""
        # Group entries by teacher and day
        teacher_day_entries = defaultdict(lambda: defaultdict(list))
        
        for entry in self.timetable.schedule:
            teacher_day_entries[entry.teacher.id][entry.time_slot.day].append(entry)
        
        # Look for opportunities to swap time slots to reduce gaps
        # This is a simplified implementation
        pass
    
    def _group_related_sessions(self) -> None:
        """Try to group related sessions together."""
        # Group sessions of the same subject on the same day if possible
        # This is a simplified implementation
        pass
    
    def reschedule_entry(self, entry: ScheduleEntry, new_time_slot: TimeSlot) -> bool:
        """
        Reschedule an existing entry to a new time slot.
        
        Args:
            entry: The schedule entry to reschedule
            new_time_slot: The new time slot
            
        Returns:
            True if rescheduling was successful, False otherwise
        """
        # Remove the existing entry temporarily
        self.timetable.remove_schedule_entry(entry)
        
        # Update the time slot
        entry.time_slot = new_time_slot
        
        try:
            self.timetable.add_schedule_entry(entry)
            return True
        except (SchedulingConflictError, ResourceNotAvailableError):
            # If rescheduling fails, try to add the original entry back
            try:
                entry.time_slot = entry.time_slot  # Reset to original
                self.timetable.add_schedule_entry(entry)
            except:
                pass  # Original entry is lost, but this shouldn't happen in normal operation
            return False
    
    def get_scheduling_suggestions(self, subject: Subject) -> List[Tuple[TimeSlot, float]]:
        """Get ranked suggestions for scheduling a subject."""
        available_slots = [
            slot for slot in self.available_time_slots
            if self._is_slot_suitable(slot, subject)
        ]
        
        suggestions = []
        for slot in available_slots:
            if (self._find_available_teacher(subject, slot) and
                self._find_available_classroom(subject, slot)):
                score = self._score_time_slot(slot, subject, set())
                suggestions.append((slot, score))
        
        return sorted(suggestions, key=lambda x: x[1], reverse=True)
    
    def get_scheduling_report(self) -> Dict[str, any]:
        """Generate a report on the scheduling process."""
        issues = self.timetable.validate_schedule()
        stats = self.timetable.get_statistics()
        
        return {
            "schedule_generated": len(self.timetable.schedule) > 0,
            "total_entries": len(self.timetable.schedule),
            "scheduling_issues": issues,
            "statistics": stats,
            "success_rate": self._calculate_success_rate(),
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of scheduling."""
        total_required_sessions = sum(
            subject.sessions_per_week for subject in self.timetable.subjects.values()
        )
        
        if total_required_sessions == 0:
            return 100.0
        
        actual_sessions = len(self.timetable.schedule)
        return (actual_sessions / total_required_sessions) * 100.0