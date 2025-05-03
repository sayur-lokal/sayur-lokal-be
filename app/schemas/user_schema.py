from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRoleEnum(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_suspended: Optional[bool] = None


class BuyerProfileResponse(BaseModel):
    id: str
    username: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

    class Config:
        from_attributes = True


class SellerProfileResponse(BaseModel):
    id: str
    shop_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    location_address: Optional[str] = None
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_suspended: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    success: bool = True
    user: UserResponse
    buyer_profile: Optional[BuyerProfileResponse] = None
    seller_profile: Optional[SellerProfileResponse] = None
    admin_info: Optional[Dict[str, Any]] = None
