from typing import Dict, Any, Optional, Type, Union
from .base import BaseModel

class APIResponse(BaseModel):
    """Wrapper for API responses"""
    
    def __init__(self, data: Any, status_code: int, headers: Dict[str, str], 
                 response_model: Optional[Type[BaseModel]] = None):
        self.raw_data = data
        self.status_code = status_code
        self.headers = headers
        self.response_model = response_model
        self._parsed_data = None
    
    @property
    def data(self) -> Union[BaseModel, Dict, Any]:
        """Get parsed data as model or raw data"""
        if self._parsed_data is None:
            if self.response_model and isinstance(self.raw_data, dict):
                try:
                    self._parsed_data = self.response_model.from_dict(self.raw_data)
                except Exception:
                    self._parsed_data = self.raw_data
            else:
                self._parsed_data = self.raw_data
        
        return self._parsed_data
    
    @property
    def is_success(self) -> bool:
        """Check if response is successful"""
        return 200 <= self.status_code < 300
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'data': self.data.to_dict() if hasattr(self.data, 'to_dict') else self.data,
            'status_code': self.status_code,
            'headers': dict(self.headers),
            'is_success': self.is_success
        }