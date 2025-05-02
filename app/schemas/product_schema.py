from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int


class ProductCreate(ProductBase):
    seller_id: int
    image_url: Optional[List[str]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    # image_url: Optional[List[str]] = None
    # is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    seller_id: int
    # image_url: Optional[List[str]] = None
    # is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
