"""Base model class for all timetable entities."""

from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar
from uuid import uuid4

from pydantic import BaseModel as PydanticBaseModel, Field

T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel, ABC):
    """Base model class with common fields and methods for all timetable entities."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        
    def update(self: T, **kwargs: Any) -> T:
        """Update model fields and set updated_at timestamp."""
        update_data = kwargs.copy()
        update_data['updated_at'] = datetime.now()
        
        for field, value in update_data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the model."""
        return f"{self.__class__.__name__}({self.dict()})"