from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
import re


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_category_name(cls, v):
        # Validasi format nama kategori
        if not re.match(r"^[a-zA-Z0-9\s&\-]+$", v):
            raise ValueError(
                "Nama kategori hanya boleh berisi huruf, angka, spasi, &, dan tanda hubung"
            )

        # Validasi tidak boleh hanya berisi spasi
        if v.strip() == "":
            raise ValueError("Nama kategori tidak boleh kosong")

        # Validasi kapitalisasi (kata pertama kapital)
        words = v.split()
        if words and not words[0][0].isupper():
            raise ValueError("Nama kategori harus diawali dengan huruf kapital")

        # Validasi tidak boleh ada spasi berlebih
        if "  " in v:
            raise ValueError("Nama kategori tidak boleh mengandung spasi ganda")

        # Validasi tidak boleh diawali atau diakhiri dengan spasi
        if v != v.strip():
            raise ValueError("Nama kategori tidak boleh diawali atau diakhiri dengan spasi")

        # Validasi tidak boleh mengandung karakter khusus berurutan
        if re.search(r"[-&]{2,}", v):
            raise ValueError("Nama kategori tidak boleh mengandung karakter khusus berurutan")

        return v


class CategoryCreate(CategoryBase):
    @model_validator(mode="after")
    def normalize_name(self):
        """Normalisasi nama kategori: kapitalisasi kata pertama dan hapus spasi berlebih"""
        if self.name:
            # Hapus spasi di awal dan akhir
            name = self.name.strip()
            # Kapitalisasi kata pertama
            if name:
                name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
            # Hapus spasi ganda
            while "  " in name:
                name = name.replace("  ", " ")
            self.name = name
        return self


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_category_name(cls, v):
        if v is None:
            return v

        # Validasi format nama kategori
        if not re.match(r"^[a-zA-Z0-9\s&\-]+$", v):
            raise ValueError(
                "Nama kategori hanya boleh berisi huruf, angka, spasi, &, dan tanda hubung"
            )

        # Validasi tidak boleh hanya berisi spasi
        if v.strip() == "":
            raise ValueError("Nama kategori tidak boleh kosong")

        # Validasi kapitalisasi (kata pertama kapital)
        words = v.split()
        if words and not words[0][0].isupper():
            raise ValueError("Nama kategori harus diawali dengan huruf kapital")

        # Validasi tidak boleh ada spasi berlebih
        if "  " in v:
            raise ValueError("Nama kategori tidak boleh mengandung spasi ganda")

        # Validasi tidak boleh diawali atau diakhiri dengan spasi
        if v != v.strip():
            raise ValueError("Nama kategori tidak boleh diawali atau diakhiri dengan spasi")

        # Validasi tidak boleh mengandung karakter khusus berurutan
        if re.search(r"[-&]{2,}", v):
            raise ValueError("Nama kategori tidak boleh mengandung karakter khusus berurutan")

        return v

    @model_validator(mode="after")
    def normalize_name(self):
        """Normalisasi nama kategori: kapitalisasi kata pertama dan hapus spasi berlebih"""
        if self.name:
            # Hapus spasi di awal dan akhir
            name = self.name.strip()
            # Kapitalisasi kata pertama
            if name:
                name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
            # Hapus spasi ganda
            while "  " in name:
                name = name.replace("  ", " ")
            self.name = name
        return self


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    product_count: Optional[int] = None

    model_config = {"from_attributes": True}


class CategoryWithProductsResponse(CategoryResponse):
    products: List["ProductBriefResponse"] = []

    model_config = {"from_attributes": True}


# Untuk menghindari circular import
class ProductBriefResponse(BaseModel):
    id: int
    name: str
    price: float
    image_url: Optional[str] = None
    seller_id: int
    seller_name: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Harga tidak boleh negatif")
        return v

    @field_validator("name")
    @classmethod
    def validate_product_name(cls, v):
        if len(v) < 3:
            raise ValueError("Nama produk minimal 3 karakter")
        return v