from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int

    @field_validator("name")
    @classmethod
    def validate_product_name(cls, v):
        # Validasi nama produk tidak boleh kosong
        if v.strip() == "":
            raise ValueError("Nama produk tidak boleh kosong")

        # Validasi nama produk harus diawali dengan huruf kapital
        if not v[0].isupper():
            raise ValueError("Nama produk harus diawali dengan huruf kapital")

        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        # Validasi harga tidak boleh terlalu tinggi (misalnya maksimal 1 miliar)
        if v > 1_000_000_000:
            raise ValueError("Harga produk terlalu tinggi (maksimal 1 miliar)")
        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v):
        # Validasi stok tidak boleh terlalu tinggi (misalnya maksimal 1 juta)
        if v > 1_000_000:
            raise ValueError("Stok produk terlalu tinggi (maksimal 1 juta)")
        return v


class ProductCreate(ProductBase):
    seller_id: int
    product_image_url: Optional[str] = None
    discount: Optional[float] = Field(default=0, ge=0, le=100)

    @field_validator("product_image_url")
    @classmethod
    def validate_image_url(cls, v):
        if v is None:
            return v

        # Validasi format URL gambar
        url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        if not re.match(url_pattern, v):
            raise ValueError("Format URL gambar tidak valid")

        # Validasi ekstensi file gambar
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError("URL harus mengarah ke file gambar (jpg, jpeg, png, gif, webp)")

        return v

    @field_validator("discount")
    @classmethod
    def validate_discount(cls, v):
        if v is None:
            return 0

        # Validasi diskon harus dalam rentang 0-100
        if v < 0 or v > 100:
            raise ValueError("Diskon harus dalam rentang 0-100 persen")

        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, min_length=10)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    product_image_url: Optional[str] = None
    discount: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator("name")
    @classmethod
    def validate_product_name(cls, v):
        if v is None:
            return v

        # Validasi nama produk tidak boleh kosong
        if v.strip() == "":
            raise ValueError("Nama produk tidak boleh kosong")

        # Validasi nama produk harus diawali dengan huruf kapital
        if not v[0].isupper():
            raise ValueError("Nama produk harus diawali dengan huruf kapital")

        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is None:
            return v

        # Validasi harga tidak boleh terlalu tinggi (misalnya maksimal 1 miliar)
        if v > 1_000_000_000:
            raise ValueError("Harga produk terlalu tinggi (maksimal 1 miliar)")

        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v):
        if v is None:
            return v

        # Validasi stok tidak boleh terlalu tinggi (misalnya maksimal 1 juta)
        if v > 1_000_000:
            raise ValueError("Stok produk terlalu tinggi (maksimal 1 juta)")

        return v

    @field_validator("product_image_url")
    @classmethod
    def validate_image_url(cls, v):
        if v is None:
            return v

        # Validasi format URL gambar
        url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        if not re.match(url_pattern, v):
            raise ValueError("Format URL gambar tidak valid")

        # Validasi ekstensi file gambar
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError("URL harus mengarah ke file gambar (jpg, jpeg, png, gif, webp)")

        return v

    @field_validator("discount")
    @classmethod
    def validate_discount(cls, v):
        if v is None:
            return v

        # Validasi diskon harus dalam rentang 0-100
        if v < 0 or v > 100:
            raise ValueError("Diskon harus dalam rentang 0-100 persen")

        return v


class ProductResponse(ProductBase):
    id: int
    seller_id: int
    product_image_url: Optional[str] = None
    discount: float = 0
    created_at: datetime
    updated_at: datetime

    @property
    def final_price(self) -> float:
        """Menghitung harga setelah diskon"""
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    model_config = {"from_attributes": True}


class ProductDetailResponse(ProductResponse):
    seller_name: Optional[str] = None
    category_name: Optional[str] = None
    final_price: Optional[float] = None

    @field_validator("final_price", mode="before")
    @classmethod
    def calculate_final_price(cls, v, info):
        # Menghitung harga setelah diskon
        values = info.data
        price = values.get("price", 0)
        discount = values.get("discount", 0)

        if discount > 0:
            return price - (price * discount / 100)
        return price