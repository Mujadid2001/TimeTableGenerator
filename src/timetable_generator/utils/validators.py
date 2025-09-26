"""Validation utilities for timetable data."""

import re
from datetime import time, datetime
from typing import Any, List, Optional, Union

from ..exceptions.timetable_exceptions import InvalidConfigurationError


def validate_time_format(time_str: str) -> bool:
    """
    Validate time format (HH:MM).
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        time.fromisoformat(time_str)
        return True
    except ValueError:
        return False


def validate_duration(duration_minutes: int, min_duration: int = 15, max_duration: int = 480) -> bool:
    """
    Validate duration in minutes.
    
    Args:
        duration_minutes: Duration to validate
        min_duration: Minimum allowed duration (default: 15 minutes)
        max_duration: Maximum allowed duration (default: 480 minutes/8 hours)
        
    Returns:
        True if valid, False otherwise
    """
    return min_duration <= duration_minutes <= max_duration


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_capacity(capacity: int, min_capacity: int = 1, max_capacity: int = 1000) -> bool:
    """
    Validate classroom capacity.
    
    Args:
        capacity: Capacity to validate
        min_capacity: Minimum allowed capacity
        max_capacity: Maximum allowed capacity
        
    Returns:
        True if valid, False otherwise
    """
    return min_capacity <= capacity <= max_capacity


def validate_code_format(code: str, pattern: Optional[str] = None) -> bool:
    """
    Validate code format (subject code, employee ID, etc.).
    
    Args:
        code: Code to validate
        pattern: Optional regex pattern to match
        
    Returns:
        True if valid, False otherwise
    """
    if not code or not code.strip():
        return False
    
    if pattern:
        return bool(re.match(pattern, code))
    
    # Default pattern: alphanumeric with hyphens, underscores, spaces
    default_pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(default_pattern, code.strip()))


def validate_time_range(start_time: str, end_time: str) -> bool:
    """
    Validate that end time is after start time.
    
    Args:
        start_time: Start time string (HH:MM)
        end_time: End time string (HH:MM)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)
        return end > start
    except ValueError:
        return False


def validate_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> bool:
    """
    Validate that end date is after start date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(start_date, str):
            start = datetime.fromisoformat(start_date)
        else:
            start = start_date
            
        if isinstance(end_date, str):
            end = datetime.fromisoformat(end_date)
        else:
            end = end_date
            
        return end > start
    except (ValueError, TypeError):
        return False


def validate_working_hours(
    daily_start: str,
    daily_end: str,
    lunch_start: str,
    lunch_end: str
) -> List[str]:
    """
    Validate working hours configuration.
    
    Args:
        daily_start: Daily start time
        daily_end: Daily end time
        lunch_start: Lunch break start time
        lunch_end: Lunch break end time
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Validate individual time formats
    for time_str, name in [
        (daily_start, "daily_start"),
        (daily_end, "daily_end"),
        (lunch_start, "lunch_start"),
        (lunch_end, "lunch_end")
    ]:
        if not validate_time_format(time_str):
            errors.append(f"Invalid time format for {name}: {time_str}")
    
    if errors:
        return errors
    
    try:
        start = time.fromisoformat(daily_start)
        end = time.fromisoformat(daily_end)
        lunch_s = time.fromisoformat(lunch_start)
        lunch_e = time.fromisoformat(lunch_end)
        
        # Check if daily end is after daily start
        if end <= start:
            errors.append("Daily end time must be after start time")
        
        # Check if lunch end is after lunch start
        if lunch_e <= lunch_s:
            errors.append("Lunch end time must be after start time")
        
        # Check if lunch break is within working hours
        if lunch_s < start or lunch_e > end:
            errors.append("Lunch break must be within working hours")
            
    except ValueError as e:
        errors.append(f"Time parsing error: {e}")
    
    return errors


def validate_subject_prerequisites(subjects: dict, subject_code: str, prerequisites: List[str]) -> List[str]:
    """
    Validate subject prerequisites.
    
    Args:
        subjects: Dictionary of all subjects
        subject_code: Code of the subject being validated
        prerequisites: List of prerequisite subject codes
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    for prereq in prerequisites:
        # Check if prerequisite exists
        if prereq not in subjects:
            errors.append(f"Prerequisite subject '{prereq}' does not exist")
        
        # Check for circular dependencies (simplified check)
        if prereq == subject_code:
            errors.append(f"Subject cannot be a prerequisite of itself")
    
    return errors


def validate_teacher_subject_assignment(teacher_subjects: List[str], subject_code: str) -> bool:
    """
    Validate if a teacher can be assigned to teach a subject.
    
    Args:
        teacher_subjects: List of subjects teacher is qualified to teach
        subject_code: Subject code to validate
        
    Returns:
        True if valid, False otherwise
    """
    return subject_code.upper() in [s.upper() for s in teacher_subjects]


def validate_classroom_requirements(classroom_features: dict, subject_requirements: dict) -> List[str]:
    """
    Validate if a classroom meets subject requirements.
    
    Args:
        classroom_features: Dictionary of classroom features
        subject_requirements: Dictionary of subject requirements
        
    Returns:
        List of missing requirements (empty if all met)
    """
    missing = []
    
    for requirement, needed in subject_requirements.items():
        if needed and not classroom_features.get(requirement, False):
            missing.append(requirement)
    
    return missing


def validate_schedule_entry_data(entry_data: dict) -> List[str]:
    """
    Validate schedule entry data.
    
    Args:
        entry_data: Dictionary containing schedule entry data
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    required_fields = ['time_slot', 'subject', 'teacher', 'classroom']
    
    for field in required_fields:
        if field not in entry_data or entry_data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate student count if provided
    if 'student_count' in entry_data:
        student_count = entry_data['student_count']
        if student_count is not None and (not isinstance(student_count, int) or student_count < 0):
            errors.append("Student count must be a non-negative integer")
    
    return errors


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation error for '{field}': {message}")


def raise_if_invalid(condition: bool, field: str, message: str, value: Any = None) -> None:
    """
    Raise validation error if condition is False.
    
    Args:
        condition: Condition to check
        field: Field name being validated
        message: Error message
        value: Value being validated
        
    Raises:
        ValidationError: If condition is False
    """
    if not condition:
        raise ValidationError(field, message, value)