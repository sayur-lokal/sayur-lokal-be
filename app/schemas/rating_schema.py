from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class RatingBase(BaseModel):
    product_id: int
    order_id: int
    rating: int = Field(ge=1, le=5, description="Rating harus antara 1-5")
    comment: Optional[str] = None

class RatingCreate(RatingBase):
    @field_validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating harus antara 1 sampai 5')
        return v

class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Rating harus antara 1-5")
    comment: Optional[str] = None

    @field_validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating harus antara 1 sampai 5')
        return v

class RatingResponse(BaseModel):
    id: int
    product_id: int
    buyer_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True