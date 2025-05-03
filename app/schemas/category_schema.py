from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    # description: Optional[str] = Field(None, max_length=500)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    # description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    product_count: Optional[int] = None

    class Config:
        from_attributes = True
        # json_schema_extra = {
        #     "example": {
        #         "id": 1,
        #         "name": "Elektronik",
        #         "description": "Produk elektronik seperti handphone, laptop, dll",
        #         "created_at": "2023-05-01T12:00:00",
        #         "updated_at": "2023-05-01T12:00:00",
        #         "product_count": 15,
        #     }
        # }


class CategoryWithProductsResponse(CategoryResponse):
    products: List["ProductBriefResponse"] = []

    class Config:
        from_attributes = True


# Untuk menghindari circular import
class ProductBriefResponse(BaseModel):
    """
    Skema untuk respons ringkas produk (digunakan dalam daftar produk kategori)
    """

    id: int
    name: str
    price: float
    image_url: Optional[str] = None
    seller_id: int
    seller_name: Optional[str] = None

    class Config:
        from_attributes = True
