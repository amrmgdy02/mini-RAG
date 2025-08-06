from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    created_at: Optional[str] = Field(None)
    updated_at: Optional[str] = Field(None)

    @field_validator('project_id')
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        return v
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True  # Allows using both 'id' and '_id'
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", 1)
                ],
                "name": "idx_project_id",
                "unique": True,
            }
        ]