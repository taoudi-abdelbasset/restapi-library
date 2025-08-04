from typing import Dict, Any, Optional, List
from .core.client import APIClient
from .core.config import ConfigParser
from .core.exceptions import *
from .models.base import BaseModel
from .models.registry import ModelRegistry
from .cache.factory import CacheFactory
from .utils.logging import APILogger

class RestAPILibrary:
    """Main library interface"""
    
    _redis_config: Optional[Dict[str, Any]] = None
    _global_logger: Optional[APILogger] = None
    _clients: Dict[str, APIClient] = {}
    
    def __init__(self, config_path: Optional[str] = None, 
                 config_dict: Optional[Dict] = None,
                 env_file: Optional[str] = '.env',
                 logger: Optional[APILogger] = None):
        """
        Initialize REST API Library
        
        Args:
            config_path: Path to JSON configuration file
            config_dict: Configuration dictionary (alternative to file)
            env_file: Path to .env file for environment variables
            logger: Custom logger instance
        """
        
        # Initialize configuration parser
        self.config_parser = ConfigParser(config_path, config_dict, env_file)
        
        # Set global logger
        self.logger = logger or APILogger()
        RestAPILibrary._global_logger = self.logger
        
        # Set Redis config if provided
        if RestAPILibrary._redis_config:
            CacheFactory.set_redis_config(RestAPILibrary._redis_config)
        
        # Initialize API clients
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize all API clients from configuration"""
        for api_name in self.config_parser.config.keys():
            try:
                client = APIClient(api_name, self.config_parser, self.logger)
                setattr(self, api_name.replace('-', '_'), client)
                RestAPILibrary._clients[api_name] = client
                
                self.logger.logger.info(f"Initialized API client: {api_name}")
            except Exception as e:
                self.logger.logger.error(f"Failed to initialize API client {api_name}: {e}")
                raise ConfigurationError(f"Failed to initialize API client {api_name}: {e}")
    
    @classmethod
    def set_redis_config(cls, redis_config: Dict[str, Any]) -> None:
        """
        Set global Redis configuration
        
        Args:
            redis_config: Redis connection parameters
            
        Example:
            RestAPILibrary.set_redis_config({
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": "mypassword"
            })
        """
        cls._redis_config = redis_config
        CacheFactory.set_redis_config(redis_config)
        
        if cls._global_logger:
            cls._global_logger.logger.info("Redis configuration updated")
    
    @classmethod
    def register_model(cls, name: str, model_class: type) -> None:
        """
        Register a model class for request/response handling
        
        Args:
            name: Model name to use in configuration
            model_class: Model class (should inherit from BaseModel)
            
        Example:
            class UserModel(BaseModel):
                def __init__(self, name: str, email: str):
                    self.name = name
                    self.email = email
            
            RestAPILibrary.register_model('UserModel', UserModel)
        """
        if not issubclass(model_class, BaseModel):
            raise ConfigurationError(f"Model class must inherit from BaseModel")
        
        ModelRegistry.register_model(name, model_class)
        
        if cls._global_logger:
            cls._global_logger.logger.info(f"Registered model: {name}")
    
    def get_client(self, api_name: str) -> APIClient:
        """
        Get API client by name
        
        Args:
            api_name: Name of the API
            
        Returns:
            APIClient instance
        """
        if api_name not in RestAPILibrary._clients:
            raise ConfigurationError(f"API client '{api_name}' not found")
        
        return RestAPILibrary._clients[api_name]
    
    def list_apis(self) -> List[str]:
        """List all available API names"""
        return list(RestAPILibrary._clients.keys())
    
    def reload_config(self, config_path: Optional[str] = None, 
                     config_dict: Optional[Dict] = None) -> None:
        """
        Reload configuration and reinitialize clients
        
        Args:
            config_path: New configuration file path
            config_dict: New configuration dictionary
        """
        # Clear existing clients
        RestAPILibrary._clients.clear()
        
        # Remove client attributes
        for api_name in self.config_parser.config.keys():
            attr_name = api_name.replace('-', '_')
            if hasattr(self, attr_name):
                delattr(self, attr_name)
        
        # Reload configuration
        if config_path or config_dict:
            self.config_parser = ConfigParser(config_path, config_dict)
        
        # Reinitialize clients
        self._initialize_clients()
        
        self.logger.logger.info("Configuration reloaded successfully")