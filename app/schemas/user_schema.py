from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re
from app.schemas.profile_schema import BuyerProfileResponse, SellerProfileResponse


class UserRoleEnum(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        if not v or "@" not in v:
            raise ValueError("Format email tidak valid")
        if len(v) > 120:
            raise ValueError("Email tidak boleh lebih dari 120 karakter")
        return v

    @field_validator("password")
    @classmethod
    def password_must_be_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        # Validasi kompleksitas password
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password harus mengandung minimal 1 huruf besar")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password harus mengandung minimal 1 huruf kecil")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password harus mengandung minimal 1 angka")
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: UserRoleEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    buyer_profile: Optional[BuyerProfileResponse] = None
    seller_profile: Optional[SellerProfileResponse] = None


class PasswordChangeSchema(BaseModel):
    current_password: str
    new_password: str

    @field_validator("current_password")
    @classmethod
    def current_password_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Password lama harus diisi")
        return v

    @field_validator("new_password")
    @classmethod
    def new_password_must_be_valid(cls, v):
        if len(v) < 8:
            raise ValueError("Password baru minimal 8 karakter")
        # Validasi kompleksitas password
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password baru harus mengandung minimal 1 huruf besar")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password baru harus mengandung minimal 1 huruf kecil")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password baru harus mengandung minimal 1 angka")
        return v


class PasswordResetSchema(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v):
        if not v or "@" not in v:
            raise ValueError("Format email tidak valid")
        return v


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def full_name_must_be_valid(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError("Nama lengkap tidak boleh lebih dari 100 karakter")
        return v