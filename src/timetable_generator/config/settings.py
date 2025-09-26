"""Configuration settings for the TimeTable Generator."""

import os
from typing import Dict, List, Optional, Set
from functools import lru_cache

from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from ..models.time_slot import DayOfWeek


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = Field(default="TimeTable Generator", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings (for future use)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Scheduling settings
    default_session_duration: int = Field(default=60, env="DEFAULT_SESSION_DURATION")  # minutes
    working_days: Set[DayOfWeek] = Field(
        default={DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
                DayOfWeek.THURSDAY, DayOfWeek.FRIDAY}
    )
    daily_start_time: str = Field(default="09:00", env="DAILY_START_TIME")
    daily_end_time: str = Field(default="17:00", env="DAILY_END_TIME")
    lunch_break_start: str = Field(default="12:00", env="LUNCH_BREAK_START")
    lunch_break_end: str = Field(default="13:00", env="LUNCH_BREAK_END")
    break_duration: int = Field(default=15, env="BREAK_DURATION")  # minutes
    
    # Scheduling constraints
    max_consecutive_hours: int = Field(default=3, env="MAX_CONSECUTIVE_HOURS")
    max_daily_hours_per_teacher: int = Field(default=8, env="MAX_DAILY_HOURS_PER_TEACHER")
    max_weekly_hours_per_teacher: int = Field(default=40, env="MAX_WEEKLY_HOURS_PER_TEACHER")
    prefer_morning_sessions: bool = Field(default=True, env="PREFER_MORNING_SESSIONS")
    avoid_single_hour_gaps: bool = Field(default=True, env="AVOID_SINGLE_HOUR_GAPS")
    
    # File paths
    data_directory: str = Field(default="data", env="DATA_DIRECTORY")
    export_directory: str = Field(default="exports", env="EXPORT_DIRECTORY")
    template_directory: str = Field(default="templates", env="TEMPLATE_DIRECTORY")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Export settings
    default_export_format: str = Field(default="xlsx", env="DEFAULT_EXPORT_FORMAT")
    include_metadata_in_export: bool = Field(default=True, env="INCLUDE_METADATA_IN_EXPORT")
    
    # Validation settings
    strict_validation: bool = Field(default=True, env="STRICT_VALIDATION")
    allow_teacher_overload: bool = Field(default=False, env="ALLOW_TEACHER_OVERLOAD")
    allow_classroom_double_booking: bool = Field(default=False, env="ALLOW_CLASSROOM_DOUBLE_BOOKING")
    
    # Optimization settings
    max_scheduling_attempts: int = Field(default=1000, env="MAX_SCHEDULING_ATTEMPTS")
    optimization_algorithm: str = Field(default="greedy", env="OPTIMIZATION_ALGORITHM")
    genetic_algorithm_population: int = Field(default=100, env="GA_POPULATION")
    genetic_algorithm_generations: int = Field(default=50, env="GA_GENERATIONS")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_working_hours_per_day(self) -> float:
        """Calculate working hours per day."""
        from datetime import time
        start = time.fromisoformat(self.daily_start_time)
        end = time.fromisoformat(self.daily_end_time)
        lunch_start = time.fromisoformat(self.lunch_break_start)
        lunch_end = time.fromisoformat(self.lunch_break_end)
        
        total_minutes = (end.hour - start.hour) * 60 + (end.minute - start.minute)
        lunch_minutes = (lunch_end.hour - lunch_start.hour) * 60 + (lunch_end.minute - lunch_start.minute)
        
        return (total_minutes - lunch_minutes) / 60.0
    
    def get_total_weekly_slots(self) -> int:
        """Calculate total available time slots per week."""
        daily_hours = self.get_working_hours_per_day()
        slots_per_day = int(daily_hours * 60 / self.default_session_duration)
        return slots_per_day * len(self.working_days)
    
    def get_data_file_path(self, filename: str) -> str:
        """Get full path for a data file."""
        return os.path.join(self.data_directory, filename)
    
    def get_export_file_path(self, filename: str) -> str:
        """Get full path for an export file."""
        return os.path.join(self.export_directory, filename)
    
    def get_template_file_path(self, filename: str) -> str:
        """Get full path for a template file."""
        return os.path.join(self.template_directory, filename)
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.data_directory,
            self.export_directory,
            self.template_directory
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def to_dict(self) -> Dict:
        """Convert settings to dictionary."""
        return self.dict()
    
    def update_from_dict(self, config_dict: Dict) -> None:
        """Update settings from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()