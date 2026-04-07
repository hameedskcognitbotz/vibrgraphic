from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    topic: str
    user_id: Optional[int] = None # Optional for now

class JobResponse(BaseModel):
    id: int
    topic: str
    status: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: int
    status: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
