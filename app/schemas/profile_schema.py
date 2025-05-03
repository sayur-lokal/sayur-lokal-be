# from pydantic import BaseModel, Field
# from typing import Optional

# class BuyerProfileCreate(BaseModel):
#     user_id: int
#     username: str
#     address: Optional[str] = None
#     phone_number: Optional[str] = None
#     location_lat: Optional[float] = None
#     location_lng: Optional[float] = None

# class SellerProfileCreate(BaseModel):
#     user_id: int
#     shop_name: str
#     description: Optional[str] = None
#     logo_url: Optional[str] = None
#     cover_image_url: Optional[str] = None
#     location_address: Optional[str] = None
#     location_lat: Optional[float] = None
#     location_lng: Optional[float] = None
#     bank_account: Optional[str] = None
#     qris_account: Optional[str] = None
#     is_supports_cod: Optional[bool] = True
#     phone_number: Optional[str] = None
