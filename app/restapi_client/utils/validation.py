from typing import Any, Dict, List
from ..core.exceptions import ValidationError

class Validator:
    """Parameter and model validation"""
    
    @staticmethod
    def validate_type(value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_mapping = {
            'int': int,
            'str': str,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict
        }
        
        if expected_type not in type_mapping:
            return True
        
        return isinstance(value, type_mapping[expected_type])
    
    @staticmethod
    def validate_required(params: Dict[str, Any], param_config: Dict[str, Dict]) -> None:
        """Validate required parameters"""
        for param_name, config in param_config.items():
            if config.get('required', False) and param_name not in params:
                raise ValidationError(f"Required parameter '{param_name}' is missing")
    
    @staticmethod
    def validate_params(params: Dict[str, Any], param_config: Dict[str, Dict]) -> Dict[str, Any]:
        """Validate and process parameters"""
        Validator.validate_required(params, param_config)
        
        validated_params = {}
        for param_name, value in params.items():
            if param_name in param_config:
                config = param_config[param_name]
                expected_type = config.get('type', 'str')
                
                if not Validator.validate_type(value, expected_type):
                    raise ValidationError(f"Parameter '{param_name}' must be of type {expected_type}")
                
                # Type conversion if needed
                if expected_type == 'int' and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValidationError(f"Cannot convert '{param_name}' to integer")
                
                validated_params[param_name] = value
        
        return validated_params