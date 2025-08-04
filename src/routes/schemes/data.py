from pydantic import BaseModel
from typing import Optional

class ProcessFileRequest(BaseModel):
    filename: str
    chunk_size: Optional[int] = 100
    overlap: Optional[int] = 20 