from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=200)
    created_at: str
    updated_at: str
    
    @field_validator('project_id')
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        return v
    
    class Config:
        arbitrary_types_allowed = True