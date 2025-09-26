"""Input/Output handlers for timetable data."""

import json
import yaml
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.timetable import TimeTable, ScheduleEntry
from ..models.subject import Subject
from ..models.teacher import Teacher
from ..models.classroom import Classroom
from ..models.time_slot import TimeSlot
from ..config.logging_config import get_logger
from ..exceptions.timetable_exceptions import TimeTableError

logger = get_logger(__name__)


def save_timetable(timetable: TimeTable, file_path: Union[str, Path], format_type: str = "json") -> bool:
    """
    Save timetable to file.
    
    Args:
        timetable: TimeTable instance to save
        file_path: Path to save file
        format_type: File format ("json", "yaml", "csv")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type.lower() == "json":
            return _save_timetable_json(timetable, file_path)
        elif format_type.lower() == "yaml":
            return _save_timetable_yaml(timetable, file_path)
        elif format_type.lower() == "csv":
            return _save_timetable_csv(timetable, file_path)
        else:
            logger.error(f"Unsupported format type: {format_type}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to save timetable: {e}")
        return False


def load_timetable(file_path: Union[str, Path], format_type: str = "json") -> Optional[TimeTable]:
    """
    Load timetable from file.
    
    Args:
        file_path: Path to load file
        format_type: File format ("json", "yaml", "csv")
        
    Returns:
        TimeTable instance if successful, None otherwise
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if format_type.lower() == "json":
            return _load_timetable_json(file_path)
        elif format_type.lower() == "yaml":
            return _load_timetable_yaml(file_path)
        elif format_type.lower() == "csv":
            return _load_timetable_csv(file_path)
        else:
            logger.error(f"Unsupported format type: {format_type}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to load timetable: {e}")
        return None


def _save_timetable_json(timetable: TimeTable, file_path: Path) -> bool:
    """Save timetable as JSON."""
    try:
        data = _timetable_to_dict(timetable)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Timetable saved to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        return False


def _load_timetable_json(file_path: Path) -> Optional[TimeTable]:
    """Load timetable from JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timetable = _dict_to_timetable(data)
        logger.info(f"Timetable loaded from {file_path}")
        return timetable
        
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return None


def _save_timetable_yaml(timetable: TimeTable, file_path: Path) -> bool:
    """Save timetable as YAML."""
    try:
        data = _timetable_to_dict(timetable)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"Timetable saved to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save YAML: {e}")
        return False


def _load_timetable_yaml(file_path: Path) -> Optional[TimeTable]:
    """Load timetable from YAML."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        timetable = _dict_to_timetable(data)
        logger.info(f"Timetable loaded from {file_path}")
        return timetable
        
    except Exception as e:
        logger.error(f"Failed to load YAML: {e}")
        return None


def _save_timetable_csv(timetable: TimeTable, file_path: Path) -> bool:
    """Save timetable schedule as CSV."""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            header = [
                'Day', 'Start Time', 'End Time', 'Subject Code', 'Subject Name',
                'Teacher Name', 'Teacher ID', 'Classroom Name', 'Room Number',
                'Student Count', 'Notes'
            ]
            writer.writerow(header)
            
            # Write schedule entries
            for entry in timetable.schedule:
                row = [
                    entry.time_slot.day.value,
                    entry.time_slot.start_time.strftime('%H:%M'),
                    entry.time_slot.end_time.strftime('%H:%M'),
                    entry.subject.code,
                    entry.subject.name,
                    entry.teacher.name,
                    entry.teacher.employee_id,
                    entry.classroom.name,
                    entry.classroom.room_number,
                    entry.student_count or '',
                    entry.notes or ''
                ]
                writer.writerow(row)
        
        logger.info(f"Timetable schedule saved to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")
        return False


def _load_timetable_csv(file_path: Path) -> Optional[TimeTable]:
    """Load timetable from CSV (schedule only)."""
    logger.warning("CSV loading only supports schedule entries, not complete timetable data")
    return None  # CSV loading is complex and would require additional metadata


def _timetable_to_dict(timetable: TimeTable) -> Dict[str, Any]:
    """Convert TimeTable to dictionary."""
    return {
        "metadata": {
            "id": timetable.id,
            "name": timetable.name,
            "academic_year": timetable.academic_year,
            "semester": timetable.semester,
            "start_date": timetable.start_date.isoformat(),
            "end_date": timetable.end_date.isoformat(),
            "created_at": timetable.created_at.isoformat(),
            "updated_at": timetable.updated_at.isoformat() if timetable.updated_at else None,
            "working_days": [day.value for day in timetable.working_days],
            "daily_start_time": timetable.daily_start_time,
            "daily_end_time": timetable.daily_end_time,
            "break_duration_minutes": timetable.break_duration_minutes,
            "lunch_break_duration_minutes": timetable.lunch_break_duration_minutes,
        },
        "subjects": {code: subject.dict() for code, subject in timetable.subjects.items()},
        "teachers": {id_: teacher.dict() for id_, teacher in timetable.teachers.items()},
        "classrooms": {num: classroom.dict() for num, classroom in timetable.classrooms.items()},
        "schedule": [entry.dict() for entry in timetable.schedule]
    }


def _dict_to_timetable(data: Dict[str, Any]) -> TimeTable:
    """Convert dictionary to TimeTable."""
    metadata = data["metadata"]
    
    # Create TimeTable instance
    timetable = TimeTable(
        id=metadata["id"],
        name=metadata["name"],
        academic_year=metadata["academic_year"],
        semester=metadata["semester"],
        start_date=datetime.fromisoformat(metadata["start_date"]),
        end_date=datetime.fromisoformat(metadata["end_date"]),
        created_at=datetime.fromisoformat(metadata["created_at"]),
        updated_at=datetime.fromisoformat(metadata["updated_at"]) if metadata.get("updated_at") else None,
        daily_start_time=metadata["daily_start_time"],
        daily_end_time=metadata["daily_end_time"],
        break_duration_minutes=metadata["break_duration_minutes"],
        lunch_break_duration_minutes=metadata["lunch_break_duration_minutes"],
    )
    
    # Set working days
    from ..models.time_slot import DayOfWeek
    timetable.working_days = {DayOfWeek(day) for day in metadata["working_days"]}
    
    # Load subjects
    for code, subject_data in data["subjects"].items():
        subject = Subject(**subject_data)
        timetable.subjects[code] = subject
    
    # Load teachers
    for id_, teacher_data in data["teachers"].items():
        teacher = Teacher(**teacher_data)
        timetable.teachers[id_] = teacher
    
    # Load classrooms
    for num, classroom_data in data["classrooms"].items():
        classroom = Classroom(**classroom_data)
        timetable.classrooms[num] = classroom
    
    # Load schedule entries
    for entry_data in data["schedule"]:
        # Reconstruct the entry with proper object references
        time_slot = TimeSlot(**entry_data["time_slot"])
        subject = timetable.subjects[entry_data["subject"]["code"]]
        teacher = timetable.teachers[entry_data["teacher"]["employee_id"]]
        classroom = timetable.classrooms[entry_data["classroom"]["room_number"]]
        
        entry = ScheduleEntry(
            id=entry_data["id"],
            time_slot=time_slot,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            student_count=entry_data.get("student_count"),
            notes=entry_data.get("notes"),
            created_at=datetime.fromisoformat(entry_data["created_at"]),
            updated_at=datetime.fromisoformat(entry_data["updated_at"]) if entry_data.get("updated_at") else None,
        )
        timetable.schedule.append(entry)
    
    return timetable


def export_timetable_html(timetable: TimeTable, file_path: Union[str, Path]) -> bool:
    """Export timetable as HTML."""
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = _generate_html_timetable(timetable)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Timetable exported to HTML: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export HTML: {e}")
        return False


def _generate_html_timetable(timetable: TimeTable) -> str:
    """Generate HTML representation of timetable."""
    from collections import defaultdict
    
    # Group entries by day and time
    schedule_grid = defaultdict(lambda: defaultdict(list))
    time_slots = set()
    
    for entry in timetable.schedule:
        time_key = f"{entry.time_slot.start_time.strftime('%H:%M')}-{entry.time_slot.end_time.strftime('%H:%M')}"
        schedule_grid[entry.time_slot.day][time_key].append(entry)
        time_slots.add(time_key)
    
    # Sort time slots
    sorted_times = sorted(time_slots)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{timetable.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .info {{ margin-bottom: 20px; color: #666; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .entry {{ background-color: #f9f9f9; margin: 2px 0; padding: 2px; border-radius: 3px; }}
            .subject {{ font-weight: bold; }}
            .teacher {{ color: #666; font-size: 0.9em; }}
            .classroom {{ color: #999; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <h1>{timetable.name}</h1>
        <div class="info">
            <p><strong>Academic Year:</strong> {timetable.academic_year} | <strong>Semester:</strong> {timetable.semester}</p>
            <p><strong>Period:</strong> {timetable.start_date.strftime('%Y-%m-%d')} to {timetable.end_date.strftime('%Y-%m-%d')}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Time</th>
    """
    
    # Add day headers
    for day in timetable.working_days:
        html += f"<th>{day.value}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Add time slot rows
    for time_slot in sorted_times:
        html += f"<tr><td><strong>{time_slot}</strong></td>"
        
        for day in timetable.working_days:
            html += "<td>"
            
            if day in schedule_grid and time_slot in schedule_grid[day]:
                for entry in schedule_grid[day][time_slot]:
                    html += f"""
                    <div class="entry">
                        <div class="subject">{entry.subject.name}</div>
                        <div class="teacher">{entry.teacher.name}</div>
                        <div class="classroom">{entry.classroom.name}</div>
                    </div>
                    """
            
            html += "</td>"
        
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
        
        <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
            Generated on {generation_time}
        </div>
    </body>
    </html>
    """.format(generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return html


def import_subjects_from_csv(file_path: Union[str, Path]) -> List[Subject]:
    """Import subjects from CSV file."""
    subjects = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                subject = Subject(
                    name=row['name'],
                    code=row['code'],
                    duration_minutes=int(row['duration_minutes']),
                    sessions_per_week=int(row.get('sessions_per_week', 1)),
                    max_students=int(row['max_students']) if row.get('max_students') else None,
                    description=row.get('description'),
                )
                subjects.append(subject)
                
        logger.info(f"Imported {len(subjects)} subjects from {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to import subjects: {e}")
    
    return subjects


def import_teachers_from_csv(file_path: Union[str, Path]) -> List[Teacher]:
    """Import teachers from CSV file."""
    teachers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                teacher = Teacher(
                    name=row['name'],
                    employee_id=row['employee_id'],
                    email=row.get('email'),
                    phone=row.get('phone'),
                    department=row.get('department'),
                    subjects_qualified=row.get('subjects_qualified', '').split(',') if row.get('subjects_qualified') else [],
                    max_hours_per_week=int(row.get('max_hours_per_week', 40)),
                )
                teachers.append(teacher)
                
        logger.info(f"Imported {len(teachers)} teachers from {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to import teachers: {e}")
    
    return teachers


def import_classrooms_from_csv(file_path: Union[str, Path]) -> List[Classroom]:
    """Import classrooms from CSV file."""
    classrooms = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                classroom = Classroom(
                    name=row['name'],
                    room_number=row['room_number'],
                    building=row.get('building'),
                    capacity=int(row['capacity']),
                    has_projector=row.get('has_projector', '').lower() == 'true',
                    has_computers=row.get('has_computers', '').lower() == 'true',
                    has_internet=row.get('has_internet', 'true').lower() == 'true',
                )
                classrooms.append(classroom)
                
        logger.info(f"Imported {len(classrooms)} classrooms from {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to import classrooms: {e}")
    
    return classrooms