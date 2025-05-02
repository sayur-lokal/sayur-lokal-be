from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RatingBase(BaseModel):
    buyer_id: int
    product_id: int
    order_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    
class RatingCreate(RatingBase):
    pass
    
class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
    
class RatingResponse(RatingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True