"""Custom exceptions for timetable generation operations."""


class TimeTableError(Exception):
    """Base exception for all timetable-related errors."""
    
    def __init__(self, message: str, details: str = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class SchedulingConflictError(TimeTableError):
    """Raised when there's a scheduling conflict (time, resource, etc.)."""
    
    def __init__(self, message: str, conflicting_resources: list = None) -> None:
        self.conflicting_resources = conflicting_resources or []
        super().__init__(message)


class ResourceNotAvailableError(TimeTableError):
    """Raised when a required resource is not available."""
    
    def __init__(self, resource_type: str, resource_id: str, time_slot: str = None) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.time_slot = time_slot
        
        message = f"{resource_type} '{resource_id}' is not available"
        if time_slot:
            message += f" at {time_slot}"
        
        super().__init__(message)


class InvalidConfigurationError(TimeTableError):
    """Raised when configuration is invalid or incomplete."""
    
    def __init__(self, config_field: str, reason: str) -> None:
        self.config_field = config_field
        self.reason = reason
        message = f"Invalid configuration for '{config_field}': {reason}"
        super().__init__(message)