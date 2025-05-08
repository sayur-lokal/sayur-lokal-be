from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class BuyerProfileCreate(BaseModel):
    user_id: int
    username: str = Field(min_length=3, max_length=50)
    address: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v):
        if not v:
            raise ValueError("Username harus diisi")
        if len(v) < 3:
            raise ValueError("Username minimal 3 karakter")
        if len(v) > 50:
            raise ValueError("Username maksimal 50 karakter")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username hanya boleh berisi huruf, angka, dan underscore")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_number_must_be_valid(cls, v):
        if v is not None:
            if not re.match(r"^[0-9+\-\s]+$", v):
                raise ValueError("Nomor telepon hanya boleh berisi angka, +, -, dan spasi")
            if len(v) < 8 or len(v) > 20:
                raise ValueError("Nomor telepon harus antara 8-20 karakter")
        return v

    @field_validator("profile_picture_url")
    @classmethod
    def profile_picture_url_must_be_valid(cls, v):
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL foto profil harus diawali dengan http:// atau https://")
        return v


class BuyerProfileUpdate(BaseModel):
    username: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Username minimal 3 karakter")
            if len(v) > 50:
                raise ValueError("Username maksimal 50 karakter")
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError("Username hanya boleh berisi huruf, angka, dan underscore")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_number_must_be_valid(cls, v):
        if v is not None:
            if not re.match(r"^[0-9+\-\s]+$", v):
                raise ValueError("Nomor telepon hanya boleh berisi angka, +, -, dan spasi")
            if len(v) < 8 or len(v) > 20:
                raise ValueError("Nomor telepon harus antara 8-20 karakter")
        return v


class BuyerProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class SellerProfileCreate(BaseModel):
    user_id: int
    shop_name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    bank_account: Optional[str] = None
    qris_account: Optional[str] = None
    is_supports_cod: bool = True
    phone_number: Optional[str] = None

    @field_validator("shop_name")
    @classmethod
    def shop_name_must_be_valid(cls, v):
        if not v:
            raise ValueError("Nama toko harus diisi")
        if len(v) < 3:
            raise ValueError("Nama toko minimal 3 karakter")
        if len(v) > 100:
            raise ValueError("Nama toko maksimal 100 karakter")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_number_must_be_valid(cls, v):
        if v is not None:
            if not re.match(r"^[0-9+\-\s]+$", v):
                raise ValueError("Nomor telepon hanya boleh berisi angka, +, -, dan spasi")
            if len(v) < 8 or len(v) > 20:
                raise ValueError("Nomor telepon harus antara 8-20 karakter")
        return v

    @field_validator("logo_url", "cover_image_url")
    @classmethod
    def url_must_be_valid(cls, v):
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL gambar harus diawali dengan http:// atau https://")
        return v


class SellerProfileUpdate(BaseModel):
    shop_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    bank_account: Optional[str] = None
    qris_account: Optional[str] = None
    is_supports_cod: Optional[bool] = None
    phone_number: Optional[str] = None

    @field_validator("shop_name")
    @classmethod
    def shop_name_must_be_valid(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Nama toko minimal 3 karakter")
            if len(v) > 100:
                raise ValueError("Nama toko maksimal 100 karakter")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_number_must_be_valid(cls, v):
        if v is not None:
            if not re.match(r"^[0-9+\-\s]+$", v):
                raise ValueError("Nomor telepon hanya boleh berisi angka, +, -, dan spasi")
            if len(v) < 8 or len(v) > 20:
                raise ValueError("Nomor telepon harus antara 8-20 karakter")
        return v


class SellerProfileResponse(BaseModel):
    id: int
    user_id: int
    shop_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    bank_account: Optional[str] = None
    qris_account: Optional[str] = None
    is_supports_cod: bool
    phone_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None