from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union, Literal
from datetime import datetime

class BrandKitPayload(BaseModel):
    brand_name: Optional[str] = None
    social_handle: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    cta_text: Optional[str] = None
    logo_url: Optional[str] = None

class JobCreate(BaseModel):
    topic: str
    audience: Optional[str] = "general" # can be 'educator', 'creator', etc.
    format: Optional[str] = "infographic" # 'infographic' or 'carousel'
    tone: Optional[str] = "Educational"
    user_id: Optional[int] = None
    template_key: Optional[str] = None
    export_preset: Optional[str] = None
    source_job_id: Optional[int] = None
    brand_kit: Optional[BrandKitPayload] = None
    generation_mode: Optional[Literal["creative", "grounded"]] = "creative"

class JobResponse(BaseModel):
    id: int
    topic: str
    status: str
    tone: Optional[str] = "Educational"
    result_url: Optional[Union[str, List[str]]] = None
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: int
    topic: Optional[str] = None
    status: str
    result_url: Optional[Union[str, List[str]]] = None
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
