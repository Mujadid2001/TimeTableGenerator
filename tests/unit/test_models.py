"""Unit tests for data models."""

import pytest
from datetime import time, datetime
from timetable_generator.models.subject import Subject, SubjectType, SubjectPriority
from timetable_generator.models.teacher import Teacher, TeacherType, TeacherStatus
from timetable_generator.models.classroom import Classroom, RoomType, RoomStatus
from timetable_generator.models.time_slot import TimeSlot, DayOfWeek


class TestSubject:
    """Test Subject model."""
    
    def test_create_subject(self):
        """Test creating a subject."""
        subject = Subject(
            name="Mathematics",
            code="MATH101",
            duration_minutes=60,
            sessions_per_week=3
        )
        
        assert subject.name == "Mathematics"
        assert subject.code == "MATH101"
        assert subject.duration_minutes == 60
        assert subject.sessions_per_week == 3
        assert subject.subject_type == SubjectType.LECTURE
        assert subject.priority == SubjectPriority.MEDIUM
    
    def test_subject_code_uppercase_conversion(self):
        """Test that subject code is converted to uppercase."""
        subject = Subject(
            name="Physics",
            code="phys101",
            duration_minutes=60
        )
        
        assert subject.code == "PHYS101"
    
    def test_invalid_duration(self):
        """Test validation of invalid duration."""
        with pytest.raises(ValueError):
            Subject(
                name="Chemistry",
                code="CHEM101",
                duration_minutes=10  # Too short
            )
    
    def test_get_total_hours_per_week(self):
        """Test calculation of total hours per week."""
        subject = Subject(
            name="Biology",
            code="BIO101",
            duration_minutes=90,
            sessions_per_week=2
        )
        
        assert subject.get_total_hours_per_week() == 3.0
    
    def test_has_prerequisite(self):
        """Test prerequisite checking."""
        subject = Subject(
            name="Advanced Math",
            code="MATH201",
            duration_minutes=60,
            prerequisites=["MATH101", "MATH102"]
        )
        
        assert subject.has_prerequisite("MATH101")
        assert subject.has_prerequisite("math101")  # Case insensitive
        assert not subject.has_prerequisite("PHYS101")


class TestTeacher:
    """Test Teacher model."""
    
    def test_create_teacher(self):
        """Test creating a teacher."""
        teacher = Teacher(
            name="Dr. John Smith",
            employee_id="T001",
            email="john.smith@university.edu",
            subjects_qualified=["MATH101", "MATH201"]
        )
        
        assert teacher.name == "Dr. John Smith"
        assert teacher.employee_id == "T001"
        assert teacher.email == "john.smith@university.edu"
        assert teacher.teacher_type == TeacherType.FULL_TIME
        assert teacher.status == TeacherStatus.ACTIVE
        assert "MATH101" in teacher.subjects_qualified
    
    def test_employee_id_uppercase_conversion(self):
        """Test that employee ID is converted to uppercase."""
        teacher = Teacher(
            name="Jane Doe",
            employee_id="t002"
        )
        
        assert teacher.employee_id == "T002"
    
    def test_can_teach_subject(self):
        """Test subject teaching capability check."""
        teacher = Teacher(
            name="Dr. Smith",
            employee_id="T001",
            subjects_qualified=["MATH101", "PHYS101"]
        )
        
        assert teacher.can_teach_subject("MATH101")
        assert teacher.can_teach_subject("math101")  # Case insensitive
        assert not teacher.can_teach_subject("CHEM101")
    
    def test_add_subject_qualification(self):
        """Test adding subject qualification."""
        teacher = Teacher(
            name="Dr. Smith",
            employee_id="T001",
            subjects_qualified=["MATH101"]
        )
        
        teacher.add_subject_qualification("PHYS101")
        assert teacher.can_teach_subject("PHYS101")
        
        # Should not add duplicate
        teacher.add_subject_qualification("MATH101")
        assert teacher.subjects_qualified.count("MATH101") == 1
    
    def test_assign_hours(self):
        """Test assigning teaching hours."""
        teacher = Teacher(
            name="Dr. Smith",
            employee_id="T001",
            max_hours_per_week=20
        )
        
        teacher.assign_hours("MATH101", 6.0)
        teacher.assign_hours("PHYS101", 4.0)
        
        assert teacher.current_weekly_hours == 10.0
        assert teacher.get_available_hours() == 10.0
        assert teacher.get_workload_percentage() == 50.0


class TestClassroom:
    """Test Classroom model."""
    
    def test_create_classroom(self):
        """Test creating a classroom."""
        classroom = Classroom(
            name="Main Lecture Hall",
            room_number="A101",
            capacity=50,
            has_projector=True
        )
        
        assert classroom.name == "Main Lecture Hall"
        assert classroom.room_number == "A101"
        assert classroom.capacity == 50
        assert classroom.has_projector is True
        assert classroom.room_type == RoomType.CLASSROOM
        assert classroom.status == RoomStatus.AVAILABLE
    
    def test_room_number_uppercase_conversion(self):
        """Test that room number is converted to uppercase."""
        classroom = Classroom(
            name="Lab",
            room_number="b202",
            capacity=25
        )
        
        assert classroom.room_number == "B202"
    
    def test_can_accommodate(self):
        """Test student capacity check."""
        classroom = Classroom(
            name="Small Room",
            room_number="C101",
            capacity=20
        )
        
        assert classroom.can_accommodate(15)
        assert classroom.can_accommodate(20)
        assert not classroom.can_accommodate(25)
    
    def test_meets_requirements(self):
        """Test requirements checking."""
        classroom = Classroom(
            name="Computer Lab",
            room_number="D101",
            capacity=30,
            has_computers=True,
            has_projector=True
        )
        
        requirements = {
            'has_computers': True,
            'has_projector': True
        }
        assert classroom.meets_requirements(requirements)
        
        requirements['has_audio_system'] = True
        assert not classroom.meets_requirements(requirements)
    
    def test_add_remove_equipment(self):
        """Test adding and removing equipment."""
        classroom = Classroom(
            name="Workshop",
            room_number="W101",
            capacity=15
        )
        
        classroom.add_equipment("3D Printer")
        assert "3D Printer" in classroom.special_equipment
        
        classroom.remove_equipment("3D Printer")
        assert "3D Printer" not in classroom.special_equipment


class TestTimeSlot:
    """Test TimeSlot model."""
    
    def test_create_time_slot(self):
        """Test creating a time slot."""
        slot = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        assert slot.day == DayOfWeek.MONDAY
        assert slot.start_time == time(9, 0)
        assert slot.end_time == time(10, 0)
        assert slot.duration_minutes == 60
    
    def test_duration_calculation(self):
        """Test automatic duration calculation."""
        slot = TimeSlot(
            day=DayOfWeek.TUESDAY,
            start_time=time(14, 0),
            end_time=time(15, 30)
        )
        
        assert slot.duration_minutes == 90
    
    def test_invalid_time_range(self):
        """Test validation of invalid time range."""
        with pytest.raises(ValueError):
            TimeSlot(
                day=DayOfWeek.WEDNESDAY,
                start_time=time(10, 0),
                end_time=time(9, 0)  # End before start
            )
    
    def test_overlaps_with(self):
        """Test time slot overlap detection."""
        slot1 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        slot2 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(9, 30),
            end_time=time(10, 30)
        )
        
        slot3 = TimeSlot(
            day=DayOfWeek.TUESDAY,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        slot4 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        assert slot1.overlaps_with(slot2)  # Same day, overlapping time
        assert not slot1.overlaps_with(slot3)  # Different day
        assert not slot1.overlaps_with(slot4)  # Adjacent, not overlapping
    
    def test_is_adjacent_to(self):
        """Test time slot adjacency detection."""
        slot1 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        slot2 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        slot3 = TimeSlot(
            day=DayOfWeek.MONDAY,
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        
        assert slot1.is_adjacent_to(slot2)
        assert slot2.is_adjacent_to(slot3)
        assert not slot1.is_adjacent_to(slot3)
    
    def test_string_representation(self):
        """Test string representation of time slot."""
        slot = TimeSlot(
            day=DayOfWeek.FRIDAY,
            start_time=time(14, 30),
            end_time=time(16, 0)
        )
        
        expected = "Friday 14:30-16:00"
        assert str(slot) == expected