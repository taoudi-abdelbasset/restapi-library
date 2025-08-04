import json
from restapi_library import RestAPILibrary, BaseModel
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class ObjectDOMModel(BaseModel):
    name: str
    data: Optional[Dict[str, Any]] = None
    
    def validate(self) -> bool:
        """Custom validation for request body"""
        return len(self.name) > 0

@dataclass
class ObjectModel(BaseModel):  # Removed inheritance from ObjectDOMModel for clarity
    id: str
    name: str
    createdat: str  # Match API's camelCase field name
    data: Optional[Dict[str, Any]] = None
    
    def validate(self) -> bool:
        """Custom validation for response model"""
        return len(self.id) > 0 and len(self.name) > 0 and len(self.createdAt) > 0

@dataclass
class ObjectListModel(BaseModel):
    """Model for API response containing a list of objects"""
    items: List[ObjectDOMModel]
    
    def validate(self) -> bool:
        """Custom validation for list model"""
        return isinstance(self.items, list) and all(item.validate() for item in self.items)

def main():
    try:
        # Register models
        RestAPILibrary.register_model('ObjectDOMModel', ObjectDOMModel)
        RestAPILibrary.register_model('ObjectModel', ObjectModel)
        RestAPILibrary.register_model('ObjectListModel', ObjectListModel)

        # Initialize library with configuration
        api = RestAPILibrary(
            config_path="./config.json",
            env_file="./.env"
        )

        # # Print start message in JSON
        # print(json.dumps({"message": "Executing API calls... Config loaded successfully"}, indent=2))

        # # GET request for getObjectByID with id=ff8081819782e69e019874d73ddf231f
        # response = api.example_api.getObjectByID(params={'id': 'ff8081819782e69e019874d73ddf231f'})
        # print(json.dumps({"object_by_id": response.to_dict()}, indent=2))

        # Print start message in JSON
        print(json.dumps({"message": "Executing API calls... Config loaded successfully"}, indent=2))

        # GET request for getObjectsByIDs with id=3,5,10
        response = api.example_api.objectsList()
        print(json.dumps({"objects_by_ids": response.to_dict()}, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))

if __name__ == "__main__":
    main()