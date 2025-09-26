# TimeTable Generator

A professional, industry-standard timetable generation system for educational institutes built with Python and modern software engineering practices.

## 🎯 Features

- **Object-Oriented Design**: Built using modern OOP principles with Pydantic models
- **Intelligent Scheduling**: Advanced algorithm with configurable constraints and optimization
- **Professional CLI**: Rich command-line interface with colored output and interactive features
- **Multiple Export Formats**: JSON, YAML, CSV, and HTML export capabilities
- **Data Validation**: Comprehensive validation with custom error handling
- **Conflict Detection**: Automatic detection and resolution of scheduling conflicts
- **Resource Management**: Efficient management of teachers, classrooms, and subjects
- **Configurable**: Environment-based configuration with sensible defaults
- **Extensible**: Modular architecture for easy extension and customization
- **Well-Tested**: Comprehensive test suite with unit and integration tests

## 🏗️ Architecture

The project follows modern Python package structure with clear separation of concerns:

```
src/timetable_generator/
├── core/              # Core business logic
│   ├── timetable.py   # Main TimeTable class
│   └── scheduler.py   # Scheduling algorithms
├── models/            # Data models
│   ├── base.py        # Base model class
│   ├── subject.py     # Subject model
│   ├── teacher.py     # Teacher model
│   ├── classroom.py   # Classroom model
│   └── time_slot.py   # TimeSlot model
├── utils/             # Utility functions
│   ├── validators.py  # Data validation
│   ├── formatters.py  # Output formatting
│   └── io_handlers.py # File I/O operations
├── config/            # Configuration management
│   ├── settings.py    # Application settings
│   └── logging_config.py # Logging setup
├── exceptions/        # Custom exceptions
└── cli.py            # Command-line interface
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mujadid2001/TimeTableGenerator.git
   cd TimeTableGenerator
   ```

2. **Set up the development environment:**
   ```bash
   make setup-dev
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or for development
   pip install -r requirements-dev.txt
   pip install -e .
   ```

### Basic Usage

1. **Create a new timetable:**
   ```bash
   timetable-gen create "Fall 2024 Schedule" --year "2024-2025" --semester "Fall"
   ```

2. **Add subjects:**
   ```bash
   timetable-gen add-subject "Mathematics" "MATH101" --duration 60 --sessions 3
   timetable-gen add-subject "Physics" "PHYS101" --duration 90 --sessions 2 --type lab
   ```

3. **Add teachers:**
   ```bash
   timetable-gen add-teacher "Dr. John Smith" "T001" --email "john@university.edu" --subjects "MATH101,PHYS101"
   ```

4. **Add classrooms:**
   ```bash
   timetable-gen add-classroom "Main Hall" "A101" 50 --projector --building "Main Building"
   timetable-gen add-classroom "Physics Lab" "B201" 25 --type laboratory --computers
   ```

5. **Generate schedule:**
   ```bash
   timetable-gen generate --optimize
   ```

6. **View the timetable:**
   ```bash
   timetable-gen show --format grid
   ```

7. **Save and export:**
   ```bash
   timetable-gen save schedule.json
   timetable-gen export-html schedule.html
   ```

## 📖 Detailed Usage

### CLI Commands

- `create` - Create a new timetable
- `load` - Load an existing timetable
- `save` - Save timetable to file
- `add-subject` - Add a subject
- `add-teacher` - Add a teacher
- `add-classroom` - Add a classroom
- `generate` - Generate schedule automatically
- `show` - Display timetable in various formats
- `list-subjects` - List all subjects
- `list-teachers` - List all teachers
- `list-classrooms` - List all classrooms
- `teacher-schedule` - Show specific teacher's schedule
- `classroom-schedule` - Show specific classroom's schedule
- `validate` - Validate timetable for conflicts
- `export-html` - Export as HTML
- `clear` - Clear the schedule
- `info` - Show timetable information

### Configuration

Copy `.env.example` to `.env` and customize:

```env
# Scheduling Settings
DAILY_START_TIME="09:00"
DAILY_END_TIME="17:00"
LUNCH_BREAK_START="12:00"
LUNCH_BREAK_END="13:00"

# Constraints
MAX_CONSECUTIVE_HOURS=3
MAX_WEEKLY_HOURS_PER_TEACHER=40
PREFER_MORNING_SESSIONS=true
```

### Python API Usage

```python
from datetime import datetime
from timetable_generator import TimeTable, Subject, Teacher, Classroom, Scheduler

# Create timetable
timetable = TimeTable(
    name="Spring 2024",
    academic_year="2023-2024",
    semester="Spring",
    start_date=datetime(2024, 1, 15),
    end_date=datetime(2024, 5, 15)
)

# Add resources
subject = Subject(name="Math", code="MATH101", duration_minutes=60)
teacher = Teacher(name="Dr. Smith", employee_id="T001", subjects_qualified=["MATH101"])
classroom = Classroom(name="Room A", room_number="A101", capacity=30)

timetable.add_subject(subject)
timetable.add_teacher(teacher)
timetable.add_classroom(classroom)

# Generate schedule
scheduler = Scheduler(timetable)
success = scheduler.generate_schedule()

if success:
    print(f"Generated {len(timetable.schedule)} schedule entries")
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_models.py -v
```

## 🔧 Development

### Code Quality

```bash
# Run all quality checks
make all-checks

# Individual checks
make lint          # Linting with flake8
make format        # Format with black
make type-check    # Type checking with mypy
```

### Project Structure Standards

- **src/ layout** for clean package structure
- **Pydantic models** for data validation
- **Type hints** throughout the codebase
- **Comprehensive logging** with configurable levels
- **Error handling** with custom exceptions
- **Configuration management** with environment variables
- **CLI interface** with rich formatting
- **Modular architecture** for extensibility

## 📊 Features in Detail

### Scheduling Algorithm

The scheduler uses an intelligent algorithm with:
- **Priority-based scheduling** for critical subjects
- **Conflict detection** and resolution
- **Resource optimization** for maximum utilization
- **Constraint satisfaction** with configurable rules
- **Workload balancing** across teachers

### Data Models

All models inherit from a base Pydantic model with:
- **Automatic validation** of input data
- **UUID generation** for unique identification
- **Timestamp tracking** for creation and updates
- **JSON serialization** for easy export
- **Flexible metadata** storage

### Export Capabilities

- **JSON/YAML** for data interchange
- **CSV** for spreadsheet import
- **HTML** for web display and printing
- **Rich console** output with colors and tables

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`make all-checks`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Enhancements

- [ ] Web interface with FastAPI
- [ ] Database integration (SQLAlchemy)
- [ ] Genetic algorithm optimization
- [ ] REST API for integration
- [ ] Advanced reporting and analytics
- [ ] Multi-institution support
- [ ] Calendar integration
- [ ] Mobile app support

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using modern Python practices and industry standards.**
