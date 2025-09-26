"""Formatting utilities for timetable display and export."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

from ..core.timetable import TimeTable, ScheduleEntry
from ..models.time_slot import DayOfWeek


def format_timetable(timetable: TimeTable, format_type: str = "grid") -> str:
    """
    Format timetable for display.
    
    Args:
        timetable: TimeTable instance to format
        format_type: Format type ("grid", "list", "summary")
        
    Returns:
        Formatted timetable string
    """
    if format_type == "grid":
        return _format_timetable_grid(timetable)
    elif format_type == "list":
        return _format_timetable_list(timetable)
    elif format_type == "summary":
        return _format_timetable_summary(timetable)
    else:
        raise ValueError(f"Unknown format type: {format_type}")


def _format_timetable_grid(timetable: TimeTable) -> str:
    """Format timetable as a grid."""
    if not timetable.schedule:
        return "No schedule entries found."
    
    # Group entries by day and time
    day_schedule = defaultdict(list)
    for entry in timetable.schedule:
        day_schedule[entry.time_slot.day].append(entry)
    
    # Sort entries by time within each day
    for day in day_schedule:
        day_schedule[day].sort(key=lambda e: e.time_slot.start_time)
    
    output = []
    output.append(f"=== {timetable.name} ===")
    output.append(f"Academic Year: {timetable.academic_year}, Semester: {timetable.semester}")
    output.append("")
    
    for day in timetable.working_days:
        if day in day_schedule:
            output.append(f"--- {day.value} ---")
            for entry in day_schedule[day]:
                time_str = f"{entry.time_slot.start_time.strftime('%H:%M')}-{entry.time_slot.end_time.strftime('%H:%M')}"
                output.append(f"{time_str:10} | {entry.subject.name:20} | {entry.teacher.name:15} | {entry.classroom.name}")
            output.append("")
    
    return "\n".join(output)


def _format_timetable_list(timetable: TimeTable) -> str:
    """Format timetable as a list."""
    if not timetable.schedule:
        return "No schedule entries found."
    
    output = []
    output.append(f"=== {timetable.name} ===")
    output.append(f"Total Entries: {len(timetable.schedule)}")
    output.append("")
    
    # Sort by day and time
    sorted_entries = sorted(
        timetable.schedule,
        key=lambda e: (list(DayOfWeek).index(e.time_slot.day), e.time_slot.start_time)
    )
    
    for i, entry in enumerate(sorted_entries, 1):
        output.append(f"{i:3}. {entry}")
        output.append(f"     Teacher: {entry.teacher.name} ({entry.teacher.employee_id})")
        output.append(f"     Classroom: {entry.classroom.name} (Capacity: {entry.classroom.capacity})")
        if entry.student_count:
            output.append(f"     Students: {entry.student_count}")
        if entry.notes:
            output.append(f"     Notes: {entry.notes}")
        output.append("")
    
    return "\n".join(output)


def _format_timetable_summary(timetable: TimeTable) -> str:
    """Format timetable summary."""
    stats = timetable.get_statistics()
    teacher_hours = timetable.get_weekly_hours_by_teacher()
    
    output = []
    output.append(f"=== {timetable.name} Summary ===")
    output.append(f"Academic Year: {timetable.academic_year}, Semester: {timetable.semester}")
    output.append("")
    
    output.append("📊 Statistics:")
    output.append(f"  • Total Schedule Entries: {stats['total_schedule_entries']}")
    output.append(f"  • Total Subjects: {stats['total_subjects']}")
    output.append(f"  • Total Teachers: {stats['total_teachers']}")
    output.append(f"  • Total Classrooms: {stats['total_classrooms']}")
    output.append(f"  • Total Teaching Hours: {stats['total_teaching_hours']:.1f}")
    output.append(f"  • Average Teacher Hours: {stats['average_teacher_hours']:.1f}")
    output.append(f"  • Schedule Conflicts: {stats['schedule_conflicts']}")
    output.append("")
    
    if teacher_hours:
        output.append("👨‍🏫 Teacher Workload:")
        for teacher_id, hours in sorted(teacher_hours.items()):
            teacher = timetable.teachers[teacher_id]
            percentage = (hours / teacher.max_hours_per_week * 100) if teacher.max_hours_per_week > 0 else 0
            output.append(f"  • {teacher.name}: {hours:.1f}h ({percentage:.1f}%)")
        output.append("")
    
    # Show validation issues if any
    issues = timetable.validate_schedule()
    if issues:
        output.append("⚠️  Issues Found:")
        for issue in issues:
            output.append(f"  • {issue}")
    else:
        output.append("✅ No issues found in schedule")
    
    return "\n".join(output)


def format_schedule(entries: List[ScheduleEntry], title: str = "Schedule") -> str:
    """
    Format a list of schedule entries.
    
    Args:
        entries: List of schedule entries
        title: Title for the schedule
        
    Returns:
        Formatted schedule string
    """
    if not entries:
        return f"=== {title} ===\nNo entries found."
    
    output = []
    output.append(f"=== {title} ===")
    output.append(f"Total Entries: {len(entries)}")
    output.append("")
    
    # Group by day
    day_entries = defaultdict(list)
    for entry in entries:
        day_entries[entry.time_slot.day].append(entry)
    
    # Sort entries within each day
    for day in day_entries:
        day_entries[day].sort(key=lambda e: e.time_slot.start_time)
    
    for day in DayOfWeek:
        if day in day_entries:
            output.append(f"--- {day.value} ---")
            for entry in day_entries[day]:
                time_str = f"{entry.time_slot.start_time.strftime('%H:%M')}-{entry.time_slot.end_time.strftime('%H:%M')}"
                output.append(f"{time_str} - {entry.subject.name} ({entry.teacher.name})")
            output.append("")
    
    return "\n".join(output)


def format_teacher_schedule(timetable: TimeTable, teacher_id: str) -> str:
    """Format schedule for a specific teacher."""
    if teacher_id not in timetable.teachers:
        return f"Teacher with ID '{teacher_id}' not found."
    
    teacher = timetable.teachers[teacher_id]
    entries = timetable.get_teacher_schedule(teacher_id)
    
    title = f"{teacher.name} ({teacher.employee_id}) Schedule"
    return format_schedule(entries, title)


def format_classroom_schedule(timetable: TimeTable, room_number: str) -> str:
    """Format schedule for a specific classroom."""
    if room_number not in timetable.classrooms:
        return f"Classroom '{room_number}' not found."
    
    classroom = timetable.classrooms[room_number]
    entries = timetable.get_classroom_schedule(room_number)
    
    title = f"{classroom.name} ({room_number}) Schedule"
    return format_schedule(entries, title)


def format_subject_schedule(timetable: TimeTable, subject_code: str) -> str:
    """Format schedule for a specific subject."""
    if subject_code not in timetable.subjects:
        return f"Subject '{subject_code}' not found."
    
    subject = timetable.subjects[subject_code]
    entries = timetable.get_subject_schedule(subject_code)
    
    title = f"{subject.name} ({subject_code}) Schedule"
    return format_schedule(entries, title)


def format_time_slot(time_slot) -> str:
    """Format a time slot for display."""
    return f"{time_slot.day.value} {time_slot.start_time.strftime('%H:%M')}-{time_slot.end_time.strftime('%H:%M')}"


def format_duration(minutes: int) -> str:
    """Format duration in minutes to hours and minutes."""
    hours = minutes // 60
    mins = minutes % 60
    
    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"


def format_utilization_report(timetable: TimeTable) -> str:
    """Format classroom utilization report."""
    utilization = timetable.get_classroom_utilization()
    
    if not utilization:
        return "No utilization data available."
    
    output = []
    output.append("=== Classroom Utilization Report ===")
    output.append("")
    
    for room_number, daily_hours in utilization.items():
        classroom = timetable.classrooms[room_number]
        output.append(f"🏫 {classroom.name} ({room_number})")
        
        total_hours = sum(daily_hours.values())
        max_possible = len(timetable.working_days) * 8  # Assuming 8-hour workday
        utilization_rate = (total_hours / max_possible * 100) if max_possible > 0 else 0
        
        output.append(f"   Total Hours: {total_hours:.1f}h")
        output.append(f"   Utilization: {utilization_rate:.1f}%")
        
        for day, hours in daily_hours.items():
            daily_rate = (hours / 8 * 100) if hours > 0 else 0
            output.append(f"   {day}: {hours:.1f}h ({daily_rate:.1f}%)")
        output.append("")
    
    return "\n".join(output)


def format_conflicts_report(timetable: TimeTable) -> str:
    """Format conflicts report."""
    issues = timetable.validate_schedule()
    conflicts = [issue for issue in issues if "Conflict" in issue]
    
    if not conflicts:
        return "✅ No conflicts found in the schedule."
    
    output = []
    output.append("⚠️  Schedule Conflicts Report")
    output.append("=" * 40)
    output.append("")
    
    for i, conflict in enumerate(conflicts, 1):
        output.append(f"{i}. {conflict}")
    
    output.append("")
    output.append(f"Total conflicts found: {len(conflicts)}")
    
    return "\n".join(output)


def format_workload_report(timetable: TimeTable) -> str:
    """Format teacher workload report."""
    teacher_hours = timetable.get_weekly_hours_by_teacher()
    
    if not teacher_hours:
        return "No workload data available."
    
    output = []
    output.append("=== Teacher Workload Report ===")
    output.append("")
    
    # Sort teachers by workload (descending)
    sorted_teachers = sorted(
        teacher_hours.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for teacher_id, hours in sorted_teachers:
        teacher = timetable.teachers[teacher_id]
        percentage = (hours / teacher.max_hours_per_week * 100) if teacher.max_hours_per_week > 0 else 0
        
        status = "🟢" if percentage <= 100 else "🔴"
        output.append(f"{status} {teacher.name} ({teacher.employee_id})")
        output.append(f"   Hours: {hours:.1f}h / {teacher.max_hours_per_week}h ({percentage:.1f}%)")
        
        if percentage > 100:
            overload = hours - teacher.max_hours_per_week
            output.append(f"   ⚠️  Overloaded by {overload:.1f}h")
        
        output.append("")
    
    return "\n".join(output)