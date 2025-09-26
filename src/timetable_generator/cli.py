"""Command Line Interface for TimeTable Generator."""

import typer
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

from .core.timetable import TimeTable, ScheduleEntry
from .core.scheduler import Scheduler, SchedulingConstraints
from .models.subject import Subject, SubjectType, SubjectPriority
from .models.teacher import Teacher, TeacherType
from .models.classroom import Classroom, RoomType
from .models.time_slot import TimeSlot, DayOfWeek
from .utils.formatters import format_timetable, format_teacher_schedule, format_classroom_schedule
from .utils.io_handlers import save_timetable, load_timetable, export_timetable_html
from .utils.validators import validate_time_format, validate_email
from .config.settings import get_settings
from .config.logging_config import setup_logging
from .exceptions.timetable_exceptions import TimeTableError

app = typer.Typer(
    name="timetable-gen",
    help="Professional TimeTable Generator - Create and manage educational timetables",
    add_completion=False
)
console = Console()

# Global state
current_timetable: Optional[TimeTable] = None


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    log_file: Optional[str] = typer.Option(None, "--log-file", help="Log file path"),
):
    """TimeTable Generator CLI."""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level=log_level, log_file=log_file)
    
    if verbose:
        rprint("[dim]Verbose mode enabled[/dim]")


@app.command()
def create(
    name: str = typer.Argument(..., help="Timetable name"),
    academic_year: str = typer.Option(..., "--year", "-y", help="Academic year (e.g., 2023-2024)"),
    semester: str = typer.Option(..., "--semester", "-s", help="Semester (e.g., Fall, Spring)"),
    start_date: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d"),
        "--start-date",
        help="Start date (YYYY-MM-DD)"
    ),
    end_date: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d"),
        "--end-date", 
        help="End date (YYYY-MM-DD)"
    ),
):
    """Create a new timetable."""
    global current_timetable
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        current_timetable = TimeTable(
            name=name,
            academic_year=academic_year,
            semester=semester,
            start_date=start,
            end_date=end
        )
        
        rprint(f"✅ Created timetable: [bold]{name}[/bold]")
        rprint(f"   Academic Year: {academic_year}")
        rprint(f"   Semester: {semester}")
        rprint(f"   Period: {start_date} to {end_date}")
        
    except Exception as e:
        rprint(f"❌ Error creating timetable: {e}")
        raise typer.Exit(1)


@app.command()
def load(file_path: str = typer.Argument(..., help="Path to timetable file")):
    """Load a timetable from file."""
    global current_timetable
    
    path = Path(file_path)
    if not path.exists():
        rprint(f"❌ File not found: {file_path}")
        raise typer.Exit(1)
    
    # Determine format from extension
    format_type = path.suffix.lower().replace('.', '') or 'json'
    
    current_timetable = load_timetable(path, format_type)
    
    if current_timetable:
        rprint(f"✅ Loaded timetable: [bold]{current_timetable.name}[/bold]")
        _show_timetable_info(current_timetable)
    else:
        rprint(f"❌ Failed to load timetable from {file_path}")
        raise typer.Exit(1)


@app.command()
def save(
    file_path: str = typer.Argument(..., help="Path to save timetable"),
    format_type: str = typer.Option("json", "--format", "-f", help="File format (json, yaml, csv)")
):
    """Save the current timetable to file."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if save_timetable(current_timetable, file_path, format_type):
        rprint(f"✅ Timetable saved to: {file_path}")
    else:
        rprint(f"❌ Failed to save timetable to {file_path}")
        raise typer.Exit(1)


@app.command()
def add_subject(
    name: str = typer.Argument(..., help="Subject name"),
    code: str = typer.Argument(..., help="Subject code"),
    duration: int = typer.Option(60, "--duration", "-d", help="Duration in minutes"),
    sessions: int = typer.Option(1, "--sessions", "-s", help="Sessions per week"),
    subject_type: str = typer.Option("lecture", "--type", "-t", help="Subject type"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority level"),
    max_students: Optional[int] = typer.Option(None, "--max-students", help="Maximum students"),
):
    """Add a subject to the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    try:
        subject = Subject(
            name=name,
            code=code,
            duration_minutes=duration,
            sessions_per_week=sessions,
            subject_type=SubjectType(subject_type),
            priority=SubjectPriority(priority),
            max_students=max_students
        )
        
        current_timetable.add_subject(subject)
        rprint(f"✅ Added subject: [bold]{name}[/bold] ({code})")
        
    except Exception as e:
        rprint(f"❌ Error adding subject: {e}")
        raise typer.Exit(1)


@app.command()
def add_teacher(
    name: str = typer.Argument(..., help="Teacher name"),
    employee_id: str = typer.Argument(..., help="Employee ID"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    department: Optional[str] = typer.Option(None, "--dept", "-d", help="Department"),
    max_hours: int = typer.Option(40, "--max-hours", help="Maximum hours per week"),
    subjects: Optional[str] = typer.Option(None, "--subjects", "-s", help="Qualified subjects (comma-separated)"),
):
    """Add a teacher to the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    try:
        if email and not validate_email(email):
            rprint("❌ Invalid email format")
            raise typer.Exit(1)
        
        subjects_list = subjects.split(',') if subjects else []
        subjects_list = [s.strip() for s in subjects_list]
        
        teacher = Teacher(
            name=name,
            employee_id=employee_id,
            email=email,
            department=department,
            max_hours_per_week=max_hours,
            subjects_qualified=subjects_list
        )
        
        current_timetable.add_teacher(teacher)
        rprint(f"✅ Added teacher: [bold]{name}[/bold] ({employee_id})")
        
    except Exception as e:
        rprint(f"❌ Error adding teacher: {e}")
        raise typer.Exit(1)


@app.command()
def add_classroom(
    name: str = typer.Argument(..., help="Classroom name"),
    room_number: str = typer.Argument(..., help="Room number"),
    capacity: int = typer.Argument(..., help="Student capacity"),
    building: Optional[str] = typer.Option(None, "--building", "-b", help="Building name"),
    room_type: str = typer.Option("classroom", "--type", "-t", help="Room type"),
    has_projector: bool = typer.Option(False, "--projector", help="Has projector"),
    has_computers: bool = typer.Option(False, "--computers", help="Has computers"),
):
    """Add a classroom to the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    try:
        classroom = Classroom(
            name=name,
            room_number=room_number,
            capacity=capacity,
            building=building,
            room_type=RoomType(room_type),
            has_projector=has_projector,
            has_computers=has_computers
        )
        
        current_timetable.add_classroom(classroom)
        rprint(f"✅ Added classroom: [bold]{name}[/bold] ({room_number}) - Capacity: {capacity}")
        
    except Exception as e:
        rprint(f"❌ Error adding classroom: {e}")
        raise typer.Exit(1)


@app.command()
def generate(
    optimize: bool = typer.Option(True, "--optimize/--no-optimize", help="Optimize the schedule"),
    max_attempts: int = typer.Option(1000, "--max-attempts", help="Maximum scheduling attempts"),
):
    """Generate a timetable schedule automatically."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if not current_timetable.subjects:
        rprint("❌ No subjects found. Add subjects first.")
        raise typer.Exit(1)
    
    if not current_timetable.teachers:
        rprint("❌ No teachers found. Add teachers first.")
        raise typer.Exit(1)
    
    if not current_timetable.classrooms:
        rprint("❌ No classrooms found. Add classrooms first.")
        raise typer.Exit(1)
    
    try:
        constraints = SchedulingConstraints()
        constraints.max_attempts = max_attempts
        
        scheduler = Scheduler(current_timetable, constraints)
        
        with Progress() as progress:
            task = progress.add_task("Generating schedule...", total=100)
            
            success = scheduler.generate_schedule(optimize)
            progress.update(task, completed=100)
        
        if success:
            report = scheduler.get_scheduling_report()
            rprint("✅ Schedule generated successfully!")
            rprint(f"   Total entries: {report['total_entries']}")
            rprint(f"   Success rate: {report['success_rate']:.1f}%")
            
            if report['scheduling_issues']:
                rprint("⚠️  Issues found:")
                for issue in report['scheduling_issues'][:5]:  # Show first 5 issues
                    rprint(f"   • {issue}")
        else:
            rprint("❌ Failed to generate complete schedule")
            
    except Exception as e:
        rprint(f"❌ Error generating schedule: {e}")
        raise typer.Exit(1)


@app.command()
def show(
    format_type: str = typer.Option("summary", "--format", "-f", help="Display format (grid, list, summary)"),
):
    """Show the current timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    try:
        output = format_timetable(current_timetable, format_type)
        rprint(output)
        
    except Exception as e:
        rprint(f"❌ Error displaying timetable: {e}")
        raise typer.Exit(1)


@app.command()
def list_subjects():
    """List all subjects in the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if not current_timetable.subjects:
        rprint("No subjects found.")
        return
    
    table = Table(title="Subjects")
    table.add_column("Code", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Sessions/Week", style="blue")
    table.add_column("Priority", style="red")
    
    for subject in current_timetable.subjects.values():
        table.add_row(
            subject.code,
            subject.name,
            subject.subject_type.value,
            f"{subject.duration_minutes}m",
            str(subject.sessions_per_week),
            subject.priority.value
        )
    
    console.print(table)


@app.command()
def list_teachers():
    """List all teachers in the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if not current_timetable.teachers:
        rprint("No teachers found.")
        return
    
    table = Table(title="Teachers")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Department", style="green")
    table.add_column("Max Hours", style="yellow")
    table.add_column("Subjects", style="blue")
    
    for teacher in current_timetable.teachers.values():
        subjects_str = ", ".join(teacher.subjects_qualified[:3])  # Show first 3
        if len(teacher.subjects_qualified) > 3:
            subjects_str += "..."
        
        table.add_row(
            teacher.employee_id,
            teacher.name,
            teacher.department or "N/A",
            str(teacher.max_hours_per_week),
            subjects_str
        )
    
    console.print(table)


@app.command()
def list_classrooms():
    """List all classrooms in the timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if not current_timetable.classrooms:
        rprint("No classrooms found.")
        return
    
    table = Table(title="Classrooms")
    table.add_column("Room #", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Capacity", style="yellow")
    table.add_column("Features", style="blue")
    
    for classroom in current_timetable.classrooms.values():
        features = []
        if classroom.has_projector:
            features.append("Projector")
        if classroom.has_computers:
            features.append("Computers")
        if classroom.has_internet:
            features.append("Internet")
        
        table.add_row(
            classroom.room_number,
            classroom.name,
            classroom.room_type.value,
            str(classroom.capacity),
            ", ".join(features) or "Basic"
        )
    
    console.print(table)


@app.command()
def teacher_schedule(teacher_id: str = typer.Argument(..., help="Teacher employee ID")):
    """Show schedule for a specific teacher."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if teacher_id not in current_timetable.teachers:
        rprint(f"❌ Teacher with ID '{teacher_id}' not found.")
        raise typer.Exit(1)
    
    output = format_teacher_schedule(current_timetable, teacher_id)
    rprint(output)


@app.command()
def classroom_schedule(room_number: str = typer.Argument(..., help="Classroom room number")):
    """Show schedule for a specific classroom."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if room_number not in current_timetable.classrooms:
        rprint(f"❌ Classroom '{room_number}' not found.")
        raise typer.Exit(1)
    
    output = format_classroom_schedule(current_timetable, room_number)
    rprint(output)


@app.command()
def validate():
    """Validate the current timetable for conflicts and issues."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    issues = current_timetable.validate_schedule()
    
    if not issues:
        rprint("✅ No issues found in the timetable!")
    else:
        rprint(f"⚠️  Found {len(issues)} issues:")
        for i, issue in enumerate(issues, 1):
            rprint(f"{i:2}. {issue}")


@app.command()
def export_html(file_path: str = typer.Argument(..., help="HTML file path")):
    """Export timetable as HTML."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if export_timetable_html(current_timetable, file_path):
        rprint(f"✅ Timetable exported to HTML: {file_path}")
    else:
        rprint(f"❌ Failed to export HTML to {file_path}")
        raise typer.Exit(1)


@app.command()
def clear():
    """Clear the current timetable schedule."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    if typer.confirm("Are you sure you want to clear the schedule?"):
        current_timetable.clear_schedule()
        rprint("✅ Schedule cleared.")
    else:
        rprint("Operation cancelled.")


@app.command()
def info():
    """Show information about the current timetable."""
    if not current_timetable:
        rprint("❌ No timetable loaded. Create or load a timetable first.")
        raise typer.Exit(1)
    
    _show_timetable_info(current_timetable)


def _show_timetable_info(timetable: TimeTable):
    """Display timetable information."""
    stats = timetable.get_statistics()
    
    panel_content = f"""
[bold]Name:[/bold] {timetable.name}
[bold]Academic Year:[/bold] {timetable.academic_year}
[bold]Semester:[/bold] {timetable.semester}
[bold]Period:[/bold] {timetable.start_date.strftime('%Y-%m-%d')} to {timetable.end_date.strftime('%Y-%m-%d')}

[bold]Resources:[/bold]
• Subjects: {stats['total_subjects']}
• Teachers: {stats['total_teachers']}
• Classrooms: {stats['total_classrooms']}

[bold]Schedule:[/bold]
• Total Entries: {stats['total_schedule_entries']}
• Total Hours: {stats['total_teaching_hours']:.1f}h
• Conflicts: {stats['schedule_conflicts']}
    """
    
    console.print(Panel(panel_content, title="Timetable Information", border_style="blue"))


if __name__ == "__main__":
    app()


def main():
    """Entry point for the CLI."""
    app()