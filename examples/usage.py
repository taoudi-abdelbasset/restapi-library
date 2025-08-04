from restapi_library import RestAPILibrary, BaseModel
from dataclasses import dataclass
from typing import Optional

# Define custom models
@dataclass
class UserModel(BaseModel):
    """User model for API requests/responses"""
    name: str
    email: str
    age: Optional[int] = None
    
    def validate(self) -> bool:
        """Custom validation"""
        return "@" in self.email and len(self.name) > 0

@dataclass
class PaymentModel(BaseModel):
    """Payment model"""
    amount: float
    currency: str
    user_id: int
    
    def validate(self) -> bool:
        return self.amount > 0 and len(self.currency) == 3

def main():
    # Set Redis configuration (optional)
    RestAPILibrary.set_redis_config({
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None
    })
    
    # Register models
    RestAPILibrary.register_model('UserModel', UserModel)
    RestAPILibrary.register_model('PaymentModel', PaymentModel)
    
    # Initialize library with configuration
    api = RestAPILibrary(
        config_path="examples/config.json",
        env_file="examples/.env"
    )
    
    try:
        # Example 1: GET request with path parameters
        user_response = api.api_payment.get_user(params={'user_id': 123})
        print("User:", user_response)
        
        # Example 2: POST request with model
        new_user = UserModel(name="John Doe", email="john@example.com", age=30)
        create_response = api.api_payment.create_user(body=new_user)
        print("Created user:", create_response)
        
        # Example 3: Using different API version
        user_v2 = api.api_payment.get_user_v2(params={'user_id': 123})
        print("User (v2):", user_v2)
        
        # Example 4: Custom headers and parameters
        custom_response = api.api_payment.get_user(
            params={'user_id': 456},
            headers={'X-Custom-Header': 'value'},
            timeout=60
        )
        print("Custom request:", custom_response)
        
        # Example 5: Error handling
        try:
            error_response = api.api_payment.get_user(params={'user_id': -1})
        except Exception as e:
            print(f"Error: {e}")
        
    except Exception as e:
        print(f"Failed to execute API calls: {e}")

if __name__ == "__main__":
    main()