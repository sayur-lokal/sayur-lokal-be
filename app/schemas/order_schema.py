# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime
# from enum import Enum

# class OrderStatusEnum(str, Enum):
#     PENDING = "pending"
#     PAID = "paid"
#     SHIPPED = "shipped"
#     DELIVERED = "delivered"
#     CANCELLED = "cancelled"

# class OrderItemBase(BaseModel):
#     product_id: int
#     quantity: int = Field(gt=0)
#     price_per_unit: float = Field(gt=0)

# class OrderItemCreate(OrderItemBase):
#     pass

# class OrderItemResponse(OrderItemBase):
#     id: int
#     subtotal: float

#     class Config:
#         from_attributes = True

# class OrderBase(BaseModel):
#     buyer_id: int
#     shipping_address: str

# class OrderCreate(OrderBase):
#     items: List[OrderItemCreate]

# class OrderUpdate(BaseModel):
#     status: Optional[OrderStatusEnum] = None
#     shipping_address: Optional[str] = None

# class OrderResponse(OrderBase):
#     id: int
#     order_number: str
#     status: OrderStatusEnum
#     total_amount: float
#     items: List[OrderItemResponse]
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True
