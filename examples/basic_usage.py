#!/usr/bin/env python3
"""
Basic usage example for TimeTable Generator.

This example demonstrates how to create a simple timetable using the Python API.
"""

from datetime import datetime, time
from timetable_generator import (
    TimeTable, Subject, Teacher, Classroom, TimeSlot,
    Scheduler, SchedulingConstraints,
    SubjectType, SubjectPriority, TeacherType, RoomType, DayOfWeek
)
from timetable_generator.utils.formatters import format_timetable
from timetable_generator.utils.io_handlers import save_timetable, export_timetable_html


def create_sample_timetable():
    """Create a sample timetable with subjects, teachers, and classrooms."""
    
    # Create timetable
    timetable = TimeTable(
        name="Computer Science Department - Fall 2024",
        academic_year="2024-2025",
        semester="Fall",
        start_date=datetime(2024, 8, 26),
        end_date=datetime(2024, 12, 15)
    )
    
    print(f"✅ Created timetable: {timetable.name}")
    
    # Add subjects
    subjects_data = [
        ("Programming Fundamentals", "CS101", 90, 2, SubjectType.LAB, SubjectPriority.HIGH, True),
        ("Data Structures", "CS201", 60, 3, SubjectType.LECTURE, SubjectPriority.HIGH, False),
        ("Database Systems", "CS301", 60, 2, SubjectType.LECTURE, SubjectPriority.MEDIUM, False),
        ("Web Development", "CS302", 120, 2, SubjectType.LAB, SubjectPriority.MEDIUM, True),
        ("Software Engineering", "CS401", 60, 3, SubjectType.SEMINAR, SubjectPriority.HIGH, False),
    ]
    
    for name, code, duration, sessions, subj_type, priority, requires_comp in subjects_data:
        subject = Subject(
            name=name,
            code=code,
            duration_minutes=duration,
            sessions_per_week=sessions,
            subject_type=subj_type,
            priority=priority,
            requires_computer=requires_comp,
            max_students=30
        )
        timetable.add_subject(subject)
        print(f"  📚 Added subject: {name} ({code})")
    
    # Add teachers
    teachers_data = [
        ("Dr. Alice Johnson", "T001", "alice@university.edu", "Computer Science", ["CS101", "CS201"]),
        ("Prof. Bob Smith", "T002", "bob@university.edu", "Computer Science", ["CS301", "CS401"]),
        ("Dr. Carol Davis", "T003", "carol@university.edu", "Computer Science", ["CS302", "CS401"]),
        ("Mr. David Wilson", "T004", "david@university.edu", "Computer Science", ["CS101", "CS302"]),
    ]
    
    for name, emp_id, email, dept, subjects in teachers_data:
        teacher = Teacher(
            name=name,
            employee_id=emp_id,
            email=email,
            department=dept,
            teacher_type=TeacherType.FULL_TIME,
            subjects_qualified=subjects,
            max_hours_per_week=20,
            max_hours_per_day=6
        )
        timetable.add_teacher(teacher)
        print(f"  👨‍🏫 Added teacher: {name} ({emp_id})")
    
    # Add classrooms
    classrooms_data = [
        ("Lecture Hall A", "LH-A", 100, RoomType.LECTURE_HALL, False, True, False),
        ("Lecture Hall B", "LH-B", 80, RoomType.LECTURE_HALL, False, True, False),
        ("Computer Lab 1", "CL-1", 30, RoomType.COMPUTER_LAB, True, True, True),
        ("Computer Lab 2", "CL-2", 25, RoomType.COMPUTER_LAB, True, True, True),
        ("Seminar Room", "SR-1", 40, RoomType.SEMINAR_ROOM, False, True, False),
    ]
    
    for name, room_num, capacity, room_type, has_comp, has_proj, has_internet in classrooms_data:
        classroom = Classroom(
            name=name,
            room_number=room_num,
            capacity=capacity,
            room_type=room_type,
            has_computers=has_comp,
            has_projector=has_proj,
            has_internet=has_internet,
            building="Main Campus"
        )
        timetable.add_classroom(classroom)
        print(f"  🏫 Added classroom: {name} ({room_num}) - Capacity: {capacity}")
    
    return timetable


def generate_schedule(timetable):
    """Generate an optimized schedule for the timetable."""
    
    print("\n🤖 Generating schedule...")
    
    # Configure scheduling constraints
    constraints = SchedulingConstraints()
    constraints.max_attempts = 2000
    constraints.prefer_morning_sessions = True
    constraints.avoid_single_hour_gaps = True
    constraints.max_consecutive_hours = 3
    
    # Create scheduler
    scheduler = Scheduler(timetable, constraints)
    
    # Generate schedule
    success = scheduler.generate_schedule(optimize=True)
    
    if success:
        report = scheduler.get_scheduling_report()
        print(f"✅ Schedule generated successfully!")
        print(f"   📊 Total entries: {report['total_entries']}")
        print(f"   📈 Success rate: {report['success_rate']:.1f}%")
        
        # Show any issues
        if report['scheduling_issues']:
            print("⚠️  Issues found:")
            for issue in report['scheduling_issues'][:3]:  # Show first 3
                print(f"   • {issue}")
        
        return True
    else:
        print("❌ Failed to generate complete schedule")
        return False


def demonstrate_queries(timetable):
    """Demonstrate various queries on the timetable."""
    
    print("\n📋 Demonstrating queries...")
    
    # Get statistics
    stats = timetable.get_statistics()
    print(f"📊 Statistics:")
    print(f"   • Total subjects: {stats['total_subjects']}")
    print(f"   • Total teachers: {stats['total_teachers']}")
    print(f"   • Total classrooms: {stats['total_classrooms']}")
    print(f"   • Schedule entries: {stats['total_schedule_entries']}")
    print(f"   • Teaching hours: {stats['total_teaching_hours']:.1f}h")
    
    # Show teacher workload
    teacher_hours = timetable.get_weekly_hours_by_teacher()
    print(f"\n👨‍🏫 Teacher workload:")
    for teacher_id, hours in teacher_hours.items():
        teacher = timetable.teachers[teacher_id]
        percentage = (hours / teacher.max_hours_per_week * 100) if teacher.max_hours_per_week > 0 else 0
        print(f"   • {teacher.name}: {hours:.1f}h ({percentage:.1f}%)")
    
    # Show classroom utilization
    utilization = timetable.get_classroom_utilization()
    print(f"\n🏫 Classroom utilization:")
    for room_num, daily_hours in utilization.items():
        classroom = timetable.classrooms[room_num]
        total_hours = sum(daily_hours.values())
        print(f"   • {classroom.name}: {total_hours:.1f}h/week")
    
    # Validate schedule
    issues = timetable.validate_schedule()
    if not issues:
        print("\n✅ No scheduling conflicts found!")
    else:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for issue in issues[:3]:  # Show first 3
            print(f"   • {issue}")


def save_and_export(timetable):
    """Save timetable in various formats."""
    
    print("\n💾 Saving and exporting...")
    
    # Save as JSON
    if save_timetable(timetable, "examples/sample_timetable.json", "json"):
        print("✅ Saved as JSON: sample_timetable.json")
    
    # Save as YAML
    if save_timetable(timetable, "examples/sample_timetable.yaml", "yaml"):
        print("✅ Saved as YAML: sample_timetable.yaml")
    
    # Export as HTML
    if export_timetable_html(timetable, "examples/sample_timetable.html"):
        print("✅ Exported as HTML: sample_timetable.html")
    
    print("\n📄 Files created in examples/ directory")


def main():
    """Main function to run the example."""
    
    print("🎓 TimeTable Generator - Basic Usage Example")
    print("=" * 50)
    
    try:
        # Create sample timetable with data
        timetable = create_sample_timetable()
        
        # Generate schedule
        if generate_schedule(timetable):
            # Show formatted timetable
            print("\n📅 Generated Timetable (Summary):")
            print(format_timetable(timetable, "summary"))
            
            # Demonstrate queries
            demonstrate_queries(timetable)
            
            # Save and export
            save_and_export(timetable)
            
            print("\n🎉 Example completed successfully!")
            print("\nTry the CLI interface:")
            print("  timetable-gen load examples/sample_timetable.json")
            print("  timetable-gen show --format grid")
            
        else:
            print("\n❌ Could not generate a complete schedule")
            print("This might happen with complex constraints or insufficient resources.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()