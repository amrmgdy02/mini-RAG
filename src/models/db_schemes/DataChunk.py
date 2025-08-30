from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True  # Allows using both 'id' and '_id'
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "name": "idx_chunk_project_id",
                "unique": False,
            }
        ]