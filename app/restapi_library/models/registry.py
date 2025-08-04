from typing import Dict, Type, Optional, Any
from .base import BaseModel

class ModelRegistry:
    """Registry for request/response models"""
    
    _models: Dict[str, Type[BaseModel]] = {}
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[BaseModel]) -> None:
        """Register a model class"""
        cls._models[name] = model_class
    
    @classmethod
    def get_model(cls, name: str) -> Optional[Type[BaseModel]]:
        """Get a registered model class"""
        return cls._models.get(name)
    
    @classmethod
    def create_instance(cls, name: str, data: Any) -> Optional[BaseModel]:
        """Create model instance from data"""
        model_class = cls.get_model(name)
        if model_class is None:
            return None
        
        if isinstance(data, dict):
            return model_class.from_dict(data)
        elif isinstance(data, str):
            return model_class.from_json(data)
        elif isinstance(data, model_class):
            return data
        else:
            return model_class(data)
    
    @classmethod
    def list_models(cls) -> Dict[str, Type[BaseModel]]:
        """List all registered models"""
        return cls._models.copy()