import json
from abc import ABC
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime

class BaseModel(ABC):
    """Base class for all request/response models"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        if is_dataclass(self):
            result = {}
            for field in fields(self):
                value = getattr(self, field.name)
                if hasattr(value, 'to_dict'):
                    result[field.name] = value.to_dict()
                else:
                    result[field.name] = value
            return result
        
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return json.dumps(self.to_dict(), default=self._json_serializer)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        if is_dataclass(cls):
            field_types = {f.name: f.type for f in fields(cls)}
            processed_data = {}
            
            for field_name, field_type in field_types.items():
                if field_name in data:
                    value = data[field_name]
                    if (hasattr(field_type, '__origin__') is False and 
                        isinstance(field_type, type) and 
                        issubclass(field_type, BaseModel)):
                        if isinstance(value, dict):
                            processed_data[field_name] = field_type.from_dict(value)
                        else:
                            processed_data[field_name] = value
                    else:
                        processed_data[field_name] = value
            
            return cls(**processed_data)
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create model instance from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    @staticmethod
    def _json_serializer(obj):
        """Custom JSON serializer for complex objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def validate(self) -> bool:
        """Validate model data - override in subclasses"""
        return True
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"