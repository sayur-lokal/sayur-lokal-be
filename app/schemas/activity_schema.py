from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ActivityBase(BaseModel):
    """Schema dasar untuk aktivitas"""
    activity_type: str = Field(..., description="Tipe aktivitas")
    description: str = Field(..., description="Deskripsi aktivitas")
    reference_id: Optional[int] = Field(None, description="ID referensi")

class ActivityCreate(ActivityBase):
    """Schema untuk membuat aktivitas baru"""
    seller_id: int = Field(..., description="ID seller")

class ActivityResponse(ActivityBase):
    """Schema untuk response aktivitas"""
    id: int = Field(..., description="ID aktivitas")
    seller_id: int = Field(..., description="ID seller")
    created_at: datetime = Field(..., description="Waktu pembuatan")

    class Config:
        from_attributes = True